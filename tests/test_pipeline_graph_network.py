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
# Looped networks: the drops around every loop add up to zero
# --------------------------------------------------------------------------

def _two_paths(first, second, flow_m3h, reverse_second=False, **kwargs):
    """S -> A (6 in, 10 m), then A -> B through two pipes in parallel."""
    net = PipelineNetwork("TwoPaths")
    for name in ("S", "A", "B"):
        net.add_node(name)
    net.add_edge(_pipe("SA", 6, 10), "S", "A")
    net.add_edge(first, "A", "B")
    if reverse_second:
        net.add_edge(second, "B", "A")
    else:
        net.add_edge(second, "A", "B")
    return _run(net, flow_m3h, **kwargs)


def test_identical_parallel_pipes_share_the_flow_equally():
    """
    Two equal 4 in, 20 m pipes between A and B, 100 m3/h: by symmetry
    50 m3/h each, with the same drop. Before: both carried 100 m3/h and
    their drops were added.
    """
    results, _ = _two_paths(_pipe("P1", 4, 20), _pipe("P2", 4, 20), 100)
    comps = _by_name(results)
    assert results["summary"]["number_of_loops"] == 1
    assert results["summary"]["solver_converged"] is True
    assert comps["P1"]["flow_m3s"] == pytest.approx(_m3s(50), rel=1e-6)
    assert comps["P2"]["flow_m3s"] == pytest.approx(_m3s(50), rel=1e-6)
    assert comps["P1"]["pressure_drop_Pa"] == pytest.approx(
        comps["P2"]["pressure_drop_Pa"], rel=1e-6
    )
    # The network drop is S-A plus one path, not both.
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        comps["SA"]["pressure_drop_Pa"] + comps["P1"]["pressure_drop_Pa"], rel=1e-6
    )


def test_laminar_split_matches_hagen_poiseuille():
    """
    Laminar flow (f = 64 / Re) has dp = 128 mu L q / (pi D^4), linear in q,
    so two pipes of one bore split the flow in inverse ratio to their
    lengths: 1 in (26.64 mm), 10 m and 20 m, 0.1 m3/h in total:
      q1 = 0.1 * 20 / 30 = 0.06667 m3/h, q2 = 0.03333 m3/h.
    Re of the larger: 4 rho q / (pi mu D) = 4 * 994.679 * 1.852e-5
      / (pi * 0.000913 * 0.02664) = 964, laminar.
    dp = 128 * 0.000913 * 10 * 1.852e-5 / (pi * 0.02664^4) = 13.67 Pa.
    """
    _, rho, mu = _water()
    p1, p2 = _pipe("P1", 1, 10), _pipe("P2", 1, 20)
    results, _ = _two_paths(p1, p2, 0.1)
    comps = _by_name(results)
    bore = 0.02664
    assert p1.internal_diameter.to("m").value == pytest.approx(bore)
    q1 = comps["P1"]["flow_m3s"]
    assert q1 == pytest.approx(_m3s(0.1) * 2.0 / 3.0, rel=1e-6)
    assert comps["P2"]["flow_m3s"] == pytest.approx(_m3s(0.1) / 3.0, rel=1e-6)
    assert comps["P1"]["reynolds"].value < 2000
    hagen_poiseuille = 128.0 * mu * 10.0 * q1 / (math.pi * bore ** 4)
    assert comps["P1"]["pressure_drop_Pa"] == pytest.approx(hagen_poiseuille, rel=1e-6)
    assert comps["P1"]["pressure_drop_Pa"] == pytest.approx(13.67, rel=1e-3)


def test_hazen_williams_split_matches_the_power_law():
    """
    Hazen-Williams: h = 10.67 L q^1.852 / (C^1.852 D^4.87). For one bore and
    C, equal drops give q1 / q2 = (L2 / L1)^(1 / 1.852): 4 in, 10 m and
    30 m, 100 m3/h: q1 / q2 = 3^0.53996 = 1.8102,
      q1 = 100 * 1.8102 / 2.8102 = 64.41 m3/h, q2 = 35.59 m3/h.
    """
    results, _ = _two_paths(
        _pipe("P1", 4, 10), _pipe("P2", 4, 30), 100, method="hazen_williams"
    )
    comps = _by_name(results)
    ratio = 3.0 ** (1.0 / 1.852)
    q1 = _m3s(100) * ratio / (1.0 + ratio)
    assert comps["P1"]["flow_m3s"] == pytest.approx(q1, rel=1e-6)
    assert comps["P1"]["flow_m3s"] == pytest.approx(_m3s(64.41), rel=1e-4)
    assert comps["P2"]["flow_m3s"] == pytest.approx(_m3s(100) - q1, rel=1e-6)


