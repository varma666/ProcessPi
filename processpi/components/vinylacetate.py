from .base import Component
from processpi.units import *

class VinylAcetate(Component):
    """
    Represents the properties and constants for Vinyl acetate(C4?H6?O2?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Vinyl acetate, which are essential for various process engineering calculations.
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
    name = "Vinyl acetate"
    formula = "C4?H6?O2?"
    molecular_weight = 86.089

    # Critical properties
    _critical_temperature = Temperature(519.13, "K")
    _critical_pressure = Pressure(3.958, "MPa")
    _critical_volume = Volume(0.27, "m3")
    _critical_zc = 0.248
    _critical_acentric_factor = 0.3513

    _density_constants = [0.9591, 0.2593, 519.13, 0.27448]
    _specific_heat_constants = [0.0, -106.17, 0.75175, 0.0, 0.0, 1.5939, 2.0892]
    _viscosity_constants = [-22.407, 1462.8, 1.7006]
    _thermal_conductivity_constants = [0.256, -0.0003542]
    _vapor_pressure_constants = [57.406, 0.0, -5.0307, 1.1e-17, 6.0]
    _enthalpy_constants = [4.77, 0.3765]
