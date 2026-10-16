from processpi.units import *
from processpi.components import Water, Benzene
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchangerEngine
hot_fluid = Benzene()
cold_fluid = Water()
hot_in = MaterialStream(
    "Benzene IN", 
    component = hot_fluid, 
    temperature = Temperature(90,"C"), 
    pressure = Pressure(5,"bar"), 
    mass_flow = MassFlowRate(20000,"kg/h"))
hot_out = MaterialStream(
    "Benzene OUT",
    component = hot_fluid,
    temperature = Temperature(60,"C"))

cold_in = MaterialStream(
    "Water IN",
    component = cold_fluid,
    temperature = Temperature(30,"C"),
    pressure = Pressure(6.5,"bar"))
cold_out = MaterialStream(
    "Water OUT",
    component = cold_fluid,
    temperature = Temperature(37,"C"))
hx = HeatExchangerEngine()
hx.fit(
    hot_in = hot_in, 
    hot_out = hot_out, 
    cold_in = cold_in, 
    cold_out = cold_out, 
    tube_length = Length(5,"m"),
    hx_type = "shell_and_tube",
    #tube_od = Length(0.025,"m"),
    shell_dp = Pressure(0.8,"bar"),
    tube_dp = Pressure(0.8,"bar"),
    )
result = hx.run()
#print(result.summary())
#print(f"Area Required: {result.detailed_summary()['Area_required']}")
#print(f"Area: {result.detailed_summary()['U_Calculated']}")
#print(result.detailed_summary())
print(f"Tube OD: {result.detailed_summary()['tube_od']}")
"""
from processpi.components import Water, Benzene
hot_fluid = Benzene()
cold_fluid = Water()
hot_in = MaterialStream(
    "Benzene IN",
    component = hot_fluid,
    temperature = Temperature(90,"C"),
    mass_flow = MassFlowRate(21000,"kg/h"))
hot_out = MaterialStream(
    "Benzene OUT",
    component = hot_fluid,
    temperature = Temperature(30,"C"))
cold_in = MaterialStream(
    "Water IN",
    component = cold_fluid,
    temperature = Temperature(15,"C"),
    mass_flow = MassFlowRate(60500,"kg/h"))
hx = HeatExchangerEngine()
hx.fit(
    hot_in = hot_in,
    cold_in = cold_in,
    hot_out = hot_out,
    shell_dp = Pressure(1,"bar"),
    tube_dp = Pressure(1,"bar"),
    u_assumed = HeatTransferCoefficient(500,"W/m2K"),
)
result = hx.run()
print(result.summary())"""

