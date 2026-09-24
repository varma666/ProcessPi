"""HeatExchangerEngine says when it picked the exchanger type itself, and why.

With no hx_type and no phase change, the engine compares the larger of the two
inlet mass flows with a 1 kg/s limit: at or below it a double pipe, above it a
shell and tube. That switch used to happen in silence (1.00 kg/s gave a double
pipe, 1.01 kg/s a shell and tube). The limit is now a named class constant that
a spec can override, and the results record the choice.
"""

import pytest

from processpi.components import Water
from processpi.equipment.heatexchangers import (
    CondenserHX,
    DoublePipeHX,
    HeatExchangerEngine,
    ShellAndTubeHX,
)
from processpi.equipment.heatexchangers.engine import HeatExchangerResults
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


def _run(hot_m, cold_m, **specs):
    return HeatExchangerEngine(method="kern").fit(
        hot_in=_stream("hot", 90, hot_m), cold_in=_stream("cold", 20, cold_m),
        mode="design", **specs,
    ).run()


def test_threshold_is_a_named_class_constant_with_the_old_value():
    assert HeatExchangerEngine.DOUBLE_PIPE_MAX_MASS_FLOW_KG_S == 1.0


def test_at_the_threshold_double_pipe_is_chosen_and_recorded(monkeypatch):
    called = _capture_design(monkeypatch, DoublePipeHX)
    out = _run(0.4, 1.0)

    assert type(called["hx"]) is DoublePipeHX
    selection = out.data["hx_type_selection"]
    assert selection["auto_selected"] is True
    assert selection["hx_type"] == "double_pipe"
    assert selection["criterion"] == "max_stream_mass_flow"
    assert selection["max_stream_mass_flow_kg_s"] == pytest.approx(1.0)
    assert selection["hot_mass_flow_kg_s"] == pytest.approx(0.4)
    assert selection["cold_mass_flow_kg_s"] == pytest.approx(1.0)
    assert selection["double_pipe_max_mass_flow_kg_s"] == 1.0
    assert "1 kg/s <= double pipe limit 1 kg/s" in selection["reason"]


def test_just_above_the_threshold_shell_and_tube_is_chosen_and_recorded(monkeypatch):
    called = _capture_design(monkeypatch, ShellAndTubeHX)
    out = _run(1.01, 0.5)

    assert type(called["hx"]) is ShellAndTubeHX
    selection = out.data["hx_type_selection"]
    assert selection["hx_type"] == "shell_and_tube"
    assert selection["max_stream_mass_flow_kg_s"] == pytest.approx(1.01)
    assert "1.01 kg/s > double pipe limit 1 kg/s" in selection["reason"]


def test_explicit_hx_type_wins_and_is_not_annotated(monkeypatch):
    called = _capture_design(monkeypatch, DoublePipeHX)
    out = _run(5.0, 5.0, hx_type="double_pipe")

    assert type(called["hx"]) is DoublePipeHX
    assert "hx_type_selection" not in out.data


def test_threshold_can_be_overridden_by_a_spec(monkeypatch):
    called = _capture_design(monkeypatch, DoublePipeHX)
    out = _run(1.5, 1.5, double_pipe_max_mass_flow=2.0)

    assert type(called["hx"]) is DoublePipeHX
    assert out.data["hx_type_selection"]["double_pipe_max_mass_flow_kg_s"] == 2.0
    # An engine setting, not an exchanger spec.
    assert "double_pipe_max_mass_flow" not in called["hx"].specs


def test_threshold_spec_accepts_a_mass_flow_rate(monkeypatch):
    called = _capture_design(monkeypatch, ShellAndTubeHX)
    out = _run(1.5, 1.5, double_pipe_max_mass_flow=MassFlowRate(3600, "kg/h"))

    assert type(called["hx"]) is ShellAndTubeHX
    assert out.data["hx_type_selection"]["double_pipe_max_mass_flow_kg_s"] == pytest.approx(1.0)


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_non_positive_threshold_is_refused(bad):
    with pytest.raises(ValueError, match="double_pipe_max_mass_flow"):
        _run(0.5, 0.5, double_pipe_max_mass_flow=bad)


def test_phase_change_selection_is_recorded(monkeypatch):
    called = _capture_design(monkeypatch, CondenserHX)
    out = HeatExchangerEngine(method="kern").fit(
        hot_in=_stream("hot", 110, 2.0, "vapor"), cold_in=_stream("cold", 20, 5.0),
        hot_out=_stream("hot_out", 100, phase="liquid"), mode="design",
    ).run()

    assert type(called["hx"]) is CondenserHX
    selection = out.data["hx_type_selection"]
    assert selection["hx_type"] == "condenser"
    assert selection["criterion"] == "phase_change"


def test_summary_reports_an_automatic_selection():
    results = HeatExchangerResults({
        "hx_type": "double_pipe",
        "hx_type_selection": {"reason": "no hx_type given; larger inlet mass flow "
                                        "0.8 kg/s <= double pipe limit 1 kg/s"},
    })
    assert "Type Selection        : auto, no hx_type given" in results.summary()
    assert "Type Selection" not in HeatExchangerResults({"hx_type": "double_pipe"}).summary()
