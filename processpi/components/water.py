# processpi/components/water.py
from .base import Component
from processpi.units import *
class Water(Component):
    name = "Water"
    formula = "H2O"
    molecular_weight = 18.015

    def density(self, temperature:Temperature):
        # Simplified polynomial valid from 0 to 100 °C
        den = 1000 - 0.07 * (temperature.value - 4) ** 2
        return Density(den, "kg/m3")

    def specific_heat(self, temperature: Temperature):
        # Rough approximation in kJ/kg.K
        return SpecificHeat(4.18, "kJ/kgK")
