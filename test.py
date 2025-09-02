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
ahu_diameters = [0.08, 0.1, 0.1, 0.12, 0.15]  # meters
ahu_flows = [8, 10, 10, 12, 15]               # m3/h per AHU

for b in range(1, 6):
    for a in range(1, 6):
        dia = ahu_diameters[(a - 1) % len(ahu_diameters)]
        in_node = f"Branch_{b}_In" if a == 1 else f"AHU_{b}_{a-1}_EqOut"
        pipe_out = f"AHU_{b}_{a}_PipeOut"
        eq_out = f"AHU_{b}_{a}_EqOut"

        # Fixed AHU pipe diameter
        net.add_edge(Pipe(f"AHUPipe_{b}_{a}", nominal_diameter=dia, length=5), in_node, pipe_out)

        # AHU equipment pressure drop (varied slightly with flow)
        pd = 0.05 + 0.01 * (ahu_flows[(a - 1) % len(ahu_flows)] / 10)
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
