import pytest
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.pumps import Pump
from processpi.pipelines.vessels import Vessel
from processpi.pipelines.equipment import Equipment
from processpi.pipelines.units import Diameter

# ---------- FIXTURES ----------
@pytest.fixture
def network():
    return PipelineNetwork()

@pytest.fixture
def sample_nodes():
    return {
        "tank": Vessel(name="CoolingTowerTank", volume=10.0),
        "pump": Pump(name="CirculationPump", head=20.0, flow_rate=200.0),
        "pipe1": Pipe(length=10.0, diameter=Diameter(200), roughness=0.045),
        "pipe2": Pipe(length=15.0, diameter=Diameter(150), roughness=0.045),
        "condenser": Equipment(name="Condenser", pressure_drop=0.5),
        "fitting": Fitting(fitting_type="elbow_90", diameter=Diameter(150))
    }

# ---------- TESTS ----------
def test_add_nodes_success(network, sample_nodes):
    """Test adding nodes successfully."""
    for name, node in sample_nodes.items():
        network.add_node(name, node)
    assert len(network.nodes) == len(sample_nodes)

def test_add_duplicate_node_raises(network, sample_nodes):
    """Test duplicate node addition raises ValueError."""
    network.add_node("tank", sample_nodes["tank"])
    with pytest.raises(ValueError, match="already exists"):
        network.add_node("tank", sample_nodes["tank"])

def test_add_edge_success(network, sample_nodes):
    """Test successful edge creation."""
    network.add_node("tank", sample_nodes["tank"])
    network.add_node("pump", sample_nodes["pump"])
    edge_data = {"pipe": sample_nodes["pipe1"]}
    network.add_edge("tank", "pump", edge_data=edge_data, connection_type="series")
    assert len(network.edges) == 1

def test_add_edge_invalid_node_raises(network, sample_nodes):
    """Edge creation fails if nodes are missing."""
    network.add_node("tank", sample_nodes["tank"])
    with pytest.raises(ValueError, match="must be added before connecting"):
        network.add_edge("tank", "pump", edge_data={"pipe": sample_nodes["pipe1"]})

def test_add_edge_invalid_connection_type_raises(network, sample_nodes):
    """Edge creation fails with invalid connection type."""
    network.add_node("tank", sample_nodes["tank"])
    network.add_node("pump", sample_nodes["pump"])
    with pytest.raises(ValueError, match="Invalid connection type"):
        network.add_edge("tank", "pump", connection_type="wrong_type")

def test_add_parallel_edge_missing_ref_raises(network, sample_nodes):
    """Parallel edge must have a reference edge."""
    network.add_node("tank", sample_nodes["tank"])
    network.add_node("pump", sample_nodes["pump"])
    with pytest.raises(ValueError, match="Reference edge.*required"):
        network.add_edge("tank", "pump", connection_type="parallel")

def test_to_dict(network, sample_nodes):
    """Ensure network dict export works."""
    network.add_node("tank", sample_nodes["tank"])
    network.add_node("pump", sample_nodes["pump"])
    network.add_edge("tank", "pump", edge_data={"pipe": sample_nodes["pipe1"]}, connection_type="series")
    result = network.to_dict()
    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1
