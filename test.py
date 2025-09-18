from processpi.units import *
from processpi.equipment.heatexchangers import HeatExchanger

hx = HeatExchanger("HX-101")

Q = HeatFlow(1e6, "W")  # 1 MW duty
U = HeatTransferCoefficient(500, "W/m2K")
dT_lm = Temperature(20, "K")

area = hx.calculate_area(Q, U, dT_lm)
print("Required HX area:", area)
