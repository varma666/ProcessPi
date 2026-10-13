"""Rating (mode="rate") of condensers, reboilers and evaporators.

rate() re-inferred the service from the specs alone and, with no `service`
spec, rated a condensing stream as a sensible cooler. The vapour of the docs
n-propanol condenser (docs/examples/equipment/heatexchanger/
nproponal_condenser.md) goes in and out at 118 C, so its sensible duty was
0 kW, its required area 0 m2 and its thermal check a PASS by default. A boiling
stream in a reboiler or evaporator gave the same zero duty.

rate() now rates a CondenserHX, EvaporatorHX or ReboilerHX, or streams that go
from vapour to liquid (or liquid to vapour), on the latent duty, the duty
design() sizes on, and refuses to rate a zero duty.

The latent heats below are inputs (`latent_heat`), so the hand calculations
need no property data: 663 kJ/kg is the value the docs page passes.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, OrganicLiquid, Toluene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.streams import MaterialStream
from processpi.units import HeatTransferCoefficient, Length, MassFlowRate, Pressure, Temperature


# The docs page: 60 000 lb/h of n-propanol vapour condensing at 118 C. The
# library converts lb at 0.453592 kg (1 ppm off 0.45359237): 7.55987 kg/s.
M_HOT = MassFlowRate(60000, "lb/h").to("kg/s").value
LATENT = 663000.0  # J/kg
T_COND = 118.0 + 273.15
TC_IN = 29.4 + 273.15
TC_OUT = 40.6 + 273.15


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _w(value, unit):
    return value.to(unit).value


def _condenser_streams(cold_flow=None, hot_out_phase="liquid"):
    cold_in = dict(component=Water(), phase="liquid",
                   temperature=Temperature(29.4, "C"), pressure=Pressure(1, "bar"))
    if cold_flow is not None:
        cold_in["mass_flow"] = MassFlowRate(cold_flow, "kg/s")
    return dict(
        hot_in=MaterialStream("npropanol_vapor_in", component=OrganicLiquid(), phase="vapor",
                              temperature=Temperature(118, "C"), pressure=Pressure(2.03, "bar"),
                              mass_flow=MassFlowRate(60000, "lb/h")),
        hot_out=MaterialStream("npropanol_liquid_out", component=OrganicLiquid(),
                               phase=hot_out_phase, temperature=Temperature(118, "C")),
        cold_in=MaterialStream("cooling_water_in", **cold_in),
        cold_out=MaterialStream("cooling_water_out", component=Water(),
                                temperature=Temperature(40.6, "C")),
    )


def _rate_condenser(hx_type="condenser", cold_flow=None, hot_out_phase="liquid", **specs):
    """The docs page's rating run, with `specs` overriding its keywords."""
    keywords = dict(
        latent_heat=LATENT,
        orientation="horizontal",
        shell_passes=1,
        tube_passes=4,
        tube_length=Length(8, "ft").to("m").value,
        tube_od=Length(0.75, "in").to("m").value,
        tube_id=Length(0.70, "in").to("m").value,
        tube_count=766,
        shell_diameter=Length(31, "in").to("m").value,
        tube_pitch=Length(1.0625, "in").to("m").value,
        tube_layout="triangular",
        shell_dp=Pressure(2, "psi"),
        tube_dp=Pressure(10, "psi"),
        assumed_U=HeatTransferCoefficient(568, "W/m2K"),
        mode="rate",
    )
    keywords.update(specs)
    keywords = {k: v for k, v in keywords.items() if v is not None}
    engine = HeatExchangerEngine(method="bell_delaware").fit(
        hx_type=hx_type, **_condenser_streams(cold_flow, hot_out_phase), **keywords,
    )
    return _quiet(engine.run).data


def _condensing_lmtd():
    """Condensing LMTD of the docs page, hand calculation."""
    dt_hot_end = T_COND - TC_OUT
    dt_cold_end = T_COND - TC_IN
    return (dt_cold_end - dt_hot_end) / math.log(dt_cold_end / dt_hot_end)


