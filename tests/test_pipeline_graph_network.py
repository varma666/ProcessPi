"""Networks built with `add_node` and `add_edge` are solved as a graph.

They used to run as one series chain, in the order the edges were added, with
the full network flow in every edge: in the chilled water example the 25 AHU
pipes all carried the 300 m3/h of the pump, so the 3 in ones ran at 17.48 m/s.
The engine now finds the flow in each edge from the mass balance at the nodes
(node demands, outlets) and evaluates each edge at its own flow.

Hand calculations: v = Q / A on the ASME B36.10M STD bore, and the Darcy drop
dp = f (L/D) rho v^2 / 2 with the Colebrook friction factor (CS, 0.045 mm).
Water() is 994.679 kg/m3 and 0.000913 Pa s.
"""

import contextlib
import io
import math
import warnings

import pytest

from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.equipment import Equipment
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.pumps import Pump
from processpi.units import Diameter, Length, Pressure, VolumetricFlowRate

G = 9.80665

# ASME B36.10M STD bores (m)
BORE_3IN = 0.07792
BORE_4IN = 0.10226
BORE_6IN = 0.15408


def _m3s(m3h):
    return m3h / 3600.0


def _velocity(q_m3s, bore_m):
    return q_m3s / (math.pi * bore_m ** 2 / 4.0)


def _darcy_dp(q_m3s, bore_m, length_m, rho, mu, eps_m=0.045e-3):
    """Darcy-Weisbach drop with the Colebrook friction factor."""
    v = _velocity(q_m3s, bore_m)
    re = rho * v * bore_m / mu
    f = 0.02
    for _ in range(100):
        f = (-2.0 * math.log10(eps_m / (3.7 * bore_m) + 2.51 / (re * math.sqrt(f)))) ** -2
    return f * (length_m / bore_m) * rho * v * v / 2.0


def _water():
    water = Water()
    return water, water.density().value, water.viscosity().value


def _run(net, flow_m3h, **kwargs):
    """Run the network; return (results dict, printed text)."""
    engine = PipelineEngine().fit(
        fluid=Water(), flowrate=VolumetricFlowRate(flow_m3h, "m3/h"), network=net, **kwargs
    )
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        results = engine.run()
    return results.results, out.getvalue()


def _by_name(results):
    return {c["name"]: c for c in results["components"]}


def _single_pipe_dp(pipe, flow_m3s):
    """Total drop of the same pipe run on its own at the given flow."""
    engine = PipelineEngine().fit(
        fluid=Water(), flowrate=VolumetricFlowRate(flow_m3s, "m3/s"), pipe=pipe
    )
    with contextlib.redirect_stdout(io.StringIO()):
        results = engine.run()
    return results.results["summary"]["total_pressure_drop_Pa"]


def _pipe(name, nps, length_m):
    return Pipe(name, nominal_diameter=Diameter(nps, "in"), length=Length(length_m, "m"))


def _assert_mass_balance(results, net, flow_m3s):
    """Flow in - flow out at every node equals what leaves there."""
    summary = results["summary"]
    inlet = summary["inlet_node"]
    outlets = summary["outlet_flows_m3s"]
    for name in net.nodes:
        q_in = sum(c["flow_m3s"] for c in results["components"] if c.get("end_node") == name)
        q_out = sum(c["flow_m3s"] for c in results["components"] if c.get("start_node") == name)
        leaving = outlets.get(name, 0.0) - (flow_m3s if name == inlet else 0.0)
        assert q_in - q_out == pytest.approx(leaving, abs=1e-12), name


# --------------------------------------------------------------------------
# Tree networks: flows from the node demands
# --------------------------------------------------------------------------

def _tree():
    """
    S -> A (6 in, 50 m), A -> B (4 in, 30 m), A -> C (3 in, 30 m).
    A takes 10 m3/h, B takes 30 m3/h, C has no demand.
    """
    net = PipelineNetwork("Tree")
    net.add_node("S")
    net.add_node("A", demand=VolumetricFlowRate(10, "m3/h"))
    net.add_node("B", demand=VolumetricFlowRate(30, "m3/h"))
    net.add_node("C")
    pipes = {
        "SA": _pipe("SA", 6, 50),
        "AB": _pipe("AB", 4, 30),
        "AC": _pipe("AC", 3, 30),
    }
    net.add_edge(pipes["SA"], "S", "A")
    net.add_edge(pipes["AB"], "A", "B")
    net.add_edge(pipes["AC"], "A", "C")
    return net, pipes


