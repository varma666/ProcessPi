from abc import ABC, abstractmethod
from processpi.units import *
from math import exp, log

class Component(ABC):
    """
    Abstract base class for a chemical component.
    """

    def __init__(self, temperature: Temperature = None, pressure: Pressure = None,
                 density: Density = None, specific_heat: SpecificHeat = None,
                 viscosity: Viscosity = None, thermal_conductivity: ThermalConductivity = None,
                 vapor_pressure: Pressure = None, enthalpy: HeatOfVaporization = None):
        """
        Initializes the component with optional physical properties.
        Any property provided directly will be used instead of the calculated value.
        """
        self.temperature = temperature or Temperature(35, "C")
        self.pressure = pressure or Pressure(101325, "Pa")

        # Private attributes to store directly provided values
        self._density = density
        self._specific_heat = specific_heat
        self._viscosity = viscosity
        self._thermal_conductivity = thermal_conductivity
        self._vapor_pressure = vapor_pressure
        self._enthalpy = enthalpy

    @property
    @abstractmethod
    def name(self):
        """Abstract property for the component's name."""
        pass

    @property
    @abstractmethod
    def formula(self):
        """Abstract property for the component's chemical formula."""
        pass

    @property
    @abstractmethod
    def molecular_weight(self):
        """Abstract property for the component's molecular weight."""
        pass

    def _get_temperature(self, temperature: Temperature):
        """Helper method to get the temperature for calculations."""
        return temperature or self.temperature

    # --- Property Getters (Prioritize pre-set values) ---

    @property
    def density(self) -> Density:
        """Returns the pre-set density or calculates it if not set."""
        if self._density is not None:
            return self._density
        T = self.temperature.value
        a, b, Tc, n = self._density_constants
        den = a / (b ** (1 + (1 - (T / Tc)**n)))
        den = den * self.molecular_weight
        return Density(den, "kg/m3")

    @property
    def specific_heat(self) -> SpecificHeat:
        """Returns the pre-set specific heat or calculates it if not set."""
        if self._specific_heat is not None:
            return self._specific_heat
        T = self.temperature.value
        cp = (self._specific_heat_constants[0] + self._specific_heat_constants[1] * T +
              self._specific_heat_constants[2] * T**2 + self._specific_heat_constants[3] * T**3 +
              self._specific_heat_constants[4] * T**4)
        cp = cp * self.molecular_weight
        return SpecificHeat(cp, "J/kgK")

    @property
    def viscosity(self) -> Viscosity:
        """Returns the pre-set viscosity or calculates it if not set."""
        if self._viscosity is not None:
            return self._viscosity
        T = self.temperature.value
        po = (self._viscosity_constants[0] + (self._viscosity_constants[1] / T) + 
              (self._viscosity_constants[2] * log(T)) + 
              (self._viscosity_constants[3] * (T**self._viscosity_constants[4])))
        vis = exp(po)
        return Viscosity(vis, "Pa·s")

    @property
    def thermal_conductivity(self) -> ThermalConductivity:
        """Returns the pre-set thermal conductivity or calculates it if not set."""
        if self._thermal_conductivity is not None:
            return self._thermal_conductivity
        T = self.temperature.value
        k = (self._thermal_conductivity_constants[0] + self._thermal_conductivity_constants[1] * T +
             self._thermal_conductivity_constants[2] * T**2 + self._thermal_conductivity_constants[3] * T**3 +
             self._thermal_conductivity_constants[4] * T**4)
        return ThermalConductivity(k, "W/mK")

    @property
    def vapor_pressure(self) -> Pressure:
        """Returns the pre-set vapor pressure or calculates it if not set."""
        if self._vapor_pressure is not None:
            return self._vapor_pressure
        T = self.temperature.value
        po = (self._vapor_pressure_constants[0] + (self._vapor_pressure_constants[1] / T) +
              (self._vapor_pressure_constants[2] * log(T)) +
              (self._vapor_pressure_constants[3] * (T**self._vapor_pressure_constants[4])))
        vp = exp(po)
        return Pressure(vp, "Pa")

    @property
    def enthalpy(self) -> HeatOfVaporization:
        """Returns the pre-set enthalpy or calculates it if not set."""
        if self._enthalpy is not None:
            return self._enthalpy
        T = self.temperature.value
        Tr = T / self._critical_temperature.value
        tou = 1 - Tr
        dH = self._enthalpy_constants[0] * (tou**((self._enthalpy_constants[1]) +
                                                 (self._enthalpy_constants[2] * tou) +
                                                 (self._enthalpy_constants[3] * (tou**2)) +
                                                 (self._enthalpy_constants[4] * (tou**3))))
        dH = dH * self.molecular_weight
        return HeatOfVaporization(dH, "J/kg")