def test_turbulent_split_matches_a_hand_balance():
    """
    Darcy with Colebrook: 4 in, 10 m and 30 m, 100 m3/h. The hand balance
    finds q1 with dp(q1, 10 m) = dp(100 - q1, 30 m) by bisection on the
    independent Darcy drop: q1 = 64.09 m3/h, q2 = 35.91 m3/h, 4.16 kPa on
    both. (Friction falls slightly with Re, so the split is a little less
    uneven than the q^2 law's sqrt(3) = 1.732: 64.09 / 35.91 = 1.785.)
    """
    _, rho, mu = _water()
    q_total = _m3s(100)
    lo, hi = 0.0, q_total
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        gap = _darcy_dp(mid, BORE_4IN, 10, rho, mu) - _darcy_dp(q_total - mid, BORE_4IN, 30, rho, mu)
        lo, hi = (lo, mid) if gap > 0 else (mid, hi)
    q1_hand = 0.5 * (lo + hi)
    assert q1_hand == pytest.approx(_m3s(64.09), rel=1e-4)

    results, _ = _two_paths(_pipe("P1", 4, 10), _pipe("P2", 4, 30), 100)
    comps = _by_name(results)
    assert comps["P1"]["flow_m3s"] == pytest.approx(q1_hand, rel=1e-4)
    # Converged to 1e-6 of the loss around the loop (both drops).
    assert comps["P1"]["pressure_drop_Pa"] == pytest.approx(
        comps["P2"]["pressure_drop_Pa"], rel=2e-6
    )
    assert comps["P1"]["pressure_drop_Pa"] == pytest.approx(4156, rel=1e-3)


def test_an_edge_drawn_against_the_flow_carries_a_negative_flow():
    """
    The ring main below with its cross-connection added as D -> B instead
    of B -> D: the same solution, the flow and drop of that pipe negative.
    """
    forward, _ = _run(_ring_main(), 80)
    backward, _ = _run(_ring_main(cross_from="D"), 80)
    f, b = _by_name(forward), _by_name(backward)
    assert f["BD"]["flow_m3s"] > 0
    assert b["BD"]["start_node"] == "D"
    assert b["BD"]["flow_m3s"] == pytest.approx(-f["BD"]["flow_m3s"], rel=1e-5)
    assert b["BD"]["pressure_drop_Pa"] == pytest.approx(-f["BD"]["pressure_drop_Pa"], rel=1e-5)
    assert b["BD"]["velocity"].to("m/s").value == pytest.approx(
        f["BD"]["velocity"].to("m/s").value, rel=1e-5
    )
    for name in ("SA", "AB", "BC", "AD", "DC"):
        assert b[name]["flow_m3s"] == pytest.approx(f[name]["flow_m3s"], rel=1e-5)


def test_outlets_without_a_demand_share_one_pressure():
    """
    S -> A, then A -> B (4 in, 10 m) and A -> C (3 in, 30 m), both open
    outlets: the flow splits so that B and C end at the same pressure.
    """
    net = PipelineNetwork("Outlets")
    for name in ("S", "A", "B", "C"):
        net.add_node(name)
    net.add_edge(_pipe("SA", 6, 10), "S", "A")
    net.add_edge(_pipe("AB", 4, 10), "A", "B")
    net.add_edge(_pipe("AC", 3, 30), "A", "C")
    results, _ = _run(net, 100)
    summary, comps = results["summary"], _by_name(results)
    drops = summary["node_pressure_drop_Pa"]
    assert drops["B"] == pytest.approx(drops["C"], rel=1e-6)
    assert "(outlets)" not in drops
    q_b, q_c = summary["outlet_flows_m3s"]["B"], summary["outlet_flows_m3s"]["C"]
    assert q_b + q_c == pytest.approx(_m3s(100), rel=1e-12)
    assert comps["AB"]["flow_m3s"] == pytest.approx(q_b, rel=1e-12)
    assert q_b > q_c > 0
    _assert_mass_balance(results, net, _m3s(100))


