from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.network import PipelineNetwork
from processpi.units import *
from processpi.components import Water

# -----------------------------
# Cooling Tower Network Parameters
# -----------------------------
fluid = Water(temperature=Temperature(30, "C"), pressure=Pressure(101325, "Pa"))

flow_rate_per_condenser_m3h = VolumetricFlowRate(50, "m3/h")
flow_rate_per_condenser_m3s = flow_rate_per_condenser_m3h.to("m3/s")
#print(flow_rate_per_condenser_m3s)
num_condensers = 8

total_flow_rate_m3s = flow_rate_per_condenser_m3s.value * num_condensers
#print(total_flow_rate_m3h)
total_flow_rate_m3s = VolumetricFlowRate(total_flow_rate_m3s)
branch_flow_m3s = flow_rate_per_condenser_m3s


# -----------------------------
# Build main network
# -----------------------------
network = PipelineNetwork.series("Cooling Tower Header")
network.add_node("Tower")
network.add_node("Header_Distribution")

# Main header pipe (auto-size)
header_pipe = Pipe(
    name="Main Header",
    length=Length(100, "m"),
    diameter=None,          # auto-size
    flow_rate=total_flow_rate_m3s,
    roughness=0.000045,
    schedule="STD"
)
network.add_edge(header_pipe, "Tower", "Header_Distribution")

# -----------------------------
# Build parallel branches
# -----------------------------
parallel_branches = []

for i in range(num_condensers):
    branch_net = PipelineNetwork.series(f"Branch-{i+1}")
    branch_net.add_node(f"Header_Distribution")
    branch_net.add_node(f"Condenser-{i+1}")

    branch_pipe = Pipe(
        name=f"Branch Pipe {i+1}",
        length=Length(30, "m"),
        diameter=Diameter(2,"in"),       # auto-size
        flow_rate=branch_flow_m3s,
        roughness=0.000045,
        schedule="STD"
    )

    # Set a non-zero initial flow to avoid Re=0 in solver
    branch_pipe.flow_rate = branch_flow_m3s

    branch_net.add_edge(branch_pipe, "Header_Distribution", f"Condenser-{i+1}")
    parallel_branches.append(branch_net)

# Combine parallel branches into one network
parallel_network = PipelineNetwork.parallel("Branch Distribution", *parallel_branches)
network.add_subnetwork(parallel_network)

# Initialize engine
engine = PipelineEngine()
engine.fit(network=network, flow_rate=total_flow_rate_m3s, fluid=fluid)

# Optional: ensure all pipes have initial flows
for branch in engine._normalize_branches(network):
    for pipe in branch:
        if pipe.flow_rate is None:
            pipe.flow_rate = VolumetricFlowRate(0.001, "m3/s")  # small non-zero guess

# Run solver
results = engine.run()

# Print summaries
print("\n--- Cooling Tower Network Results ---")
results.summary()
results.detailed_summary()