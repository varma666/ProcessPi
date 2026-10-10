# tests/test_engine_network.py
"""
PipelineEngine single-pipe and network results.

These tests were written against an earlier API (`run(requested=[...])`,
`engine.add_pipe(...)`, bare-number lengths) and failed on every run. The same
four checks now use the current fit/run interface, and each one compares the
reported value with a hand calculation instead of only its sign.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, VolumetricFlowRate

D_4IN_S40 = Diameter(102.26, "mm")   # 4 in schedule 40 bore


def _run(**specs):
    engine = PipelineEngine().fit(fluid=Water(), **specs)
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.run().results


def _water():
    water = Water()
    return water.density().value, water.viscosity().value


def test_single_pipe_reynolds():
    """Re = rho v D / mu, with v = Q / (pi D^2 / 4); 0.01 m3/s in 4 in S40 is turbulent."""
    results = _run(flowrate=VolumetricFlowRate(0.01, "m3/s"), diameter=D_4IN_S40,
                   length=Length(50, "m"))
    rho, mu = _water()
    d = 0.10226
    v = 0.01 / (math.pi * d ** 2 / 4.0)
    re = results["summary"]["reynolds"]
    re = float(getattr(re, "value", re))
    assert results["summary"]["velocity"] == pytest.approx(v, rel=1e-9)
    assert re == pytest.approx(rho * v * d / mu, rel=1e-6)
    assert re > 2000


def test_pressure_drop_from_inputs():
    """Darcy-Weisbach with the reported friction factor: dp = f (L/D) rho v^2 / 2."""
    results = _run(flowrate=VolumetricFlowRate(0.005, "m3/s"), diameter=D_4IN_S40,
                   length=Length(100, "m"))
    rho, _ = _water()
    d = 0.10226
    v = 0.005 / (math.pi * d ** 2 / 4.0)
    f = results["summary"]["friction_factor"]
    f = float(getattr(f, "value", f))
    expected = f * (100.0 / d) * rho * v ** 2 / 2.0
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(expected, rel=1e-9)
    assert expected > 0


def test_network_two_pipes():
    """Two identical pipes in series: each carries the full flow, and the total is twice one."""
    p1 = Pipe("P1", nominal_diameter=Diameter(4, "in"), schedule="S40", length=Length(100, "m"))
    p2 = Pipe("P2", nominal_diameter=Diameter(4, "in"), schedule="S40", length=Length(100, "m"))
    results = _run(flowrate=VolumetricFlowRate(0.01, "m3/s"),
                   network=PipelineNetwork.series("Main", p1, p2))
    pipes = [c for c in results["components"] if c["type"] == "pipe"]
    assert [c["name"] for c in pipes] == ["P1", "P2"]
    for c in pipes:
        assert c["flow_m3s"] == pytest.approx(0.01, rel=1e-9)
        assert float(getattr(c["velocity"], "value", c["velocity"])) == pytest.approx(
            0.01 / (math.pi * 0.10226 ** 2 / 4.0), rel=1e-9)
    drops = [c["total_dp"].to("Pa").value for c in pipes]
    assert drops[0] == pytest.approx(drops[1], rel=1e-12)
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(sum(drops), rel=1e-9)


def test_dependency_auto_resolution():
    """With only flow, fluid and length, the engine sizes the pipe and resolves
    velocity and Re on the diameter it chose."""
    results = _run(flowrate=VolumetricFlowRate(0.002, "m3/s"), length=Length(20, "m"))
    summary = results["summary"]
    rho, mu = _water()
    d = summary["calculated_diameter_m"]
    v = summary["velocity"]
    re = float(getattr(summary["reynolds"], "value", summary["reynolds"]))
    assert d > 0
    assert v == pytest.approx(0.002 / (math.pi * d ** 2 / 4.0), rel=1e-6)
    assert re == pytest.approx(rho * v * d / mu, rel=1e-6)
