from .base import Component
from processpi.units import *


class Benzene(Component):
    """
    Represents the chemical component Benzene ($C_6H_6$).

    This class provides a comprehensive set of physical and thermodynamic
    properties for Benzene, including its molecular weight, critical properties,
    and constants for various property calculations.
    """
    name = "Benzene"
    formula = "C6H6"
    molecular_weight = 78.114
    # Critical properties of Benzene. These are essential reference points for
    # many thermodynamic correlations.
    _critical_temperature = Temperature(562.1, "K")
    _critical_pressure = Pressure(4.895, "MPa")
    _critical_volume = Volume(0.256, "m3")  # Placeholder for critical volume per Kmole
    _critical_zc = 0.268  # Placeholder for critical compressibility factor
    _critical_acentric_factor = 0.2103  # Placeholder for critical acentric factor
    _density_constants = [1.0259, 0.26666, 562.05, 0.28394]
    # Specific heat constants for a polynomial fit, valid for different temperature ranges.
    # These constants are for Cp in J/kmol K.
    _specific_heat_constants_1 = [129440, -169.5, 0.64781, 0, 0]
    _specific_heat_constants_2 = [162940, -344.94, 0.85562, 0, 0]
    _viscosity_constants = [7.5117, 294.68, -2.794, 0, 0]
    _thermal_conductivity_constants = [0.23444, -0.00030572, 0, 0, 0]
    _vapor_pressure_constants = [83.107, -6486.2, -9.2194, 0.0000069844, 2]
    _enthalpy_constants = [4.5346E-7, 0.39053, 278.68, 3.4705, 0]  # Placeholder for enthalpy constants

    def specific_heat(self, temperature: Temperature):
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
        T = temperature.value
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
