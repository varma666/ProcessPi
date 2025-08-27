from .base import Component
from ..units import *
from .constants import R_UNIVERSAL  # R = 8.314 J/mol·K

class Gas(Component):
    name = "Generic Gas"
    formula = "Gas"
    molecular_weight = 28.0  # g/mol

    _critical_temperature = Temperature(350, "K")
    _critical_pressure = Pressure(4.0, "MPa")
    _critical_volume = Volume(0.31, "m3")
    _critical_zc = 0.27
    _critical_acentric_factor = 0.1

    # Constants (for Cp, viscosity, etc.)
    _specific_heat_constants = [1000, 0, 0, 0, 0]  # J/kg·K
    _viscosity_constants = [-10.5, 800, 0.55, 0, 0]
    _thermal_conductivity_constants = [0.02, 0, 0, 0, 0]
    _vapor_pressure_constants = [50, -5000, -6.8, 0.000005, 2]
    _enthalpy_constants = [3.5E-7, 0.28, 150, 3.2, 0]

    # Override density to use ideal gas law
    def density(self) -> Density:
        """
        Density for a generic gas using the ideal gas equation:
            rho = (P * M) / (R * T)
        """
        P = self.pressure.to("Pa").value
        T = self.temperature.to("K").value
        M = self.molecular_weight / 1000  # convert g/mol to kg/mol
        rho = (P * M) / (R_UNIVERSAL * T)
        return Density(rho, "kg/m3")
