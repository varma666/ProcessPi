"""Stream and exchanger properties belong to the stream's own state.

A MaterialStream took its density and specific heat from the component at the
component's default 25 C and 1 atm, whatever temperature the stream was given,
and the heat exchangers read viscosity and conductivity the same way, so every
film coefficient, velocity and pressure drop was computed at 25 C. An outlet
stream built without a temperature also carried that 25 C into the duty, the
double-pipe outlet and the rating targets.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.double_pipe import DoublePipeHX
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


def _value(x):
    return float(getattr(x, "value", x))


def _stream(name, component, t_c=None, kg_h=None, **kwargs):
    if t_c is not None:
        kwargs["temperature"] = Temperature(t_c, "C")
    if kg_h is not None:
        kwargs["mass_flow"] = MassFlowRate(kg_h, "kg/h")
    return MaterialStream(name, component=component(), **kwargs)


# ----------------------------------------------------------------------------
# MaterialStream
# ----------------------------------------------------------------------------

def test_stream_density_and_cp_are_at_the_stream_temperature_and_pressure():
    stream = _stream("s", Benzene, 60, pressure=Pressure(3, "bar"))
    at_state = Benzene(temperature=Temperature(60, "C"), pressure=Pressure(3, "bar"))
    at_25c = Benzene()
    assert _value(stream.density) == pytest.approx(_value(at_state.density()), rel=1e-12)
    assert _value(stream.specific_heat) == pytest.approx(_value(at_state.specific_heat()), rel=1e-12)
    # Liquid benzene is lighter at 60 C than at 25 C; it used to report the 25 C value.
    assert _value(stream.density) < _value(at_25c.density()) - 30.0


def test_the_callers_component_is_not_changed():
    benzene = Benzene()
    stream = MaterialStream("s", component=benzene, temperature=Temperature(60, "C"))
    assert stream.component is not benzene
    assert _value(benzene.temperature.to("K")) == pytest.approx(298.15)
    assert _value(stream.component.temperature.to("K")) == pytest.approx(333.15)


def test_a_stated_phase_overrides_the_vapour_pressure_test():
    # Benzene boils at about 80 C at 1 atm, so at 90 C and the default 1 atm
    # the component says vapour; a stream stated as liquid is liquid.
    vapour = _stream("v", Benzene, 90)
    liquid = _stream("l", Benzene, 90, phase="liquid")
    assert vapour.component.phase() == "gas"
    assert liquid.component.phase() == "liquid"
    assert _value(vapour.density) < 5.0
    assert _value(liquid.density) > 700.0
    assert liquid.component.hx_data()["phase"] == "liquid"
    assert vapour.component.hx_data()["phase"] == "vapor"


def test_a_stream_without_a_temperature_still_reads_as_unspecified():
    stream = _stream("out", Water)
    assert stream.temperature is stream.component.temperature
    specified = _stream("out", Water, 40)
    assert specified.temperature is not specified.component.temperature


def test_given_density_and_cp_are_kept():
    from processpi.units import Density, SpecificHeat
    stream = MaterialStream("s", component=Benzene(), temperature=Temperature(60, "C"),
                            density=Density(850, "kg/m3"),
                            specific_heat=SpecificHeat(1900, "J/kgK"))
    assert _value(stream.density) == pytest.approx(850.0)
    assert stream.given_density is not None


# ----------------------------------------------------------------------------
# Shell-and-tube design and rating
# ----------------------------------------------------------------------------

def _benzene_cooler_engine(**specs):
    """docs/examples benzene cooler: benzene 21 000 kg/h 90 to 30 C, water 60 500 kg/h from 15 C."""
    return HeatExchangerEngine(method="kern").fit(
        hot_in=_stream("hot_in", Benzene, 90, 21000),
        hot_out=_stream("hot_out", Benzene, 30),
        cold_in=_stream("cold_in", Water, 15, 60500),
        cold_out=specs.pop("cold_out", _stream("cold_out", Water)),
        U=HeatTransferCoefficient(575, "W/m2K"),
        shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
        **specs,
    )


def test_design_properties_are_at_each_sides_mean_temperature():
    data = _quiet(_benzene_cooler_engine(mode="design").run).data
    hot = data["property_basis"]["hot"]
    cold = data["property_basis"]["cold"]

    # Hot side: both ends given, mean (90 + 30) / 2 = 60 C.
    assert hot["temperature_K"] == pytest.approx(333.15, rel=1e-12)
    benzene_60c = Benzene(temperature=Temperature(60, "C"), phase="liquid")
    assert hot["density_kg_m3"] == pytest.approx(_value(benzene_60c.density()), rel=1e-12)
    assert hot["viscosity_Pa_s"] == pytest.approx(_value(benzene_60c.viscosity()), rel=1e-12)
    assert hot["cp_J_kgK"] == pytest.approx(_value(benzene_60c.specific_heat()), rel=1e-12)
    assert hot["k_W_mK"] == pytest.approx(_value(benzene_60c.thermal_conductivity()), rel=1e-12)

    # Cold side: the outlet follows from the balance, and the balance is
    # closed on the cp at the mean of that outlet and the inlet.
    q_w = _value(data["Q"].to("W"))
    assert q_w == pytest.approx(21000 / 3600 * hot["cp_J_kgK"] * 60.0, rel=1e-12)
    tc_out = 2.0 * cold["temperature_K"] - 288.15
    assert tc_out == pytest.approx(288.15 + q_w / (60500 / 3600 * cold["cp_J_kgK"]), abs=0.02)

    # The film coefficients no longer use 25 C: at 25 C benzene is about 25%
    # more viscous than at 60 C.
    assert _value(Benzene().viscosity()) > 1.2 * hot["viscosity_Pa_s"]


def test_rating_properties_are_at_the_mean_of_the_given_ends():
    data = _quiet(_benzene_cooler_engine(
        mode="rate", cold_out=_stream("cold_out", Water, 25),
        tube_od=0.01905, tube_id=0.016, tube_length=4.88, tube_count=200,
        tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18,
    ).run).data
    assert data["property_basis"]["hot"]["temperature_K"] == pytest.approx(333.15, rel=1e-12)
    assert data["property_basis"]["cold"]["temperature_K"] == pytest.approx(293.15, rel=1e-12)


def test_rating_needs_outlet_temperatures_that_were_given():
    engine = _benzene_cooler_engine(
        mode="rate", tube_od=0.01905, tube_id=0.016, tube_length=4.88, tube_count=200,
        tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18,
    )
    # cold_out has no temperature: it used to be rated as a 25 C target.
    with pytest.raises(ValueError, match="cold_out.temperature"):
        _quiet(engine.run)


# ----------------------------------------------------------------------------
# Outlets without a temperature
# ----------------------------------------------------------------------------

def test_duty_comes_from_the_specified_outlet_not_an_inherited_25c():
    """Only the cold outlet is given. The hot outlet carried 25 C, which the
    duty took as specified: 80 to 25 C instead of the cold side's 20 to 40 C."""
    hx = DoublePipeHX(hot_in=_stream("hi", Water, 80, 2000), hot_out=_stream("ho", Water),
                      cold_in=_stream("ci", Water, 20, 3000), cold_out=_stream("co", Water, 40))
    hot = hx._stream_props(hx.hot_in)
    cold = hx._stream_props(hx.cold_in)
    assert hx.heat_duty(hot, cold) == pytest.approx(3000 / 3600 * cold["cp"] * 20.0, rel=1e-12)


def test_double_pipe_cold_outlet_comes_from_the_balance():
    """Water 2000 kg/h 80 to 50 C heats water 3000 kg/h from 20 C, so the cold
    outlet is about 40 C. The unspecified cold outlet carried 25 C, which the
    design used as the outlet: LMTD (55 - 30) / ln(55/30) = 41.2 K instead of
    (40 - 30) / ln(40/30) = 34.8 K."""
    hx = DoublePipeHX(hot_in=_stream("hi", Water, 80, 2000), hot_out=_stream("ho", Water, 50),
                      cold_in=_stream("ci", Water, 20, 3000), cold_out=_stream("co", Water))
    data = _quiet(hx.design)
    q_w = _value(data["Q"].to("W"))
    cold_cp = data["property_basis"]["cold"]["cp_J_kgK"]
    tc_out = 293.15 + q_w / (3000 / 3600 * cold_cp)
    assert tc_out - 273.15 == pytest.approx(40.0, abs=0.2)
    dt1, dt2 = 353.15 - tc_out, 323.15 - 293.15
    assert _value(data["LMTD"]) == pytest.approx((dt1 - dt2) / math.log(dt1 / dt2), rel=1e-9)
