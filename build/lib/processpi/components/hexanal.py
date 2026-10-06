from .base import Component
from processpi.units import *

class Hexanal(Component):
    """
    Represents the properties and constants for Hexanal(C6?H12?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hexanal, which are essential for various process engineering calculations.
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
    name = "Hexanal"
    formula = "C6?H12?O"
    molecular_weight = 100.159

    # Critical properties
    _critical_temperature = Temperature(591.0, "K")
    _critical_pressure = Pressure(3.46, "MPa")
    _critical_volume = Volume(0.369, "m3")
    _critical_zc = 0.26
    _critical_acentric_factor = 0.3872

    _density_constants = [0.71899, 0.26531, 591.0, 0.27628]
    _specific_heat_constants = [0.0, 329.52, 0.0, 0.0, 0.0, 1.8926, 2.4999]
    _viscosity_constants = [-10.745, 1021.4, -5.5427e-05]
    _thermal_conductivity_constants = [0.22196, -0.00032053, 1.16e-07]
    _vapor_pressure_constants = [81.507, 0.0, -8.4516, 1.51e-17, 6.0]
    _enthalpy_constants = [5.6661, 0.38533]
