from .base import Component
from processpi.units import *

class DimethylEther(Component):
    """
    Represents the properties and constants for Dimethyl ether(C2?H6?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Dimethyl ether, which are essential for various process engineering calculations.
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
    name = "Dimethyl ether"
    formula = "C2?H6?O"
    molecular_weight = 46.068

    # Critical properties
    _critical_temperature = Temperature(400.1, "K")
    _critical_pressure = Pressure(5.37, "MPa")
    _critical_volume = Volume(0.17, "m3")
    _critical_zc = 0.2744
    _critical_acentric_factor = 0.2002

    _density_constants = [1.5693, 0.2679, 400.1, 0.2882]
    _specific_heat_constants = [0.0, -157.47, 0.51853, 0.0, 0.0, 0.9836, 1.0314]
    _viscosity_constants = [-10.62, 448.99, 8.3967e-05]
    _thermal_conductivity_constants = [0.31174, -0.0005638]
    _vapor_pressure_constants = [44.704, 0.0, -3.4444, 5.46e-17, 6.0]
    _enthalpy_constants = [2.994, 0.3505]