# ----------------------------------------------------------------------------
# Condenser
# ----------------------------------------------------------------------------

def test_condenser_rating_duty_is_the_latent_duty():
    data = _rate_condenser()
    # Q = m lambda = 7.5599 kg/s x 663 kJ/kg = 5012.19 kW (was 0 kW).
    assert _w(data["Q"], "W") == pytest.approx(M_HOT * LATENT, rel=1e-9)
    # Area the duty needs at assumed_U 568 W/m2K and F = 1:
    # 5012.19 kW / (568 x 82.874) = 106.48 m2 (was 0 m2).
    required = M_HOT * LATENT / (568.0 * _condensing_lmtd())
    assert _w(data["Area_required"], "m2") == pytest.approx(required, rel=1e-6)
    assert data["feasibility_summary"]["thermal_ok"] is True  # 111.78 m2 >= 106.48 m2


def test_condenser_rating_duty_matches_the_cold_side_duty():
    # Cooling water flow that takes the latent duty from 29.4 to 40.6 C, at the
    # cp of the library's Water at the 35 C mean temperature.
    cp_water = Water(temperature=Temperature(35, "C")).specific_heat().to("J/kgK").value
    cold_flow = M_HOT * LATENT / (cp_water * (TC_OUT - TC_IN))
    data = _rate_condenser(cold_flow=cold_flow)
    cold = data["property_basis"]["cold"]
    assert cold["temperature_K"] == pytest.approx(0.5 * (TC_IN + TC_OUT))
    assert cold["cp_J_kgK"] == pytest.approx(cp_water, rel=1e-12)
    q_cold = cold_flow * cold["cp_J_kgK"] * (TC_OUT - TC_IN)
    assert _w(data["Q"], "W") == pytest.approx(q_cold, rel=1e-9)
    assert not any(w.startswith("[BALANCE_WARNING]") for w in data["warnings"])


def test_condenser_rating_warns_when_the_cold_outlet_disagrees_with_the_duty():
    cp_water = Water(temperature=Temperature(35, "C")).specific_heat().to("J/kgK").value
    cold_flow = 1.2 * M_HOT * LATENT / (cp_water * (TC_OUT - TC_IN))
    data = _rate_condenser(cold_flow=cold_flow)
    # The latent duty stays the rated duty; the 20% larger water flow would
    # leave at 29.4 + 11.2 / 1.2 = 38.73 C, not the 40.6 C specified.
    assert _w(data["Q"], "W") == pytest.approx(M_HOT * LATENT, rel=1e-9)
    assert any(
        w.startswith("[BALANCE_WARNING]") and "cold outlet at 311.88 K" in w
        for w in data["warnings"]
    )


def test_partial_condenser_rating_uses_the_condensed_fraction():
    # design() condenses `vapor_fraction_condensed` of the vapour; so does rate().
    data = _rate_condenser(condensation_mode="partial", vapor_fraction_condensed=0.7)
    assert _w(data["Q"], "W") == pytest.approx(0.7 * M_HOT * LATENT, rel=1e-9)


def test_undersized_condenser_fails_the_thermal_check():
    # 600 tubes give 600 pi 0.01905 x 2.4384 = 87.56 m2, short of the 106.48 m2
    # the latent duty needs. The zero duty used to pass this exchanger.
    data = _rate_condenser(tube_count=600)
    area = 600 * math.pi * Length(0.75, "in").to("m").value * Length(8, "ft").to("m").value
    assert _w(data["Area"], "m2") == pytest.approx(area, rel=1e-6)
    assert _w(data["Area_required"], "m2") > area
    assert data["feasibility_summary"]["thermal_ok"] is False
    assert data["status"] == "THERMAL_FAILURE"


def test_shell_and_tube_rating_reads_condensation_from_the_stream_phases():
    # A plain shell-and-tube exchanger whose hot stream goes in as vapour and
    # out as liquid condenses it, as the engine's own type selection reads it.
    data = _rate_condenser(hx_type="shell_and_tube", cold_flow=107.0)
    assert data["service"] == "condenser"
    assert _w(data["Q"], "W") == pytest.approx(M_HOT * LATENT, rel=1e-9)


