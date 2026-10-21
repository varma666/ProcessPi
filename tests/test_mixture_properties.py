"""Mixture: a composition stream gets physical properties.

A stream made from a composition (a column's distillate or bottoms) had
`component=None` and no specific heat, so every exchanger refused it ("has no
specific heat"). `Mixture` combines the pure-component properties at the
mixture's own temperature, pressure and phase and has the Component interface,
so it can be the stream's component.

Mixing rules checked here (ideal solution, ideal gas):
    M      = sum x_i M_i
    liquid 1/rho = sum w_i / rho_i        gas rho = P M / (R T)
    cp     = sum w_i cp_i                 dHv = sum w_i dHv_i
    liquid ln mu = sum x_i ln mu_i
    bubble P = sum x_i Psat_i             dew 1/P = sum y_i / Psat_i

Reference values: 40/60 mol% benzene/toluene, M = 0.4 * 78.114 + 0.6 * 92.138
= 86.5284 g/mol; as a vapour at 130 C and 1 atm,
rho = 101325 * 0.0865284 / (8.314462618 * 403.15) = 2.6156 kg/m3.
"""

import contextlib
import copy
import io
import math

import pytest

from processpi.components import Benzene, Component, Methane, Mixture, Toluene, Water
from processpi.equipment.distillation.vle import IdealVLE
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.streams import MaterialStream
from processpi.units import MassFlowRate, Pressure, Temperature

ATM = Pressure(101325, "Pa")


def _value(x):
    return float(getattr(x, "value", x))


def _btx(t_c, phase=None, x_benzene=0.4, pressure=ATM):
    return Mixture(
        {Benzene: x_benzene, Toluene: 1.0 - x_benzene},
        temperature=Temperature(t_c + 273.15, "K"),
        pressure=pressure,
        phase=phase,
    )


def _pure(cls, t_c, phase="liquid", pressure=ATM):
    return cls(temperature=Temperature(t_c + 273.15, "K"), pressure=pressure, phase=phase)


# ----------------------------------------------------------------------------
# Composition
# ----------------------------------------------------------------------------

def test_mean_molecular_weight_and_mass_fractions():
    mix = _btx(25)
    assert mix.molecular_weight == pytest.approx(0.4 * 78.114 + 0.6 * 92.138, rel=1e-12)
    w = mix.mass_fractions()
    assert w["Benzene"] == pytest.approx(0.4 * 78.114 / 86.5284, rel=1e-12)
    assert sum(w.values()) == pytest.approx(1.0, rel=1e-12)


def test_mass_basis_is_converted_to_mole_fractions():
    mix = Mixture({Benzene: 0.4, Toluene: 0.6}, basis="mass")
    n_b, n_t = 0.4 / 78.114, 0.6 / 92.138
    assert mix.mole_fractions()["Benzene"] == pytest.approx(n_b / (n_b + n_t), rel=1e-12)
    assert mix.mass_fractions()["Benzene"] == pytest.approx(0.4, rel=1e-12)


def test_fractions_are_normalised_and_instances_accepted():
    mix = Mixture({Benzene(): 2.0, Toluene(): 3.0})
    assert mix.mole_fractions() == pytest.approx({"Benzene": 0.4, "Toluene": 0.6})
    assert mix.component_names == ["Benzene", "Toluene"]


def test_from_names_resolves_a_stream_composition():
    mix = Mixture.from_names({"benzene": 0.4, "TOLUENE": 0.6}, [Benzene(), Toluene], phase="liquid")
    assert mix.mole_fractions() == pytest.approx({"Benzene": 0.4, "Toluene": 0.6})
    with pytest.raises(KeyError, match="Xylene"):
        Mixture.from_names({"Benzene": 0.5, "Xylene": 0.5}, [Benzene, Toluene])


@pytest.mark.parametrize(
    "composition, kwargs, error",
    [
        ({}, {}, ValueError),
        ({Benzene: 0.0}, {}, ValueError),
        ({Benzene: -0.1, Toluene: 1.1}, {}, ValueError),
        ({Benzene: 0.5, Toluene: 0.5}, {"basis": "volume"}, ValueError),
        ({"Benzene": 1.0}, {}, TypeError),
    ],
)
def test_bad_compositions_are_refused(composition, kwargs, error):
    with pytest.raises(error):
        Mixture(composition, **kwargs)


def test_a_mixture_is_a_component():
    assert isinstance(_btx(25), Component)


# ----------------------------------------------------------------------------
# Liquid properties
# ----------------------------------------------------------------------------

