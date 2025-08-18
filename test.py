from processpi.calculations.thermodynamics.enthalpy_change import EnthalpyChange
from processpi.calculations.thermodynamics.entropy_change import EntropyChange
from processpi.calculations.thermodynamics.heat_of_vaporization import HeatOfVaporization
from processpi.calculations.engine import CalculationEngine

engine = CalculationEngine()

engine.register_calculation("enthalpy_change", EnthalpyChange)
engine.register_calculation("entropy_change", EntropyChange)
engine.register_calculation("heat_of_vaporization", HeatOfVaporization)
