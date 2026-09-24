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


# ----------------------------------------------------------------------------
# Bundle diameter: Sinnott, Coulson & Richardson Vol. 6, 4th ed., Table 12.4
# ----------------------------------------------------------------------------

# (layout, passes, K1, n1), typed in from the table, pitch 1.25 do.
_SINNOTT_TABLE_12_4 = [
    ("triangular", 1, 0.319, 2.142),
    ("triangular", 2, 0.249, 2.207),
    ("triangular", 4, 0.175, 2.285),
    ("triangular", 6, 0.0743, 2.499),
    ("triangular", 8, 0.0365, 2.675),
    ("square", 1, 0.215, 2.207),
    ("square", 2, 0.156, 2.291),
    ("square", 4, 0.158, 2.263),
    ("square", 6, 0.0402, 2.617),
    ("square", 8, 0.0331, 2.643),
]


@pytest.mark.parametrize("layout,passes,k1,n1", _SINNOTT_TABLE_12_4)
def test_bundle_diameter_follows_the_layout_and_the_passes(layout, passes, k1, n1):
    hx = _hx(_benzene_cooler(), tube_layout=layout)
    tube_count, tube_od = 500, 0.019
    expected = tube_od * (tube_count / k1) ** (1.0 / n1)
    assert hx._calculate_bundle_diameter(tube_count, tube_od, passes) == pytest.approx(expected, rel=1e-12)


def test_bundle_diameter_at_eight_passes_by_hand():
    """500 tubes of 19 mm, triangular pitch, 8 passes:
    Db = 0.019 (500 / 0.0365)^(1/2.675) = 0.019 x 35.19 = 0.6686 m,
    against 0.019 (500 / 0.249)^(1/2.207) = 0.5960 m from the 2-pass constants
    the code used for every layout (-10.9%)."""
    hx = _hx(_benzene_cooler())
    assert hx._calculate_bundle_diameter(500, 0.019, 8) == pytest.approx(0.6686, abs=1e-4)
    assert hx._calculate_bundle_diameter(500, 0.019, 2) == pytest.approx(0.5960, abs=1e-4)


@pytest.mark.parametrize("layout,passes", [("rotated_square", 2), ("triangular", 3), ("square", 12)])
def test_bundle_diameter_refuses_what_the_table_does_not_cover(layout, passes):
    hx = _hx(_benzene_cooler(), tube_layout=layout)
    with pytest.raises(ValueError, match="Table 12.4"):
        hx._calculate_bundle_diameter(500, 0.019, passes)


def test_bundle_constants_can_be_overridden_as_a_pair_only():
    hx = _hx(_benzene_cooler(), bundle_k1=0.2, bundle_n1=2.2)
    assert hx._calculate_bundle_diameter(500, 0.019, 8) == pytest.approx(0.019 * (500 / 0.2) ** (1 / 2.2))
    with pytest.raises(ValueError, match="together"):
        _hx(_benzene_cooler(), bundle_k1=0.2)._calculate_bundle_diameter(500, 0.019, 2)


def test_design_shell_holds_the_bundle_of_the_settled_passes():
    data = _run(_benzene_cooler(), force_hot_in_tubes=True)
    hx = _hx(_benzene_cooler())
    bundle = hx._calculate_bundle_diameter(
        data["tube_count"], _value(data["tube_od"]), data["tube_passes"]
    )
    assert _value(data["shell_diameter"]) > bundle
