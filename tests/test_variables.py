import pytest

from processpi.units.length import Length
from processpi.units.velocity import Velocity
from processpi.units.density import Density
from processpi.units.kinetic_viscosity import KineticViscousity
from processpi.units.temperature import Temperature
from processpi.units.flowrate import Flowrate
from processpi.units.volumetric_flowrate import VolumetricFlowrate
from processpi.units.mass_flowrate import MassFlowrate
from processpi.units.diameter import Diameter
from processpi.units.pressure import Pressure
from processpi.units.volume import Volume
from processpi.units.area import Area
from processpi.units.mass import Mass
from processpi.units.specific_heat import SpecificHeat
from processpi.units.thermal_conductivity import ThermalConductivity
from processpi.units.heat_transfer_coefficient import HeatTransferCoefficient
from processpi.units.thermal_resistance import ThermalResistance
from processpi.units.heat_flux import HeatFlux

def test_length():
    l = Length(10, "cm")
    assert round(l.value, 2) == 0.10
    assert l.units == "m"

def test_velocity():
    v = Velocity(36, "kmph")
    assert round(v.value, 2) == 10.0

def test_density():
    d = Density(1, "g/cm3")
    assert round(d.value, 0) == 1000

def test_kinetic_viscosity():
    kv = KineticViscousity(1, "cst")
    assert round(kv.value, 6) == 1e-6

def test_temperature():
    t = Temperature(100, "C")
    assert round(t.value, 2) == 373.15

def test_flowrate():
    f = Flowrate(10, "lpm")
    assert round(f.value, 4) == 1.6667e-4

def test_volumetric_flowrate():
    vf = VolumetricFlowrate(60, "lpm")
    assert round(vf.value, 4) == 0.001

def test_mass_flowrate():
    mf = MassFlowrate(1000, "gph")
    assert round(mf.value, 5) == 0.00027778

def test_diameter():
    d = Diameter(2, "in")
    assert round(d.value, 4) == 0.0508

def test_pressure():
    p = Pressure(1, "atm")
    assert round(p.value, 2) == 101325

def test_volume():
    v = Volume(1, "l")
    assert round(v.value, 3) == 0.001

def test_area():
    a = Area(100, "cm2")
    assert round(a.value, 4) == 0.01

def test_mass():
    m = Mass(1, "kg")
    assert m.value == 1

def test_specific_heat():
    sh = SpecificHeat(1, "kcal/kg.C")
    assert round(sh.value, 3) == 4184

def test_thermal_conductivity():
    tc = ThermalConductivity(1, "W/m.K")
    assert tc.value == 1

def test_heat_transfer_coefficient():
    htc = HeatTransferCoefficient(100, "kcal/hr.m2.C")
    assert round(htc.value, 2) == 116.28

def test_thermal_resistance():
    tr = ThermalResistance(1, "K/W")
    assert tr.value == 1

def test_heat_flux():
    hf = HeatFlux(1000, "kcal/hr.m2")
    assert round(hf.value, 2) == 1.163