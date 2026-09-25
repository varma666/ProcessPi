"""`BellDelawareHX` sizes an exchanger instead of raising NotImplementedError.

The class is exported from `processpi.equipment.heatexchangers`, but it used
to be a stub whose `design()` raised `NotImplementedError`, while the working
Bell-Delaware path was `ShellAndTubeHX(method="bell_delaware")` and
`HeatExchangerEngine(method="bell_delaware")`. It is now that same exchanger
with the method fixed, so all three routes must give the same design.

The case is the one in `test_shell_tube_kern_bell_workflow.py`: water 360 to
330 K against water from 300 K, 2 kg/s each, cp 4200 J/kg.K, so the duty is
m cp dT = 2 x 4200 x 30 = 252 kW.
"""

import contextlib
import io

import pytest

from processpi.components import Water
from processpi.equipment.heatexchangers import (
    BellDelawareHX,
    HeatExchangerEngine,
    ShellAndTubeHX,
)
from processpi.streams.material import MaterialStream
from processpi.units import MassFlowRate, Pressure, SpecificHeat, Temperature

CP = 4200.0
M_DOT = 2.0


def _stream(name, temp_k, m_dot=None):
    kwargs = {
        "component": Water(),
        "temperature": Temperature(temp_k, "K"),
        "pressure": Pressure(2, "bar"),
        "specific_heat": SpecificHeat(CP, "J/kgK"),
    }
    if m_dot is not None:
        kwargs["mass_flow"] = MassFlowRate(m_dot, "kg/s")
    return MaterialStream(name=name, **kwargs)


def _streams():
    return {
        "hot_in": _stream("hot", 360, M_DOT),
        "hot_out": _stream("hot_out", 330),
        "cold_in": _stream("cold", 300, M_DOT),
    }


def _quiet(fn):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn()


def _normalise(value):
    """Unit objects compare by identity inside dicts; compare their numbers."""
    if hasattr(value, "value") and hasattr(value, "units"):
        return (type(value).__name__, float(value.value), str(value.units))
    if isinstance(value, dict):
        return {key: _normalise(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalise(item) for item in value]
    return value


def _class_design(cls, **kwargs):
    hx = cls(**_streams(), hx_type="shell_and_tube", mode="design", **kwargs)
    return _quiet(hx.design)


def _engine_design():
    engine = HeatExchangerEngine(method="bell_delaware").fit(
        **_streams(), hx_type="shell_and_tube", mode="design",
    )
    return _quiet(engine.run).data


def test_bell_delaware_hx_designs_with_the_bell_method():
    out = _class_design(BellDelawareHX)

    assert out["method"] == "bell_delaware"
    assert set(out["bell_factors"]) == {"Fn", "Fw", "Fb", "Fl", "Fs"}
    assert float(getattr(out["Q"], "value", out["Q"])) == pytest.approx(M_DOT * CP * 30.0)


def test_bell_delaware_hx_matches_the_engine_route():
    assert _normalise(_class_design(BellDelawareHX)) == _normalise(_engine_design())


def test_bell_delaware_hx_matches_shell_and_tube_with_bell_method():
    bell = _class_design(BellDelawareHX)
    shell_and_tube = _class_design(ShellAndTubeHX, method="bell_delaware")
    assert _normalise(bell) == _normalise(shell_and_tube)


def test_bell_delaware_hx_is_a_shell_and_tube_exchanger():
    hx = BellDelawareHX(**_streams())
    assert isinstance(hx, ShellAndTubeHX)
    assert hx.method == "bell_delaware"


@pytest.mark.parametrize("method", ["bell_delaware", "Bell_Delaware"])
def test_bell_delaware_hx_accepts_its_own_method(method):
    assert BellDelawareHX(**_streams(), method=method).method == "bell_delaware"


@pytest.mark.parametrize("method", ["kern", "ntu"])
def test_bell_delaware_hx_refuses_another_method(method):
    with pytest.raises(ValueError, match="BellDelawareHX always uses method='bell_delaware'"):
        BellDelawareHX(**_streams(), method=method)
