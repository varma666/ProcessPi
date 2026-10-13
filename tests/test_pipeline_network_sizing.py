"""Regression tests for pipe sizing in the pipeline engine.

- Network pipes are sized for the flow they carry in the network. They were
  all sized for the 0.001 m3/s placeholder of `Pipe.flow_rate`, and the solver
  then ran the real flow through them (86 m/s in the chilled water example).
- A network pipe given a nominal or internal diameter keeps it; sizing used to
  resize every pipe.
- `fit(pipe=...)` uses the diameter of that pipe; only fit() diameters were
  read, so the pipe was sized all over again.
- Sizing keeps the velocity in the recommended range of the fluid when a
  standard size allows it (chlorine at 10 000 kg/h: 6 in, not 8 in).

Hand calculations: v = Q / A on the ASME B36.10M STD bore, and the Darcy drop
dp = f (L/D) rho v^2 / 2 with the Colebrook friction factor (CS, 0.045 mm).
Water() is 994.679 kg/m3 and 0.000913 Pa s.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Chlorine, Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import (
    Diameter, Length, MassFlowRate, Pressure, Temperature, VolumetricFlowRate
)

# ASME B36.10M STD bores (m)
BORE_3IN = 0.07792
BORE_4IN = 0.10226
BORE_5IN = 0.12820
BORE_6IN = 0.15408
BORE_2IN = 0.05248


def _run(engine):
    """Run the engine and return (results dict, printed text)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        results = engine.run()
    return results.results, out.getvalue()


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


def _by_name(results):
    return {c["name"]: c for c in results["components"]}


def _inches(d):
    # Unit objects hold their SI value: metres for a Diameter.
    return d.to("m").value / 0.0254


# --------------------------------------------------------------------------
# Network pipes are sized for the flow they carry
# --------------------------------------------------------------------------

def _header_and_two_branches(flow_split=None):
    """A -> (B | C) -> D, with D fixed at 4 in."""
    a = Pipe("A", length=Length(20, "m"))
    b = Pipe("B", length=Length(10, "m"))
    c = Pipe("C", length=Length(10, "m"))
    d = Pipe("D", nominal_diameter=Diameter(4, "in"), length=Length(10, "m"))
    net = PipelineNetwork.series(
        "Loop", a, PipelineNetwork.parallel("PAR", b, c), d
    )
    engine = PipelineEngine()
    kwargs = {"flow_split": flow_split} if flow_split else {}
    engine.fit(
        fluid=Water(), flowrate=VolumetricFlowRate(100, "m3/h"), network=net, **kwargs
    )
    return engine, (a, b, c, d)


def test_network_pipes_are_sized_for_their_own_flow():
    """
    Water, 100 m3/h, recommended 1.0 to 2.5 m/s, sized at the middle (1.75 m/s)
    and rounded up to the next standard bore:

    A carries 100 m3/h = 0.027778 m3/s: D = sqrt(4Q / (pi 1.75)) = 142.2 mm
      -> 6 in (154.08 mm), v = 0.027778 / 0.018646 = 1.490 m/s
    B and C carry 50 m3/h each (even split, equal pipes): D = 100.5 mm
      -> 4 in (102.26 mm), v = 0.013889 / 0.0082130 = 1.691 m/s
    Before: every pipe was sized for 0.001 m3/s (1.25 in) and then ran the
    real flow, A at 0.027778 / 9.665e-4 = 28.7 m/s.
    """
    engine, (a, b, c, d) = _header_and_two_branches()
    results, _ = _run(engine)

    assert _inches(a.nominal_diameter) == pytest.approx(6)
    assert _inches(b.nominal_diameter) == pytest.approx(4)
    assert _inches(c.nominal_diameter) == pytest.approx(4)
    assert a.internal_diameter.to("m").value == pytest.approx(BORE_6IN)

    comps = _by_name(results)
    assert comps["A"]["velocity"].to("m/s").value == pytest.approx(1.490, rel=1e-3)
    assert comps["B"]["velocity"].to("m/s").value == pytest.approx(1.691, rel=1e-3)
    assert comps["C"]["velocity"].to("m/s").value == pytest.approx(1.691, rel=1e-3)

    # The solver runs the real flow through them: A at the full 100 m3/h.
    assert comps["A"]["flow_m3s"] == pytest.approx(0.027778, rel=1e-4)
    water = Water()
    rho, mu = water.density().value, water.viscosity().value
    assert comps["A"]["pressure_drop_Pa"] == pytest.approx(
        _darcy_dp(100 / 3600, BORE_6IN, 20, rho, mu), rel=5e-3
    )


