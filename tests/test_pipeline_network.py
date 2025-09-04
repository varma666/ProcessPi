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
results.detailed_summary()
""" 
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

17.685884 kg/m3
✅ Found optimal diameter based on recommended velocity.
   Selected Diameter: 8.0 in 
   Calculated Pressure Drop: 15.43 Pa
⚠️ Warning: Final velocity 4.87 m/s outside recommended range (5.00-10.00 m/s) for Chlorine.

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 8 in 
Inlet Flow: 0.157 m3/s 
Outlet Flow: 0.157 m3/s
Total Pressure Drop: 0.02 kPa
Total Head Loss: 0.09 m
Total Power Required: 0.00 kW
Velocity: 4.867 m/s
Reynolds Number: 987160 (dimensionless)
Friction Factor: 0.0149 (dimensionless)

=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+------------+-------------------+------------+
| Name      | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+===========+========+=================+============+============+===================+============+
| Main Pipe | pipe   |           15.43 |       4.87 |     987160 |            0.0149 | 8 in       |
+-----------+--------+-----------------+------------+------------+-------------------+------------+
(.venv) PS P:\processpi>  """


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

"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

1.609882 kg/m3 0.019523 cP (dynamic)
✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 22.0 in (0.559 m)
   Calculated Pressure Drop: 18414.26 Pa (allowed: 24000.00 Pa)
⚠️ Warning: Final velocity 31.41 m/s outside recommended range (8.00-15.00 m/s) for Carbon Dioxide.

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 22 in 
Inlet Flow: 7.189 m3/s 
Outlet Flow: 7.189 m3/s
Total Pressure Drop: 18.41 kPa
Total Head Loss: 1166.38 m
Total Power Required: 189.12 kW
Velocity: 31.415 m/s
Reynolds Number: 1398318 (dimensionless)
Friction Factor: 0.0128 (dimensionless)

=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+-------------+-------------------+------------+
| Name      | Type   |   Pressure Drop |   Velocity |    Reynolds |   Friction Factor | Diameter   |
+===========+========+=================+============+=============+===================+============+
| Main Pipe | pipe   |         18414.3 |      31.41 | 1.39832e+06 |            0.0128 | 22 in      |
+-----------+--------+-----------------+------------+-------------+-------------------+------------+
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
results.detailed_summary()

"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 8.0 in (0.203 m)
   Calculated Pressure Drop: 28658.34 Pa (allowed: 50000.00 Pa)

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 8 in 
Inlet Flow: 0.394 m3/s 
Outlet Flow: 0.394 m3/s 
Total Pressure Drop: 28.66 kPa
Total Head Loss: 2766.55 m
Total Power Required: 16.15 kW
Velocity: 12.224 m/s
Reynolds Number: 137230 (dimensionless)
Friction Factor: 0.0182 (dimensionless)
0.282836 atm

=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+------------+-------------------+------------+
| Name      | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+===========+========+=================+============+============+===================+============+
| Main Pipe | pipe   |         28658.3 |      12.22 |     137230 |            0.0182 | 8 in       |
+-----------+--------+-----------------+------------+------------+-------------------+------------+
(.venv) PS P:\processpi> 

