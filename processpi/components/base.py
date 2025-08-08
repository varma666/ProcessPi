from abc import ABC, abstractmethod
from processpi.units import *
from math import exp, log
class Component(ABC):
    """
    Base class for a chemical component.
    Each subclass must define its own physical and chemical properties.
    """

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

    @abstractmethod
    def density(self, temperature: float) -> float:
        """Return density in kg/m3 as a function of temperature in °C"""
        pass

    
    def density(self, temperature:Temperature):
        T = temperature.value
        # Using a polynomial fit for density as a function of temperature
        den = self._density_constants[0] / (self._density_constants[1] ** (1 + (1 - (T/self._density_constants[2])**self._density_constants[3])))
        den = den * self.molecular_weight
        return Density(den, "kg/m3")
    
    def specific_heat(self, temperature: Temperature):
        """Return specific heat in kJ/kg.K as a function of temperature in °C"""
        Tr = temperature.value / self._critical_temperature.value
        # Using a polynomial fit for specific heat as a function of reduced temperature
        
        T = temperature.value
        cp = (self._specific_heat_constants[0] +
              self._specific_heat_constants[1] * T +
              self._specific_heat_constants[2] * T**2 +
              self._specific_heat_constants[3] * T**3 +
              self._specific_heat_constants[4] * T**4)
        # Convert to kJ/kg.K
        #cp /= 1000.0
        cp = cp * self.molecular_weight
        return SpecificHeat(cp, "J/kgK")
    def viscosity(self, temperature: Temperature):
        T = temperature.value
        po = self._viscosity_constants[0] + (self._viscosity_constants[1] / T) + (self._viscosity_constants[2] * log(T)) + (self._viscosity_constants[3] * (T**self._viscosity_constants[4]))
        vis = exp(po)
        return Viscosity(vis, "Pa·s")
    def thermal_conductivity(self, temperature: Temperature):
        T = temperature.value
        # Using a polynomial fit for thermal conductivity as a function of temperature
        k = (self._thermal_conductivity_constants[0] +
             self._thermal_conductivity_constants[1] * T +
             self._thermal_conductivity_constants[2] * T**2 +
             self._thermal_conductivity_constants[3] * T**3 +
             self._thermal_conductivity_constants[4] * T**4)
        
        return ThermalConductivity(k, "W/mK")
    def vapor_pressure(self, temperature: Temperature):
        T = temperature.value
        # Using a polynomial fit for vapor pressure as a function of temperature
        po = (self._vapor_pressure_constants[0] +   (self._vapor_pressure_constants[1] / T) + 
              (self._vapor_pressure_constants[2] * log(T)) + 
              (self._vapor_pressure_constants[3] * (T**self._vapor_pressure_constants[4])))
        vp = exp(po)
        return Pressure(vp, "Pa")
    def enthalpy(self, temperature: Temperature):
        # Using a polynomial fit for enthalpy as a function of temperature
        T = temperature.value
        Tr = T / self._critical_temperature.value
        # Using a polynomial fit for enthalpy as a function of reduced temperature
        tou = 1 - Tr
        dH =  self._enthalpy_constants[0] * (tou**((self._enthalpy_constants[1]) + (self._enthalpy_constants[2] * tou) + (self._enthalpy_constants[3] * (tou**2)) + (self._enthalpy_constants[4] * (tou**3))))
       
        # Convert to kJ/kg
        dH = dH * self.molecular_weight
        return HeatOfVaporization(dH, "J/kg")