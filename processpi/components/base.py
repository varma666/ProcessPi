from abc import ABC, abstractmethod
from math import exp, log
from processpi.units import (
    Temperature, Pressure, Density, SpecificHeat, Viscosity,
    ThermalConductivity, HeatOfVaporization
)
from processpi.constants import R_UNIVERSAL  # J/kmol-K

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
        def wrapper(*args, **kwargs):
            return self.func(instance, *args, **kwargs)
        wrapper.value = self.func(instance)
        return wrapper


class Component(ABC):
    """
    Abstract base class for a chemical component with DIPPR-style property methods.
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
        self.temperature = temperature or Temperature(35, "C")
        self.pressure = pressure or Pressure(101325, "Pa")

        self._density = density
        self._specific_heat = specific_heat
        self._viscosity = viscosity
        self._thermal_conductivity = thermal_conductivity
        self._vapor_pressure = vapor_pressure
        self._enthalpy = enthalpy

    # ----------------------------------------------------------------------
    # Abstract Properties
    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def name(self): pass

    @property
    @abstractmethod
    def formula(self): pass

    @property
    @abstractmethod
    def molecular_weight(self):  # in g/mol
        pass

    # ----------------------------------------------------------------------
    # Phase Detection
    # ----------------------------------------------------------------------
    @PropertyMethod
    def phase(self) -> str:
        """
        Detects phase based on system pressure and vapor pressure.
        Returns: "gas" or "liquid"
        """
        P = self.pressure.to("Pa").value
        Pvap = self.vapor_pressure().to("Pa").value
        return "gas" if P < Pvap else "liquid"

    # ----------------------------------------------------------------------
    # Density
    # ----------------------------------------------------------------------
    @PropertyMethod
    def density(self) -> Density:
        """
        Returns density (kg/m³):
        - Gas: Ideal Gas Law (PV = nRT)
        - Liquid: DIPPR correlation
        """
        if self._density is not None:
            return self._density

        T = self.temperature.to("K").value
        P = self.pressure.to("Pa").value
        phase = self.phase.value

        MW_kg_per_mol = self.molecular_weight / 1000  # g/mol → kg/mol

        if phase == "gas":
            rho = (P * MW_kg_per_mol) / (R_UNIVERSAL * T)
            return Density(rho, "kg/m3")

        # Liquid DIPPR correlation
        a, b, Tc, n = self._density_constants
        T_celsius = self.temperature.to("C").value
        rho = a / (b ** (1 + (1 - (T_celsius / Tc)) ** n))
        rho *= self.molecular_weight
        return Density(rho, "kg/m3")

    # ----------------------------------------------------------------------
    # Specific Heat
    # ----------------------------------------------------------------------
    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
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
        Returns viscosity (Pa·s):
        - Liquid: DIPPR correlation
        - Gas: Sutherland approximation
        """
        if self._viscosity is not None:
            return self._viscosity

        phase = self.phase.value
        T = self.temperature.to("K").value

        if phase == "liquid":
            po = (self._viscosity_constants[0] +
                  (self._viscosity_constants[1] / self.temperature.value) +
                  (self._viscosity_constants[2] * log(self.temperature.value)) +
                  (self._viscosity_constants[3] *
                   (self.temperature.value ** self._viscosity_constants[4])))
            mu = exp(po)
            return Viscosity(mu, "Pa·s")

        # --- Gas phase: Sutherland's law ---
        mu0 = getattr(self, "_gas_viscosity_ref", 1.8e-5)  # air baseline (Pa·s)
        T0 = getattr(self, "_gas_viscosity_Tref", 300.0)   # reference K
        C = getattr(self, "_sutherland_constant", 120.0)   # Sutherland constant
        mu = mu0 * ((T0 + C) / (T + C)) * ((T / T0) ** 1.5)
        return Viscosity(mu, "Pa·s")

    # ----------------------------------------------------------------------
    # Thermal Conductivity
    # ----------------------------------------------------------------------
    @PropertyMethod
    def thermal_conductivity(self) -> ThermalConductivity:
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