def test_liquid_properties_follow_the_ideal_mixing_rules():
    mix = _btx(80, phase="liquid")
    b, t = _pure(Benzene, 80), _pure(Toluene, 80)
    w, x = mix.mass_fractions(), mix.mole_fractions()

    rho = 1.0 / (w["Benzene"] / _value(b.density()) + w["Toluene"] / _value(t.density()))
    cp = w["Benzene"] * _value(b.specific_heat()) + w["Toluene"] * _value(t.specific_heat())
    dhv = w["Benzene"] * _value(b.enthalpy()) + w["Toluene"] * _value(t.enthalpy())
    mu = math.exp(x["Benzene"] * math.log(_value(b.viscosity())) + x["Toluene"] * math.log(_value(t.viscosity())))

    assert _value(mix.density()) == pytest.approx(rho, rel=1e-6)
    assert _value(mix.specific_heat()) == pytest.approx(cp, rel=1e-6)
    assert _value(mix.latent_heat()) == pytest.approx(dhv, rel=1e-6)
    assert _value(mix.enthalpy()) == pytest.approx(dhv, rel=1e-6)
    assert _value(mix.viscosity()) == pytest.approx(mu, rel=1e-6)
    # Liquid density at 80 C lies between the pure values (benzene 815, toluene 811 kg/m3).
    lo, hi = sorted([_value(b.density()), _value(t.density())])
    assert lo <= _value(mix.density()) <= hi


def test_a_single_component_mixture_is_the_pure_component():
    mix = Mixture({Benzene: 1.0}, temperature=Temperature(333.15, "K"), phase="liquid")
    pure = _pure(Benzene, 60)
    assert mix.molecular_weight == pytest.approx(78.114)
    for prop in ("density", "specific_heat", "viscosity", "thermal_conductivity", "enthalpy"):
        assert _value(getattr(mix, prop)()) == pytest.approx(_value(getattr(pure, prop)()), rel=1e-6), prop


def test_a_component_above_its_critical_temperature_has_no_liquid_to_mix():
    mix = Mixture({Methane: 0.1, Benzene: 0.9}, temperature=Temperature(300, "K"), phase="liquid")
    with pytest.raises(ValueError, match="Methane.*critical temperature"):
        mix.density()


# ----------------------------------------------------------------------------
# Phase from Raoult's law
# ----------------------------------------------------------------------------

def test_bubble_and_dew_pressures_agree_with_the_column_vle():
    vle = IdealVLE([Benzene, Toluene])
    z = {"Benzene": 0.4, "Toluene": 0.6}
    t_bubble = vle.bubble_temperature(z, 101325.0)
    t_dew = vle.dew_temperature(z, 101325.0)
    at_bubble = Mixture({Benzene: 0.4, Toluene: 0.6}, temperature=Temperature(t_bubble, "K"))
    at_dew = Mixture({Benzene: 0.4, Toluene: 0.6}, temperature=Temperature(t_dew, "K"))
    assert _value(at_bubble.bubble_pressure()) == pytest.approx(101325.0, rel=1e-6)
    assert _value(at_dew.dew_pressure()) == pytest.approx(101325.0, rel=1e-6)
    assert _value(at_bubble.vapor_pressure()) == pytest.approx(101325.0, rel=1e-6)


def test_phase_is_liquid_two_phase_or_gas_across_the_boiling_range():
    vle = IdealVLE([Benzene, Toluene])
    z = {"Benzene": 0.4, "Toluene": 0.6}
    t_bubble = vle.bubble_temperature(z, 101325.0) - 273.15  # about 95 C
    t_dew = vle.dew_temperature(z, 101325.0) - 273.15        # about 102 C
    assert _btx(t_bubble - 5).phase() == "liquid"
    assert _btx(0.5 * (t_bubble + t_dew)).phase() == "two-phase"
    assert _btx(t_dew + 5).phase() == "gas"


def test_two_phase_has_no_single_phase_property():
    vle = IdealVLE([Benzene, Toluene])
    z = {"Benzene": 0.4, "Toluene": 0.6}
    t_mid = 0.5 * (vle.bubble_temperature(z, 101325.0) + vle.dew_temperature(z, 101325.0))
    mix = Mixture({Benzene: 0.4, Toluene: 0.6}, temperature=Temperature(t_mid, "K"))
    with pytest.raises(ValueError, match="two-phase"):
        mix.density()


