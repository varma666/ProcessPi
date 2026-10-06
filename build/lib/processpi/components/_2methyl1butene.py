from .base import Component
from processpi.units import *

class _2Methyl1Butene(Component):
    """
    Represents the properties and constants for 2Methyl1butene(C5?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methyl1butene, which are essential for various process engineering calculations.
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
    name = "2Methyl1butene"
    formula = "C5?H10?"
    molecular_weight = 70.133

    # Critical properties
    _critical_temperature = Temperature(465.0, "K")
    _critical_pressure = Pressure(3.447, "MPa")
    _critical_volume = Volume(0.292, "m3")
    _critical_zc = 0.26
    _critical_acentric_factor = 0.2341

    _density_constants = [0.91619, 0.26752, 465.0, 0.28164]
    _specific_heat_constants = [0.0, -247.63, 0.91849, 0.0, 0.0, 1.3282, 1.5921]
    _viscosity_constants = [-10.755, 705.48, -0.011113]
    _thermal_conductivity_constants = [0.19447, -0.0002901]
    _vapor_pressure_constants = [93.131, 0.0, -11.852, 0.0142, 1.0]
    _enthalpy_constants = [3.9091, 0.39866]
