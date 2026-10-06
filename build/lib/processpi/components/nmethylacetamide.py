from .base import Component
from processpi.units import *

class NmethylAcetamide(Component):
    """
    Represents the properties and constants for NMethyl acetamide(C3?H7?NO).

    This class provides a comprehensive set of physical and thermodynamic properties
    for NMethyl acetamide, which are essential for various process engineering calculations.
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
    name = "NMethyl acetamide"
    formula = "C3?H7?NO"
    molecular_weight = 73.094

    # Critical properties
    _critical_temperature = Temperature(718.0, "K")
    _critical_pressure = Pressure(4.98, "MPa")
    _critical_volume = Volume(0.267, "m3")
    _critical_zc = 0.223
    _critical_acentric_factor = 0.4351

    _density_constants = [0.88268, 0.23568, 718.0, 0.27379]
    _specific_heat_constants = [0.0, 243.4, 0.0, 0.0, 0.0, 1.4998, 1.9367]
    _viscosity_constants = [-4.648, 1832.0, -1.2191]
    _thermal_conductivity_constants = [0.23743, -0.0002362]
    _vapor_pressure_constants = [79.128, 0.0, -7.7355, 3.16e-18, 6.0]
    _enthalpy_constants = [7.3402, 0.38974]
