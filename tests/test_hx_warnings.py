"""Heat exchanger design warnings describe the design reported (#86 follow-up).

The Kern design loop tries several geometries before it settles. Warnings
raised on the way (velocity out of band, tube count capped) were appended on
every pass and never cleared, so the results listed warnings about geometries
that were not the one reported: the docs benzene cooler said its shell
velocity was 0.462 m/s and outside 0.5-1.5 m/s while reporting 0.545 m/s.

An outlet stream built without a temperature also carried the component's
default 25 C, which the outlet check read as a user value and flagged as
disagreeing with the energy balance.
"""

import contextlib
import io
import logging
import re

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
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


def _benzene_cooler(cold_out=None, **specs):
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
        cold_out=cold_out if cold_out is not None else MaterialStream("cold_out", component=Water()),
        U=HeatTransferCoefficient(575, "W/m2K"),
        shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
        mode="design", **specs,
    )
    return _quiet(engine.run).data


def _benzene_condenser():
    """docs/examples benzene condenser; its U cycles between 192 and 280 tubes."""
    engine = HeatExchangerEngine(method="bell_delaware").fit(
        hx_type="condenser",
        hot_in=MaterialStream("benzene_vapor_in", component=Benzene(), phase="vapor",
                              temperature=Temperature(95, "C"),
                              pressure=Pressure(1.2, "bar"),
                              mass_flow=MassFlowRate(12000, "kg/h")),
        hot_out=MaterialStream("benzene_liquid_out", component=Benzene(), phase="liquid",
                               temperature=Temperature(95, "C")),
        cold_in=MaterialStream("cw_in", component=Water(), phase="liquid",
                               temperature=Temperature(30, "C"),
                               pressure=Pressure(1, "bar"),
                               mass_flow=MassFlowRate(50000, "kg/h")),
        cold_out=MaterialStream("cw_out", component=Water()),
        latent_heat=394000,
        shell_dp=Pressure(0.5, "bar"), tube_dp=Pressure(0.5, "bar"),
        orientation="horizontal", mode="design",
    )
    return _quiet(engine.run).data


def _velocity(data, side):
    return data[f"{side}_velocity"].to("m/s").value


def _assert_velocity_warnings_match(data):
    """Every velocity a warning quotes, or says is out of band, is the reported one."""
    for warning in data["warnings"]:
        for side in ("tube", "shell"):
            band = re.search(
                rf"{side.capitalize()} velocity slightly outside preferred range "
                r"\(([\d.]+)-([\d.]+) m/s\)", warning)
            if band:
                lo, hi = float(band.group(1)), float(band.group(2))
                v = _velocity(data, side)
                assert not lo <= v <= hi, (
                    f"'{warning}' but the reported {side} velocity is {v:.3f} m/s")
            quoted = re.search(rf"{side.capitalize()} velocity ([\d.]+) m/s is outside", warning)
            if quoted:
                assert float(quoted.group(1)) == pytest.approx(_velocity(data, side), abs=5e-4), warning


# ----------------------------------------------------------------------------
# Warnings belong to the reported geometry
# ----------------------------------------------------------------------------

def test_cooler_warnings_describe_the_reported_geometry():
    data = _benzene_cooler()
    assert 0.5 <= _velocity(data, "shell") <= 1.5
    _assert_velocity_warnings_match(data)
    assert not [w for w in data["warnings"] if "Shell velocity" in w]


def test_condenser_cycle_keeps_the_warnings_of_the_pass_it_settles_on():
    """The condenser settles on 192 tubes out of a 192/280 cycle. The warnings
    reported must be those of the 192-tube pass, plus the cycle warning."""
    data = _benzene_condenser()
    assert data["tube_count"] == 192
    assert any("U cycles between tube counts" in w for w in data["warnings"])
    _assert_velocity_warnings_match(data)


def test_warnings_are_not_repeated():
    for data in (_benzene_cooler(), _benzene_condenser()):
        assert len(data["warnings"]) == len(set(data["warnings"]))


def test_each_warning_is_logged_once(caplog):
    with caplog.at_level(logging.WARNING, logger="processpi.hx"):
        data = _benzene_cooler()
    logged = [r.getMessage() for r in caplog.records if r.name.startswith("processpi.hx")]
    assert logged, "expected the Sieder-Tate assumption warnings to be logged"
    assert len(logged) == len(set(logged))
    for message in logged:
        if message.startswith("[ASSUMPTION_WARNING]"):
            assert message in data["warnings"]


# ----------------------------------------------------------------------------
# Specified outlet check
# ----------------------------------------------------------------------------

def _balance_warnings(data):
    return [w for w in data["warnings"] if w.startswith("[BALANCE_WARNING]")]


def test_outlet_without_temperature_is_not_checked():
    """cold_out has no temperature, so it carries Water()'s default 25 C."""
    data = _benzene_cooler(cold_out=MaterialStream("cold_out", component=Water()))
    assert _balance_warnings(data) == []


def test_specified_outlet_that_disagrees_is_still_reported():
    data = _benzene_cooler(cold_out=MaterialStream("cold_out", component=Water(),
                                                   temperature=Temperature(40, "C")))
    (warning,) = _balance_warnings(data)
    assert "Specified cold outlet 313.15 K" in warning


def test_specified_outlet_that_agrees_is_not_reported():
    """The balance gives 296.85 K for the cold outlet."""
    data = _benzene_cooler(cold_out=MaterialStream("cold_out", component=Water(),
                                                   temperature=Temperature(296.85, "K")))
    assert _balance_warnings(data) == []