def _ring_main(cross_from="B"):
    """
    A ring with a cross-connection: two independent loops.

        S -> A -> B -> C
             A -> D -> C,  B -> D
    B takes 20 m3/h, D takes 30 m3/h, C (the outlet) the rest of 80 m3/h.
    """
    net = PipelineNetwork("Ring")
    net.add_node("S", elevation=0)
    net.add_node("A", elevation=2)
    net.add_node("B", elevation=3, demand=VolumetricFlowRate(20, "m3/h"))
    net.add_node("C", elevation=1)
    net.add_node("D", elevation=5, demand=VolumetricFlowRate(30, "m3/h"))
    net.add_edge(_pipe("SA", 6, 20), "S", "A")
    net.add_edge(_pipe("AB", 4, 60), "A", "B")
    net.add_edge(_pipe("BC", 3, 40), "B", "C")
    net.add_edge(_pipe("AD", 4, 80), "A", "D")
    net.add_edge(_pipe("DC", 3, 50), "D", "C")
    if cross_from == "B":
        net.add_edge(_pipe("BD", 3, 30), "B", "D")
    else:
        net.add_edge(_pipe("BD", 3, 30), "D", "B")
    return net


def test_ring_main_meets_mass_and_loop_balances():
    """
    Mass: flow in - flow out at every node is what leaves there.
    Energy: each edge's drop equals the difference of its node pressures,
    so the drops around both loops add up to zero (static heads included).
    """
    net = _ring_main()
    results, _ = _run(net, 80)
    summary, comps = results["summary"], _by_name(results)
    assert summary["number_of_loops"] == 2
    assert summary["solver_converged"] is True
    _assert_mass_balance(results, net, _m3s(80))
    assert summary["outlet_flows_m3s"]["C"] == pytest.approx(_m3s(30), rel=1e-9)

    pressure = {n: -dp for n, dp in summary["node_pressure_drop_Pa"].items()}
    scale = sum(abs(c["pressure_drop_Pa"]) for c in comps.values())
    for c in comps.values():
        assert c["pressure_drop_Pa"] == pytest.approx(
            pressure[c["start_node"]] - pressure[c["end_node"]], abs=1e-6 * scale
        )
    # Loop A-B-D-A and loop B-C-D-B, written out.
    assert comps["AB"]["pressure_drop_Pa"] + comps["BD"]["pressure_drop_Pa"] - comps["AD"][
        "pressure_drop_Pa"] == pytest.approx(0.0, abs=1e-6 * scale)
    assert comps["BC"]["pressure_drop_Pa"] - comps["DC"]["pressure_drop_Pa"] - comps["BD"][
        "pressure_drop_Pa"] == pytest.approx(0.0, abs=1e-6 * scale)
    # Each pipe's drop is a single-pipe run at its flow, static head added.
    _, rho, _ = _water()
    elevation = {"S": 0, "A": 2, "B": 3, "C": 1, "D": 5}
    for name in ("AB", "AD", "BD"):
        c = comps[name]
        q = abs(c["flow_m3s"])
        static = rho * G * (elevation[c["end_node"]] - elevation[c["start_node"]])
        pipe = next(p for p in net.get_all_pipes() if p.name == name)
        # A copy without nodes: the friction and fitting losses alone.
        friction = _single_pipe_dp(Pipe(name, nominal_diameter=pipe.nominal_diameter,
                                        length=pipe.length), q)
        assert c["pressure_drop_Pa"] == pytest.approx(
            math.copysign(friction, c["flow_m3s"]) + static, rel=1e-9
        )


def test_a_loop_without_a_pipe_raises():
    """Two fixed-drop items in parallel: nothing sets how they share the flow."""
    net = PipelineNetwork("NoPipe")
    for name in ("S", "A", "B"):
        net.add_node(name)
    net.add_edge(_pipe("SA", 4, 10), "S", "A")
    net.add_edge(Equipment("HX1", pressure_drop=0.2), "A", "B")
    net.add_edge(Equipment("HX2", pressure_drop=0.2), "A", "B")
    with pytest.raises(ValueError, match="has no pipe"):
        _run(net, 40)


# --------------------------------------------------------------------------
# Sizing on the flow of each edge
# --------------------------------------------------------------------------

BORE_5IN = 0.12820
BORE_10IN = 0.25446


def _inches(d):
    # Unit objects hold their SI value: metres for a Diameter.
    return d.to("m").value / 0.0254