def test_a_given_phase_overrides_raoults_law():
    # 130 C at 1 atm is above the dew point, but a liquid held there by a
    # pressure the caller does not state is still a liquid.
    assert _btx(130).phase() == "gas"
    assert _btx(130, phase="liquid").phase() == "liquid"
    assert _btx(60, phase="vapor").phase() == "gas"


# ----------------------------------------------------------------------------
# Gas properties
# ----------------------------------------------------------------------------

def test_gas_density_is_the_ideal_gas_value():
    mix = _btx(130)
    assert mix.phase() == "gas"
    assert _value(mix.density()) == pytest.approx(
        101325 * 0.0865284 / (8.314462618 * 403.15), rel=1e-6
    )
    assert _value(mix.density()) == pytest.approx(2.6156, rel=1e-4)


def test_gas_properties_use_each_component_in_the_gas_phase():
    mix = _btx(130)
    b, t = _pure(Benzene, 130, "gas"), _pure(Toluene, 130, "gas")
    w, x = mix.mass_fractions(), mix.mole_fractions()
    assert _value(mix.specific_heat()) == pytest.approx(
        w["Benzene"] * _value(b.specific_heat()) + w["Toluene"] * _value(t.specific_heat()), rel=1e-6
    )
    assert _value(mix.viscosity()) == pytest.approx(
        x["Benzene"] * _value(b.viscosity()) + x["Toluene"] * _value(t.viscosity()), rel=1e-6
    )


# ----------------------------------------------------------------------------
# Heat exchanger interface
# ----------------------------------------------------------------------------

def test_hx_keys_are_those_of_the_main_component_by_mass():
    wet = Mixture({Water: 0.9, Benzene: 0.1}, temperature=Temperature(300, "K"), phase="liquid")
    assert wet.hx_data() == _pure(Water, 300 - 273.15).hx_data()
    assert wet.httype() == "water"
    # 50/50 by mole is 46/54 by mass, so toluene leads.
    btx = _btx(25, phase="liquid", x_benzene=0.5)
    assert btx.hx_data() == _pure(Toluene, 25).hx_data()


def test_a_copy_at_another_temperature_has_its_own_properties():
    # The exchangers copy the stream's component and set the temperature.
    mix = _btx(25, phase="liquid")
    rho_25 = _value(mix.density())
    hot = copy.copy(mix)
    hot.temperature = Temperature(353.15, "K")
    assert _value(hot.density()) == pytest.approx(_value(_btx(80, phase="liquid").density()), rel=1e-12)
    assert _value(mix.density()) == rho_25


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def test_an_exchanger_designs_with_a_mixture_stream():
    distillate = Mixture({Benzene: 0.97, Toluene: 0.03})

    def stream(name, component, t_c=None, kg_h=None, **kwargs):
        if t_c is not None:
            kwargs["temperature"] = Temperature(t_c, "C")
        if kg_h is not None:
            kwargs["mass_flow"] = MassFlowRate(kg_h, "kg/h")
        return MaterialStream(name, component=component, **kwargs)

    engine = HeatExchangerEngine().fit(
        mode="design",
        hot_in=stream("D", distillate, 80, 7600, phase="liquid"),
        hot_out=stream("D_cooled", distillate, 35, phase="liquid"),
        cold_in=stream("cw_in", Water(), 25, 30000),
        cold_out=stream("cw_out", Water()),
        shell_dp=Pressure(1, "bar"),
        tube_dp=Pressure(1, "bar"),
    )
    data = _quiet(engine.run).data
    hot = data["property_basis"]["hot"]

    # Properties at the hot side's mean temperature, (80 + 35) / 2 = 57.5 C.
    at_mean = Mixture(
        {Benzene: 0.97, Toluene: 0.03}, temperature=Temperature(330.65, "K"), phase="liquid"
    )
    assert hot["temperature_K"] == pytest.approx(330.65, rel=1e-12)
    assert hot["density_kg_m3"] == pytest.approx(_value(at_mean.density()), rel=1e-6)
    assert hot["cp_J_kgK"] == pytest.approx(_value(at_mean.specific_heat()), rel=1e-6)
    assert hot["viscosity_Pa_s"] == pytest.approx(_value(at_mean.viscosity()), rel=1e-6)
    assert hot["k_W_mK"] == pytest.approx(_value(at_mean.thermal_conductivity()), rel=1e-6)
    # Q = m cp dT on the hot side.
    assert _value(data["Q"].to("W")) == pytest.approx(7600 / 3600 * hot["cp_J_kgK"] * 45.0, rel=1e-9)
