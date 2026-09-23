from .base import Component
from processpi.units import *

class _124Tetrahydronaphthalene(Component):
    """
    Represents the properties and constants for 12,4Tetrahydronaphthalene(C10?H12?).

    This class provides a comprehensive set of physical and thermodynamic properties
    for 12,4Tetrahydronaphthalene, which are essential for various process engineering calculations.
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
    name = "12,4Tetrahydronaphthalene"
    formula = "C10?H12?"
    molecular_weight = 132.202

    # Critical properties
    _critical_temperature = Temperature(720.0, "K")
    _critical_pressure = Pressure(3.65, "MPa")
    _critical_volume = Volume(0.408, "m3")
    _critical_zc = 0.249
    _critical_acentric_factor = 0.3353

    _density_constants = [0.67717, 0.27772, 720.0, 0.2878]
    _specific_heat_constants = [0.0, 455.38, 0.0, 0.0, 0.0, 1.8986, 3.0069]
    _viscosity_constants = [-11.167, 1193.2, 0.096226, 960000000000.0, -5.0]
    _thermal_conductivity_constants = [0.14563, -5.36e-05]
    _vapor_pressure_constants = [137.23, 0.0, -17.908, 0.0145, 1.0]
    _enthalpy_constants = [6.8086, 0.43054]