def test_network_sizing_uses_the_flow_split_given_for_a_parallel_block():
    """
    flow_split {"PAR": [3, 1]}: B carries 75 m3/h, C 25 m3/h.

    B: D = sqrt(4 x 0.020833 / (pi 1.75)) = 123.1 mm -> 5 in (128.20 mm),
       v = 0.020833 / 0.012908 = 1.614 m/s
    C: D = 71.1 mm -> 3 in (77.92 mm), v = 0.0069444 / 0.0047686 = 1.456 m/s
    """
    engine, (a, b, c, d) = _header_and_two_branches(flow_split={"PAR": [3, 1]})
    results, _ = _run(engine)

    assert _inches(b.nominal_diameter) == pytest.approx(5)
    assert _inches(c.nominal_diameter) == pytest.approx(3)
    comps = _by_name(results)
    assert comps["B"]["velocity"].to("m/s").value == pytest.approx(1.614, rel=1e-3)
    assert comps["C"]["velocity"].to("m/s").value == pytest.approx(1.456, rel=1e-3)


# --------------------------------------------------------------------------
# Pipes with a diameter keep it
# --------------------------------------------------------------------------

def test_network_pipe_with_a_nominal_diameter_keeps_it():
    """
    D is 4 in and carries the full 100 m3/h:
    v = 0.027778 / (pi 0.10226^2 / 4) = 3.382 m/s, and its drop is the Darcy
    drop on the 4 in bore. Before: D was resized to 1.25 in like the rest.
    """
    engine, (a, b, c, d) = _header_and_two_branches()
    results, _ = _run(engine)

    assert _inches(d.nominal_diameter) == pytest.approx(4)
    assert d.internal_diameter.to("m").value == pytest.approx(BORE_4IN)
    comps = _by_name(results)
    assert comps["D"]["velocity"].to("m/s").value == pytest.approx(3.382, rel=1e-3)
    water = Water()
    rho, mu = water.density().value, water.viscosity().value
    assert comps["D"]["pressure_drop_Pa"] == pytest.approx(
        _darcy_dp(100 / 3600, BORE_4IN, 10, rho, mu), rel=5e-3
    )


def test_network_pipe_with_an_internal_diameter_keeps_it():
    """A non-standard bore (90 mm) is not replaced by a standard size."""
    lined = Pipe("Lined", internal_diameter=Diameter(90, "mm"), length=Length(10, "m"))
    free = Pipe("Free", length=Length(10, "m"))
    net = PipelineNetwork.series("S", free, lined)
    engine = PipelineEngine()
    engine.fit(fluid=Water(), flowrate=VolumetricFlowRate(100, "m3/h"), network=net)
    results, _ = _run(engine)

    assert lined.internal_diameter.to("m").value == pytest.approx(0.090)
    assert lined.nominal_diameter is None
    # v = 0.027778 / (pi 0.090^2 / 4) = 4.366 m/s
    assert _by_name(results)["Lined"]["velocity"].to("m/s").value == pytest.approx(
        4.366, rel=1e-3
    )
    assert _inches(free.nominal_diameter) == pytest.approx(6)


def test_fixed_pipe_keeps_its_size_next_to_a_sized_pipe_of_the_same_name():
    """The sized diameters were copied again to every pipe of the same name."""
    fixed = Pipe("P", nominal_diameter=Diameter(3, "in"), length=Length(10, "m"))
    free = Pipe("P", length=Length(10, "m"))
    net = PipelineNetwork.series("S", free, fixed)
    engine = PipelineEngine()
    engine.fit(fluid=Water(), flowrate=VolumetricFlowRate(100, "m3/h"), network=net)
    _run(engine)

    assert _inches(fixed.nominal_diameter) == pytest.approx(3)
    assert fixed.internal_diameter.to("m").value == pytest.approx(BORE_3IN)
    assert _inches(free.nominal_diameter) == pytest.approx(6)


