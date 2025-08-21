from processpi.components import Water
fluid = Water()
from processpi.units import VolumetricFlowRate
flowrate = VolumetricFlowRate(10, "m3/h")
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.fittings import Fitting
from processpi.units import *
main_net = PipelineNetwork("Main Network")

        # Add nodes
main_net.add_node("A", elevation=0)
main_net.add_node("B", elevation=5)
main_net.add_node("C", elevation=10)
main_net.add_node("D", elevation=8)

        # Add pipes in series
main_net.add_pipe(Pipe(nominal_diameter=Diameter(4,"in"), length=50, schedule="40",material="CS"), "A", "B")
main_net.add_pipe(Pipe(nominal_diameter=Diameter(6,"in"), length=75, schedule="40",material="CS"), "B", "C")

        # Add fitting
main_net.add_fitting(Fitting(fitting_type="elbow_90_standard",diameter=Diameter(6,"in")), "B")

        # Create a parallel subnetwork between C and D
parallel_net = PipelineNetwork("Parallel Branch")
parallel_net.add_node("C")
parallel_net.add_node("D")

parallel_net.add_pipe(Pipe(nominal_diameter=Diameter(80,"mm"), length=40, material="CS", schedule="40"), "C", "D")
parallel_net.add_pipe(Pipe(nominal_diameter=Diameter(120,"mm"), length=30, material="CS", schedule="40"), "C", "D")

        # Add the subnetwork as parallel
main_net.add_subnetwork(parallel_net, connection_type="parallel")
engine = PipelineEngine(
            flowrate=VolumetricFlowRate(0.01, "m3/s"),
            fluid=Water(),
            network=main_net,
        )
result = engine.run()
result.summary()
engine.summary()