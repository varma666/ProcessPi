"""Regression tests for heat exchanger convergence reporting and crashes.

The U iteration called a 30% step converged, its verdict never reached the
result, warnings raised inside it were thrown away, every design run reported
status "UNKNOWN", and the phase-change exchangers either crashed or reported
zero pressure drop because they read a velocity keyword nobody passes.
"""

import contextlib
import io

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import (
    HeatTransferCoefficient,
    MassFlowRate,
    Pressure,
    Temperature,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _benzene_cooler(**extra):
    """The benzene cooler from docs/examples/equipment/heatexchanger."""
    hot_in = MaterialStream("hot_in", component=Benzene(),
                            temperature=Temperature(90, "C"),
                            mass_flow=MassFlowRate(21000, "kg/h"))
    hot_out = MaterialStream("hot_out", component=Benzene(),
                             temperature=Temperature(30, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(15, "C"),
                             mass_flow=MassFlowRate(60500, "kg/h"))
    cold_out = MaterialStream("cold_out", component=Water())
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out,
               U=HeatTransferCoefficient(575, "W/m2K"),
               shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
               mode="design", **extra)
    return engine


def _phase_change_engine(hx_type, **extra):
    hot_in = MaterialStream("hot_in", component=Water(),
                            temperature=Temperature(120, "C"),
                            pressure=Pressure(2, "bar"),
                            mass_flow=MassFlowRate(3, "kg/s"), phase="vapor")
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(25, "C"),
                             pressure=Pressure(2, "bar"),
                             mass_flow=MassFlowRate(10, "kg/s"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, cold_in=cold_in, hx_type=hx_type, mode="design",
               orientation="horizontal", **extra)
    return engine


def test_results_before_run_raises():
    engine = _benzene_cooler()
    with pytest.raises(RuntimeError):
        engine.results()


def test_results_after_run_are_returned():
    engine = _benzene_cooler()
    _quiet(engine.run)
    assert engine.results() is not None


def test_convergence_tolerance_is_honoured():
    """The first U step is about 10% out; only a tolerance above it may accept it.

    That step size belongs to the benzene-in-tubes arrangement, which the fluid
    assignment no longer picks by default for this case (it puts the water in
    the tubes), so the arrangement is forced to keep the test on the case it
    was calibrated for.
    """
    loose = _quiet(_benzene_cooler(u_tolerance_percent=15.0, force_hot_in_tubes=True).run).data
    assert loose["converged"] is True
    assert len(loose["convergence_history"]) == 1
    assert 5.0 < loose["convergence_history"][0] < 15.0

    # With the bundle diameter for the settled pass count, the default 0.8
    # relaxation walks this case into a 168/174 tube cycle, which the cycle rule
    # settles (tested below) before the 1% test is reached. Plain successive
    # substitution (relaxation 1.0) reaches the tolerance test.
    tight = _quiet(_benzene_cooler(u_tolerance_percent=1.0, force_hot_in_tubes=True,
                                   u_relaxation=1.0).run).data
    assert tight["converged"] is True
    assert len(tight["convergence_history"]) > 1
    assert tight["convergence_history"][-1] < 1.0
    assert not any("cycles between tube counts" in w for w in tight["warnings"])
    # The settled area is within 5% of what its own U requires.
    assert tight["status"] == "MARGINAL"


def test_failed_convergence_reaches_the_status():
    data = _quiet(_benzene_cooler(u_tolerance_percent=1.0, max_u_iterations=2).run).data
    assert data["converged"] is False
    assert data["status"] == "FAILED_CONVERGENCE"
    assert any("CONVERGENCE_WARNING" in w for w in data["warnings"])


def test_design_status_is_never_unknown():
    for tolerance in (1.0, 5.0, 30.0):
        data = _quiet(_benzene_cooler(u_tolerance_percent=tolerance).run).data
        assert data["status"] != "UNKNOWN"
        assert data["status"] is not None


def test_warnings_raised_inside_the_iteration_survive(monkeypatch):
    """The hydraulic and convergence warnings are raised during _iterate_U.

    The cooler's own HYDRAULIC_WARNING came from its first pass (shell velocity
    0.462 m/s, where the reported one is 0.503 m/s) and is no longer carried
    once warnings are kept per pass, so a probe raised by `_check_velocities`
    on every pass stands in for a hydraulic warning of the final geometry.
    """
    original = ShellAndTubeHX._check_velocities

    def probed(self, *args, **kwargs):
        self._warn_with_category("HYDRAULIC_WARNING", "probe raised on the final pass")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ShellAndTubeHX, "_check_velocities", probed)
    data = _quiet(_benzene_cooler(u_tolerance_percent=1.0, max_u_iterations=2).run).data
    categories = {w.split("]")[0].lstrip("[") for w in data["warnings"] if w.startswith("[")}
    assert "[HYDRAULIC_WARNING] probe raised on the final pass" in data["warnings"]
    assert "CONVERGENCE_WARNING" in categories


