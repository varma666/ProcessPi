from .base import Component
from processpi.units import *

class Hydrazine(Component):
    """
    Represents the properties and constants for Hydrazine(H4?N2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrazine, which are essential for various process engineering calculations.
    These properties are stored as class attributes and are available for use by other
    calculation modules within the ProcessPI library.

    **Properties:**
    - `name`: The common name of the compound.
    - `formula`: The chemical formula.
    - `molecular_weight`: The molar mass in g/mol.
    - `_critical_temperature`: The critical temperature, above which a substance
      cannot exist as a liquid, regardless of pressure.
    - `_critical_pressure`: The critical pressure, the vapor pressure at the
      critical temperature.
    - `_critical_volume`: The critical volume per kmole.
    - `_critical_zc`: The critical compressibility factor.
    - `_critical_acentric_factor`: The acentric factor, a measure of the
      non-sphericity of the molecule.
    - `_density_constants`: Constants for calculating density as a function of temperature.
    - `_specific_heat_constants`: Constants for calculating specific heat capacity as a
      function of temperature.
    - `_viscosity_constants`: Constants for calculating viscosity as a function of
      temperature.
    - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity
      as a function of temperature.
    - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a
      function of temperature using the Antoine equation or similar models.
    - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.
    """
    name = "Hydrazine"
    formula = "H4?N2?"
    molecular_weight = 32.045

    # Critical properties
    _critical_temperature = Temperature(653.15, "K")
    _critical_pressure = Pressure(14.7, "MPa")
    _critical_volume = Volume(0.158, "m3")
    _critical_zc = 0.428
    _critical_acentric_factor = 0.3143

    _density_constants = [1.0516, 0.16613, 653.15, 0.1898]
    _specific_heat_constants = [0.0, 50.929, 0.043379, 0.0, 0.0, 0.9708, 1.3158]
    _viscosity_constants = [-75.781, 4175.4, 9.6508, -7.27e-09, 3.0]
    _thermal_conductivity_constants = [1.3675, -0.0015895]
    _vapor_pressure_constants = [76.858, 0.0, -8.22, 0.00616, 1.0]
    _enthalpy_constants = [5.9794, 0.9424, -1.398, 0.8862]
