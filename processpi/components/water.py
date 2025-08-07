# processpi/components/water.py
from .base import Component
from processpi.units import *
from math import *

class Water(Component):
    name = "Water"
    formula = "H2O"
    molecular_weight = 18.015
    _density_constants = [-13.851, 0.654, -0.00191, 0.000002]
    _specific_heat_constants = [276370,-2090.10,8.125,-0.014116,9.37e-6]
    _viscosity_constants = [-52.843, 3703.6, 5.866, -5.879e-29, 10] 
    _thermal_conductivity_constants = [-0.432, 0.0057255, -0.000008078,1.861E-09,0]
    _vapor_pressure_constants = [73.649, -7258.2, -7.3037, 4.1653E-06, 2] 
    _enthalpy_constants = [5.2053, 0.3199, -0.212, 0.25795, 0]  # Placeholder for enthalpy constants
    _critical_temperature = 647.096  # K

    def density(self, temperature:Temperature):
        Tr = temperature.value / self._critical_temperature
        # Using a polynomial fit for density as a function of reduced temperature
        tou = 1 - Tr
        den = 17.863 + (58.606 * (tou**0.35)) -  (95.396 * (tou**(2/3))) + (213.89 * tou) - (141.26 * (tou**(4/3)))
        den = den *  self.molecular_weight
        return Density(den, "kg/m3")

    def specific_heat(self, temperature: Temperature):
        Tr = temperature.value / self._critical_temperature
        # Using a polynomial fit for specific heat as a function of reduced temperature
        tou = 1 - Tr
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
        Tr = T / self._critical_temperature
        tou = 1 - Tr
        dH =  self._enthalpy_constants[0] * (tou**((self._enthalpy_constants[1]) + (self._enthalpy_constants[2] * tou) + (self._enthalpy_constants[3] * (tou**2)) + (self._enthalpy_constants[4] * (tou**3))))
       
        # Convert to kJ/kg
        dH = dH * self.molecular_weight
        return HeatOfVaporization(dH, "J/kg")