def test_feasibility_flags_reflect_the_design_that_was_produced():
    """Design mode reported nothing, so every flag defaulted to True."""
    hot_in = MaterialStream("hot_in", component=Water(),
                            temperature=Temperature(95, "C"),
                            mass_flow=MassFlowRate(12, "kg/s"))
    hot_out = MaterialStream("hot_out", component=Water(),
                             temperature=Temperature(65, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(25, "C"),
                             mass_flow=MassFlowRate(18, "kg/s"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, mode="design")

    data = _quiet(engine.run).data
    summary = data.get("feasibility_summary", {})
    for key in ("thermal_ok", "hydraulic_ok", "pressure_drop_ok"):
        assert isinstance(summary.get(key), bool)

    # This duty overruns the shell-side pressure drop limit, and the warning says
    # so, so the flag and the status must say so too.
    assert any("pressure drop" in w.lower() for w in data["warnings"])
    assert summary["pressure_drop_ok"] is False
    assert data["status"] == "PRESSURE_DROP_FAILURE"


@pytest.mark.parametrize(
    "hx_type,extra",
    [
        ("condenser", {"condensation_mode": "total", "condensing_side": "shell",
                       "latent_heat": 2.1e6}),
        ("evaporator", {"boiling_side": "shell", "latent_heat": 2.25e6}),
        ("reboiler", {"boiling_side": "shell", "latent_heat": 2.25e6}),
    ],
)
def test_phase_change_exchangers_run_and_report_pressure_drop(hx_type, extra):
    """They read v_tube/v_shell now, and no longer drop the shell diameter."""
    data = _quiet(_phase_change_engine(hx_type, **extra).run).data

    tube_dp = float(getattr(data["tube_dp"], "value", data["tube_dp"]))
    shell_dp = float(getattr(data["shell_dp"], "value", data["shell_dp"]))
    tube_velocity = float(getattr(data["tube_velocity"], "value", data["tube_velocity"]))

    assert tube_velocity > 0
    assert tube_dp > 0
    assert shell_dp > 0
    # A dropped shell diameter forced a 1e-6 m baffle spacing and so a baffle
    # count in the hundreds of thousands.
    assert shell_dp < 1e7


def test_specified_outlet_that_breaks_the_balance_is_reported():
    """A supplied outlet used to be dropped in silence."""
    hot_in = MaterialStream("hot_in", component=Water(),
                            temperature=Temperature(95, "C"),
                            mass_flow=MassFlowRate(12, "kg/s"))
    hot_out = MaterialStream("hot_out", component=Water(),
                             temperature=Temperature(65, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(25, "C"),
                             mass_flow=MassFlowRate(18, "kg/s"))
    # Far from anything the energy balance can produce.
    cold_out = MaterialStream("cold_out", component=Water(),
                              temperature=Temperature(90, "C"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out,
               mode="design")

    data = _quiet(engine.run).data
    assert any("BALANCE_WARNING" in w for w in data["warnings"])


def _benzene_condenser(**extra):
    """The benzene condenser from docs/examples/equipment/heatexchanger."""
    hot_in = MaterialStream("benzene_vapor_in", component=Benzene(), phase="vapor",
                            temperature=Temperature(95, "C"), pressure=Pressure(1.2, "bar"),
                            mass_flow=MassFlowRate(12000, "kg/h"))
    hot_out = MaterialStream("benzene_liquid_out", component=Benzene(), phase="liquid",
                             temperature=Temperature(95, "C"))
    cold_in = MaterialStream("cw_in", component=Water(), phase="liquid",
                             temperature=Temperature(30, "C"), pressure=Pressure(1, "bar"),
                             mass_flow=MassFlowRate(50000, "kg/h"))
    cold_out = MaterialStream("cw_out", component=Water())
    engine = HeatExchangerEngine(method="bell_delaware")
    engine.fit(hx_type="condenser", hot_in=hot_in, hot_out=hot_out, cold_in=cold_in,
               cold_out=cold_out, latent_heat=394000,
               shell_dp=Pressure(0.5, "bar"), tube_dp=Pressure(0.5, "bar"),
               orientation="horizontal", mode="design", **extra)
    return engine


def test_a_cycle_between_tube_counts_settles_on_the_smallest_adequate_one():
    """The tube count is a step function of U, so this case alternates between
    192 and 280 tubes for ever; it used to run out of iterations."""
    data = _quiet(_benzene_condenser().run).data
    assert data["converged"] is True
    assert data["status"] != "FAILED_CONVERGENCE"
    assert any("cycles between tube counts" in w for w in data["warnings"])
    # It settled on one of the cycling counts, and one with the area its own U
    # requires.
    assert data["tube_count"] in {key[0] for key in data["geometry_history"]}
    assert data["feasibility_summary"]["thermal_ok"] is True


def test_hydraulic_violation_does_not_block_convergence():
    """This condenser sits outside its velocity band on every pass. The loop used
    to `continue` past the convergence test and report FAILED_CONVERGENCE while
    the U error fell to 0.26%."""
    data = _quiet(_phase_change_engine(
        "condenser", condensation_mode="total", condensing_side="shell",
        latent_heat=2.1e6).run).data
    assert data["converged"] is True
    assert data["convergence_history"][-1] < 1.0
    assert data["status"] != "FAILED_CONVERGENCE"


def test_shell_is_never_smaller_than_the_bundle():
    """Shrinking the shell to raise the shell velocity had no floor, so this
    condenser got a 0.58 m shell round a 0.69 m bundle and every geometry was
    then rejected for tube packing."""
    data = _quiet(_phase_change_engine(
        "condenser", condensation_mode="total", condensing_side="shell",
        latent_heat=2.1e6).run).data
    from types import SimpleNamespace

    from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX

    tube_od = float(getattr(data["tube_od"], "value", data["tube_od"]))
    shell = float(getattr(data["shell_diameter"], "value", data["shell_diameter"]))
    bundle = ShellAndTubeHX._calculate_bundle_diameter(
        SimpleNamespace(specs={}), data["tube_count"], tube_od, data["tube_passes"], "triangular"
    )
    assert shell > bundle


def test_every_geometry_rejected_reports_failed_convergence(monkeypatch):
    """With no pass reaching the U test, the warning used to index an empty
    history and raise IndexError."""
    from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX

    monkeypatch.setattr(ShellAndTubeHX, "_validate_bundle_geometry",
                        lambda self, geometry: (False, "rejected for the test"))
    engine = _benzene_cooler(max_u_iterations=3)
    with pytest.raises(Exception) as excinfo:
        _quiet(engine.run)
    assert not isinstance(excinfo.value, IndexError)


@pytest.mark.parametrize("relaxation", [0.0, -0.5, 1.5])
def test_relaxation_outside_its_range_is_rejected(relaxation):
    with pytest.raises(ValueError, match="u_relaxation"):
        _quiet(_benzene_cooler(u_relaxation=relaxation).run)


def test_relaxation_is_configurable():
    fast = _quiet(_benzene_cooler(u_relaxation=0.8).run).data
    slow = _quiet(_benzene_cooler(u_relaxation=0.4).run).data
    assert fast["converged"] and slow["converged"]
    assert len(fast["convergence_history"]) < len(slow["convergence_history"])
