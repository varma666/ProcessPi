from unittest import result
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchanger
from processpi.units import *
from processpi.components import Water, OrganicLiquid

'''
# Define streams without component
hot_in = MaterialStream(name="HotIn", mass_flow=MassFlowRate(9692,"lb/h"),temperature=Temperature(150,"F"), specific_heat = SpecificHeat(0.52,"BTU/lbF")) 
hot_out = MaterialStream(name="HotOut", component=OrganicLiquid(temperature=Temperature(100,"F")))
cold_in = MaterialStream(name="ColdIn", mass_flow=MassFlowRate(10000,"lb/h"),temperature=Temperature(60,"F"), specific_heat = SpecificHeat(0.42,"BTU/lbF"))
cold_out = MaterialStream(name="ColdOut", component=OrganicLiquid(temperature=Temperature(120,"F")))
'''

# Define streams with component
hot_in = MaterialStream(name="HotIn", component=OrganicLiquid(temperature=Temperature(150,"F"), specific_heat = SpecificHeat(0.52,"BTU/lbF")) )
hot_out = MaterialStream(name="HotOut", component=OrganicLiquid(temperature=Temperature(100,"F")))
cold_in = MaterialStream(name="ColdIn", mass_flow=MassFlowRate(10000,"lb/h"), component=OrganicLiquid(temperature=Temperature(60,"F"), specific_heat = SpecificHeat(0.42,"BTU/lbF")))
cold_out = MaterialStream(name="ColdOut", component=OrganicLiquid(temperature=Temperature(120,"F")))


# Create exchanger
hx = HeatExchanger(name="HX1")

hx.attach_stream(hot_in, port = "hot_in")
hx.attach_stream(hot_out, port = "hot_out")
hx.attach_stream(cold_in, port = "cold_in")
hx.attach_stream(cold_out,port = "cold_out")

# Thermal simulation
result = hx.simulate()
print(result)


'''# Mechanical design → Double Pipe
print(hx.design(module="DoublePipe"))

# Mechanical design → Shell-and-Tube with Bell
print(hx.design(module="ShellAndTube", method="bell", baffle_cut=0.25, num_shell_passes=2))'''
