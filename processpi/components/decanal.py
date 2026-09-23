from .base import Component
from processpi.units import *

class Decanal(Component):
    """
    Represents the properties and constants for Decanal(C10?H20?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Decanal, which are essential for various process engineering calculations.
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
    name = "Decanal"
    formula = "C10?H20?O"
    molecular_weight = 156.265

    # Critical properties
    _critical_temperature = Temperature(674.2, "K")
    _critical_pressure = Pressure(2.6, "MPa")
    _critical_volume = Volume(0.58, "m3")
    _critical_zc = 0.269
    _critical_acentric_factor = 0.582

    _density_constants = [0.46802, 0.27146, 674.2, 0.26869]
    _specific_heat_constants = [0.0, 586.63, 0.0, 0.0, 0.0, 3.0718, 4.3682]
    _viscosity_constants = [-10.115, 1111.9, -0.015659]
    _thermal_conductivity_constants = [0.20383, -0.0002]
    _vapor_pressure_constants = [201.64, 0.0, -26.264, 1.46e-05, 2.0]
    _enthalpy_constants = [7.9073, 0.4129]
