from .base import Component
from processpi.units import *

class MethylPropionate(Component):
    """
    Represents the properties and constants for Methyl propionate(C4H8O2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Methyl propionate, which are essential for various process engineering calculations.
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
    name = "Methyl propionate"
    formula = "C4H8O2"
    molecular_weight = 88.105

    # Critical properties
    _critical_temperature = Temperature(530.6, "K")
    _critical_pressure = Pressure(4.004, "MPa")
    _critical_volume = Volume(0.282, "m3")
    _critical_zc = 0.256
    _critical_acentric_factor = 0.3466

    _density_constants = [0.9147, 0.2594, 530.6, 0.2774]
    _specific_heat_constants = [71140, 335.5, 0.0, 0.0, 0.0]
    _viscosity_constants = [-4.841, 696.7, -0.9194, 0.0, 0.0]
    _thermal_conductivity_constants = [0.22534, -0.0002683, 0.0, 0.0, 0.0]
    _vapor_pressure_constants = [70.717, -6439.7, -6.9845, 2.0129E-17, 6]
    _enthalpy_constants = [5.008e-7, 0.3959, 0.0, 0.0, 0.0]
