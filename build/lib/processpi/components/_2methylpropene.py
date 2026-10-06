from .base import Component
from processpi.units import *

class _2MethylPropene(Component):
    """
    Represents the properties and constants for 2Methyl propene(C4?H8?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 2Methyl propene, which are essential for various process engineering calculations.
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
    name = "2Methyl propene"
    formula = "C4?H8?"
    molecular_weight = 56.106

    # Critical properties
    _critical_temperature = Temperature(417.9, "K")
    _critical_pressure = Pressure(4.0, "MPa")
    _critical_volume = Volume(0.239, "m3")
    _critical_zc = 0.275
    _critical_acentric_factor = 0.1948

    _density_constants = [1.1446, 0.2724, 417.9, 0.28172]
    _specific_heat_constants = [0.0, 217.1, -0.9153, 0.002266, 0.0, 1.0568, 1.4596]
    _viscosity_constants = [-10.385, 599.59, -0.046088]
    _thermal_conductivity_constants = [0.2802, -0.000786, 6.52e-07]
    _vapor_pressure_constants = [78.01, 0.0, -8.9575, 1.34e-05, 2.0]
    _enthalpy_constants = [3.2614, 0.38073]