"""
#Example 4
"""
100 000 kg/h of water is to be transferred from canal to reservoir by gravity. Maximum
height of water level above the discharge of pipe in reservoir will be 2 m. Difference
between minimum level of water in canal and maximum level of water in reservoir is
8 m.
Length of pipe = 3000 m
Equivalent length of pipe for fittings and valves = 200 m
Maximum temperature of water = 40oC
Density of water at 40oC = 993 kg/m3
Viscosity of water at 40oC = 0.67 mPa • s or cP
Surface roughness for carbon steel, s = 0.0457 mm
Surface roughness for concrete, e= 1.2 mm
Material of pipe is carbon steel. Determine the suitable pipe size. If material of pipe is
concrete will there be any change in pipe size required?
Solution:
Maximum allowable pressure drop in pipe = 8 - 2 = 6 m WC
APmax = 6 m WC = 58.84 kPa = 0.58 atm
"""

from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
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

"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 10.0 in (0.254 m)
   Calculated Pressure Drop: 41071.98 Pa (allowed: 58768.50 Pa)
⚠️ Warning: Final velocity 0.55 m/s outside recommended range (1.00-2.50 m/s) for Water.
✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 10.0 in (0.254 m)
   Calculated Pressure Drop: 31967.63 Pa (allowed: 58768.50 Pa)
⚠️ Warning: Final velocity 0.55 m/s outside recommended range (1.00-2.50 m/s) for Water.

=== Pipeline Result 1 (Main Water Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 10 in
Inlet Flow: 0.028 m3/s
Outlet Flow: 0.028 m3/s
Total Pressure Drop: 41.07 kPa
Total Head Loss: 4.24 m
Total Power Required: 1.65 kW
Velocity: 0.552 m/s
Reynolds Number: 207071 (dimensionless)
Friction Factor: 0.0217 (dimensionless)

=== Detailed Components for Result 1 (Main Water Pipe) ===
+-----------------+--------+-----------------+------------+------------+-------------------+------------+
| Name            | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+=================+========+=================+============+============+===================+============+
| Main Water Pipe | pipe   |           41072 |       0.55 |     207071 |            0.0217 | 10 in      |
+-----------------+--------+-----------------+------------+------------+-------------------+------------+

=== Pipeline Result 1 (Main Water Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 10 in
Inlet Flow: 0.028 m3/s
Outlet Flow: 0.028 m3/s
Total Pressure Drop: 31.97 kPa
Total Head Loss: 3.30 m
Total Power Required: 1.28 kW
Velocity: 0.552 m/s
Reynolds Number: 207071 (dimensionless)
Friction Factor: 0.0169 (dimensionless)

=== Detailed Components for Result 1 (Main Water Pipe) ===
+-----------------+--------+-----------------+------------+------------+-------------------+------------+
| Name            | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+=================+========+=================+============+============+===================+============+
| Main Water Pipe | pipe   |         31967.6 |       0.55 |     207071 |            0.0169 | 10 in      |
+-----------------+--------+-----------------+------------+------------+-------------------+------------+
(.venv) PS P:\processpi> 
"""

#Example 5

"""
An organic liquid is discharged at the rate of 5000 kg/h from a reactor to a storage tank
at 50oC as shown in Fig. 5.2. Reactor is under pressure at 600 kPa g. Density of the
organic liquid is 930 kg/m1 and viscosity is 0.91mPa • s or cP. Assume no flashing of the
organic liquid across the control valve.

Piping System Details:
Linear length of straight pipe = 50 m
No. of 90° elbows of standard radius = 6
No. of Tees = 2

Pressure drop in orifice meter = 40 kPa
No. of gate valves = 4
No. of globe valve = 1
No. of flow control valve = 1
Determine the pipe size. Assume it to be uniform throughout. Also find the residual
pressure drop that must be taken by the flow control valve.
"""
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.pumps import Pump
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork

fluid = OrganicLiquid(density=Density(930, "kg/m3"),viscosity=Viscosity(0.91, "cP"))


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
"""(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

✅ Found optimal diameter based on recommended velocity.
   Selected Diameter: 1.5 in 
   Calculated Pressure Drop: 31801.98 Pa
⚠️ Warning: Final velocity 1.14 m/s outside recommended range (1.80-2.00 m/s) for Organic Liquid.

=== Pipeline Result 1 (Main Organic Liquid Pipe) ===
Mode: Single_pipe
Calculated Pipe Diameter: 1.5 in 
Inlet Flow: 0.001 m3/s 
Outlet Flow: 0.001 m3/s 
Total Pressure Drop: 31.80 kPa
Total Head Loss: 3.49 m
Total Power Required: 0.07 kW
Velocity: 1.139 m/s
Reynolds Number: 47546 (dimensionless)
Friction Factor: 0.0245 (dimensionless)

=== Detailed Components for Result 1 (Main Organic Liquid Pipe) ===
+--------------------------+--------+-----------------+------------+------------+-------------------+------------+
| Name                     | Type   |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Diameter   |
+==========================+========+=================+============+============+===================+============+
| Main Organic Liquid Pipe | pipe   |           31802 |       1.14 |    47545.9 |            0.0245 | 1.5 in     |
+--------------------------+--------+-----------------+------------+------------+-------------------+------------+
(.venv) PS P:\processpi> 
"""

from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.pumps import Pump
from processpi.pipelines.vessel import Vessel
from processpi.pipelines.equipment import Equipment
from processpi.units import Diameter

