"""Single-pipe sizing and the internal diameter it reports.

- `available_dp` sizing tested the pipe friction alone, then added the
  fittings without checking again, so the size it called optimal could exceed
  the available drop (P10).
- Both sizing routes reported the nominal size as the diameter while the
  calculation used the internal diameter (P14).
- A schedule written "40" or "Sch40" was not found in the table, and the
  nominal size was then used as the bore (P15).
"""

import contextlib
import io
import math

import pytest

from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.standards import PIPE_SCHEDULES, normalize_schedule
from processpi.units import Diameter, Length, Pressure, VolumetricFlowRate

Q = VolumetricFlowRate(50, "m3/h")


def _run(**specs):
    engine = PipelineEngine().fit(fluid=Water(), flowrate=Q, length=Length(100, "m"), **specs)
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.run().results["summary"]


def _fittings():
    return [Fitting("globe_valve", quantity=2), Fitting("standard_elbow_90_deg", quantity=6)]


# ----------------------------------------------------------------------------
# P10
# ----------------------------------------------------------------------------

def test_available_dp_sizing_meets_the_drop_with_the_fittings():
    """Two globe valves and six elbows: the friction-only search stopped at
    3.5 in, whose full drop is 86.9 kPa against the 50 kPa available."""
    summary = _run(available_dp=Pressure(50000, "Pa"), fittings=_fittings())
    assert summary["available_dp_met"] is True
    assert summary["total_pressure_drop_Pa"] <= 50000.0
    assert summary["nominal_diameter"] == Diameter(4, "in")


def test_the_selected_size_is_the_smallest_that_fits():
    summary = _run(available_dp=Pressure(50000, "Pa"), fittings=_fittings())
    sizes = sorted(PIPE_SCHEDULES, key=lambda d: d.to("m").value)
    smaller = sizes[sizes.index(summary["nominal_diameter"]) - 1]
    engine = PipelineEngine().fit(fluid=Water(), flowrate=Q, length=Length(100, "m"))
    trial = Pipe("t", nominal_diameter=smaller, length=Length(100, "m"))
    trial.fittings = _fittings()
    with contextlib.redirect_stdout(io.StringIO()):
        dp = engine._pipe_calculation(trial, Q)["pressure_drop"]
    assert dp.to("Pa").value > 50000.0


def test_an_unreachable_drop_is_reported_as_not_met():
    summary = _run(available_dp=Pressure(1, "Pa"), fittings=_fittings())
    assert summary["available_dp_met"] is False
    assert summary["total_pressure_drop_Pa"] > 1.0


# ----------------------------------------------------------------------------
# P14
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("specs", [{}, {"available_dp": Pressure(50000, "Pa")}])
def test_sizing_reports_the_internal_diameter_it_used(specs):
    summary = _run(**specs)
    implied = math.sqrt(4.0 * Q.to("m3/s").value / (math.pi * summary["velocity"]))
    assert summary["calculated_diameter_m"] == pytest.approx(implied, rel=1e-9)
    nominal = summary["nominal_diameter"]
    assert summary["calculated_diameter_m"] == pytest.approx(
        PIPE_SCHEDULES[nominal]["STD"][2].to("m").value, rel=1e-12)


def test_standard_diameter_selection_returns_a_bore():
    engine = PipelineEngine()
    # 3.5 in STD has a 90.12 mm bore, too small for 95 mm; 4 in STD is 102.26 mm.
    label, d = engine._select_standard_diameter(0.095)
    assert label == "4 in"
    assert d.to("mm").original_value == pytest.approx(102.26)


# ----------------------------------------------------------------------------
# P15
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("given, key", [
    ("40", "S40"), ("Sch40", "S40"), ("sch 40", "S40"), ("SCH-80", "S80"),
    ("schedule 160", "S160"), ("40s", "40S"), ("std", "STD"), ("xs", "XS"),
    ("S40", "S40"), ("XXS", "XXS"),
])
def test_schedule_spellings(given, key):
    assert normalize_schedule(given) == key


def test_sch40_pipe_uses_the_sch40_bore():
    pipe = Pipe("X", nominal_diameter=Diameter(4, "in"), schedule="40", length=Length(100, "m"))
    assert pipe.schedule == "S40"
    assert pipe.internal_diameter.to("mm").original_value == pytest.approx(102.26)


def test_an_untabulated_schedule_is_refused():
    with pytest.raises(ValueError, match="not tabulated for 4 in"):
        Pipe("X", nominal_diameter=Diameter(4, "in"), schedule="S35", length=Length(100, "m"))
