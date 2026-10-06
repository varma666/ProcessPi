from .base import Component
from processpi.units import *

class Ethyltrichlorosilane(Component):
    """
    Represents the properties and constants for Ethyltrichlorosilane(C2?H5?Cl3?Si).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Ethyltrichlorosilane, which are essential for various process engineering calculations.
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
    name = "Ethyltrichlorosilane"
    formula = "C2?H5?Cl3?Si"
    molecular_weight = 163.506

    # Critical properties
    _critical_temperature = Temperature(559.95, "K")
    _critical_pressure = Pressure(3.33, "MPa")
    _critical_volume = Volume(0.414, "m3")
    _critical_zc = 0.296
    _critical_acentric_factor = 0.2691

    _density_constants = [0.58579, 0.24246, 559.95, 0.29509]
    _specific_heat_constants = [0.0, 85.318, 0.46693, 0.0, 0.0, 1.3255, 2.0109]
    _viscosity_constants = [7.8744, -106.34, -2.6884, 42800000000000.0, -6.0]
    _thermal_conductivity_constants = [0.19769, -0.00017713, -1.54e-07]
    _vapor_pressure_constants = [62.614, 0.0, -5.84, 1.09e-17, 6.0]
    _enthalpy_constants = [4.9482, 0.39871]
