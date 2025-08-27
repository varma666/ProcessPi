from abc import ABC, abstractmethod
from math import exp, log
from processpi.units import (
    Temperature, Pressure, Density, SpecificHeat, Viscosity,
    ThermalConductivity, HeatOfVaporization
)

class PropertyMethod:
    """
    Descriptor that allows both property-style and method-style access.

    Example:
        @PropertyMethod
        def density(self):
            return 100
        # obj.density -> 100
        # obj.density() -> 100
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Wrapper for dual behavior
        def wrapper(*args, **kwargs):
            return self.func(instance, *args, **kwargs)
        # Allow direct attribute-style usage
        wrapper.value = self.func(instance)
        return wrapper


class Component(ABC):
    """
    Abstract base class for a chemical component.

    Provides a common interface and default DIPPR-style
    correlations for:
      - Density
      - Specific Heat
      - Viscosity
      - Thermal Conductivity
      - Vapor Pressure
      - Enthalpy of Vaporization

    Subclasses must define:
      - name
      - formula
      - molecular_weight
      - correlation constants for each property
    """

    def __init__(
        self,
        temperature: Temperature = None,
        pressure: Pressure = None,
        density: Density = None,
        specific_heat: SpecificHeat = None,
        viscosity: Viscosity = None,
        thermal_conductivity: ThermalConductivity = None,
        vapor_pressure: Pressure = None,
        enthalpy: HeatOfVaporization = None,
    ):
        """
        Initialize the component.

        Args:
            temperature (Temperature): Operating temperature (default 35°C).
            pressure (Pressure): Operating pressure (default 101,325 Pa).
            density (Density): Optional override for density.
            specific_heat (SpecificHeat): Optional override for Cp.
            viscosity (Viscosity): Optional override for viscosity.
            thermal_conductivity (ThermalConductivity): Optional override for k.
            vapor_pressure (Pressure): Optional override for vapor pressure.
            enthalpy (HeatOfVaporization): Optional override for latent heat.
        """
        self.temperature = temperature or Temperature(35, "C")
        self.pressure = pressure or Pressure(101325, "Pa")

        # Optional overrides
        self._density = density
        self._specific_heat = specific_heat
        self._viscosity = viscosity
        self._thermal_conductivity = thermal_conductivity
        self._vapor_pressure = vapor_pressure
        self._enthalpy = enthalpy

    # ----------------------------------------------------------------------
    # Abstract properties
    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def name(self):
        """Component name (e.g., 'Acetone')."""
        pass

    @property
    @abstractmethod
    def formula(self):
        """Chemical formula (e.g., 'C3H6O')."""
        pass

    @property
    @abstractmethod
    def molecular_weight(self):
        """Molecular weight in g/mol."""
        pass

    # ----------------------------------------------------------------------
    # Density
    # ----------------------------------------------------------------------
    @PropertyMethod
    def density(self) -> Density:
        """
        Density (kg/m³).
        Uses DIPPR correlation unless overridden.
        """
        if self._density is not None:
            return self._density
        T = self.temperature.value
        a, b, Tc, n = self._density_constants
        rho = a / (b ** (1 + (1 - (T / Tc)) ** n))
        rho *= self.molecular_weight
        return Density(rho, "kg/m3")

    # ----------------------------------------------------------------------
    # Specific Heat
    # ----------------------------------------------------------------------
    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        """
        Specific heat (J/kg·K).
        Polynomial correlation: Cp = A + B·T + C·T² + D·T³ + E·T⁴.
        """
        if self._specific_heat is not None:
            return self._specific_heat
        T = self.temperature.value
        cp = sum(c * (T ** i) for i, c in enumerate(self._specific_heat_constants))
        cp *= self.molecular_weight
        return SpecificHeat(cp, "J/kgK")

    # ----------------------------------------------------------------------
    # Viscosity
    # ----------------------------------------------------------------------
    @PropertyMethod
    def viscosity(self) -> Viscosity:
        """
        Dynamic viscosity (Pa·s).
        Exponential DIPPR correlation.
        """
        if self._viscosity is not None:
            return self._viscosity
        T = self.temperature.value
        po = (self._viscosity_constants[0] +
              (self._viscosity_constants[1] / T) +
              (self._viscosity_constants[2] * log(T)) +
              (self._viscosity_constants[3] * (T ** self._viscosity_constants[4])))
        mu = exp(po)
        return Viscosity(mu, "Pa·s")

    # ----------------------------------------------------------------------
    # Thermal Conductivity
    # ----------------------------------------------------------------------
    @PropertyMethod
    def thermal_conductivity(self) -> ThermalConductivity:
        """
        Thermal conductivity (W/m·K).
        Polynomial correlation: k = A + B·T + C·T² + D·T³ + E·T⁴.
        """
        if self._thermal_conductivity is not None:
            return self._thermal_conductivity
        T = self.temperature.value
        k = sum(c * (T ** i) for i, c in enumerate(self._thermal_conductivity_constants))
        return ThermalConductivity(k, "W/mK")

    # ----------------------------------------------------------------------
    # Vapor Pressure
    # ----------------------------------------------------------------------
    @PropertyMethod
    def vapor_pressure(self) -> Pressure:
        """
        Vapor pressure (Pa).
        Exponential DIPPR correlation.
        """
        if self._vapor_pressure is not None:
            return self._vapor_pressure
        T = self.temperature.value
        po = (self._vapor_pressure_constants[0] +
              (self._vapor_pressure_constants[1] / T) +
              (self._vapor_pressure_constants[2] * log(T)) +
              (self._vapor_pressure_constants[3] * (T ** self._vapor_pressure_constants[4])))
        vp = exp(po)
        return Pressure(vp, "Pa")

    # ----------------------------------------------------------------------
    # Enthalpy of Vaporization
    # ----------------------------------------------------------------------
    @PropertyMethod
    def enthalpy(self) -> HeatOfVaporization:
        """
        Enthalpy of vaporization (J/kg).
        Based on reduced temperature (Tr = T/Tc).
        """
        if self._enthalpy is not None:
            return self._enthalpy
        T = self.temperature.value
        Tr = T / self._critical_temperature.value
        tau = 1 - Tr
        dH = (self._enthalpy_constants[0] *
              (tau ** (self._enthalpy_constants[1] +
                       (self._enthalpy_constants[2] * tau) +
                       (self._enthalpy_constants[3] * tau ** 2) +
                       (self._enthalpy_constants[4] * tau ** 3))))
        dH *= self.molecular_weight
        return HeatOfVaporization(dH, "J/kg")
