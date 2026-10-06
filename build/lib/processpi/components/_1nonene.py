from .base import Component
from processpi.units import *

class _1Nonene(Component):
    """
    Represents the properties and constants for 1Nonene(C9?H18?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 1Nonene, which are essential for various process engineering calculations.
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
    name = "1Nonene"
    formula = "C9?H18?"
    molecular_weight = 126.239

    # Critical properties
    _critical_temperature = Temperature(593.1, "K")
    _critical_pressure = Pressure(2.428, "MPa")
    _critical_volume = Volume(0.524, "m3")
    _critical_zc = 0.258
    _critical_acentric_factor = 0.4367

    _density_constants = [0.48661, 0.25722, 593.1, 0.28571]
    _specific_heat_constants = [0.0, -298.06, 1.1707, 0.0, 0.0, 2.4041, 3.3583]
    _viscosity_constants = [-21.921, 1603.9, 1.5971]
    _thermal_conductivity_constants = [0.20468, -0.00025738]
    _vapor_pressure_constants = [63.313, 0.0, -5.8055, 7.58e-18, 6.0]
    _enthalpy_constants = [5.9054, 0.61039, -0.54533, 0.30683]