def test_shell_and_tube_rating_of_a_condensing_stream_needs_its_latent_heat():
    with pytest.raises(ValueError, match="latent_heat"):
        _rate_condenser(hx_type="shell_and_tube", latent_heat=None, cold_flow=107.0)


# ----------------------------------------------------------------------------
# Reboiler and evaporator
# ----------------------------------------------------------------------------

def _rate_boiler(hx_type):
    """Toluene boiling at 111 C on pressurised water cooling from 180 to 150 C."""
    streams = dict(
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
    engine = HeatExchangerEngine(method="kern").fit(
        hx_type=hx_type, **streams, latent_heat=360000.0, tube_passes=2,
        tube_length=4.88, tube_od=0.01905, tube_id=0.0157, tube_count=300,
        shell_diameter=0.6, tube_pitch=0.0254, mode="rate",
    )
    return _quiet(engine.run).data


@pytest.mark.parametrize("hx_type", ["reboiler", "evaporator"])
def test_boiler_rating_duty_is_the_latent_duty(hx_type):
    data = _rate_boiler(hx_type)
    # Q = m lambda = 6 kg/s x 360 kJ/kg = 2160 kW (was 0 kW).
    assert _w(data["Q"], "W") == pytest.approx(6.0 * 360000.0, rel=1e-9)
    # Boiling at constant temperature: LMTD from 180 -> 150 C against 111 C.
    lmtd = (69.0 - 39.0) / math.log(69.0 / 39.0)
    assert data["corrected_lmtd"] == pytest.approx(lmtd, rel=1e-9)
    u_assumed = _w(data["U_assumed"], "W/m2K")
    assert _w(data["Area_required"], "m2") == pytest.approx(
        6.0 * 360000.0 / (u_assumed * lmtd), rel=1e-6
    )


# ----------------------------------------------------------------------------
# Zero duty
# ----------------------------------------------------------------------------

def test_condensing_stream_without_phase_change_information_is_not_passed():
    # Vapour in and out at 118 C with nothing saying it condenses: no sensible
    # duty. This used to rate as 0 kW, 0 m2 required and a thermal PASS.
    with pytest.raises(ValueError, match="no heat duty"):
        _rate_condenser(hx_type="shell_and_tube", hot_out_phase=None, cold_flow=107.0)


def test_zero_sensible_duty_is_not_passed():
    streams = dict(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(90, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water(), temperature=Temperature(25, "C")),
    )
    engine = HeatExchangerEngine().fit(
        **streams, mode="rate", tube_od=0.01905, tube_id=0.016, tube_length=4.88,
        tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18,
    )
    with pytest.raises(ValueError, match="no heat duty"):
        _quiet(engine.run)


# ----------------------------------------------------------------------------
# Guard: sensible rating is unchanged
# ----------------------------------------------------------------------------

def test_cooler_rating_is_unchanged():
    """docs benzene cooler, rated: 21 000 kg/h benzene 90 to 30 C on water 15 to 25 C."""
    streams = dict(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water(), temperature=Temperature(25, "C")),
    )
    engine = HeatExchangerEngine().fit(
        **streams, mode="rate", tube_od=0.01905, tube_id=0.016, tube_length=4.88,
        tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18,
    )
    data = _quiet(engine.run).data
    assert data["service"] == "cooler"
    # The smaller of the two sensible duties, here the benzene side's.
    cp_hot = data["property_basis"]["hot"]["cp_J_kgK"]
    q_hot = 21000 / 3600.0 * cp_hot * 60.0
    assert _w(data["Q"], "W") == pytest.approx(q_hot, rel=1e-9)
    # Values before this change (9b137a9), unchanged.
    assert _w(data["Q"], "W") == pytest.approx(649112.6188603034, rel=1e-9)
    assert _w(data["Area_required"], "m2") == pytest.approx(42.55873965185944, rel=1e-9)
    assert data["status"] == "PRESSURE_DROP_FAILURE"
