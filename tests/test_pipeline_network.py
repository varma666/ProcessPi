"""Example 1
Estimate the optimum pipe diameter for a flow of dry chlorine gas of 10 000 kg/h at 6
atm a and at 20oC through carbon steel pipe """
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine

# Define fluid and mass flow
fluid = Chlorine(temperature=Temperature(20, "C"), pressure=Pressure(6, "atm"))
mass_flow = MassFlowRate(10000, "kg/h")

print(fluid.density())

# Create engine without an explicit network
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow
     # realistic pipe length
)
results = model.run()  # auto diameter sizing
results.summary()
""" 
🔍 No available pressure drop given. Displaying results for three standard diameters:

--- Results for Diameter: 6.0 in (0.152 m) ---
Velocity: 8.61 m/s
Reynolds: 1312974.38 (dimensionless)
Total Pressure Drop: 971.36 Pa

--- Results for Diameter: 8.0 in (0.203 m) ---
Velocity: 4.84 m/s
Reynolds: 984730.79 (dimensionless)
Total Pressure Drop: 184.18 Pa

--- Results for Diameter: 10.0 in (0.254 m) ---
Velocity: 3.10 m/s
Reynolds: 787784.63 (dimensionless)
Total Pressure Drop: 51.52 Pa
⚠️ Warning: Final velocity 4.84 m/s outside recommended range (5.00-10.00 m/s) for Chlorine.

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 8.00 in  (0.203 m)
Inlet Flow: 0.157 m3/s
Outlet Flow: 0.157 m3/s
Total Pressure Drop: 0.18 kPa
Total Head Loss: 1.06 m
Total Power Required: 0.04 kW
Velocity: 4.843 m/s
Reynolds Number: 984731 (dimensionless)
Friction Factor: 0.1804 (dimensionless)
(.venv) PS P:\processpi> """


"""
Example 2 
Carbon dioxide is to be conveyed from the top of the stripper of ammonia plant to urea
plant. Calculate the pipe size required based on following data.
Flow rate of CCb = 1000 t/day
Total length of pipe = 800 m
Available pressure at inlet of pipe = 24 kPa g
Discharge pressure of CCX from pipe required = atmospheric
No. of 90° elbows in pipe line = 8
No. of butterfly valve = 1
No. of flow nozzle = 1
Temperature of gas = 60oC
Viscosity of CCb gas = 0.016 mPa' s or cP
"""

from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
fluid = Carbondioxide(temperature=Temperature(60, "C"))
print(fluid.density(),fluid.viscosity().to("cP"))

mass_flow = MassFlowRate(1000, "t/day")
pipe = Pipe(name="Main Pipe", length=Length(800, "m"), material="CS")
elbow = Fitting(fitting_type="standard_elbow_90_deg", quantity=8)
valve = Fitting(fitting_type="gate_valve", quantity=1)
nozzle = Fitting(fitting_type="flow_nozzle", quantity=1)
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbow, valve, nozzle],
    available_dp=Pressure(24, "kPa"),
)
model.run()
model.summary()

"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ ProcessPI Ready!
✅ Calculations module ready!
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

1.609882 kg/m3 0.019523 cP (dynamic)
✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 34.0 in (0.864 m)
   Calculated Pressure Drop: 8617.03 Pa (allowed: 24000.00 Pa)

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 34.00 in  (0.864 m)
Inlet Flow: 7.189 m3/s 
Outlet Flow: 7.189 m3/s 
Total Pressure Drop: 8.62 kPa
Total Head Loss: 545.81 m
Total Power Required: 88.50 kW
Velocity: 12.274 m/s
Reynolds Number: 874029 (dimensionless)
Friction Factor: 0.0767 (dimensionless)
(.venv) PS P:\processpi> 

"""

#Example 3
"""
Calculate the pipe size based on following data. Fluid flowing through pipe is carbon
monoxide. Discharge pressure of carbon monoxide required from the pipe is atmospheric.
Available pressure at inlet of pipe = 50 kPa g
Length of pipe = 4 km
Flow rate of CO = 1500 kg/h
Temperature of gas = 50° C
No. of gate valves in pipe line = 2
No. of 45° elbows = 3
Nos. of 90° elbows = 6
Viscosity of CO = 0.018 mPa • s or cP
"""

from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

fluid = CarbonMonoxide(temperature=Temperature(50, "C"))

mass_flow = MassFlowRate(1500, "kg/h")
length = Length(4, "km")
pipe = Pipe(name="Main Pipe", length=length, material="CS")
valves = Fitting(fitting_type="gate_valve", quantity=2)
elbows_45 = Fitting(fitting_type="standard_elbow_45_deg", quantity=3)
elbows_90 = Fitting(fitting_type="standard_elbow_90_deg", quantity=6)

model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbows_45, elbows_90, valves],
    available_dp=Pressure(50, "kPa"),
)
results = model.run()
model.summary()
print(results.total_pressure_drop.to("atm"))

"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ ProcessPI Ready!
✅ Calculations module ready!
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 12.0 in (0.305 m)
   Calculated Pressure Drop: 27683.14 Pa (allowed: 50000.00 Pa)
⚠️ Warning: Final velocity 5.41 m/s outside recommended range (8.00-15.00 m/s) for Carbon Monoxide.

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 12.00 in  (0.305 m)
Inlet Flow: 0.394 m3/s 
Outlet Flow: 0.394 m3/s 
Total Pressure Drop: 27.68 kPa
Total Head Loss: 2672.41 m
Total Power Required: 15.60 kW
Velocity: 5.406 m/s
Reynolds Number: 91262 (dimensionless)
Friction Factor: 0.1367 (dimensionless)
0.273211 atm
(.venv) PS P:\processpi> 

"""