# Chilled Water Loop with Branches & AHUs

**Problem**

Design and simulate a chilled water loop with:  

- Central pump and expansion tank  
- Main distribution header  
- 5 branch lines, each feeding 5 AHUs (Air Handling Units)  
- Return headers combining flow back to the tank  
- Optional chiller and expansion vessel  

Demonstrates handling **large network topologies**, fixed diameters, and multiple equipment elements.

## Code

```python
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
# Tank → Pump
net.add_edge(Pipe("TankPipe", length=5), "Tank", "Pump_In")
net.add_edge(pump, "Pump_In", "Pump_Out")

# Pump → Main header
net.add_edge(Pipe("MainPipe", length=15), "Pump_Out", "Main_In")
net.add_edge(Pipe("MainPipe_Out", length=5), "Main_In", "Main_Out")

# Branch inlets
for b in range(1, 6):
    net.add_edge(Pipe(f"MainToBranch_{b}", length=3), "Main_Out", f"Branch_{b}_In")

# ---------------- AHU pipes (fixed diameters) ----------------
ahu_diameters = [Diameter(3, "in"), Diameter(4, "in"), Diameter(4, "in"),
                 Diameter(5, "in"), Diameter(6, "in")]
ahu_flows = [VolumetricFlowRate(8, "m3/h"), VolumetricFlowRate(10, "m3/h"),
             VolumetricFlowRate(10, "m3/h"), VolumetricFlowRate(12, "m3/h"),
             VolumetricFlowRate(15, "m3/h")]

for b in range(1, 6):
    for a in range(1, 6):
        dia = ahu_diameters[(a - 1) % len(ahu_diameters)]
        in_node = f"Branch_{b}_In" if a == 1 else f"AHU_{b}_{a-1}_EqOut"
        pipe_out = f"AHU_{b}_{a}_PipeOut"
        eq_out = f"AHU_{b}_{a}_EqOut"

        # Pipe
        net.add_edge(Pipe(f"AHUPipe_{b}_{a}", nominal_diameter=dia, length=5), in_node, pipe_out)

        # AHU equipment
        pd = 0.05 + 0.01 * (ahu_flows[(a - 1) % len(ahu_flows)].to("m3/h").value / 10)
        net.add_edge(Equipment(f"AHU_{b}_{a}", pressure_drop=pd), pipe_out, eq_out)

# Branch returns
for b in range(1, 6):
    last_ahu_out = f"AHU_{b}_5_EqOut"
    net.add_edge(Pipe(f"BranchReturnPipe_{b}", length=5), last_ahu_out, f"Return_{b}")

# Returns → Tank
for b in range(1, 6):
    net.add_edge(Pipe(f"ReturnPipe_{b}", length=10), f"Return_{b}", "Return_Tank")

# Expansion vessel & chiller
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
```

## Output
```py
# Summary
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

# Detailed Summary

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

```