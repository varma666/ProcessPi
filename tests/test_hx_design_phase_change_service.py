"""design() runs a condenser, reboiler or evaporator as the service rate() does.

design() classified the service itself: a `service` spec of "condenser" (with
a vapour inlet) or "evaporator" (with a vapour cold inlet), otherwise a heater
when the hot inlet is a vapour and a cooler when it is not. rate() takes the
`service` spec, then the phase-change service of the exchanger class
(`_PHASE_CHANGE_SERVICE`), then a phase change the outlet phases prove. So a
CondenserHX, EvaporatorHX or ReboilerHX designed with no `service` spec was
designed as a heater or cooler, and a `service` of "reboiler" was ignored.
Its duty was still the latent one, but the velocity bands keyed on the
service were not: the docs benzene condenser
(docs/examples/equipment/heatexchanger/benzene_condenser.md) was sized on the
1.0-2.5 m/s liquid band for its cooling-water tubes, came out at 120 tubes
with 2.33 m/s in them, and passed its hydraulic check, while rate() judges the
same tubes against the 0.6-2.0 m/s condenser band, which 2.33 m/s fails.

design() now calls `_infer_service_type`, the resolution rate() uses, before
its energy balance. A vapour inlet alone still does not make a condenser
(cb682f1): the class, an explicit `service` or a proven phase change does.

The bands are those of `_get_velocity_limits`; no limit is changed here.
"""

import contextlib
import io

import pytest

from processpi.components import Benzene, Toluene, Water
from processpi.equipment.heatexchangers import (
    CondenserHX,
    EvaporatorHX,
    HeatExchangerEngine,
    ReboilerHX,
)
from processpi.streams import MaterialStream
from processpi.units import HeatTransferCoefficient, MassFlowRate, Pressure, Temperature


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _w(value, unit):
    return value.to(unit).value


# ----------------------------------------------------------------------------
# Cases
# ----------------------------------------------------------------------------

def _benzene_streams(cold_out_c=None):
    """The docs benzene condenser: 12 000 kg/h benzene vapour at 95 C on water."""
    cold_out = dict(component=Water())
    if cold_out_c is not None:
        cold_out["temperature"] = Temperature(cold_out_c, "C")
    return dict(
        hot_in=MaterialStream("benzene_vapor_in", component=Benzene(), phase="vapor",
                              temperature=Temperature(95, "C"), pressure=Pressure(1.2, "bar"),
                              mass_flow=MassFlowRate(12000, "kg/h")),
        hot_out=MaterialStream("benzene_liquid_out", component=Benzene(), phase="liquid",
                               temperature=Temperature(95, "C")),
        cold_in=MaterialStream("cw_in", component=Water(), phase="liquid",
                               temperature=Temperature(30, "C"), pressure=Pressure(1, "bar"),
                               mass_flow=MassFlowRate(50000, "kg/h")),
        cold_out=MaterialStream("cw_out", **cold_out),
    )


BENZENE_SPECS = dict(
    latent_heat=394000,
    shell_dp=Pressure(0.5, "bar"),
    tube_dp=Pressure(0.5, "bar"),
    orientation="horizontal",
)


def _boiler_streams():
    """Toluene boiling at 111 C on pressurised water cooling from 180 to 150 C."""
    return dict(
        hot_in=MaterialStream("hot_in", component=Water(), phase="liquid",
                              temperature=Temperature(180, "C"), pressure=Pressure(15, "bar"),
                              mass_flow=MassFlowRate(20, "kg/s")),
        hot_out=MaterialStream("hot_out", component=Water(), phase="liquid",
                               temperature=Temperature(150, "C")),
        cold_in=MaterialStream("cold_in", component=Toluene(), phase="liquid",
                               temperature=Temperature(111, "C"), pressure=Pressure(1.013, "bar"),
                               mass_flow=MassFlowRate(6, "kg/s")),
        cold_out=MaterialStream("cold_out", component=Toluene(), phase="vapor",
                                temperature=Temperature(111, "C")),
    )


BOILER_SPECS = dict(latent_heat=360000.0)

# Class, streams, specs, method, and the (tube, shell) bands of
# `_get_velocity_limits` for its phase-change service: the coolant tubes of
# a shell-side condenser take the condenser band, its vapour shell the vapour
# band; the reboiler and evaporator bands hold on both sides.
CASES = {
    "condenser": (CondenserHX, _benzene_streams, BENZENE_SPECS, "bell_delaware",
                  (0.6, 2.0), (10.0, 30.0)),
    "reboiler": (ReboilerHX, _boiler_streams, BOILER_SPECS, "kern",
                 (0.6, 2.0), (0.3, 1.0)),
    "evaporator": (EvaporatorHX, _boiler_streams, BOILER_SPECS, "kern",
                   (0.8, 2.0), (0.3, 1.0)),
}