# ---------------- Step 1: Create main network and nodes ----------------
main_net = PipelineNetwork("MainPlantLoop")

for node_name in ["A", "B", "C", "D", "E", "F", "G", "H"]:
    main_net.add_node(node_name)

# ---------------- Step 2: Create pipes, pumps, fittings, vessel, equipment ----------------
# Series pipes
pipe1 = Pipe(name="Pipe1", nominal_diameter=100, length=10)
pipe2 = Pipe(name="Pipe2", nominal_diameter=150, length=15)
pump1 = Pump(name="Pump1", pump_type="Centrifugal", head=20)

# Fittings with K-factor
elbow1 = Fitting(fitting_type="Elbow", diameter=Diameter(100, "mm"))
tee1 = Fitting(fitting_type="Tee", diameter=Diameter(150, "mm"))

# Parallel branch components
pipe_branch1 = Pipe(name="PipeBranch1", nominal_diameter=80, length=5)
vessel1 = Vessel(name="Separator1")

pipe_branch2 = Pipe(name="PipeBranch2", nominal_diameter=120, length=8)
equipment1 = Equipment(name="HeatExchanger", pressure_drop=0.5)

# Final pipes to outputs
pipe_EG = Pipe(name="PipeEG", nominal_diameter=100, length=12)
pipe_FH = Pipe(name="PipeFH", nominal_diameter=100, length=12)

# ---------------- Step 3: Connect series pipes ----------------
main_net.add_edge(pipe1, "A", "B")
main_net.add_edge(pipe2, "B", "C")
main_net.add_edge(pump1, "C", "D")

# Add fittings at nodes
main_net.add_fitting(elbow1, "B")
main_net.add_fitting(tee1, "C")

# ---------------- Step 4: Create parallel branches ----------------
branch1 = PipelineNetwork.series("Branch1").add(pipe_branch1, vessel1)
branch2 = PipelineNetwork.series("Branch2").add(pipe_branch2, equipment1)

# Connect parallel branches to D
main_net.add_edge(pipe_branch1, "D", "E")
main_net.add_edge(pipe_branch2, "D", "F")

# Add subnetwork branches
main_net.add_subnetwork(branch1)
main_net.add_subnetwork(branch2)

# ---------------- Step 5: Connect final pipes ----------------
main_net.add_edge(pipe_EG, "E", "G")
main_net.add_edge(pipe_FH, "F", "H")

# ---------------- Step 6: Validate ----------------
try:
    main_net.validate()
    print("Network is valid ✅\n")
except ValueError as e:
    print(e)

# ---------------- Step 7: Describe ----------------
print("--- Network Description ---")
print(main_net.describe())

# ---------------- Step 8: ASCII schematic ----------------
print("\n--- ASCII Schematic ---")
print(main_net.schematic())

# ---------------- Step 9: Visualize network ----------------
main_net.visualize_network(compact=True)

"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

Network validation failed:
Fitting 'Elbow' has no 'K' or 'L/D' data in standards.
Fitting 'Tee' has no 'K' or 'L/D' data in standards.
--- Network Description ---
Network: MainPlantLoop (connection: series)
  Nodes:
    Node(name='A', elevation=0.0 m)
    Node(name='B', elevation=0.0 m)
    Node(name='C', elevation=0.0 m)
    Node(name='D', elevation=0.0 m)
    Node(name='E', elevation=0.0 m)
    Node(name='F', elevation=0.0 m)
    Node(name='G', elevation=0.0 m)
    Node(name='H', elevation=0.0 m)
  Elements:
    Pipe: 100 mm, L=10 m, from A → B
    Pipe: 150 mm, L=15 m, from B → C
    Pump: Centrifugal, from C → D
    Fitting: Elbow at B
    Fitting: Tee at C
    Pipe: 80 mm, L=5 m, from D → E
    Pipe: 120 mm, L=8 m, from D → F
  Network: Branch1 (connection: series)
    Elements:
      Pipe: 80 mm, L=5 m, from D → E
      Vessel: Separator1, In: , Out:
  Network: Branch2 (connection: series)
    Elements:
      Pipe: 120 mm, L=8 m, from D → F
      Equipment: HeatExchanger, In: , Out:
    Pipe: 100 mm, L=12 m, from E → G
    Pipe: 100 mm, L=12 m, from F → H


