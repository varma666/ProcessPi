"""Regression tests for pipe sizing in the pipeline engine.

- `fit(pipe=...)` uses the diameter of that pipe; only fit() diameters were
  read, so the pipe was sized all over again.

Hand calculations: v = Q / A on the ASME B36.10M STD bore, and the Darcy drop
dp = f (L/D) rho v^2 / 2 with the Colebrook friction factor (CS, 0.045 mm).
Water() is 994.679 kg/m3 and 0.000913 Pa s.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, VolumetricFlowRate

# ASME B36.10M STD bores (m)
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


def _inches(d):
    # Unit objects hold their SI value: metres for a Diameter.
    return d.to("m").value / 0.0254


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
