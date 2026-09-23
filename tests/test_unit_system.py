"""Regression tests for the unit system (issue #81).

`.value` is documented as the quantity in SI, and the calculations read it
blindly. Pressure stored whatever unit it was given, SpecificHeat stored
kJ/kg.K, and every constructor rounded the SI value to 6 decimals, so small
quantities became exactly zero. The heat exchangers carried `* 1000`
compensations for the kJ base that made latent duty and the double-pipe
outlet temperature 1000x wrong.
"""

import contextlib
import io
import math

import pytest

from processpi.calculations.heat_transfer import PrandtlNumber, SensibleHeatDuty
from processpi.components import OrganicLiquid, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.pipelines.pipelineresults import PipelineResults
from processpi.streams import MaterialStream
from processpi.units import (
    Area,
    Diameter,
    HeatFlow,
    Length,
    Mass,
    MassFlowRate,
    Pressure,
    SpecificHeat,
    Temperature,
    Volume,
    VolumetricFlowRate,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


# ---------------------------------------------------------------------------
# Pressure stores Pa
# ---------------------------------------------------------------------------

def test_pressure_value_is_in_pa_whatever_unit_it_was_given_in():
    p = Pressure(1, "bar")
    assert p.value == pytest.approx(1e5)
    assert p.units == "Pa"
    assert Pressure(1, "atm").value == pytest.approx(101325)
    assert Pressure(1, "psi").value == pytest.approx(6894.76)


def test_pressure_conversion_and_display_keep_the_given_unit():
    p = Pressure(2.5, "bar")
    assert str(p) == "2.5 bar"
    assert p.to("kPa").original_value == pytest.approx(250)
    assert p.to("kPa").value == pytest.approx(2.5e5)
    assert p.to("psi").to("bar").original_value == pytest.approx(2.5)


def test_pressure_equality_ordering_and_arithmetic_across_units():
    assert Pressure(1, "bar") == Pressure(100, "kPa")
    assert Pressure(1, "bar") < Pressure(1, "atm")
    total = Pressure(1, "bar") + Pressure(50, "kPa")
    assert total.original_unit == "bar"
    assert total.original_value == pytest.approx(1.5)
    assert total.value == pytest.approx(1.5e5)
    assert (Pressure(1, "bar") - Pressure(50, "kPa")).original_value == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# SpecificHeat has a J/kg.K base
# ---------------------------------------------------------------------------

def test_specific_heat_value_is_in_j_per_kg_k():
    assert SpecificHeat(4180, "J/kgK").value == pytest.approx(4180)
    assert SpecificHeat(4.18, "kJ/kgK").value == pytest.approx(4180)
    assert SpecificHeat(1, "cal/gK").value == pytest.approx(4186.8)
    assert SpecificHeat(1, "BTU/lbF").value == pytest.approx(4186.8)
    # The default unit is unchanged, so SpecificHeat(4.18) still means kJ/kg.K.
    assert SpecificHeat(4.18).value == pytest.approx(4180)


def test_specific_heat_to_j_gives_joules():
    """`.to("J/kgK")` used to return an object whose `.value` was in kJ."""
    cp = SpecificHeat(2.47, "kJ/kgK").to("J/kgK")
    assert cp.value == pytest.approx(2470)
    assert cp.original_value == pytest.approx(2470)


def test_prandtl_is_the_same_for_a_unit_object_and_a_float():
    """The object form used to come out 1000x low (0.006 for water)."""
    with_object = PrandtlNumber(mu=0.00089, Cp=SpecificHeat(4180, "J/kgK"), k=0.607).calculate()
    with_float = PrandtlNumber(mu=0.00089, Cp=4180, k=0.607).calculate()
    assert with_object.value == pytest.approx(with_float.value)
    assert with_object.value == pytest.approx(6.1289, rel=1e-4)


def test_sensible_heat_duty_of_water_is_in_kilowatts_not_watts():
    """10 kg/s of water over 20 K is 836 kW; it used to come out 836 W."""
    q = SensibleHeatDuty(
        mass_flow_rate=MassFlowRate(10, "kg/s"),
        specific_heat=SpecificHeat(4180, "J/kgK"),
        t_in=Temperature(80, "C"),
        t_out=Temperature(60, "C"),
    ).calculate()
    assert q.value == pytest.approx(836_000)


def test_component_specific_heat_value_matches_what_it_prints():
    cp = Water(temperature=Temperature(25, "C")).specific_heat()
    assert cp.value == pytest.approx(cp.original_value)
    assert 4000 < cp.value < 4300


# ---------------------------------------------------------------------------
# No rounding of stored values
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "quantity,expected",
    [
        (MassFlowRate(1, "g/h"), 1e-3 / 3600),
        (VolumetricFlowRate(1, "L/h"), 1e-3 / 3600),
        (Mass(1, "ug"), 1e-9),
        (Area(0.5, "mm2"), 5e-7),
        # Drawn-tubing roughness: rounding to 6 decimals stored 2e-6 m (+33%).
        (Length(0.0015, "mm"), 1.5e-6),
    ],
)
def test_small_quantities_are_not_rounded_to_zero(quantity, expected):
    assert quantity.value == pytest.approx(expected, rel=1e-12)


def test_round_trip_keeps_full_precision():
    """1 gal came back as 0.999892 gal."""
    assert Volume(1, "gal").to("m3").to("gal").original_value == pytest.approx(1, rel=1e-12)
    assert Diameter(1.5, "in").to("mm").to("in").original_value == pytest.approx(1.5, rel=1e-12)


