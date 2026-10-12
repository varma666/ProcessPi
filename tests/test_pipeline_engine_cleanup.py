"""
PipelineEngine clean-up: no shadowed method definitions, node elevations given
as a Length, and a warning (not a print) for a fitting with no K-factor.

A node elevation given as Length(5, "m") used to raise TypeError inside a bare
`except Exception: pass`, so the pipe's static head was silently zero.
"""

import ast
import inspect
import warnings

import pytest

from processpi.components import Water
from processpi.pipelines import engine as engine_module
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, Velocity, VolumetricFlowRate

G = 9.80665


def _engine():
    return PipelineEngine().fit(fluid=Water(), flowrate=VolumetricFlowRate(0.01, "m3/s"))


def _pipe_between(elev_a, elev_b):
    net = PipelineNetwork("Lift")
    net.add_node("A", elevation=elev_a)
    net.add_node("B", elevation=elev_b)
    pipe = Pipe("A-B", nominal_diameter=Diameter(4, "in"), schedule="S40", length=Length(50, "m"))
    net.add_edge(pipe, "A", "B")
    return pipe


def _elevation_dp(elev_a, elev_b):
    eng = _engine()
    calc = eng._pipe_calculation(_pipe_between(elev_a, elev_b), VolumetricFlowRate(0.01, "m3/s"))
    return calc["elevation_dp_pa"], eng._get_density().value


def test_no_method_is_defined_twice():
    """Python keeps only the last of two same-named methods; the first is dead code."""
    tree = ast.parse(inspect.getsource(engine_module))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PipelineEngine")
    names = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
    assert sorted({n for n in names if names.count(n) > 1}) == []


@pytest.mark.parametrize("name", [
    "_hardy_cross", "_matrix_solver", "_compute_series", "_resolve_parallel_flows",
    "_fitting_dp_pa", "_maybe_velocity", "_internal_diameter_m",
])
def test_unused_solvers_are_gone(name):
    assert not hasattr(PipelineEngine, name)


def test_numeric_elevation_gives_static_head():
    """dp_static = rho g dz for a 5 m rise."""
    dp, rho = _elevation_dp(0, 5)
    assert dp == pytest.approx(rho * G * 5.0, rel=1e-12)


def test_length_elevation_matches_numeric():
    dp_len, _ = _elevation_dp(Length(0, "m"), Length(500, "cm"))
    dp_num, _ = _elevation_dp(0, 5)
    assert dp_len == pytest.approx(dp_num, rel=1e-12)
    assert dp_len > 0


def test_downhill_pipe_keeps_previous_result():
    """Pressure cannot be negative, so a 5 m drop gets no credit, as before.
    This pins the existing behaviour until the sign convention is decided."""
    dp, _ = _elevation_dp(5, 0)
    assert dp == 0.0


def test_pipe_without_nodes_has_no_static_head():
    eng = _engine()
    pipe = Pipe("Loose", nominal_diameter=Diameter(4, "in"), schedule="S40", length=Length(50, "m"))
    calc = eng._pipe_calculation(pipe, VolumetricFlowRate(0.01, "m3/s"))
    assert calc["elevation_dp_pa"] == 0.0


def test_bad_elevation_raises_instead_of_zero():
    with pytest.raises(TypeError, match="elevation"):
        _elevation_dp(0, "five metres")


def test_unknown_fitting_warns_and_adds_nothing(capsys):
    eng = _engine()
    d = Diameter(0.10226, "m")
    with pytest.warns(UserWarning, match="no_such_fitting"):
        dp = eng._minor_dp_pa(Fitting(fitting_type="no_such_fitting"), Velocity(1.2, "m/s"), 0.02, d)
    assert dp.value == 0.0
    assert "no_such_fitting" not in capsys.readouterr().out


def test_known_fitting_does_not_warn():
    eng = _engine()
    d = Diameter(0.10226, "m")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        dp = eng._minor_dp_pa(Fitting(fitting_type="gate_valve"), Velocity(1.2, "m/s"), 0.02, d)
    assert dp.value > 0
