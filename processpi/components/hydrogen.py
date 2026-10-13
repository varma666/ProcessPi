from .base import Component
from processpi.units import *

class Hydrogen(Component):
    """
    Represents the properties and constants for Hydrogen(H2).

    This class provides a comprehensive set of physical and thermodynamic properties
    for Hydrogen, which are essential for various process engineering calculations.
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
    name = "Hydrogen"
    formula = "H2"
    molecular_weight = 2.016

    # Critical properties
    _critical_temperature = Temperature(33.19, "K")
    _critical_pressure = Pressure(1.313, "MPa")
    _critical_volume = Volume(0.064147, "m3")
    _critical_zc = 0.305
    _critical_acentric_factor = -0.216

    _density_constants = [5.414, 0.34893, 33.19, 0.2706]
    _specific_heat_constants = [66.653, 6765.90, -123.63, 478.27, 0.0]
    _viscosity_constants = [-11.661, 24.7, -0.261, -4.1e-16, 10.0]
    _thermal_conductivity_constants = [-0.0917, 0.017678, -0.000382, -3.33e-06, 1.03e-07]
    _vapor_pressure_constants = [12.69, -94.896, 1.1125, 0.000329, 2.0]
    _enthalpy_constants = [0.10127e-7, 0.698, -1.817, 1.447,0.0]

    @property
    def specific_heat(self):
                """
                Calculates the specific heat of Benzene at a given temperature.
        
                The calculation uses a polynomial fit for specific heat ($C_p$) as a
                function of temperature. The function selects a set of constants
                based on the provided temperature value to ensure accuracy.
        
                Args:
                    temperature (Temperature): The temperature at which to calculate
                                               the specific heat, in Kelvin.
        
                Returns:
                    SpecificHeat: The calculated specific heat in units of J/kgK.
                """
                T = self.temperature.value
                # Use a conditional to select the correct set of polynomial constants.
                if T <= 353.24:
                    constants = self._specific_heat_constants_1
                else:
                    constants = self._specific_heat_constants_2
        
                # Calculate Cp using the polynomial fit. The result is in J/kmol K.
                cp_kmol = (constants[0] +
                           constants[1] * T +
                           constants[2] * T**2 +
                           constants[3] * T**3 +
                           constants[4] * T**4)
        
                # Convert the specific heat from J/kmol K to J/kg K by dividing by
                # the molecular weight (g/mol), since 1 kmol is 1000 mol and 1 kg
                # is 1000 g.
                cp_kg = cp_kmol / self.molecular_weight
                
                return SpecificHeat(cp_kg, "J/kgK")
    