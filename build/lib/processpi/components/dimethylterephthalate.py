from .base import Component
from processpi.units import *

class DimethylTerephthalate(Component):
    """
    Represents the properties and constants for Dimethyl terephthalate(C10?H10?O4?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl terephthalate, which are essential for various process engineering calculations.
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
    name = "Dimethyl terephthalate"
    formula = "C10?H10?O4?"
    molecular_weight = 194.184

    # Critical properties
    _critical_temperature = Temperature(772.0, "K")
    _critical_pressure = Pressure(2.78, "MPa")
    _critical_volume = Volume(0.529, "m3")
    _critical_zc = 0.229
    _critical_acentric_factor = 0.6371

    _density_constants = [0.50824, 0.26885, 772.0, 0.2612]
    _specific_heat_constants = [0.0, 431.04, 0.0, 0.0, 0.0, 3.7252, 3.9104]
    _viscosity_constants = [-11.488, 1922.6]
    _thermal_conductivity_constants = [0.21593, -0.00020805]
    _vapor_pressure_constants = [43.541, 0.0, -2.7519, 1.05e-18, 6.0]
    _enthalpy_constants = [7.236, 0.2424]
