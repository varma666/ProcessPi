"""HeatExchangerResults.summary() display (#86 follow-up).

The summary prints each quantity in a fixed display unit. Since the unit
objects store SI (#87), `x.to(unit).value` is the SI base value, not the
number in `unit`, so the duty came out in W labelled kW and the pressure
drops in Pa labelled kPa. These tests pin the printed numbers against the
values in the results.
"""

import contextlib
import io
import math
import re

import pytest

from processpi.components import Benzene, OrganicLiquid, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.engine import HeatExchangerResults
from processpi.streams import MaterialStream
from processpi.units import (
    Area,
    HeatFlow,
    HeatTransferCoefficient,
    Length,
    MassFlowRate,
    Pressure,
    SpecificHeat,
    Temperature,
    Velocity,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _line(summary, label):
    """The value part of the summary line that starts with `label`."""
    for line in summary.splitlines():
        if line.startswith(label):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"no '{label}' line in summary:\n{summary}")


def _number(text):
    return float(re.match(r"-?[\d.]+", text).group())


def _benzene_cooler(**specs):
    """docs/examples benzene cooler: benzene 21 000 kg/h 90 to 30 C, water 60 500 kg/h from 15 C."""
    engine = HeatExchangerEngine().fit(
        hot_in=MaterialStream("hot_in", component=Benzene(),
                              temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(),
                               temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(),
                               temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
        U=HeatTransferCoefficient(575, "W/m2K"),
        mode="design",
        **specs,
    )
    return _quiet(engine.run)


def _kerosene_double_pipe(mode="design", **specs):
    """Kerosene 2 kg/s 120 to 80 C against water 1.5 kg/s from 20 C (test_unit_system H10)."""
    engine = HeatExchangerEngine(method="kern").fit(
        hot_in=MaterialStream("kerosene_in", component=OrganicLiquid(),
                              temperature=Temperature(120, "C"),
                              mass_flow=MassFlowRate(2, "kg/s"),
                              specific_heat=SpecificHeat(2470, "J/kgK")),
        hot_out=MaterialStream("kerosene_out", component=OrganicLiquid(),
                               temperature=Temperature(80, "C")),
        cold_in=MaterialStream("water_in", component=Water(),
                               temperature=Temperature(20, "C"),
                               mass_flow=MassFlowRate(1.5, "kg/s"),
                               specific_heat=SpecificHeat(4180, "J/kgK")),
        hx_type="double_pipe", mode=mode, U=350.0, **specs,
    )
    return _quiet(engine.run)


# ----------------------------------------------------------------------------
# Display units
# ----------------------------------------------------------------------------

def test_summary_prints_each_quantity_in_its_display_unit():
    summary = HeatExchangerResults({
        "hx_type": "shell_and_tube",
        "Q": HeatFlow(611.56, "kW"),
        "Area": Area(27.935, "m2"),
        "U_calculated": HeatTransferCoefficient(705.119, "W/m2K"),
        "tube_velocity": Velocity(2.155, "m/s"),
        "shell_velocity": Velocity(0.545, "m/s"),
        "tube_dp": Pressure(76244.734, "Pa"),
        "shell_dp": Pressure(0.2136, "bar"),
        "tube_length": Length(3000, "mm"),
    }).summary()

    assert _line(summary, "Heat Duty") == "611.560 kW"
    assert _line(summary, "Area") == "27.935 m2"
    assert _line(summary, "U Calculated") == "705.119 W/m2K"
    assert _line(summary, "Tube Velocity") == "2.155 m/s"
    assert _line(summary, "Shell Velocity") == "0.545 m/s"
    assert _line(summary, "Tube Pressure Drop") == "76.245 kPa"
    assert _line(summary, "Shell Pressure Drop") == "21.360 kPa"
    assert _line(summary, "Tube Length") == "3.000 m"


def test_summary_of_a_design_run_matches_its_results():
    """The docs benzene cooler printed 611559.619 kW and 76244.734 kPa."""
    results = _benzene_cooler(shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"))
    data, summary = results.data, results.summary()

    assert _number(_line(summary, "Heat Duty")) == pytest.approx(
        data["Q"].to("W").value / 1000.0, abs=1e-3)
    assert 500 < _number(_line(summary, "Heat Duty")) < 800
    assert _number(_line(summary, "Tube Pressure Drop")) == pytest.approx(
        data["tube_dp"].to("Pa").value / 1000.0, abs=1e-3)
    assert _number(_line(summary, "Shell Pressure Drop")) == pytest.approx(
        data["shell_dp"].to("Pa").value / 1000.0, abs=1e-3)
    assert _number(_line(summary, "Tube Pressure Drop")) < 100.0


# ----------------------------------------------------------------------------
# Pressure drop limits
# ----------------------------------------------------------------------------

def test_design_reports_the_user_pressure_drop_limits():
    """The Pressure Drop Assessment block read `data["specs"]`, which no result
    carries, so it never printed. The exchanger now reports the limits it
    checked the pressure drops against."""
    results = _benzene_cooler(shell_dp=Pressure(1, "bar"), tube_dp=Pressure(0.8, "bar"))

    assert results.data["tube_dp_limit"].to("Pa").value == pytest.approx(80_000)
    assert results.data["shell_dp_limit"].to("Pa").value == pytest.approx(100_000)

    summary = results.summary()
    assert "Pressure Drop Assessment" in summary
    assert _line(summary, "Tube ΔP Limit") == "80.000 kPa"
    assert _line(summary, "Shell ΔP Limit") == "100.000 kPa"
    assert _line(summary, "Tube ΔP Actual") == _line(summary, "Tube Pressure Drop")
    assert _line(summary, "Shell ΔP Actual") == _line(summary, "Shell Pressure Drop")


def test_design_without_limits_reports_the_default_it_applied():
    results = _benzene_cooler()
    tube_limit = results.data["tube_dp_limit"].to("Pa").value
    shell_limit = results.data["shell_dp_limit"].to("Pa").value

    # Both liquids are below 1 cP, so the built-in limit is 35 kPa on each side.
    assert tube_limit == pytest.approx(35_000)
    assert shell_limit == pytest.approx(35_000)
    assert _line(results.summary(), "Tube ΔP Limit") == "35.000 kPa"

    pressure_ok = results.data["feasibility_summary"]["pressure_drop_ok"]
    within = (results.data["tube_dp"].to("Pa").value <= tube_limit
              and results.data["shell_dp"].to("Pa").value <= shell_limit)
    assert pressure_ok == within


def test_rating_reports_the_pressure_drop_limits():
    engine = HeatExchangerEngine().fit(
        hot_in=MaterialStream("hot_in", component=Benzene(),
                              temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(),
                               temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(),
                               temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water(),
                                temperature=Temperature(25, "C")),
        U=HeatTransferCoefficient(575, "W/m2K"), tube_dp=Pressure(50, "kPa"),
        mode="rate", tube_od=0.01905, tube_id=0.016, tube_length=4.88,
        tube_count=200, tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18,
    )
    results = _quiet(engine.run)

    assert results.data["tube_dp_limit"].to("Pa").value == pytest.approx(50_000)
    # rate() falls back to 14 kPa on the shell side when no limit is given.
    assert results.data["shell_dp_limit"].to("Pa").value == pytest.approx(14_000)
    assert _line(results.summary(), "Tube ΔP Limit") == "50.000 kPa"


# ----------------------------------------------------------------------------
# Double pipe results carry units like shell-and-tube
# ----------------------------------------------------------------------------

_DOUBLE_PIPE_UNITS = {
    "Area": "m2",
    "U_calculated": "W/m2K",
    "U_assumed": "W/m2K",
    "tube_od": "m",
    "tube_id": "m",
    "tube_length": "m",
    "shell_diameter": "m",
    "tube_velocity": "m/s",
    "shell_velocity": "m/s",
    "tube_dp": "Pa",
    "shell_dp": "Pa",
}


def test_double_pipe_design_results_are_unit_objects():
    data = _kerosene_double_pipe().data
    for key, unit in _DOUBLE_PIPE_UNITS.items():
        assert hasattr(data[key], "to"), f"{key} is a bare {type(data[key]).__name__}"
        assert data[key].to(unit).original_value > 0, key

    # Same area as test_unit_system's hand calculation: Q / (U LMTD) at U = 350.
    assert data["Area"].to("m2").value == pytest.approx(
        197_600 / (350 * data["LMTD"]), rel=1e-6)
    assert data["U_calculated"].to("W/m2K").value == pytest.approx(350.0)


def test_double_pipe_summary_shows_units():
    summary = _kerosene_double_pipe().summary()
    assert _line(summary, "Area").endswith(" m2")
    assert _line(summary, "U Calculated") == "350.000 W/m2K"
    assert _line(summary, "Tube Velocity").endswith(" m/s")
    assert _line(summary, "Tube Pressure Drop").endswith(" kPa")
    assert _line(summary, "Heat Duty") == "197.600 kW"


def test_double_pipe_rating_results_are_unit_objects():
    data = _kerosene_double_pipe(
        mode="rate", tube_od=0.0483, tube_id=0.0409, tube_length=6.0,
        annulus_diameter=0.0779, area=math.pi * 0.0483 * 6.0,
    ).data
    for key, unit in _DOUBLE_PIPE_UNITS.items():
        assert hasattr(data[key], "to"), f"{key} is a bare {type(data[key]).__name__}"
        assert data[key].to(unit).original_value > 0, key
