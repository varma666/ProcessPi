# tests/test_engine_network.py

import pytest
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
from processpi.engine import PipelineEngine


def test_simple_series_network():
    # Build network
    net = PipelineNetwork("Series Network")

    net.add_node("Pump_Suction", elevation=0.0)
    net.add_node("Pump_Discharge", elevation=1.0)
    net.add_node("Tank_Inlet", elevation=2.0)

    p1 = Pipe(nominal_diameter=100, schedule="40", material="CS", length=10.0)
    net.add_pipe(p1, "Pump_Suction", "Pump_Discharge")

    p2 = Pipe(nominal_diameter=100, schedule="40", material="CS", length=20.0)
    net.add_pipe(p2, "Pump_Discharge", "Tank_Inlet")

    # Run engine
    engine = PipelineEngine()
    engine.add_network(net)

    # Provide input: flowrate + fluid props
    results = engine.run(
        flowrate=0.05,        # m3/s
        density=1000,         # kg/m3
        viscosity=1e-3        # Pa·s
    )

    # Assertions
    assert "Series Network" in results
    assert "Pump_Suction->Pump_Discharge" in results["Series Network"]
    assert "Pump_Discharge->Tank_Inlet" in results["Series Network"]

    # Reynolds number should be positive
    for branch in results["Series Network"].values():
        assert branch["Re"] > 0


def test_parallel_network():
    # Build network
    net = PipelineNetwork("Parallel Network")

    net.add_node("Header", elevation=0.0)
    net.add_node("Branch1_Outlet", elevation=1.0)
    net.add_node("Branch2_Outlet", elevation=1.0)

    # Two parallel branches
    p1 = Pipe(nominal_diameter=50, schedule="40", material="CS", length=15.0)
    p2 = Pipe(nominal_diameter=50, schedule="40", material="CS", length=15.0)

    net.add_pipe(p1, "Header", "Branch1_Outlet")
    net.add_pipe(p2, "Header", "Branch2_Outlet")

    # Add network to engine
    engine = PipelineEngine()
    engine.add_network(net)

    # Run
    results = engine.run(
        flowrate=0.02,        # m3/s
        density=998,
        viscosity=1.1e-3
    )

    # Assertions
    assert "Parallel Network" in results
    assert len(results["Parallel Network"]) == 2

    for branch in results["Parallel Network"].values():
        assert branch["Re"] > 0
        assert branch["dp"] >= 0


def test_mixed_series_parallel_network():
    # Build network
    net = PipelineNetwork("Mixed Network")

    net.add_node("Pump_Suction", elevation=0.0)
    net.add_node("Pump_Discharge", elevation=1.0)
    net.add_node("Header", elevation=1.0)
    net.add_node("Branch1_Outlet", elevation=2.0)
    net.add_node("Branch2_Outlet", elevation=2.0)

    # Series before split
    p1 = Pipe(nominal_diameter=80, schedule="40", material="CS", length=12.0)
    net.add_pipe(p1, "Pump_Suction", "Pump_Discharge")

    p2 = Pipe(nominal_diameter=80, schedule="40", material="CS", length=8.0)
    net.add_pipe(p2, "Pump_Discharge", "Header")

    # Parallel branches
    p3 = Pipe(nominal_diameter=50, schedule="40", material="CS", length=10.0)
    p4 = Pipe(nominal_diameter=50, schedule="40", material="CS", length=10.0)

    net.add_pipe(p3, "Header", "Branch1_Outlet")
    net.add_pipe(p4, "Header", "Branch2_Outlet")

    # Add network to engine
    engine = PipelineEngine()
    engine.add_network(net)

    # Run
    results = engine.run(
        flowrate=0.04,
        density=1000,
        viscosity=1e-3
    )

    # Assertions
    assert "Mixed Network" in results
    assert len(results["Mixed Network"]) == 4
    for branch in results["Mixed Network"].values():
        assert branch["Re"] > 0
