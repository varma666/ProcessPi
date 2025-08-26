from abc import ABC, abstractmethod
from processpi.units import *
from math import exp, log

class Component(ABC):
    """
    Abstract base class for a chemical component.

    This class defines a standardized interface and common calculation methods
    for all chemical component subclasses. It provides methods to compute
    physical properties like density, specific heat, viscosity, thermal
    conductivity, vapor pressure, and enthalpy based on temperature and pressure.
    Each subclass must define its own physical and chemical properties as class
    attributes, such as name, molecular weight, and various correlation constants.
    """

    def __init__(self, temperature: Temperature = None, pressure: Pressure = None):
        """
        Initializes the component with optional temperature and pressure.

        Args:
            temperature (Temperature, optional): The operating temperature.
                                                 Defaults to 35 °C if not provided.
            pressure (Pressure, optional): The operating pressure.
                                           Defaults to 101325 Pa if not provided.
        """
        self.temperature = temperature or Temperature(35, "C")
        self.pressure = pressure or Pressure(101325, "Pa")

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

    def density(self, temperature: Temperature = None) -> Density:
        """
        Calculates the density of the component based on the correlation constants.

        The method uses a temperature-dependent correlation to compute the density.
        Subclasses must provide `_density_constants` as a class attribute.

        Args:
            temperature (Temperature, optional): The temperature for the calculation.
                                                 Defaults to the object's temperature.

        Returns:
            Density: The calculated density in kg/m³.
        """
        temperature = self._get_temperature(temperature)
        T = temperature.value  # Temperature in Kelvin
        a, b, Tc, n = self._density_constants
        
        # Calculate density using the correlation formula
        den = a / (b ** (1 + (1 - (T / Tc)**n)))
        
        # Convert to kg/m³ using molecular weight
        den = den * self.molecular_weight
        return Density(den, "kg/m3")

    def _get_temperature(self, temperature: Temperature):
        """
        Helper method to get the temperature for calculations.
        
        Returns the provided temperature or the object's default temperature.
        """
        return temperature or self.temperature

    def specific_heat(self, temperature: Temperature = None):
        """
        Calculates the specific heat capacity of the component.

        The method uses a polynomial correlation with temperature to compute the
        specific heat. Subclasses must provide `_specific_heat_constants`.

        Args:
            temperature (Temperature, optional): The temperature for the calculation.

        Returns:
            SpecificHeat: The calculated specific heat in J/kgK.
        """
        temperature = self._get_temperature(temperature)
        T = temperature.value  # Temperature in Kelvin
        
        # Calculate specific heat using the polynomial correlation
        cp = (self._specific_heat_constants[0] +
              self._specific_heat_constants[1] * T +
              self._specific_heat_constants[2] * T**2 +
              self._specific_heat_constants[3] * T**3 +
              self._specific_heat_constants[4] * T**4)
        
        # Convert to J/kgK using molecular weight
        cp = cp * self.molecular_weight
        return SpecificHeat(cp, "J/kgK")

    def viscosity(self, temperature: Temperature = None):
        """
        Calculates the dynamic viscosity of the component.

        The method uses a temperature-dependent correlation to compute the viscosity.
        Subclasses must provide `_viscosity_constants`.

        Args:
            temperature (Temperature, optional): The temperature for the calculation.

        Returns:
            Viscosity: The calculated viscosity in Pa·s.
        """
        temperature = self._get_temperature(temperature)
        T = temperature.value  # Temperature in Kelvin
        
        # Calculate viscosity using the exponential correlation
        po = self._viscosity_constants[0] + (self._viscosity_constants[1] / T) + \
             (self._viscosity_constants[2] * log(T)) + \
             (self._viscosity_constants[3] * (T**self._viscosity_constants[4]))
        vis = exp(po)
        return Viscosity(vis, "Pa·s")

    def thermal_conductivity(self, temperature: Temperature = None):
        """
        Calculates the thermal conductivity of the component.

        The method uses a polynomial correlation with temperature to compute the
        thermal conductivity. Subclasses must provide `_thermal_conductivity_constants`.

        Args:
            temperature (Temperature, optional): The temperature for the calculation.

        Returns:
            ThermalConductivity: The calculated thermal conductivity in W/mK.
        """
        temperature = self._get_temperature(temperature)
        T = temperature.value  # Temperature in Kelvin
        
        # Calculate thermal conductivity using the polynomial correlation
        k = (self._thermal_conductivity_constants[0] +
             self._thermal_conductivity_constants[1] * T +
             self._thermal_conductivity_constants[2] * T**2 +
             self._thermal_conductivity_constants[3] * T**3 +
             self._thermal_conductivity_constants[4] * T**4)
        return ThermalConductivity(k, "W/mK")

    def vapor_pressure(self, temperature: Temperature = None):
        """
        Calculates the vapor pressure of the component.

        The method uses a temperature-dependent correlation (e.g., Antoine equation)
        to compute the vapor pressure. Subclasses must provide `_vapor_pressure_constants`.

        Args:
            temperature (Temperature, optional): The temperature for the calculation.

        Returns:
            Pressure: The calculated vapor pressure in Pa.
        """
        temperature = self._get_temperature(temperature)
        T = temperature.value  # Temperature in Kelvin
        
        # Calculate vapor pressure using the correlation
        po = (self._vapor_pressure_constants[0] + (self._vapor_pressure_constants[1] / T) +
              (self._vapor_pressure_constants[2] * log(T)) +
              (self._vapor_pressure_constants[3] * (T**self._vapor_pressure_constants[4])))
        vp = exp(po)
        return Pressure(vp, "Pa")

    def enthalpy(self, temperature: Temperature = None):
        """
        Calculates the heat of vaporization (enthalpy of vaporization) of the component.

        The method uses a temperature-dependent correlation to compute the enthalpy.
        Subclasses must provide `_enthalpy_constants` and `_critical_temperature`.

        Args:
            temperature (Temperature, optional): The temperature for the calculation.

        Returns:
            HeatOfVaporization: The calculated heat of vaporization in J/kg.
        """
        temperature = self._get_temperature(temperature)
        T = temperature.value  # Temperature in Kelvin
        
        # Reduced temperature
        Tr = T / self._critical_temperature.value
        tou = 1 - Tr
        
        # Calculate enthalpy using the correlation
        dH = self._enthalpy_constants[0] * (tou**((self._enthalpy_constants[1]) + 
                                                   (self._enthalpy_constants[2] * tou) + 
                                                   (self._enthalpy_constants[3] * (tou**2)) + 
                                                   (self._enthalpy_constants[4] * (tou**3))))
        
        # Convert to J/kg using molecular weight
        dH = dH * self.molecular_weight
        return HeatOfVaporization(dH, "J/kg")
