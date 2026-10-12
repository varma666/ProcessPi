"""
Unit classes convert to their SI base value.

This file imported classes and modules that no longer exist
(`KineticViscousity`, `Flowrate`, `VolumetricFlowrate`, `MassFlowrate`,
`processpi.units.kinetic_viscosity`, `processpi.units.flowrate`) and unit
spellings the classes do not accept ("kmph", "lpm", "gph", "l", "kcal/kg.C",
"kcal/hr.m2.C", "kcal/hr.m2"), so it failed to collect. The same conversions
are checked with the current classes and spellings; where a spelling has no
current equivalent (kcal/h based heat transfer units), the BTU form is used.
"""

import pytest

from processpi.units import (
    Area,
    Density,
    Diameter,
    HeatFlux,
    HeatTransferCoefficient,
    Length,
    Mass,
    MassFlowRate,
    Pressure,
    SpecificHeat,
    Temperature,
    ThermalConductivity,
    ThermalResistance,
    Velocity,
    Viscosity,
    Volume,
    VolumetricFlowRate,
)


def test_length():
    l = Length(10, "cm")
    assert l.value == pytest.approx(0.10)
    assert l.units == "m"


def test_velocity():
    assert Velocity(36, "km/h").value == pytest.approx(10.0)


def test_density():
    assert Density(1, "g/cm3").value == pytest.approx(1000)


def test_kinematic_viscosity():
    assert Viscosity(1, "cSt").value == pytest.approx(1e-6)


def test_temperature():
    assert Temperature(100, "C").value == pytest.approx(373.15)


def test_flowrate():
    assert VolumetricFlowRate(10, "L/min").value == pytest.approx(10e-3 / 60)


def test_volumetric_flowrate():
    assert VolumetricFlowRate(60, "L/min").value == pytest.approx(0.001)


def test_mass_flowrate():
    assert MassFlowRate(1000, "g/h").value == pytest.approx(1.0 / 3600)


def test_diameter():
    assert Diameter(2, "in").value == pytest.approx(0.0508)


def test_pressure():
    assert Pressure(1, "atm").value == pytest.approx(101325)


def test_volume():
    assert Volume(1, "L").value == pytest.approx(0.001)


def test_area():
    assert Area(100, "cm2").value == pytest.approx(0.01)


def test_mass():
    assert Mass(1, "kg").value == 1


def test_specific_heat():
    # International Table calorie: 1 kcal/kg.K = 4186.8 J/kg.K.
    assert SpecificHeat(1, "kcal/kgK").value == pytest.approx(4186.8)


def test_thermal_conductivity():
    assert ThermalConductivity(1, "W/mK").value == 1


def test_heat_transfer_coefficient():
    # 1 BTU/(h ft2 F) = 5.678263 W/(m2 K).
    assert HeatTransferCoefficient(100, "BTU/hft2F").value == pytest.approx(567.8263)


def test_thermal_resistance():
    assert ThermalResistance(1, "K/W").value == 1


def test_heat_flux():
    # 1 BTU/(h ft2) = 3.1546 W/m2.
    assert HeatFlux(1000, "BTU/hft2").value == pytest.approx(3154.6)
