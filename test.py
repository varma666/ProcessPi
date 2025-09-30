from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchanger

# Define streams
hot_in = MaterialStream(name="HotIn", mass_flow=1.5, cp=4200, temperature=370)
cold_in = MaterialStream(name="ColdIn", mass_flow=2.0, cp=4180, temperature=300)

# Create exchanger
hx = HeatExchanger(name="HX1", method="LMTD", U=500, area=20)

hx.attach_stream(hot_in, "hot_in")
hx.attach_stream(cold_in, "cold_in")

# Thermal simulation
print(hx.simulate())

# Mechanical design → Double Pipe
print(hx.design(module="DoublePipe"))

# Mechanical design → Shell-and-Tube with Bell
print(hx.design(module="ShellAndTube", method="bell", baffle_cut=0.25, num_shell_passes=2))
