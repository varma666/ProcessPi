from .base import Component
from processpi.units import *

class MethylIsocyanate(Component):
    """
    Represents the properties and constants for Methyl Isocyanate(C2?H3?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl Isocyanate, which are essential for various process engineering calculations.
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
    name = "Methyl Isocyanate"
    formula = "C2?H3?NO"
    molecular_weight = 57.051

    # Critical properties
    _critical_temperature = Temperature(488.0, "K")
    _critical_pressure = Pressure(5.48, "MPa")
    _critical_volume = Volume(0.202, "m3")
    _critical_zc = 0.273
    _critical_acentric_factor = 0.3007

    _density_constants = [1.0228, 0.20692, 488.0, 0.28571]
    _specific_heat_constants = [0.0, -529.82, 1.3499, 0.0, 0.0, 1.0263, 1.3668]
    _viscosity_constants = []
    _thermal_conductivity_constants = [0.2822, -0.00042037]
    _vapor_pressure_constants = [57.612, 0.0, -5.1269, 2.17e-17, 6.0]
    _enthalpy_constants = [4.2967, 0.37922]
