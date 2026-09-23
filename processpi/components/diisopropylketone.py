from .base import Component
from processpi.units import *

class DiisopropylKetone(Component):
    """
    Represents the properties and constants for Diisopropyl ketone(C7?H14?O).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Diisopropyl ketone, which are essential for various process engineering calculations.
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
    name = "Diisopropyl ketone"
    formula = "C7?H14?O"
    molecular_weight = 114.185

    # Critical properties
    _critical_temperature = Temperature(576.0, "K")
    _critical_pressure = Pressure(3.02, "MPa")
    _critical_volume = Volume(0.416, "m3")
    _critical_zc = 0.262
    _critical_acentric_factor = 0.4044

    _density_constants = [0.64619, 0.26881, 576.0, 0.28036]
    _specific_heat_constants = [0.0, 28.37, 0.5375, 0.0, 0.0, 2.0763, 2.8126]
    _viscosity_constants = [-15.097, 1426.9, 0.51512]
    _thermal_conductivity_constants = [0.22076, -0.00027624]
    _vapor_pressure_constants = [50.868, 0.0, -4.066, 1.13e-06, 2.0]
    _enthalpy_constants = [5.0256, 0.29611]