--- ASCII Schematic ---
MainPlantLoop [series]
  │ └─1. Pipe1
  │ └─2. Pipe2
  │ └─3. Pump1
  │ └─4. Fitting
  │ └─5. Fitting
  │ └─6. PipeBranch1
  │ └─7. PipeBranch2
  │ └─Branch1 [series]
  │   │ └─1. PipeBranch1
  │     └─2. Separator1
  │ └─Branch2 [series]
  │   │ └─1. PipeBranch2
  │     └─2. HeatExchanger
  │ └─10. PipeEG
    └─11. PipeFH
(.venv) PS P:\processpi> 
"""


#Example...
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pumps import Pump
from processpi.pipelines.vessel import Vessel
from processpi.pipelines.equipment import Equipment
from processpi.units import *
from processpi.components import Water

# ---------------- Create Network ----------------
net = PipelineNetwork("Chilled Water Loop")

# ---------------- Nodes ----------------
net.add_node("Tank", elevation=0)
net.add_node("Pump_In", elevation=0)
net.add_node("Pump_Out", elevation=1)
net.add_node("Main_In", elevation=1)
net.add_node("Main_Out", elevation=1)

# Branch and AHU nodes
for b in range(1, 6):
    net.add_node(f"Branch_{b}_In", elevation=1)
    net.add_node(f"Branch_{b}_Out", elevation=1)
    for a in range(1, 6):
        net.add_node(f"AHU_{b}_{a}_PipeOut", elevation=1)
        net.add_node(f"AHU_{b}_{a}_EqOut", elevation=1)
    net.add_node(f"Return_{b}", elevation=0)

net.add_node("Return_Tank", elevation=0)

# ---------------- Components ----------------
pump = Pump(
    name="Pump1",
    pump_type="Centrifugal",
    inlet_pressure=Pressure(101325, "Pa"),
    outlet_pressure=Pressure(201325, "Pa")
)

vessel = Vessel("ExpansionTank")
chiller = Equipment("Chiller", pressure_drop=0.2)

# ---------------- Build Network ----------------
# Tank → Pump (auto diameter)
net.add_edge(Pipe("TankPipe", length=5), "Tank", "Pump_In")
net.add_edge(pump, "Pump_In", "Pump_Out")

# Pump → Main header (auto diameter)
net.add_edge(Pipe("MainPipe", length=15), "Pump_Out", "Main_In")
net.add_edge(Pipe("MainPipe_Out", length=5), "Main_In", "Main_Out")

# Branch inlets (auto diameter)
for b in range(1, 6):
    net.add_edge(Pipe(f"MainToBranch_{b}", length=3), "Main_Out", f"Branch_{b}_In")

# ---------------- AHU pipes (fixed diameters) ----------------
# Assume varying sizes and flow rates for diversity
ahu_diameters = [Diameter(3, "in"), Diameter(4, "in"), Diameter(4, "in"), Diameter(5, "in"), Diameter(6, "in")]  # meters
ahu_flows = [VolumetricFlowRate(8, "m3/h"), VolumetricFlowRate(10, "m3/h"), VolumetricFlowRate(10, "m3/h"), VolumetricFlowRate(12, "m3/h"), VolumetricFlowRate(15, "m3/h")]               # m3/h per AHU

for b in range(1, 6):
    for a in range(1, 6):
        dia = ahu_diameters[(a - 1) % len(ahu_diameters)]
        in_node = f"Branch_{b}_In" if a == 1 else f"AHU_{b}_{a-1}_EqOut"
        pipe_out = f"AHU_{b}_{a}_PipeOut"
        eq_out = f"AHU_{b}_{a}_EqOut"

        # Fixed AHU pipe diameter
        net.add_edge(Pipe(f"AHUPipe_{b}_{a}", nominal_diameter=dia, length=5), in_node, pipe_out)

        # AHU equipment pressure drop (varied slightly with flow)
        pd = 0.05 + 0.01 * (ahu_flows[(a - 1) % len(ahu_flows)].to('m3/h').value / 10)
        net.add_edge(Equipment(f"AHU_{b}_{a}", pressure_drop=pd), pipe_out, eq_out)

# Branch returns (auto diameter)
for b in range(1, 6):
    last_ahu_out = f"AHU_{b}_5_EqOut"
    net.add_edge(Pipe(f"BranchReturnPipe_{b}", length=5), last_ahu_out, f"Return_{b}")

# Returns → Tank (auto diameter)
for b in range(1, 6):
    net.add_edge(Pipe(f"ReturnPipe_{b}", length=10), f"Return_{b}", "Return_Tank")

# Optional expansion vessel and chiller (auto diameter)
net.add_edge(vessel, "Main_Out", "Return_Tank")
net.add_edge(chiller, "Return_Tank", "Pump_In")

# ---------------- Fluid & Flow ----------------
fluid = Water(temperature=Temperature(10, "C"), pressure=Pressure(101325, "Pa"))
flow_rate = VolumetricFlowRate(300, "m3/h")

# ---------------- Engine ----------------
model = PipelineEngine()
model.fit(fluid=fluid, flow_rate=flow_rate, network=net)
results = model.run()

# ---------------- Results ----------------
results.summary()
results.detailed_summary()


"""
(.venv) PS P:\processpi> & P:/processpi/.venv/Scripts/python.exe p:/processpi/test.py
✅ Calculations module ready!
✅ ProcessPI Ready!sPI ⠏
📦 ProcessPI v0.1.0 | Chemical & Process Engineering Tools Loaded!

