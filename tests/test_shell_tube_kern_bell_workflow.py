"""Shell-and-tube design through HeatExchangerEngine, Kern and Bell-Delaware.

Rewritten from the tests for `mechanical.shell_tube.design_shelltube` and
the `ShellAndTube` wrapper, whose sources were removed in a98bd35. The same
case (water 360 to 330 K against water from 300 K, 2 kg/s each, cp 4200
J/kg.K) and the same checks: the design comes back as a structured result
with the duty, U, area and both pressure drops, the Bell-Delaware run
carries its correction factors, and convergence is reported as a bool.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
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


def _design(method):
    engine = HeatExchangerEngine(method=method).fit(
        hot_in=_stream("hot", 360, M_DOT),
        hot_out=_stream("hot_out", 330),
        cold_in=_stream("cold", 300, M_DOT),
        hx_type="shell_and_tube",
        mode="design",
    )
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.run().data


def _number(value):
    return float(getattr(value, "value", value))


@pytest.mark.parametrize("method", ["kern", "bell_delaware"])
def test_shell_tube_design_returns_structured_results(method):
    out = _design(method)

    assert out["hx_type"] == "shell_and_tube"
    assert out["method"] == method
    for key in ("Q", "U_calculated", "Area", "LMTD", "tube_dp", "shell_dp",
                "tube_count", "shell_diameter", "status"):
        assert key in out, key
    assert isinstance(out["converged"], bool)

    # The duty is the hot-side balance, m cp dT = 2 x 4200 x 30 = 252 kW.
    assert _number(out["Q"]) == pytest.approx(M_DOT * CP * 30.0)
    for key in ("U_calculated", "Area", "tube_dp", "shell_dp"):
        assert _number(out[key]) > 0, key


def test_bell_delaware_applies_its_correction_factors():
    out = _design("bell_delaware")

    factors = out["bell_factors"]
    assert set(factors) == {"Fn", "Fw", "Fb", "Fl", "Fs"}
    assert all(f > 0 for f in factors.values())
    # The shell coefficient is the ideal one times the five factors.
    assert _number(out["h_shell"]) == pytest.approx(
        _number(out["h_shell_ideal"]) * math.prod(factors.values())
    )


def test_bell_delaware_and_kern_share_the_duty_and_geometry():
    kern = _design("kern")
    bell = _design("bell_delaware")

    assert _number(bell["Q"]) == pytest.approx(_number(kern["Q"]))
    assert bell["tube_count"] == kern["tube_count"]
    assert "bell_factors" not in kern
