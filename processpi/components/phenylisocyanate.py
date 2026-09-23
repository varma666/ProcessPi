from .base import Component
from processpi.units import *

class PhenylIsocyanate(Component):
    """
    Represents the properties and constants for Phenyl isocyanate(C7?H5?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Phenyl isocyanate, which are essential for various process engineering calculations.
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
    name = "Phenyl isocyanate"
    formula = "C7?H5?NO"
    molecular_weight = 119.121

    # Critical properties
    _critical_temperature = Temperature(653.0, "K")
    _critical_pressure = Pressure(4.06, "MPa")
    _critical_volume = Volume(0.37, "m3")
    _critical_zc = 0.277
    _critical_acentric_factor = 0.4123

    _density_constants = [0.63163, 0.23373, 653.0, 0.28571]
    _specific_heat_constants = [0.0, 215.89, 0.29552, 0.0, 0.0, 1.308, 2.3745]
    _viscosity_constants = [-11.31, 1280.0]
    _thermal_conductivity_constants = [0.16326, -0.00017777]
    _vapor_pressure_constants = [86.779, 0.0, -9.5303, 6.14e-06, 2.0]
    _enthalpy_constants = [5.5769, 0.30346]
