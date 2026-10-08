from .base import Component
from processpi.units import *

class DiethylSulfide(Component):
    """
    Represents the properties and constants for Diethyl sulfide(C4H10S).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diethyl sulfide, which are essential for various process engineering calculations.
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
    name = "Diethyl sulfide"
    formula = "C4H10S"
    molecular_weight = 90.187

    # Critical properties
    _critical_temperature = Temperature(557.15, "K")
    _critical_pressure = Pressure(3.96, "MPa")
    _critical_volume = Volume(0.318, "m3")
    _critical_zc = 0.272
    _critical_acentric_factor = 0.29

    _density_constants = [0.82227, 0.26314, 557.15, 0.27369]
    _specific_heat_constants = [238520,-1038.40,4.0587,-0.0044691,0]
    _viscosity_constants = [-5.135, 667.5, -0.8553,0,0]
    _thermal_conductivity_constants = [0.21065, -0.0002623,0,0,0]
    _vapor_pressure_constants = [46.705, -5177.40, -3.5985, 1.71e-06, 2.0]
    _enthalpy_constants = [4.7659e-7, 0.37987,0,0,0]
