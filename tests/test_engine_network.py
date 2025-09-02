# tests/test_engine_network.py

import pytest
from processpi.pipelines.engine import PipelineEngine
from processpi.components import Water
from processpi.units import VolumetricFlowRate
from processpi.pipelines.engine import PipelineEngine
from processpi.components import Water
from processpi.units import *
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.fittings import Fitting


def test_single_pipe_reynolds():
    """Test Reynolds number calculation with direct inputs."""
    engine = PipelineEngine(
        flowrate=VolumetricFlowRate(0.01, "m3/s"),
        fluid=Water(),
        length=50.0,
    )

    results = engine.run(requested=["reynolds_number"])
    assert "reynolds_number" in results
    assert results["reynolds_number"] > 2000  # turbulent


def test_pressure_drop_from_inputs():
    """Test pressure drop calculation when pipe and flowrate given."""
    engine = PipelineEngine(
        flowrate=VolumetricFlowRate(0.005, "m3/s"),
        fluid=Water(),
        length=100.0,
    )

    results = engine.run(requested=["pressure_drop_Pa"])
    assert "pressure_drop_Pa" in results
    assert results["pressure_drop_Pa"] > 0


def test_network_two_pipes():
    """Test a network of two pipes connected sequentially."""
    engine = PipelineEngine(
        flowrate=VolumetricFlowRate(0.01, "m3/s"),
        fluid=Water(),
        length=200.0,
    )

    # Add two pipes in sequence
    engine.add_pipe(pipe_id="P1", length=100.0, material="CS", schedule="40")
    engine.add_pipe(pipe_id="P2", length=100.0, material="CS", schedule="40")

    results = engine.run(requested=["pressure_drop_Pa", "velocity_m_s"])
    assert "pressure_drop_Pa" in results
    assert results["pressure_drop_Pa"] > 0
    assert "velocity_m_s" in results
    assert results["velocity_m_s"] > 0


def test_dependency_auto_resolution():
    """If only flowrate and pipe are given, velocity and Re should be resolved automatically."""
    engine = PipelineEngine(
        flowrate=VolumetricFlowRate(0.002, "m3/s"),
        fluid=Water(),
        length=20.0,
    )

    engine.add_pipe(pipe_id="PX", length=20.0, material="CS", schedule="40")

    results = engine.run(requested=["reynolds_number", "velocity_m_s"])
    assert "velocity_m_s" in results
    assert results["velocity_m_s"] > 0
    assert "reynolds_number" in results
    assert results["reynolds_number"] > 0

if __name__ == "__main__":
    
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
    results = engine.run()
    results.summary()


