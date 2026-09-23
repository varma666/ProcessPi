from .base import Component
from processpi.units import *

class _246Trinitrotoluene(Component):
    """
    Represents the properties and constants for 246Trinitrotoluene(C7?H5?N3?O6?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 246Trinitrotoluene, which are essential for various process engineering calculations.
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
    name = "246Trinitrotoluene"
    formula = "C7?H5?N3?O6?"
    molecular_weight = 227.131

    # Critical properties
    _critical_temperature = Temperature(828.0, "K")
    _critical_pressure = Pressure(3.04, "MPa")
    _critical_volume = Volume(0.572, "m3")
    _critical_zc = 0.253
    _critical_acentric_factor = 0.8972

    _density_constants = [0.37378, 0.21379, 828.0, 0.29905]
    _specific_heat_constants = [0.0, 514.64, 0.0, 0.0, 0.0, 3.1571, 3.7798]
    _viscosity_constants = [-11.504, 3301.0, -0.39102]
    _thermal_conductivity_constants = [-1.5128, 0.0079553, -1.0066e-05]
    _vapor_pressure_constants = [302.0, 0.0, -40.13, 1.74e-05, 2.0]
    _enthalpy_constants = [10.686, 0.40074]