def test_tree_pipes_are_sized_for_their_edge_flow():
    """
    Water, recommended 1.0 to 2.5 m/s, sized at the middle (1.75 m/s) and
    rounded up to the next STD bore:
    S-A, 100 m3/h: D = sqrt(4 * 0.027778 / (pi * 1.75)) = 142.2 mm -> 6 in,
      v = 0.027778 / 0.018646 = 1.490 m/s
    A-B and A-C, 50 m3/h each (the demands): D = 100.5 mm -> 4 in,
      v = 0.013889 / 0.0082130 = 1.691 m/s
    Before: sized as a series chain, all three for 100 m3/h (6 in).
    """
    net = PipelineNetwork("Tree")
    net.add_node("S")
    net.add_node("A")
    net.add_node("B", demand=VolumetricFlowRate(50, "m3/h"))
    net.add_node("C", demand=VolumetricFlowRate(50, "m3/h"))
    sa, ab, ac = (Pipe(n, length=Length(20, "m")) for n in ("SA", "AB", "AC"))
    net.add_edge(sa, "S", "A")
    net.add_edge(ab, "A", "B")
    net.add_edge(ac, "A", "C")
    results, printed = _run(net, 100)
    comps = _by_name(results)

    assert _inches(sa.nominal_diameter) == pytest.approx(6)
    assert _inches(ab.nominal_diameter) == pytest.approx(4)
    assert _inches(ac.nominal_diameter) == pytest.approx(4)
    assert comps["SA"]["velocity"].to("m/s").value == pytest.approx(1.490, rel=1e-3)
    assert comps["AB"]["velocity"].to("m/s").value == pytest.approx(1.691, rel=1e-3)
    assert "Pipe AB: No available DP provided" in printed


def test_looped_pipes_are_sized_for_their_solved_flow():
    """
    Two equal unsized pipes in parallel, 100 m3/h: the first pass sizes both
    for 100 m3/h (6 in), the solved split is 50/50, and the second pass sizes
    them for 50 m3/h: 4 in at 1.691 m/s. A third pass changes nothing.
    """
    p1, p2 = Pipe("P1", length=Length(20, "m")), Pipe("P2", length=Length(20, "m"))
    results, printed = _two_paths(p1, p2, 100)
    comps = _by_name(results)
    assert _inches(p1.nominal_diameter) == pytest.approx(4)
    assert _inches(p2.nominal_diameter) == pytest.approx(4)
    assert comps["P1"]["flow_m3s"] == pytest.approx(_m3s(50), rel=1e-6)
    assert comps["P1"]["velocity"].to("m/s").value == pytest.approx(1.691, rel=1e-3)
    # The sizing is printed once, for the final flows.
    assert printed.count("Pipe P1: No available DP provided") == 1


def test_user_sized_pipes_keep_their_size_in_a_graph():
    """
    A fixed 3 in branch next to a branch to size: the fixed one keeps 3 in
    and carries its own demand (20 m3/h: 1.165 m/s), the other is sized for
    its 50 m3/h (4 in).
    """
    net = PipelineNetwork("Fixed")
    net.add_node("S")
    net.add_node("A")
    net.add_node("B", demand=VolumetricFlowRate(20, "m3/h"))
    net.add_node("C", demand=VolumetricFlowRate(50, "m3/h"))
    fixed = _pipe("FIXED", 3, 20)
    sized = Pipe("SIZED", length=Length(20, "m"))
    net.add_edge(_pipe("SA", 6, 10), "S", "A")
    net.add_edge(fixed, "A", "B")
    net.add_edge(sized, "A", "C")
    results, _ = _run(net, 70)
    comps = _by_name(results)
    assert _inches(fixed.nominal_diameter) == pytest.approx(3)
    assert fixed.internal_diameter.to("m").value == pytest.approx(BORE_3IN)
    assert comps["FIXED"]["velocity"].to("m/s").value == pytest.approx(1.165, rel=1e-3)
    assert _inches(sized.nominal_diameter) == pytest.approx(4)


