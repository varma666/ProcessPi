from .base import Component
from processpi.units import *

class _1Methylcyclopentene(Component):
    """
    Represents the properties and constants for 1Methylcyclopentene(C6?H10?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Methylcyclopentene, which are essential for various process engineering calculations.
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
    name = "1Methylcyclopentene"
    formula = "C6?H10?"
    molecular_weight = 82.144

    # Critical properties
    _critical_temperature = Temperature(542.0, "K")
    _critical_pressure = Pressure(4.13, "MPa")
    _critical_volume = Volume(0.303, "m3")
    _critical_zc = 0.278
    _critical_acentric_factor = 0.2318

    _density_constants = [0.88824, 0.26914, 542.0, 0.27874]
    _specific_heat_constants = [0.0, 327.92, 0.0, 0.0, 0.0, 1.1885, 1.676]
    _viscosity_constants = [-4.8515, 679.07, -0.93238]
    _thermal_conductivity_constants = [0.20023, -0.00025581]
    _vapor_pressure_constants = [52.732, 0.0, -4.4509, 1.09e-17, 6.0]
    _enthalpy_constants = [4.3541, 0.36805]