🔄 Auto-sizing network pipe diameters...

=== Pipeline Result 1 (N/A) ===
Mode: Network
Calculated Pipe Diameter: 10 in 
Inlet Flow: 0.000 m3/s 
Outlet Flow: 0.000 m3/s 
Total Pressure Drop: 0.00 kPa
Total Head Loss: 0.00 m
Total Power Required: 0.00 kW
Velocity: 0.000 m/s
Reynolds Number: 0 (dimensionless)
Friction Factor: 0.0000 (dimensionless)

=== Detailed Components for Result 1 (N/A) ===
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| Name               | Type   |   Pressure Drop |   Velocity |        Reynolds |   Friction Factor | Diameter   |
+====================+========+=================+============+=================+===================+============+
| TankPipe           | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainPipe           | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainPipe_Out       | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainToBranch_1     | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainToBranch_2     | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainToBranch_3     | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainToBranch_4     | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| MainToBranch_5     | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_1_1        | Pipe   |               0 |      17.48 |      1.0459e+06 |            0.0177 | 3 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_1_2        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_1_3        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_1_4        | Pipe   |               0 |       6.47 | 636031          |            0.0164 | 5 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_1_5        | Pipe   |               0 |       4.47 | 528719          |            0.0161 | 6 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_2_1        | Pipe   |               0 |      17.48 |      1.0459e+06 |            0.0177 | 3 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_2_2        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_2_3        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_2_4        | Pipe   |               0 |       6.47 | 636031          |            0.0164 | 5 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_2_5        | Pipe   |               0 |       4.47 | 528719          |            0.0161 | 6 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_3_1        | Pipe   |               0 |      17.48 |      1.0459e+06 |            0.0177 | 3 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_3_2        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_3_3        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_3_4        | Pipe   |               0 |       6.47 | 636031          |            0.0164 | 5 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_3_5        | Pipe   |               0 |       4.47 | 528719          |            0.0161 | 6 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_4_1        | Pipe   |               0 |      17.48 |      1.0459e+06 |            0.0177 | 3 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_4_2        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_4_3        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_4_4        | Pipe   |               0 |       6.47 | 636031          |            0.0164 | 5 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_4_5        | Pipe   |               0 |       4.47 | 528719          |            0.0161 | 6 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_5_1        | Pipe   |               0 |      17.48 |      1.0459e+06 |            0.0177 | 3 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_5_2        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_5_3        | Pipe   |               0 |      10.14 | 796438          |            0.0169 | 4 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_5_4        | Pipe   |               0 |       6.47 | 636031          |            0.0164 | 5 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| AHUPipe_5_5        | Pipe   |               0 |       4.47 | 528719          |            0.0161 | 6 in       |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| BranchReturnPipe_1 | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| BranchReturnPipe_2 | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| BranchReturnPipe_3 | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| BranchReturnPipe_4 | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| BranchReturnPipe_5 | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| ReturnPipe_1       | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| ReturnPipe_2       | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| ReturnPipe_3       | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| ReturnPipe_4       | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
| ReturnPipe_5       | Pipe   |               0 |       1.64 | 320770          |            0.0159 | 10 in      |
+--------------------+--------+-----------------+------------+-----------------+-------------------+------------+
"""