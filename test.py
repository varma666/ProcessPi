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