# --------------------------------------------------------------------------
# fit(pipe=...) uses the pipe's diameter
# --------------------------------------------------------------------------

def _single(pipe, **kwargs):
    engine = PipelineEngine()
    engine.fit(flowrate=VolumetricFlowRate(0.001, "m3/s"), pipe=pipe, fluid=Water(), **kwargs)
    return engine


def test_fit_pipe_with_internal_diameter_is_calculated_on_it():
    """
    The README example: 0.001 m3/s through a 50 mm bore, 10 m.
    v = 0.001 / (pi 0.05^2 / 4) = 0.5093 m/s; dp is the Darcy drop on 50 mm.
    Before: the pipe was sized to 1.25 in (35.08 mm, 1.035 m/s).
    """
    pipe = Pipe("Main Pipe", internal_diameter=Diameter(50, "mm"), length=Length(10, "m"))
    results, printed = _run(_single(pipe))

    summary = results["summary"]
    assert "Found optimal diameter" not in printed
    assert summary["calculated_diameter_m"] == pytest.approx(0.050)
    assert summary["velocity"] == pytest.approx(0.5093, rel=1e-3)
    water = Water()
    assert summary["total_pressure_drop_Pa"] == pytest.approx(
        _darcy_dp(0.001, 0.050, 10, water.density().value, water.viscosity().value),
        rel=5e-3,
    )


def test_fit_pipe_with_nominal_diameter_is_calculated_on_its_bore():
    """
    Nominal 2 in, STD: bore 52.48 mm, v = 0.001 / 0.0021631 = 0.4623 m/s.
    """
    pipe = Pipe("Main Pipe", nominal_diameter=Diameter(2, "in"), length=Length(10, "m"))
    results, printed = _run(_single(pipe))

    summary = results["summary"]
    assert "Found optimal diameter" not in printed
    assert summary["calculated_diameter_m"] == pytest.approx(BORE_2IN)
    assert _inches(summary["nominal_diameter"]) == pytest.approx(2)
    assert summary["velocity"] == pytest.approx(0.4623, rel=1e-3)


def test_fit_diameter_wins_over_the_pipe_diameter_with_a_warning():
    """A fit() bore is used, as before, but the disagreement is reported."""
    pipe = Pipe("Main Pipe", internal_diameter=Diameter(50, "mm"), length=Length(10, "m"))
    with pytest.warns(UserWarning, match="differs from the diameter of the `pipe`"):
        engine = _single(pipe, internal_diameter=Diameter(40, "mm"))
    results, _ = _run(engine)

    # v = 0.001 / (pi 0.04^2 / 4) = 0.7958 m/s
    assert results["summary"]["calculated_diameter_m"] == pytest.approx(0.040)
    assert results["summary"]["velocity"] == pytest.approx(0.7958, rel=1e-3)


def test_fit_pipe_without_diameter_is_still_sized():
    """Unchanged: 0.001 m3/s of water, mid-range 1.75 m/s: D = 26.98 mm ->
    1.25 in (35.08 mm, 1.035 m/s)."""
    pipe = Pipe("Main Pipe", length=Length(10, "m"))
    results, printed = _run(_single(pipe))

    assert "Found optimal diameter based on recommended velocity" in printed
    assert _inches(results["summary"]["nominal_diameter"]) == pytest.approx(1.25)
    assert results["summary"]["velocity"] == pytest.approx(1.035, rel=1e-3)


# --------------------------------------------------------------------------
# Sizing keeps the velocity in the recommended range
# --------------------------------------------------------------------------

def _chlorine():
    return Chlorine(temperature=Temperature(20, "C"), pressure=Pressure(6, "atm"))