def test_display_still_rounds():
    assert f"{Pressure(1, 'bar').to('psi')}" == "14.503768 psi"
    assert str(Diameter(1.5, "in").to("mm").to("in")) == "1.5 in"
    # A nonzero value too small for six decimals is not displayed as zero.
    assert f"{MassFlowRate(1, 'g/h').to('kg/s')}" == "2.77778e-07 kg/s"


# ---------------------------------------------------------------------------
# Heat exchangers: the `* 1000` compensations for the kJ base
# ---------------------------------------------------------------------------

def test_latent_duty_is_not_multiplied_by_a_thousand():
    """H1: 2 kg/s condensing at 2 135 500 J/kg is 4.271 MW, not 4.271 GW."""
    hot_in = MaterialStream("steam", component=Water(), phase="vapor",
                            temperature=Temperature(120, "C"),
                            pressure=Pressure(2, "bar"),
                            mass_flow=MassFlowRate(2, "kg/s"))
    cold_in = MaterialStream("cw", component=Water(),
                             temperature=Temperature(25, "C"),
                             mass_flow=MassFlowRate(40, "kg/s"))
    hx = ShellAndTubeHX(hot_in=hot_in, cold_in=cold_in, latent_heat=2_135_500)
    hot = hx._stream_props(hot_in)
    cold = hx._stream_props(cold_in)

    q_watts, _, tc_out = hx._calculate_heat_duty(hot, cold)
    assert q_watts == pytest.approx(4_271_000)
    # And the cooling water rises by Q / (m cp), about 25 K, not 25 000 K.
    assert tc_out - cold["t_k"] == pytest.approx(4_271_000 / (40 * cold["cp"]))
    assert 20 < tc_out - cold["t_k"] < 30


def test_double_pipe_outlet_temperature_and_area():
    """H10: kerosene 2 kg/s 120 to 80 C against water 1.5 kg/s from 20 C.

    By hand: Q = 2 x 2470 x 40 = 197.6 kW, Tc_out = 20 + 197600 / (1.5 x 4180)
    = 51.515 C, LMTD = (68.485 - 60) / ln(68.485 / 60) = 64.15 K and the area
    at U = 350 is 8.80 m2. The library used to give Tc_out = 20.03 C.
    """
    hot_in = MaterialStream("kerosene_in", component=OrganicLiquid(),
                            temperature=Temperature(120, "C"),
                            mass_flow=MassFlowRate(2, "kg/s"),
                            specific_heat=SpecificHeat(2470, "J/kgK"))
    hot_out = MaterialStream("kerosene_out", component=OrganicLiquid(),
                             temperature=Temperature(80, "C"))
    cold_in = MaterialStream("water_in", component=Water(),
                             temperature=Temperature(20, "C"),
                             mass_flow=MassFlowRate(1.5, "kg/s"),
                             specific_heat=SpecificHeat(4180, "J/kgK"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in,
               hx_type="double_pipe", mode="design", U=350.0)
    data = _quiet(engine.run).data

    q = data["Q"]
    assert float(getattr(q, "value", q)) == pytest.approx(197_600, rel=1e-6)
    tc_out = 20 + 197_600 / (1.5 * 4180)
    lmtd = ((120 - tc_out) - (80 - 20)) / math.log((120 - tc_out) / (80 - 20))
    assert float(getattr(data["LMTD"], "value", data["LMTD"])) == pytest.approx(lmtd, rel=1e-6)
    area = float(getattr(data["Area"], "value", data["Area"]))
    assert area == pytest.approx(197_600 / (350 * lmtd), rel=1e-6)


def test_stream_pressure_reaches_the_exchanger_in_bar():
    stream = MaterialStream("s", component=Water(), temperature=Temperature(25, "C"),
                            pressure=Pressure(250, "kPa"),
                            mass_flow=MassFlowRate(1, "kg/s"))
    hx = ShellAndTubeHX(hot_in=stream, cold_in=stream)
    assert hx._stream_props(stream)["p_bar"] == pytest.approx(2.5)


def test_heat_duty_spec_accepts_a_heat_flow():
    stream = MaterialStream("s", component=Water(), temperature=Temperature(25, "C"),
                            mass_flow=MassFlowRate(1, "kg/s"))
    hx = ShellAndTubeHX(hot_in=stream, cold_in=stream, Q=HeatFlow(500, "kW"))
    props = hx._stream_props(stream)
    assert hx.heat_duty(props, props) == pytest.approx(500_000)


# ---------------------------------------------------------------------------
# Call sites that read `.to(unit).value` expecting the number in that unit
# ---------------------------------------------------------------------------

def test_pipeline_summary_reports_the_units_its_keys_name():
    """`.to("kPa").value` is in Pa and `.to("in").value` in m, like `.to()` on
    every unit class, so the kPa, kW and inch keys were in Pa, W and m."""
    results = PipelineResults({
        "summary": {"total_pressure_drop_Pa": 12_345.0, "pump_shaft_power_kW": 2.5},
        "components": [{"diameter": Diameter(4, "in")}],
    })
    row = _quiet(results.summary)[0]
    assert row["total_pressure_drop_kPa"] == pytest.approx(12.345)
    assert row["total_power_required_kW"] == pytest.approx(2.5)
    assert row["pipe_diameter_in"] == pytest.approx(4)