def chilled_water_loop():
    """
    The chilled water example of the docs, opened at its tank: Tank (pump
    suction) -> pump -> chiller -> header -> five branches of five AHUs in
    series -> return header -> expansion tank -> Return_Tank (the outlet).
    """
    net = PipelineNetwork("Chilled Water Loop")
    net.add_node("Tank", elevation=0)
    net.add_node("Pump_In", elevation=0)
    net.add_node("Pump_Out", elevation=1)
    net.add_node("Chiller_Out", elevation=1)
    net.add_node("Main_In", elevation=1)
    net.add_node("Main_Out", elevation=1)
    for b in range(1, 6):
        net.add_node(f"Branch_{b}_In", elevation=1)
        for a in range(1, 6):
            net.add_node(f"AHU_{b}_{a}_PipeOut", elevation=1)
            net.add_node(f"AHU_{b}_{a}_EqOut", elevation=1)
        net.add_node(f"Return_{b}", elevation=0)
    net.add_node("Return_Header", elevation=0)
    net.add_node("Return_Tank", elevation=0)

    pump = Pump("Pump1", pump_type="Centrifugal", inlet_pressure=Pressure(101325, "Pa"),
                outlet_pressure=Pressure(201325, "Pa"))
    net.add_edge(Pipe("TankPipe", length=Length(5, "m")), "Tank", "Pump_In")
    net.add_edge(pump, "Pump_In", "Pump_Out")
    net.add_edge(Equipment("Chiller", pressure_drop=0.2), "Pump_Out", "Chiller_Out")
    net.add_edge(Pipe("MainPipe", length=Length(15, "m")), "Chiller_Out", "Main_In")
    net.add_edge(Pipe("MainPipe_Out", length=Length(5, "m")), "Main_In", "Main_Out")
    for b in range(1, 6):
        net.add_edge(Pipe(f"MainToBranch_{b}", length=Length(3, "m")), "Main_Out", f"Branch_{b}_In")
    sizes = [3, 4, 4, 5, 6]
    flows = [8, 10, 10, 12, 15]
    for b in range(1, 6):
        for a in range(1, 6):
            start = f"Branch_{b}_In" if a == 1 else f"AHU_{b}_{a - 1}_EqOut"
            net.add_edge(_pipe(f"AHUPipe_{b}_{a}", sizes[a - 1], 5), start, f"AHU_{b}_{a}_PipeOut")
            net.add_edge(Equipment(f"AHU_{b}_{a}", pressure_drop=0.05 + 0.01 * flows[a - 1] / 10),
                         f"AHU_{b}_{a}_PipeOut", f"AHU_{b}_{a}_EqOut")
    for b in range(1, 6):
        net.add_edge(Pipe(f"BranchReturnPipe_{b}", length=Length(5, "m")),
                     f"AHU_{b}_5_EqOut", f"Return_{b}")
        net.add_edge(Pipe(f"ReturnPipe_{b}", length=Length(10, "m")), f"Return_{b}", "Return_Header")
    from processpi.pipelines.vessel import Vessel
    net.add_edge(Vessel("ExpansionTank"), "Return_Header", "Return_Tank")
    return net


def test_chilled_water_loop_branches_carry_their_share():
    """
    300 m3/h through five identical branches between Main_Out and
    Return_Header: 60 m3/h each (0.016667 m3/s).
    AHU pipe 3 in: v = 0.016667 / (pi / 4 * 0.07792^2) = 3.495 m/s
      (was 17.48 m/s with 300 m3/h in every pipe).
    Branch pipes sized for 60 m3/h: D = 110.1 mm -> 5 in, v = 1.291 m/s.
    Header at 300 m3/h: D = 246.2 mm -> 10 in, v = 1.639 m/s (as before).
    """
    net = chilled_water_loop()
    results, _ = _run(net, 300)
    summary, comps = results["summary"], _by_name(results)
    assert summary["solver"] == "graph"
    assert summary["number_of_loops"] == 4
    assert summary["solver_converged"] is True
    _assert_mass_balance(results, net, _m3s(300))

    for b in range(1, 6):
        assert comps[f"AHUPipe_{b}_1"]["flow_m3s"] == pytest.approx(_m3s(60), rel=1e-6)
        assert comps[f"AHUPipe_{b}_1"]["velocity"].to("m/s").value == pytest.approx(3.495, rel=1e-3)
        assert comps[f"MainToBranch_{b}"]["nominal_diameter"].to("m").value / 0.0254 == pytest.approx(5)
        assert comps[f"MainToBranch_{b}"]["velocity"].to("m/s").value == pytest.approx(1.291, rel=1e-3)
    assert comps["MainPipe"]["diameter"].to("m").value == pytest.approx(BORE_10IN)
    assert comps["MainPipe"]["velocity"].to("m/s").value == pytest.approx(1.639, rel=1e-3)

    # The governing drop is the sum of the drops along one path.
    path = summary["governing_path"]
    assert path[0] == "Tank" and path[-1] == "Return_Tank"
    on_path = [
        c for c in comps.values()
        if c["start_node"] in path and c["end_node"] in path
        and path.index(c["end_node"]) == path.index(c["start_node"]) + 1
    ]
    assert len(on_path) == len(path) - 1
    assert summary["total_pressure_drop_Pa"] == pytest.approx(
        sum(c["pressure_drop_Pa"] for c in on_path), rel=1e-9
    )


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
