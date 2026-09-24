"""Shell-and-tube thermal-hydraulic correlations (#86, item 3).

Each test pins one correlation against a calculation done by hand from the
same inputs, so a change to the formula, its constants or its inputs shows up
here and not only as a shifted design.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import (
    HeatTransferCoefficient,
    MassFlowRate,
    Pressure,
    Temperature,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _value(x):
    return float(getattr(x, "value", x))


def _benzene_cooler():
    """docs/examples benzene cooler: benzene 21 000 kg/h 90 to 30 C, water 60 500 kg/h from 15 C."""
    hot_in = MaterialStream("hot_in", component=Benzene(),
                            temperature=Temperature(90, "C"),
                            mass_flow=MassFlowRate(21000, "kg/h"))
    hot_out = MaterialStream("hot_out", component=Benzene(),
                             temperature=Temperature(30, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(15, "C"),
                             mass_flow=MassFlowRate(60500, "kg/h"))
    cold_out = MaterialStream("cold_out", component=Water())
    return dict(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out)


_SPECS = dict(U=HeatTransferCoefficient(575, "W/m2K"),
              shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"))


def _run(streams, method="kern", mode="design", **specs):
    engine = HeatExchangerEngine(method=method).fit(
        **streams, **dict(_SPECS, mode=mode, **specs)
    )
    return _quiet(engine.run).data


def _hx(streams, method="kern", **specs):
    return ShellAndTubeHX(method=method, **streams, **dict(_SPECS, **specs))


# ----------------------------------------------------------------------------
# Tube passes
# ----------------------------------------------------------------------------

def test_design_pressure_drop_uses_the_settled_tube_passes():
    """The velocity check moves the benzene cooler from 2 to 6 tube passes, and
    the reported velocity is the 6-pass velocity. The final tube-side pressure
    drop was still computed for 2 passes (a third of the friction length and of
    the return losses). It must be the pressure drop of the passes reported."""
    streams = _benzene_cooler()
    data = _run(streams, force_hot_in_tubes=True)
    assert data["tube_passes"] == 6
    assert data["shell_passes"] == 1

    benzene = _hx(streams)._stream_props(streams["hot_in"])
    v = _value(data["tube_velocity"])
    di = _value(data["tube_id"])
    length = _value(data["tube_length"])
    passes = data["tube_passes"]
    re = benzene["density"] * v * di / benzene["viscosity"]
    head = benzene["density"] * v ** 2 / 2.0
    f_fanning = 0.079 * re ** -0.25
    expected = 4.0 * f_fanning * length * passes / di * head + 4.0 * passes * head
    assert _value(data["tube_dp"]) == pytest.approx(expected, rel=1e-9)
