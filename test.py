from processpi.components import *
from processpi.streams import MaterialStream
from processpi.equipment.absorber import Absorber
from processpi.equipment.stripper import Stripper

CO2 = Carbondioxide("CO2")
N2 = Gas("N2")
MEA = Methanol("MEA")

# Absorber
gas_in = MaterialStream("GasIn", flow_rate=100, composition={CO2:0.2, N2:0.8})
gas_out = MaterialStream("GasOut")
liq_in = MaterialStream("SolventIn", flow_rate=50, composition={MEA:1.0})
liq_out = MaterialStream("SolventOut")

abs_col = Absorber("CO2 Absorber", stages=5, removal_efficiency=0.9)
abs_col.gas_in, abs_col.gas_out, abs_col.liquid_in, abs_col.liquid_out = gas_in, gas_out, liq_in, liq_out

print(abs_col.simulate())