def test_tree_flows_follow_the_node_demands():
    """
    60 m3/h enters at S (the only node no edge enters).
    S-A carries all of it: 60 m3/h.
    A keeps 10 m3/h, so 50 m3/h goes on: A-B carries B's 30 m3/h and the
    outlet C, which has no demand, takes the rest: 60 - 10 - 30 = 20 m3/h.
    Before: every edge carried 60 m3/h.
    """
    net, _ = _tree()
    results, _ = _run(net, 60)
    comps = _by_name(results)

    assert comps["SA"]["flow_m3s"] == pytest.approx(_m3s(60), rel=1e-12)
    assert comps["AB"]["flow_m3s"] == pytest.approx(_m3s(30), rel=1e-12)
    assert comps["AC"]["flow_m3s"] == pytest.approx(_m3s(20), rel=1e-12)
    assert comps["AB"]["start_node"] == "A" and comps["AB"]["end_node"] == "B"

    summary = results["summary"]
    assert summary["solver"] == "graph"
    assert summary["inlet_node"] == "S"
    assert summary["number_of_loops"] == 0
    assert summary["outlet_flows_m3s"] == pytest.approx(
        {"A": _m3s(10), "B": _m3s(30), "C": _m3s(20)}, rel=1e-12
    )
    _assert_mass_balance(results, net, _m3s(60))

    # The velocity of each pipe is that of its own flow:
    # A-C: 20 m3/h in 3 in: 0.0055556 / 0.0047686 = 1.165 m/s (was 3.50 m/s).
    v_ac = comps["AC"]["velocity"].to("m/s").value
    assert v_ac == pytest.approx(_velocity(_m3s(20), BORE_3IN), rel=1e-4)
    assert v_ac == pytest.approx(1.165, rel=1e-3)


def test_tree_edge_drop_equals_a_single_pipe_run_at_the_edge_flow():
    """
    Each edge is evaluated by the same calculation as a single pipe:
    A-B at 30 m3/h in 4 in (102.26 mm), 30 m: v = 1.0147 m/s,
    Re = 994.679 * 1.0147 * 0.10226 / 0.000913 = 1.130e5, f = 0.0197,
    dp = 0.0197 * (30 / 0.10226) * 994.679 * 1.0147^2 / 2 = 2.97 kPa.
    """
    net, pipes = _tree()
    results, _ = _run(net, 60)
    comps = _by_name(results)
    _, rho, mu = _water()

    for name, q_m3h, bore, length in (
        ("SA", 60, BORE_6IN, 50), ("AB", 30, BORE_4IN, 30), ("AC", 20, BORE_3IN, 30)
    ):
        dp = comps[name]["pressure_drop_Pa"]
        assert dp == pytest.approx(_single_pipe_dp(pipes[name], _m3s(q_m3h)), rel=1e-12)
        assert dp == pytest.approx(_darcy_dp(_m3s(q_m3h), bore, length, rho, mu), rel=1e-3)
    assert comps["AB"]["pressure_drop_Pa"] == pytest.approx(2967, rel=1e-3)


def test_tree_node_pressures_and_governing_drop():
    """
    The drop from the inlet to a node adds the edge drops on the way:
    to B: dp(S-A) + dp(A-B), to C: dp(S-A) + dp(A-C).
    C, the outlet with the lowest pressure, governs: the network drop is
    the drop from S to C, not the sum over all three pipes.
    """
    net, _ = _tree()
    results, _ = _run(net, 60, inlet_pressure=Pressure(3, "bar"))
    comps = _by_name(results)
    summary = results["summary"]
    dp = {name: comps[name]["pressure_drop_Pa"] for name in ("SA", "AB", "AC")}

    drops = summary["node_pressure_drop_Pa"]
    assert drops["S"] == 0.0
    assert drops["A"] == pytest.approx(dp["SA"], rel=1e-12)
    assert drops["B"] == pytest.approx(dp["SA"] + dp["AB"], rel=1e-12)
    assert drops["C"] == pytest.approx(dp["SA"] + dp["AC"], rel=1e-12)

    assert dp["AC"] > dp["AB"]
    assert summary["governing_outlet"] == "C"
    assert summary["governing_path"] == ["S", "A", "C"]
    assert summary["total_pressure_drop_Pa"] == pytest.approx(drops["C"], rel=1e-12)
    assert summary["total_pressure_drop_Pa"] < sum(dp.values())

    # With an inlet pressure the node pressures are absolute.
    assert summary["node_pressures_Pa"]["C"] == pytest.approx(3e5 - drops["C"], rel=1e-12)