def _design(case, **specs):
    cls, streams, base_specs, method, _, _ = CASES[case]
    hx = cls(**streams(), method=method, **{**base_specs, **specs})
    return hx, _quiet(hx.design)


def _band(results, side):
    return tuple(results[f"{side}_velocity_band"])


def _velocity(results, side):
    return _w(results[f"{side}_velocity"], "m/s")


# ----------------------------------------------------------------------------
# Design without a `service` spec
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(CASES))
def test_design_without_service_runs_the_phase_change_service(case):
    hx, results = _design(case)
    _, _, _, _, tube_band, shell_band = CASES[case]
    # Before: "heater" for the condenser (vapour hot inlet) and "cooler" for
    # the reboiler and evaporator (liquid water heating medium).
    assert hx.service_type == case
    # Before: the liquid bands, tube (1.0, 2.5) and, on the boiling shell of
    # the reboiler and evaporator, (0.5, 1.5).
    assert _band(results, "tube") == tube_band
    assert _band(results, "shell") == shell_band
    # The design meets the bands it was sized on.
    for side in ("tube", "shell"):
        vmin, vmax = _band(results, side)
        assert vmin <= _velocity(results, side) <= vmax
    assert results["feasibility_summary"]["hydraulic_ok"] is True


def test_docs_benzene_condenser_is_sized_on_the_condenser_band():
    hx = HeatExchangerEngine(method="bell_delaware").fit(
        hx_type="condenser", **_benzene_streams(), **BENZENE_SPECS, mode="design",
    )
    results = _quiet(hx.run).data
    assert _band(results, "tube") == (0.6, 2.0)
    # Before: 120 tubes, 35.81 m2, 2.330 m/s in the tubes (above the 2.0 m/s
    # rate() allows a condenser's coolant) and 29.07 m/s in the shell.
    assert results["tube_count"] == 140
    assert _w(results["Area"], "m2") == pytest.approx(41.783, abs=1e-3)
    assert _velocity(results, "tube") == pytest.approx(1.997, abs=1e-3)
    assert _velocity(results, "shell") == pytest.approx(25.587, abs=1e-3)
    # The pressure drops still exceed the page's 0.5 bar limits, as before.
    assert results["status"] == "PRESSURE_DROP_FAILURE"


def test_engine_auto_selected_condenser_is_designed_as_one():
    # No hx_type: the engine reads vapour in, liquid out and picks a condenser.
    hx = HeatExchangerEngine(method="bell_delaware").fit(
        **_benzene_streams(), **BENZENE_SPECS, mode="design",
    )
    results = _quiet(hx.run).data
    assert results["hx_type_selection"]["hx_type"] == "condenser"
    assert _band(results, "tube") == (0.6, 2.0)
    assert results["tube_count"] == 140


def test_service_type_survives_a_design_run():
    # design() used to overwrite the "condenser" __init__ sets with "heater",
    # so everything read after it (the latent side of the energy balance,
    # a later rate()) saw a heater.
    hx, _ = _design("condenser")
    assert hx.service_type == "condenser"
    assert hx._latent_side_for_energy_balance() == "hot"


# ----------------------------------------------------------------------------
# design() and rate() agree
# ----------------------------------------------------------------------------

def _rate_the_design(case, design_results, **specs):
    """Rate the geometry design() produced, with design()'s outlets."""
    cls, streams, base_specs, method, _, _ = CASES[case]
    geometry = {
        key: _w(design_results[key], "m")
        for key in ("tube_od", "tube_id", "tube_length", "shell_diameter", "baffle_spacing")
    }
    geometry.update(
        tube_count=design_results["tube_count"],
        tube_passes=design_results["tube_passes"],
        shell_passes=design_results["shell_passes"],
    )
    if case == "condenser":
        # The mean water temperature puts the outlet at 2 T_mean - T_in.
        t_mean = design_results["property_basis"]["cold"]["temperature_K"]
        rate_streams = _benzene_streams(cold_out_c=2.0 * t_mean - (30.0 + 273.15) - 273.15)
    else:
        rate_streams = streams()
    hx = cls(**rate_streams, method=method, **{**base_specs, **geometry, **specs})
    return hx, _quiet(hx.rate)


