from abc import ABC, abstractmethod
from processpi.units import *
from math import exp, log

class Component(ABC):
    """
    Base class for a chemical component.
    Each subclass must define its own physical and chemical properties.
    """

    def __init__(self, temperature: Temperature = None, pressure: Pressure = None):
        self.temperature = temperature or Temperature(35, "C")
        self.pressure = pressure or Pressure(101325, "Pa")

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def formula(self):
        pass

    @property
    @abstractmethod
    def molecular_weight(self):
        pass

    # Generic density method (can be overridden in subclasses)
    def density(self, temperature: Temperature = None) -> Density:
        temperature = self._get_temperature(temperature)
        T = temperature.value
        den = self._density_constants[0] / (self._density_constants[1] ** (1 + (1 - (T/self._density_constants[2])**self._density_constants[3])))
        den = den * self.molecular_weight
        return Density(den, "kg/m3")

    def _get_temperature(self, temperature: Temperature):
        return temperature or self.temperature

    def specific_heat(self, temperature: Temperature = None):
        temperature = self._get_temperature(temperature)
        T = temperature.value
        cp = (self._specific_heat_constants[0] +
              self._specific_heat_constants[1] * T +
              self._specific_heat_constants[2] * T**2 +
              self._specific_heat_constants[3] * T**3 +
              self._specific_heat_constants[4] * T**4)
        cp = cp * self.molecular_weight
        return SpecificHeat(cp, "J/kgK")

    def viscosity(self, temperature: Temperature = None):
        temperature = self._get_temperature(temperature)
        T = temperature.value
        po = self._viscosity_constants[0] + (self._viscosity_constants[1] / T) + (self._viscosity_constants[2] * log(T)) + (self._viscosity_constants[3] * (T**self._viscosity_constants[4]))
        vis = exp(po)
        return Viscosity(vis, "Pa·s")

    def thermal_conductivity(self, temperature: Temperature = None):
        temperature = self._get_temperature(temperature)
        T = temperature.value
        k = (self._thermal_conductivity_constants[0] +
             self._thermal_conductivity_constants[1] * T +
             self._thermal_conductivity_constants[2] * T**2 +
             self._thermal_conductivity_constants[3] * T**3 +
             self._thermal_conductivity_constants[4] * T**4)
        return ThermalConductivity(k, "W/mK")

    def vapor_pressure(self, temperature: Temperature = None):
        temperature = self._get_temperature(temperature)
        T = temperature.value
        po = (self._vapor_pressure_constants[0] + (self._vapor_pressure_constants[1] / T) +
              (self._vapor_pressure_constants[2] * log(T)) +
              (self._vapor_pressure_constants[3] * (T**self._vapor_pressure_constants[4])))
        vp = exp(po)
        return Pressure(vp, "Pa")

    def enthalpy(self, temperature: Temperature = None):
        temperature = self._get_temperature(temperature)
        T = temperature.value
        Tr = T / self._critical_temperature.value
        tou = 1 - Tr
        dH =  self._enthalpy_constants[0] * (tou**((self._enthalpy_constants[1]) + (self._enthalpy_constants[2] * tou) + (self._enthalpy_constants[3] * (tou**2)) + (self._enthalpy_constants[4] * (tou**3))))
        dH = dH * self.molecular_weight
        return HeatOfVaporization(dH, "J/kg")