def test_static_head_is_signed_on_graph_edges():
    """
    S (0 m) -> A (10 m) -> B (4 m), 4 in, 20 m each, 30 m3/h.
    Up 10 m: + rho g 10 = 994.679 * 9.80665 * 10 = 97.54 kPa.
    Down 6 m: - rho g 6 = -58.53 kPa; the node pressure rises again.
    The uphill edge has the drop of a single-pipe run, static head included.
    """
    _, rho, _ = _water()
    net = PipelineNetwork("Hill")
    net.add_node("S", elevation=0)
    net.add_node("A", elevation=10)
    net.add_node("B", elevation=4)
    up, down = _pipe("UP", 4, 20), _pipe("DOWN", 4, 20)
    net.add_edge(up, "S", "A")
    net.add_edge(down, "A", "B")
    results, _ = _run(net, 30)
    comps = _by_name(results)

    assert comps["UP"]["elevation_dp_Pa"] == pytest.approx(rho * G * 10, rel=1e-12)
    assert comps["DOWN"]["elevation_dp_Pa"] == pytest.approx(-rho * G * 6, rel=1e-12)
    assert comps["UP"]["pressure_drop_Pa"] == pytest.approx(_single_pipe_dp_between(up, 0, 10), rel=1e-12)

    friction = comps["UP"]["pressure_drop_Pa"] - rho * G * 10
    assert comps["DOWN"]["pressure_drop_Pa"] == pytest.approx(friction - rho * G * 6, rel=1e-9)
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        2 * friction + rho * G * 4, rel=1e-9
    )


def _single_pipe_dp_between(pipe, z_start, z_end):
    """`_pipe_calculation` of the pipe between nodes at the given elevations."""
    net = PipelineNetwork("One")
    net.add_node("X", elevation=z_start)
    net.add_node("Y", elevation=z_end)
    copy = Pipe(pipe.name, nominal_diameter=pipe.nominal_diameter, length=pipe.length)
    net.add_edge(copy, "X", "Y")
    engine = PipelineEngine().fit(fluid=Water(), flowrate=VolumetricFlowRate(30, "m3/h"))
    return engine._pipe_calculation(copy, VolumetricFlowRate(30, "m3/h"))["pressure_drop"].to("Pa").value


def test_a_series_chain_of_edges_matches_the_series_block():
    """
    A chain of edges has one path: the graph solve gives what the series
    block gives (same flow in every pipe, drops added), pump and equipment
    included.
    """
    def parts():
        return (
            _pipe("P1", 4, 40),
            Pump("PU", pump_type="Centrifugal", head=Length(30, "m")),
            _pipe("P2", 3, 25),
            Equipment("HX", pressure_drop=0.3),
            _pipe("P3", 4, 10),
        )

    chain = parts()
    net = PipelineNetwork("Chain")
    for name in "ABCDEF":
        net.add_node(name)
    for elem, (a, b) in zip(chain, ("AB", "BC", "CD", "DE", "EF")):
        net.add_edge(elem, a, b)
    graph_results, _ = _run(net, 40)
    block_results, _ = _run(PipelineNetwork.series("Chain", *parts()), 40)

    assert graph_results["summary"]["solver"] == "graph"
    assert graph_results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        block_results["summary"]["total_pressure_drop_Pa"], rel=1e-12
    )
    graph_comps, block_comps = _by_name(graph_results), _by_name(block_results)
    for name in ("P1", "PU", "P2", "HX", "P3"):
        assert graph_comps[name]["pressure_drop_Pa"] == pytest.approx(
            block_comps[name]["pressure_drop_Pa"], rel=1e-12
        )
        assert graph_comps[name]["flow_m3s"] == pytest.approx(_m3s(40), rel=1e-12)