def test_chlorine_is_sized_inside_its_velocity_range():
    """
    Chlorine 10 000 kg/h at 6 atm(a), 20 C: 17.686 kg/m3, Q = 0.15706 m3/s.
    Recommended 5 to 10 m/s; the middle (7.5 m/s) needs D = 163.3 mm, which
    rounds up to 8 in (202.74 mm): v = 0.15706 / 0.032283 = 4.87 m/s, below
    the range. 6 in (154.08 mm): v = 0.15706 / 0.018646 = 8.42 m/s, in it.
    """
    engine = PipelineEngine()
    engine.fit(fluid=_chlorine(), mass_flow=MassFlowRate(10000, "kg/h"))
    results, printed = _run(engine)

    summary = results["summary"]
    assert _inches(summary["nominal_diameter"]) == pytest.approx(6)
    assert summary["calculated_diameter_m"] == pytest.approx(BORE_6IN)
    assert summary["velocity"] == pytest.approx(8.42, rel=1e-3)
    assert "outside recommended range" not in printed


def test_chlorine_network_pipe_is_sized_inside_its_velocity_range():
    """The same pipe in a network: 6 in, 8.42 m/s."""
    pipe = Pipe("Cl2", length=Length(10, "m"))
    net = PipelineNetwork.series("S", pipe)
    engine = PipelineEngine()
    engine.fit(fluid=_chlorine(), mass_flow=MassFlowRate(10000, "kg/h"), network=net)
    results, _ = _run(engine)

    assert _inches(pipe.nominal_diameter) == pytest.approx(6)
    assert _by_name(results)["Cl2"]["velocity"].to("m/s").value == pytest.approx(
        8.42, rel=1e-3
    )


def test_available_dp_sizing_keeps_the_velocity_at_or_below_the_maximum():
    """
    Water 100 m3/h through 100 m with 2 bar available, maximum 2.5 m/s.
    4 in: v = 3.382 m/s, dp = 0.0170 x (100 / 0.10226) x 994.7 x 3.382^2 / 2
          = about 95 kPa, within 2 bar but over the maximum velocity.
    5 in: v = 2.152 m/s, the smallest size within both.
    Before: 4 in.
    """
    pipe = Pipe("Main Pipe", length=Length(100, "m"))
    engine = PipelineEngine()
    engine.fit(
        flowrate=VolumetricFlowRate(100, "m3/h"), pipe=pipe, fluid=Water(),
        available_dp=Pressure(2, "bar"),
    )
    results, _ = _run(engine)

    water = Water()
    dp_4in = _darcy_dp(100 / 3600, BORE_4IN, 100, water.density().value, water.viscosity().value)
    assert dp_4in < 2e5  # the drop alone would allow 4 in

    summary = results["summary"]
    assert summary["available_dp_met"] is True
    assert _inches(summary["nominal_diameter"]) == pytest.approx(5)
    assert summary["velocity"] == pytest.approx(2.152, rel=1e-3)


def test_available_dp_that_forces_a_low_velocity_says_it_governs():
    """
    Water 100 m3/h through 1000 m with 5 kPa available: only a large pipe
    meets the drop, and its velocity is below 1 m/s. 6 in (1.49 m/s, in range)
    is far over 5 kPa, so the drop governs and the warning says so.
    """
    pipe = Pipe("Main Pipe", length=Length(1000, "m"))
    engine = PipelineEngine()
    engine.fit(
        flowrate=VolumetricFlowRate(100, "m3/h"), pipe=pipe, fluid=Water(),
        available_dp=Pressure(5, "kPa"),
    )
    results, printed = _run(engine)

    assert results["summary"]["velocity"] < 1.0
    assert "outside recommended range" in printed
    assert "The available pressure drop governs" in printed


def test_velocity_sizing_says_when_no_standard_size_is_in_range():
    """
    A tiny water flow, 1e-6 m3/s: even the smallest size (0.125 in, 6.84 mm)
    gives v = 1e-6 / 3.675e-5 = 0.027 m/s, below 1 m/s.
    """
    engine = PipelineEngine()
    engine.fit(
        flowrate=VolumetricFlowRate(1e-6, "m3/s"), fluid=Water(), length=Length(1, "m")
    )
    results, printed = _run(engine)

    assert _inches(results["summary"]["nominal_diameter"]) == pytest.approx(0.125)
    assert "No standard size is in the range" in printed
    assert "too small for the smallest size" in printed
