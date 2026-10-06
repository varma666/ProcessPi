from .base import Component
from processpi.units import *

class _1Decanol(Component):
    """
    Represents the properties and constants for 1Decanol(C10?H22?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Decanol, which are essential for various process engineering calculations.
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
    name = "1Decanol"
    formula = "C10?H22?O"
    molecular_weight = 158.281

    # Critical properties
    _critical_temperature = Temperature(688.0, "K")
    _critical_pressure = Pressure(2.308, "MPa")
    _critical_volume = Volume(0.645, "m3")
    _critical_zc = 0.26
    _critical_acentric_factor = 0.607

    _density_constants = [0.38208, 0.24645, 688.0, 0.26125]
    _specific_heat_constants = [0.0, 0.0, 216.35, -0.37538, 0.00023674, 3.5373, 5.0169]
    _viscosity_constants = [-69.985, 5818.8, 8.0715]
    _thermal_conductivity_constants = [0.228, -0.000223]
    _vapor_pressure_constants = [156.239, 0.0, -18.424, 8.5e-18, 6.0]
    _enthalpy_constants = [7.9041, -1.36, 4.0854, -2.3871]
