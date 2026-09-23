"""HeatExchangerEngine picks the exchanger class and forwards the specs.

These replace the dispatch tests for `mechanical.run_mechanical_design`,
whose sources were removed in a98bd35 when the exchangers moved to the
engine. The same three things are checked against the engine: an explicit
type reaches its class, the keywords reach it too, and an unknown type is
refused with a clear message.
"""

import pytest

from processpi.components import Water
from processpi.equipment.heatexchangers import (
    CondenserHX,
    DoublePipeHX,
    HeatExchangerEngine,
    ShellAndTubeHX,
)
from processpi.streams import MaterialStream
from processpi.units import MassFlowRate, Temperature


def _stream(name, temp_c, m_dot=None, phase=None):
    kwargs = {"component": Water(), "temperature": Temperature(temp_c, "C")}
    if m_dot is not None:
        kwargs["mass_flow"] = MassFlowRate(m_dot, "kg/s")
    if phase is not None:
        kwargs["phase"] = phase
    return MaterialStream(name, **kwargs)


def _capture_design(monkeypatch, cls):
    """Replace `cls.design` so a run records the exchanger it was given."""
    called = {}

    def fake_design(self):
        called["hx"] = self
        return {"kind": cls.__name__}

    monkeypatch.setattr(cls, "design", fake_design)
    return called


def test_explicit_double_pipe_reaches_double_pipe_class(monkeypatch):
    called = _capture_design(monkeypatch, DoublePipeHX)

    engine = HeatExchangerEngine(method="kern").fit(
        hot_in=_stream("hot", 90, 5.0), cold_in=_stream("cold", 20, 5.0),
        hx_type="double_pipe", mode="design", test_arg=1,
    )
    out = engine.run()

    assert out.data == {"kind": "DoublePipeHX"}
    assert type(called["hx"]) is DoublePipeHX
    assert called["hx"].specs["test_arg"] == 1


def test_explicit_shell_and_tube_reaches_shell_and_tube_class(monkeypatch):
    called = _capture_design(monkeypatch, ShellAndTubeHX)

    engine = HeatExchangerEngine(method="kern").fit(
        hot_in=_stream("hot", 90, 0.5), cold_in=_stream("cold", 20, 0.5),
        hx_type="shell_and_tube", mode="design", rating=True,
    )
    out = engine.run()

    assert out.data == {"kind": "ShellAndTubeHX"}
    assert type(called["hx"]) is ShellAndTubeHX
    assert called["hx"].method == "kern"
    assert called["hx"].specs["rating"] is True


def test_bell_delaware_method_runs_shell_and_tube_with_that_method(monkeypatch):
    called = _capture_design(monkeypatch, ShellAndTubeHX)

    HeatExchangerEngine(method="bell_delaware").fit(
        hot_in=_stream("hot", 90, 5.0), cold_in=_stream("cold", 20, 5.0),
        hx_type="shell_and_tube", mode="design",
    ).run()

    assert type(called["hx"]) is ShellAndTubeHX
    assert called["hx"].method == "bell_delaware"


@pytest.mark.parametrize(
    "hot,cold,hot_out,expected",
    [
        # Vapor in, liquid out on the hot side: a condenser.
        (_stream("hot", 110, 2.0, "vapor"), _stream("cold", 20, 5.0),
         _stream("hot_out", 100, phase="liquid"), CondenserHX),
        # Both flows at or under 1 kg/s: a double pipe.
        (_stream("hot", 90, 0.8), _stream("cold", 20, 1.0), None, DoublePipeHX),
        # Otherwise shell and tube.
        (_stream("hot", 90, 5.0), _stream("cold", 20, 5.0), None, ShellAndTubeHX),
    ],
)
def test_type_is_inferred_when_not_given(monkeypatch, hot, cold, hot_out, expected):
    called = _capture_design(monkeypatch, expected)

    HeatExchangerEngine(method="kern").fit(
        hot_in=hot, cold_in=cold, hot_out=hot_out, mode="design",
    ).run()

    assert type(called["hx"]) is expected


def test_hx_type_is_case_insensitive(monkeypatch):
    called = _capture_design(monkeypatch, DoublePipeHX)

    HeatExchangerEngine(method="kern").fit(
        hot_in=_stream("hot", 90, 5.0), cold_in=_stream("cold", 20, 5.0),
        hx_type="Double_Pipe", mode="design",
    ).run()

    assert type(called["hx"]) is DoublePipeHX


def test_unknown_type_is_rejected_with_the_valid_types():
    """It used to surface as a bare KeyError from the class map in run()."""
    engine = HeatExchangerEngine(method="kern")

    with pytest.raises(ValueError) as excinfo:
        engine.fit(hot_in=_stream("hot", 90, 5.0), cold_in=_stream("cold", 20, 5.0),
                   hx_type="Unknown")

    message = str(excinfo.value)
    assert "Unknown hx_type 'Unknown'" in message
    for known in ("shell_and_tube", "double_pipe", "condenser", "reboiler", "evaporator"):
        assert known in message
