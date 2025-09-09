# ProcessPI - Pipeline Examples

This document contains worked examples using the **ProcessPI** pipeline
engine and network module.

------------------------------------------------------------------------

## Example 1: Chlorine Gas Pipeline

Estimate the optimum pipe diameter for a flow of dry chlorine gas of 10
000 kg/h at 6 atm and 20°C through carbon steel pipe.

``` python
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
)
results = model.run()  # auto diameter sizing
results.summary()
results.detailed_summary()
```

**Output**

    17.685884 kg/m3
    ✅ Found optimal diameter based on recommended velocity.
       Selected Diameter: 8.0 in 
       Calculated Pressure Drop: 15.43 Pa
    ⚠️ Warning: Final velocity 4.87 m/s outside recommended range (5.00-10.00 m/s) for Chlorine.

------------------------------------------------------------------------

## Example 2: CO₂ Transfer Pipeline

Carbon dioxide is to be conveyed from the top of the stripper of ammonia
plant to urea plant.

``` python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

fluid = Carbondioxide(temperature=Temperature(60, "C"))
print(fluid.density(), fluid.viscosity().to("cP"))

mass_flow = MassFlowRate(1000, "t/day")
pipe = Pipe(name="Main Pipe", length=Length(800, "m"), material="CS")
elbow = Fitting(fitting_type="standard_elbow_90_deg", quantity=8)
valve = Fitting(fitting_type="gate_valve", quantity=1)
nozzle = Fitting(fitting_type="exit", quantity=1)

model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbow, valve, nozzle],
    available_dp=Pressure(24, "kPa")
)
results = model.run()
model.summary()
results.detailed_summary()
```

**Output**

    1.609882 kg/m3 0.019523 cP (dynamic)
    ✅ Found optimal diameter for available pressure drop.
       Selected Diameter: 22.0 in (0.559 m)
       Calculated Pressure Drop: 18414.26 Pa (allowed: 24000.00 Pa)
    ⚠️ Warning: Final velocity 31.41 m/s outside recommended range (8.00-15.00 m/s) for Carbon Dioxide.

------------------------------------------------------------------------

## Example 3: Carbon Monoxide Pipeline

``` python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

fluid = CarbonMonoxide(temperature=Temperature(50, "C"))

mass_flow = MassFlowRate(1500, "kg/h")
pipe = Pipe(name="Main Pipe", length=Length(4, "km"), material="CS")
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
results.detailed_summary()
```

**Output**

    ✅ Found optimal diameter for available pressure drop.
       Selected Diameter: 8.0 in (0.203 m)
       Calculated Pressure Drop: 28658.34 Pa (allowed: 50000.00 Pa)

------------------------------------------------------------------------

## Example 4: Water Transfer (Steel vs Concrete)

``` python
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe

fluid = Water(temperature=Temperature(40, "C"))
length = Length(3200, "m")
pipe = Pipe(name="Main Water Pipe", length=length, material="Concrete")
pipe2 = Pipe(name="Main Water Pipe", length=length, material="CS")
allowable_dp = Pressure(0.58, "atm")
flow_rate = MassFlowRate(100000, "kg/h")

model = PipelineEngine()
model.fit(fluid=fluid, pipe=pipe, mass_flow=flow_rate, available_dp=allowable_dp)

model2 = PipelineEngine()
model2.fit(fluid=fluid, pipe=pipe2, mass_flow=flow_rate, available_dp=allowable_dp)

results = model.run()
results2 = model2.run()

model.summary()
results.detailed_summary()
model2.summary()
results2.detailed_summary()
```

------------------------------------------------------------------------

## Example 5: Organic Liquid with Valves

``` python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

fluid = OrganicLiquid(density=Density(930, "kg/m3"), viscosity=Viscosity(0.91, "cP"))
mass_flow = MassFlowRate(5000, "kg/h")

pipe = Pipe(name="Main Organic Liquid Pipe", length=Length(50, "m"))
elbow = Fitting(fitting_type="standard_elbow_90_deg", quantity=6)
tees = Fitting(fitting_type="standard_tee_through_flow", quantity=2)
gate_valves = Fitting(fitting_type="gate_valve", quantity=2)
globe_valves = Fitting(fitting_type="globe_valve", quantity=2)
orifice = Fitting(fitting_type="sudden_contraction", quantity=1)

model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbow, tees, gate_valves, globe_valves, orifice],
)
results = model.run()
model.summary()
results.detailed_summary()
```

------------------------------------------------------------------------

## Example 6: Complex Network (Chilled Water Loop)

``` python
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pumps import Pump
from processpi.pipelines.vessel import Vessel
from processpi.pipelines.equipment import Equipment
from processpi.units import *
from processpi.components import Water

# Build network
net = PipelineNetwork("Chilled Water Loop")

# Nodes
net.add_node("Tank", elevation=0)
net.add_node("Pump_In", elevation=0)
net.add_node("Pump_Out", elevation=1)
net.add_node("Main_In", elevation=1)
net.add_node("Main_Out", elevation=1)
net.add_node("Return_Tank", elevation=0)

pump = Pump("Pump1", pump_type="Centrifugal", inlet_pressure=Pressure(101325, "Pa"), outlet_pressure=Pressure(201325, "Pa"))
vessel = Vessel("ExpansionTank")
chiller = Equipment("Chiller", pressure_drop=0.2)

# Tank → Pump
net.add_edge(Pipe("TankPipe", length=5), "Tank", "Pump_In")
net.add_edge(pump, "Pump_In", "Pump_Out")

# Pump → Main header
net.add_edge(Pipe("MainPipe", length=15), "Pump_Out", "Main_In")
net.add_edge(Pipe("MainPipe_Out", length=5), "Main_In", "Main_Out")

# Returns → Tank
net.add_edge(vessel, "Main_Out", "Return_Tank")
net.add_edge(chiller, "Return_Tank", "Pump_In")

fluid = Water(temperature=Temperature(10, "C"), pressure=Pressure(101325, "Pa"))
flow_rate = VolumetricFlowRate(300, "m3/h")

model = PipelineEngine()
model.fit(fluid=fluid, flow_rate=flow_rate, network=net)
results = model.run()

results.summary()
results.detailed_summary()
```

------------------------------------------------------------------------