@pytest.mark.parametrize("case", sorted(CASES))
def test_design_and_rate_of_one_exchanger_agree_on_service_and_bands(case):
    hx_design, designed = _design(case)
    hx_rate, rated = _rate_the_design(case, designed)
    assert hx_design.service_type == hx_rate.service_type == case
    assert designed["service"] == rated["service"]
    for side in ("tube", "shell"):
        assert _band(designed, side) == _band(rated, side)
    # Same geometry and flows, so the same velocities to within the property
    # basis (rate() takes the specified 150 C water outlet of the boilers,
    # design() the 155 C its energy balance gives), and the same verdict.
    for side in ("tube", "shell"):
        assert _velocity(rated, side) == pytest.approx(_velocity(designed, side), rel=5e-3)
    assert rated["feasibility_summary"]["hydraulic_ok"] is designed["feasibility_summary"]["hydraulic_ok"]


def test_explicit_condenser_variant_gets_the_condenser_band_in_both_modes():
    # design() mapped service="total_condenser" to the condenser band; rate()
    # looked the name up as it was and fell back to the liquid band.
    _, designed = _design("condenser", service="total_condenser")
    hx_rate, rated = _rate_the_design("condenser", designed, service="total_condenser")
    assert hx_rate.service_type == "condenser"
    assert _band(designed, "tube") == _band(rated, "tube") == (0.6, 2.0)


# ----------------------------------------------------------------------------
# An explicit service still wins
# ----------------------------------------------------------------------------

def test_explicit_service_wins_over_the_class_service():
    # "vaporizer" is not the evaporator's own service; design() used to
    # replace it with "cooler" because the cold inlet is a liquid.
    hx, results = _design("evaporator", service="vaporizer")
    assert hx.service_type == "vaporizer"
    # No phase-change band for a vaporizer: the bands follow the phases.
    assert _band(results, "tube") == (1.0, 2.5)


@pytest.mark.parametrize("service", ["reboiler", "kettle_reboiler"])
def test_explicit_reboiler_service_is_no_longer_ignored(service):
    hx, results = _design("reboiler", service=service)
    # Before: "cooler", whatever the spec said.
    assert hx.service_type == "reboiler"
    assert _band(results, "tube") == (0.6, 2.0)


# ----------------------------------------------------------------------------
# Guard: sensible exchangers are designed as before
# ----------------------------------------------------------------------------

def test_benzene_cooler_design_is_unchanged():
    """The docs benzene cooler: liquid on both sides."""
    hx = HeatExchangerEngine().fit(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
        assumed_U=HeatTransferCoefficient(575, "W/m2K"),
        shell_dp=Pressure(1, "bar"),
        tube_dp=Pressure(1, "bar"),
        mode="design",
    )
    results = _quiet(hx.run).data
    # design() reported no service, so the results carried "unknown".
    assert results["service"] == "cooler"
    # Values before this change (0378aed), unchanged.
    assert results["tube_count"] == 168
    assert _w(results["Area"], "m2") == pytest.approx(30.083891250775856, rel=1e-9)
    assert _velocity(results, "tube") == pytest.approx(1.996899143861168, rel=1e-9)
    assert _velocity(results, "shell") == pytest.approx(0.5348009685683145, rel=1e-9)
    assert _band(results, "tube") == (1.0, 2.5)
    assert _band(results, "shell") == (0.5, 1.5)
    assert results["status"] == "MARGINAL"


def test_steam_heater_design_is_unchanged():
    # Steam at 160 C and 3 bar heating benzene: a vapour inlet that does not
    # condense in the model is a heater, as cb682f1 has it.
    hx = HeatExchangerEngine().fit(
        hot_in=MaterialStream("steam_in", component=Water(), phase="vapor",
                              temperature=Temperature(160, "C"), pressure=Pressure(3, "bar"),
                              mass_flow=MassFlowRate(2, "kg/s")),
        hot_out=MaterialStream("steam_out", component=Water(), temperature=Temperature(140, "C")),
        cold_in=MaterialStream("benzene_in", component=Benzene(), temperature=Temperature(20, "C"),
                               mass_flow=MassFlowRate(10, "kg/s")),
        cold_out=MaterialStream("benzene_out", component=Benzene()),
        hx_type="shell_and_tube",
        mode="design",
    )
    results = _quiet(hx.run).data
    assert results["service"] == "heater"
    # Values before this change (0378aed), unchanged.
    assert results["tube_count"] == 50
    assert _w(results["Area"], "m2") == pytest.approx(14.922565104551516, rel=1e-9)
    assert _velocity(results, "tube") == pytest.approx(2.2786477605406357, rel=1e-9)
    assert results["status"] == "PRESSURE_DROP_FAILURE"
