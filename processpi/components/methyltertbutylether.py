from .base import Component
from processpi.units import *

class MethylTertButylEther(Component):
    """
    Represents the properties and constants for Methyl tert-butyl ether(C5?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl tert-butyl ether, which are essential for various process engineering calculations.
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
    name = "Methyl tert-butyl ether"
    formula = "C5?H12?O"
    molecular_weight = 88.148

    # Critical properties
    _critical_temperature = Temperature(497.1, "K")
    _critical_pressure = Pressure(3.287, "MPa")
    _critical_volume = Volume(0.314, "m3")
    _critical_zc = 0.25
    _critical_acentric_factor = 0.2466

    _density_constants = [0.928, 0.289, 497.1, 0.286]
    _specific_heat_constants = [0.0, 94.356, -0.0032, 0.0009795, 0.0, 1.541, 1.9954]
    _viscosity_constants = [-6.921, 790.773, -0.654]
    _thermal_conductivity_constants = [0.2253, -0.00037273, 1.17e-07]
    _vapor_pressure_constants = [57.1511, 0.0, -5.1429, 1.65e-17, 6.0]
    _enthalpy_constants = [3.872, 0.044, 0.448, -0.112]
