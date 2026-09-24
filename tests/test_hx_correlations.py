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


# ----------------------------------------------------------------------------
# Kern shell-side pressure drop
# ----------------------------------------------------------------------------

def test_kern_shell_pressure_drop_by_hand():
    """The Peters, Timmerhaus and West shell-side example as used for `dP_Kern`
    in the `ht` library: water 11 kg/s, rho 995, mu 8.03e-4 Pa.s, shell 0.584 m,
    baffle spacing 0.1524 m, 19 mm tubes on a 25.4 mm square pitch, 22 baffles.

      As  = Ds (Pt - do) B / Pt = 0.584 x 0.0064 x 0.1524 / 0.0254 = 0.0224256 m2
      G   = 11 / 0.0224256                                          = 490.511 kg/m2s
      De  = 4 (Pt^2 - pi do^2 / 4) / (pi do)                        = 0.0242339 m
      Re  = 0.0242339 x 490.511 / 8.03e-4                           = 14 803
      f   = exp(0.576 - 0.19 ln 14 803)                             = 0.28694
      dP  = f G^2 Ds (Nb + 1) / (2 rho De)
          = 0.28694 x 490.511^2 x 0.584 x 23 / (2 x 995 x 0.0242339) = 19 229 Pa

    `ht`, reading f off its digitisation of Kern's chart instead of the fit,
    gives 18 980.6 Pa with mu_w = 6.57e-4, which is 19 521 Pa without the
    (mu/mu_w)^0.14 = 1.02849 correction: 1.5% from the fit.
    """
    streams = _benzene_cooler()
    hx = _hx(streams, tube_layout="square")
    water = {"density": 995.0, "viscosity": 8.03e-4}
    baffle = 0.1524
    geometry = {"tube_od": 0.019, "tube_pitch": 0.0254, "baffle_spacing": baffle, "tube_count": 300}
    area = 0.584 * (0.0254 - 0.019) * baffle / 0.0254
    v_shell = 11.0 / 995.0 / area
    _, shell_dp = hx._calculate_pressure_drop(
        geometry=geometry, tube=water, shell=water, shell_velocity=v_shell,
        tube_velocity=1.0, shell_diameter=0.584, tube_length=23 * baffle,
        tube_id=0.016, tube_passes=2,
    )
    assert shell_dp == pytest.approx(19_229, rel=1e-4)
    assert shell_dp == pytest.approx(18_980.58768759033 * 1.0284922525997, rel=0.02)


def test_kern_shell_pressure_drop_follows_the_equivalent_diameter_of_the_layout():
    """Triangular pitch has the smaller De, so a higher Re at the same G and a
    larger Ds/De: the same flow costs more pressure drop."""
    streams = _benzene_cooler()
    water = {"density": 995.0, "viscosity": 8.03e-4}
    geometry = {"tube_od": 0.019, "tube_pitch": 0.0254, "baffle_spacing": 0.1524, "tube_count": 300}
    kwargs = dict(geometry=geometry, tube=water, shell=water, shell_velocity=0.5,
                  tube_velocity=1.0, shell_diameter=0.584, tube_length=3.5, tube_id=0.016)
    square = _hx(streams, tube_layout="square")._calculate_pressure_drop(**kwargs)[1]
    triangular = _hx(streams, tube_layout="triangular")._calculate_pressure_drop(**kwargs)[1]

    def by_hand(de):
        g = 995.0 * 0.5
        re = de * g / 8.03e-4
        f = math.exp(0.576 - 0.19 * math.log(re))
        return f * g ** 2 * 0.584 * math.floor(3.5 / 0.1524) / (2.0 * 995.0 * de)

    pt, do = 0.0254, 0.019
    de_square = 4.0 * (pt ** 2 - math.pi * do ** 2 / 4.0) / (math.pi * do)
    de_triangular = 4.0 * (math.sqrt(3.0) / 4.0 * pt ** 2 - math.pi * do ** 2 / 8.0) / (math.pi * do / 2.0)
    assert square == pytest.approx(by_hand(de_square), rel=1e-9)
    assert triangular == pytest.approx(by_hand(de_triangular), rel=1e-9)
    assert triangular > square


def test_kern_shell_friction_factor_outside_its_checked_range_is_warned():
    streams = _benzene_cooler()
    hx = _hx(streams)
    oil = {"density": 900.0, "viscosity": 0.5}
    geometry = {"tube_od": 0.019, "tube_pitch": 0.02375, "baffle_spacing": 0.2, "tube_count": 300}
    hx._calculate_pressure_drop(geometry=geometry, tube=oil, shell=oil, shell_velocity=0.3,
                                tube_velocity=1.0, shell_diameter=0.5, tube_length=4.0, tube_id=0.016)
    assert any("HYDRAULIC_WARNING" in w and "Kern shell-side friction" in w for w in hx._warnings)


def test_bell_shell_pressure_drop_is_the_kern_one_without_an_uplift():
    """The Bell path multiplied the Kern shell pressure drop by an undocumented
    1.15 "for Bell realism". No Bell-Delaware pressure drop correlation is
    implemented, so the shell pressure drop of the Bell geometry is Kern's."""
    streams = _benzene_cooler()
    data = _run(streams, method="bell_delaware", force_hot_in_tubes=True)
    hx = _hx(streams)
    water = hx._stream_props(streams["cold_in"])
    od = _value(data["tube_od"])
    expected = hx._kern_shell_pressure_drop(
        shell=water, v_shell=_value(data["shell_velocity"]),
        shell_diameter=_value(data["shell_diameter"]),
        baffle_spacing=_value(data["baffle_spacing"]), tube_pitch=1.25 * od,
        tube_od=od, tube_length=_value(data["tube_length"]),
    )
    assert _value(data["shell_dp"]) == pytest.approx(expected, rel=1e-9)
