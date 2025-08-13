from processpi.calculations.fluids.pump_power import PumpPower
from processpi.units import *
from processpi.calculations.engine import CalculationEngine

engine = CalculationEngine()
engine.register_calculation("pump_power", PumpPower)

result = engine.calculate("pump_power", flow_rate=VolumetricFlowRate(10,"m3/h"), head=Length(15,"m"), density=Density(1000,"kg/m3"), efficiency=0.4)
print(result)