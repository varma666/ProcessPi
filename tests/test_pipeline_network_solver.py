"""Regression tests for the pipeline network solver.

Each test pins down a defect that made the network results wrong rather than
merely inconvenient: a total that ignored friction, minor losses counted twice,
parallel branches whose drops were added, a flow split that did not conserve
mass, network sizing that applied nothing, and pumps and equipment that were
dropped from the network.
"""

import contextlib
import io

import pytest

from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.equipment import Equipment
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.pumps import Pump
from processpi.units import Diameter, Length, Pressure, VolumetricFlowRate


def _run(engine):
    """Run the engine without its progress printing."""
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.run()


def _engine(**kwargs):
    engine = PipelineEngine()
    engine.fit(fluid=Water(), **kwargs)
    return engine


def test_series_network_total_is_sum_of_element_drops():
    """The reported total must carry the friction of every element."""
    p1 = Pipe("P1", nominal_diameter=Diameter(4, "in"), length=Length(100, "m"))
    p2 = Pipe("P2", nominal_diameter=Diameter(4, "in"), length=Length(50, "m"))
    net = PipelineNetwork.series("S", p1, p2)

    engine = _engine(flowrate=VolumetricFlowRate(50, "m3/h"), network=net)
    results = _run(engine).results

    element_total = sum(
        c["total_dp"].to("Pa").value for c in results["components"]
    )
    assert element_total > 0
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        element_total, rel=1e-9
    )


def test_single_pipe_total_does_not_double_count_minor_losses():
    """`pressure_drop` already holds major + minor + elevation."""
    engine = _engine(
        flowrate=VolumetricFlowRate(50, "m3/h"),
        diameter=Diameter(102.3, "mm"),
        length=Length(100, "m"),
        fittings=[Fitting("standard_elbow_90_deg", quantity=4)],
    )
    results = _run(engine).results
    component = results["components"][0]

    expected = sum(
        component[key].to("Pa").value
        for key in ("major_dp", "minor_dp", "elevation_dp")
    )
    assert component["minor_dp"].to("Pa").value > 0
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        expected, rel=1e-9
    )


def test_identical_parallel_branches_share_one_pressure_drop():
    """Two identical branches drop the same as one of them, not twice as much."""
    q_total = VolumetricFlowRate(100 / 3600, "m3/s")
    engine = _engine(flowrate=q_total)

    branch_a = [Pipe("A", nominal_diameter=Diameter(4, "in"), length=Length(100, "m"))]
    branch_b = [Pipe("B", nominal_diameter=Diameter(4, "in"), length=Length(100, "m"))]

    dp_one, _, _ = engine._compute_network(
        branch_a, VolumetricFlowRate(q_total.value / 2, "m3/s")
    )
    dp_both, _, _ = engine._compute_network([branch_a, branch_b], q_total)

    assert dp_both.to("Pa").value == pytest.approx(dp_one.to("Pa").value, rel=1e-6)


def test_parallel_split_conserves_mass_and_equalises_branch_drops():
    """Unequal branches must split the flow, not multiply it."""
    q_total = 100 / 3600
    branch_a = Pipe("A", nominal_diameter=Diameter(4, "in"), length=Length(100, "m"))
    branch_b = Pipe("B", nominal_diameter=Diameter(6, "in"), length=Length(100, "m"))
    net = PipelineNetwork.parallel("PAR", branch_a, branch_b)

    engine = _engine(flowrate=VolumetricFlowRate(q_total, "m3/s"), network=net)
    solved, _ = engine._solve_network_dual(net, VolumetricFlowRate(q_total, "m3/s"))

    flows = solved["branch_flows"]
    assert solved["success"] is True
    # VolumetricFlowRate rounds to 6 decimals in m3/s, so mass closes to that.
    assert sum(flows) == pytest.approx(q_total, rel=1e-4)
    assert all(q > 0 for q in flows)
    # The wider branch takes the larger share.
    assert flows[1] > flows[0]

    dps = [
        engine._evaluate_block(branch, VolumetricFlowRate(q, "m3/s"))[0]
        for branch, q in zip([branch_a, branch_b], flows)
    ]
    assert dps[0] == pytest.approx(dps[1], rel=1e-3)


def test_network_diameter_sizing_assigns_an_internal_diameter():
    """Sizing a network must reach its pipes and apply an internal diameter."""
    pipe = Pipe("U", length=Length(100, "m"))
    net = PipelineNetwork.series("SU", pipe)

    engine = _engine(
        flowrate=VolumetricFlowRate(50, "m3/h"),
        network=net,
        available_dp=Pressure(50000, "Pa"),
    )
    with contextlib.redirect_stdout(io.StringIO()):
        sizing = engine._solve_for_diameter_network(
            net, fluid=Water(), available_dp=Pressure(50000, "Pa")
        )

    sized = sizing.results["all_simulation_results"]
    assert len(sized) == 1

    assert pipe.internal_diameter is not None
    nominal = sized[0]["components"][0]["nominal_diameter"]
    internal = sized[0]["components"][0]["diameter"]
    # The applied value is the bore for that nominal size, not the nominal size.
    assert internal.to("m").value == pytest.approx(
        pipe.internal_diameter.to("m").value
    )
    assert internal.to("m").value != pytest.approx(nominal.to("m").value)


def test_pump_and_equipment_reach_the_network_result():
    """A pump adds head and a heat exchanger adds drop; neither may be dropped."""
    pipe = Pipe("P", nominal_diameter=Diameter(4, "in"), length=Length(100, "m"))
    pump = Pump("PU", pump_type="centrifugal", head=Length(20, "m"))
    exchanger = Equipment("HX", pressure_drop=0.5)
    net = PipelineNetwork.series("SP", pipe, pump, exchanger)

    engine = _engine(flowrate=VolumetricFlowRate(50, "m3/h"), network=net)
    results = _run(engine).results

    names = [c.get("name") for c in results["components"]]
    assert names == ["P", "PU", "HX"]

    by_name = {c["name"]: c for c in results["components"]}
    pipe_dp = by_name["P"]["pressure_drop_Pa"]
    pump_dp = by_name["PU"]["pressure_drop_Pa"]
    hx_dp = by_name["HX"]["pressure_drop_Pa"]

    assert pump_dp < 0  # a pump raises the pressure
    assert hx_dp == pytest.approx(50000.0)  # 0.5 bar
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        pipe_dp + pump_dp + hx_dp, rel=1e-9
    )


def test_pump_gain_uses_density_object_and_head_length():
    """`Pump.density` is a Density and `Pump.head` a Length; both must convert."""
    pump = Pump("PU", pump_type="centrifugal", head=Length(20, "m"))
    engine = _engine(flowrate=VolumetricFlowRate(50, "m3/h"))

    gain = engine._pump_gain_pa(pump)
    assert gain.to("Pa").value == pytest.approx(1000 * 9.80665 * 20, rel=1e-6)