# --------------------------------------------------------------------------
# Demands that do not fit, and graphs that cannot be solved
# --------------------------------------------------------------------------

def test_demands_above_the_inlet_flow_raise():
    net, _ = _tree()
    with pytest.raises(ValueError, match="more than the inlet flow"):
        _run(net, 35)  # demands: 10 + 30 = 40 m3/h


def test_demands_on_every_outlet_must_add_up_to_the_inlet_flow():
    net, _ = _tree()
    net.nodes["C"].demand = VolumetricFlowRate(5, "m3/h")
    with pytest.raises(ValueError, match="must be equal"):
        _run(net, 60)  # demands: 10 + 30 + 5 = 45 m3/h
    # 45 m3/h in: every edge flow is fixed by the demands.
    results, _ = _run(net, 45)
    assert _by_name(results)["AC"]["flow_m3s"] == pytest.approx(_m3s(5), rel=1e-12)


def test_a_demand_must_be_a_flow_rate():
    net = PipelineNetwork("N")
    with pytest.raises(TypeError, match="VolumetricFlowRate"):
        net.add_node("A", demand=10)


def test_a_closed_circuit_runs_as_before_with_a_warning():
    """
    No node is left by no edge and no node has a demand: the circuit has no
    outlet, so mass balance cannot place the flow. It runs as a series chain,
    as before, and says so.
    """
    def circuit():
        net = PipelineNetwork("Circuit")
        for name in ("T", "A", "B"):
            net.add_node(name)
        net.add_edge(_pipe("TA", 4, 10), "T", "A")
        net.add_edge(Pump("PU", pump_type="Centrifugal", head=Length(20, "m")), "A", "B")
        net.add_edge(_pipe("BA", 4, 30), "B", "A")
        return net

    with pytest.warns(UserWarning, match="has no outlet"):
        results, _ = _run(circuit(), 40)
    assert "solver" not in results["summary"]
    comps = _by_name(results)
    assert comps["BA"]["flow_m3s"] == pytest.approx(_m3s(40), rel=1e-12)


def test_a_network_mixing_edges_and_blocks_runs_as_before_with_a_warning():
    net = PipelineNetwork("Mixed")
    net.add_node("A")
    net.add_node("B")
    net.add_edge(_pipe("AB", 4, 10), "A", "B")
    net.add_subnetwork(PipelineNetwork.series("Tail", _pipe("T", 4, 10)))
    with pytest.warns(UserWarning, match="mixes edges"):
        results, _ = _run(net, 40)
    assert "solver" not in results["summary"]


# --------------------------------------------------------------------------
# Block networks (series / parallel) are evaluated as before
# --------------------------------------------------------------------------

def test_block_networks_are_unchanged():
    """
    Guard: a block network has no nodes and keeps the series/parallel
    evaluation. Values from the base branch (#116): A 6 in at 100 m3/h, B and
    C (3 in, 4 in) balanced in parallel, D 4 in.
    """
    a, d = _pipe("A", 6, 20), _pipe("D", 4, 10)
    b, c = _pipe("B", 3, 10), _pipe("C", 4, 15)
    net = PipelineNetwork.series("Loop", a, PipelineNetwork.parallel("PAR", b, c), d)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        results, _ = _run(net, 100)
    summary = results["summary"]
    assert "solver" not in summary
    comps = _by_name(results)
    assert summary["total_pressure_drop_Pa"] == pytest.approx(BLOCK_TOTAL_DP_PA, rel=1e-9)
    assert comps["B"]["flow_m3s"] == pytest.approx(BLOCK_FLOW_B_M3S, rel=1e-9)
    assert comps["C"]["flow_m3s"] == pytest.approx(BLOCK_FLOW_C_M3S, rel=1e-9)


# From the base branch (#116), unchanged here.
BLOCK_TOTAL_DP_PA = 18167.105421693966
BLOCK_FLOW_B_M3S = 0.010447782259543624
BLOCK_FLOW_C_M3S = 0.01732999551823415
