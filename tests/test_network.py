# tests/test_network.py
"""
PipelineNetwork structure: nodes, pipes on edges, a parallel subnetwork and
the text schematic.

These tests were written against an earlier API (`add_pipe`, `connections`,
`subnetworks`, `add_subnetwork(..., connection_type=...)`, bare-number
diameters, `Fitting(K=...)`) and failed on every run. The same sample network
is built with the current one (`add_edge`, `elements`, a subnetwork created
with `connection_type="parallel"`).
"""

from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length


def build_sample_network():
    main_net = PipelineNetwork("Main Network")

    main_net.add_node("A", elevation=0)
    main_net.add_node("B", elevation=5)
    main_net.add_node("C", elevation=10)
    main_net.add_node("D", elevation=8)

    # Pipes in series
    main_net.add_edge(Pipe("A-B", nominal_diameter=Diameter(4, "in"), length=Length(50, "m"),
                           material="CS"), "A", "B")
    main_net.add_edge(Pipe("B-C", nominal_diameter=Diameter(6, "in"), length=Length(75, "m"),
                           material="PVC"), "B", "C")

    # Fitting at B
    main_net.add_fitting(Fitting(fitting_type="standard_elbow_90_deg"), "B")

    # Parallel subnetwork between C and D
    parallel_net = PipelineNetwork("Parallel Branch", connection_type="parallel")
    parallel_net.add_node("C")
    parallel_net.add_node("D")
    parallel_net.add_edge(Pipe("C-D-1", nominal_diameter=Diameter(3, "in"), length=Length(40, "m"),
                               material="Copper"), "C", "D")
    parallel_net.add_edge(Pipe("C-D-2", nominal_diameter=Diameter(5, "in"), length=Length(30, "m"),
                               material="CS"), "C", "D")

    main_net.add_subnetwork(parallel_net)
    return main_net


def _pipes(net):
    return [e for e in net.elements if isinstance(e, Pipe)]


def test_pipeline_network_nodes():
    net = build_sample_network()
    assert set(net.nodes) == {"A", "B", "C", "D"}
    assert net.nodes["C"].elevation == 10


def test_pipeline_network_pipes():
    net = build_sample_network()
    ends = {(p.start_node.name, p.end_node.name) for p in _pipes(net)}
    assert ("A", "B") in ends
    assert ("B", "C") in ends
    # The fitting sits on node B.
    fittings = [e for e in net.elements if isinstance(e, Fitting)]
    assert [f.node.name for f in fittings] == ["B"]


def test_pipeline_network_parallel():
    net = build_sample_network()
    subnets = [e for e in net.elements if isinstance(e, PipelineNetwork)]
    assert [s.name for s in subnets] == ["Parallel Branch"]
    assert subnets[0].connection_type == "parallel"
    assert len(_pipes(subnets[0])) == 2


def test_pipeline_network_schematic_output():
    net = build_sample_network()
    schematic = net.schematic()
    for label in ("A-B", "B-C", "Parallel Branch", "C-D-1", "C-D-2"):
        assert label in schematic


if __name__ == "__main__":
    net = build_sample_network()
    print("=== Description ===")
    print(net.describe())
    print("\n=== Schematic ===")
    print(net.schematic())
