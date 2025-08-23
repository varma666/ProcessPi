# processpi/tests/test_network.py

from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting



def build_sample_network():
    # Main Network
    main_net = PipelineNetwork("Main Network")

    # Add nodes
    main_net.add_node("A", elevation=0)
    main_net.add_node("B", elevation=5)
    main_net.add_node("C", elevation=10)
    main_net.add_node("D", elevation=8)

    # Add pipes in series
    main_net.add_pipe(Pipe(nominal_diameter=100, length=50, material="Steel"), "A", "B")
    main_net.add_pipe(Pipe(nominal_diameter=150, length=75, material="PVC"), "B", "C")

    # Add fitting
    main_net.add_fitting(Fitting(fitting_type="Elbow", K=0.3), "B")

    # Create a parallel subnetwork between C and D
    parallel_net = PipelineNetwork("Parallel Branch")
    parallel_net.add_node("C")
    parallel_net.add_node("D")

    parallel_net.add_pipe(Pipe(nominal_diameter=80, length=40, material="Copper"), "C", "D")
    parallel_net.add_pipe(Pipe(nominal_diameter=120, length=30, material="Steel"), "C", "D")

    # Add the subnetwork as parallel
    main_net.add_subnetwork(parallel_net, connection_type="parallel")

    return main_net


def test_pipeline_network_nodes():
    net = build_sample_network()
    assert "A" in net.nodes
    assert "B" in net.nodes
    assert "C" in net.nodes
    assert "D" in net.nodes


def test_pipeline_network_pipes():
    net = build_sample_network()
    # Expect at least 2 main pipes (A-B, B-C)
    assert any("A" in conn and "B" in conn for conn in net.connections)
    assert any("B" in conn and "C" in conn for conn in net.connections)


def test_pipeline_network_parallel():
    net = build_sample_network()
    # Ensure a parallel subnetwork exists
    assert any(isinstance(c, PipelineNetwork) and c.name == "Parallel Branch"
               for c in net.subnetworks)


def test_pipeline_network_schematic_output():
    net = build_sample_network()
    schematic = net.schematic()
    # Check schematic contains expected labels
    assert "A" in schematic
    assert "B" in schematic
    assert "Parallel Branch" in schematic




if __name__ == "__main__":
    # Run manual debug mode
    net = build_sample_network()
    print("=== Description ===")
    print(net.describe())
    print("\n=== Schematic ===")
    print(net.schematic())
