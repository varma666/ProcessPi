"""Bell-Delaware shell side by Taborek's method.

The Bell path used to size the exchanger for the Kern U and then multiply the
finished Kern shell coefficient by five factors (Fn, Fw, Fb, Fl, Fs) with no
source, on an approximate geometry (a fixed 20% of tubes in the windows,
leakage areas from round numbers). It now computes the shell coefficient as
Taborek's ideal tube bank coefficient times Jc Jl Jb Jr Js on the exchanger's
own geometry, on every pass of the sizing loop.

Sources: Perry's Chemical Engineers' Handbook, 8th ed., Sec. 11 (procedure,
Eqs. 11-8 to 11-22, Figs. 11-9 to 11-14); J. Taborek, Heat Exchanger Design
Handbook (1983), Sec. 3.3, closed forms as given by Goncalves, Costa and
Bagajewicz, AIChE J. 65 (2019) e16602, Eqs. 5-29 and 47-54; ideal-bank j
coefficients as tabulated in R. W. Serth, Process Heat Transfer, Ch. 6.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import _BELL_IDEAL_J, ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import MassFlowRate, Pressure, Temperature


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _value(x):
    return float(getattr(x, "value", x))


def _streams(cold_out_c=None):
    """docs/examples benzene cooler: benzene 21 000 kg/h 90 to 30 C, water 60 500 kg/h from 15 C."""
    cold_out = {"temperature": Temperature(cold_out_c, "C")} if cold_out_c is not None else {}
    return dict(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water(), **cold_out),
    )


def _run(method="bell_delaware", mode="design", streams=None, **specs):
    engine = HeatExchangerEngine(method=method).fit(
        **(streams or _streams()), shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
        mode=mode, **specs,
    )
    return _quiet(engine.run).data


_RATE_GEOMETRY = dict(tube_od=0.01905, tube_id=0.016, tube_length=4.88, tube_count=200,
                      tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18)


def _rating(**specs):
    return _run(mode="rate", streams=_streams(cold_out_c=25), **dict(_RATE_GEOMETRY, **specs))


# ----------------------------------------------------------------------------
# Ideal tube bank j factor
# ----------------------------------------------------------------------------

def _j(layout, re, pitch_ratio=1.25):
    (a3, a4), rows = _BELL_IDEAL_J[layout]
    a1, a2 = next((a1, a2) for lower, a1, a2 in rows if re >= lower)
    return a1 * (1.33 / pitch_ratio) ** (a3 / (1.0 + 0.14 * re ** a4)) * re ** a2


@pytest.mark.parametrize("layout", sorted(_BELL_IDEAL_J))
def test_ideal_j_is_continuous_across_its_reynolds_ranges(layout):
    """Each row of the table takes over where the previous one stops; a typo in
    a coefficient (one published copy of the 45 degree table has a1 = 0.498 for
    10 < Re < 100, which would make j jump threefold at Re = 100) shows up here."""
    _, rows = _BELL_IDEAL_J[layout]
    for lower, _, _ in rows[:-1]:
        below, above = _j(layout, lower * (1 - 1e-9)), _j(layout, lower)
        assert above == pytest.approx(below, rel=0.06), (layout, lower)


@pytest.mark.parametrize("layout, re, j_perry", [
    # Read from Perry's 8th ed. Fig. 11-9 (ideal tube bank, Bergelin et al.),
    # curve 1 (triangular) and curve 3 (square), pitch 1.25 do.
    ("triangular", 10.0, 0.30),
    ("triangular", 1.0e3, 0.021),
    ("triangular", 1.0e4, 0.0093),
    ("square", 1.0e3, 0.016),
    ("square", 1.0e4, 0.0090),
])
def test_ideal_j_agrees_with_the_perry_ideal_bank_curves(layout, re, j_perry):
    assert _j(layout, re) == pytest.approx(j_perry, rel=0.12)


# ----------------------------------------------------------------------------
# The whole chain by hand, on a fixed geometry
# ----------------------------------------------------------------------------

def test_rating_shell_coefficient_by_hand():
    """Benzene in the shell (the scoring puts the water in the tubes), 200 tubes
    19.05 mm on a 23.81 mm triangular pitch, 2 passes, Ds 0.45 m, baffles 0.18 m
    apart over 4.88 m, 25% cut, TEMA clearances, no sealing strips."""
    data = _rating()
    assert data["tube_side_fluid"] == "Water"
    shell = data["property_basis"]["hot"]
    m = 21000.0 / 3600.0
    do, pt, ds, lbc, length, nt, bc = 0.01905, 1.25 * 0.01905, 0.45, 0.18, 4.88, 200, 0.25

    # Bundle (outer tube limit) diameter, Sinnott Table 12.4, triangular, 2 passes.
    dotl = do * (nt / 0.249) ** (1 / 2.207)
    lbb, dctl = ds - dotl, dotl - do
    theta_ds = 2 * math.acos(1 - 2 * bc)
    theta_ctl = 2 * math.acos(ds * (1 - 2 * bc) / dctl)
    fw = (theta_ctl - math.sin(theta_ctl)) / (2 * math.pi)
    fc = 1 - 2 * fw
    sm = lbc * (lbb + dctl / pt * (pt - do))                          # Perry 11-10b
    lsb, ltb = 3.1e-3 + 0.004 * ds, 0.8e-3
    ssb = ds * lsb / 2 * (math.pi - theta_ds / 2)                     # Perry 11-13
    stb = math.pi / 4 * ((do + ltb) ** 2 - do ** 2) * nt * (1 + fc) / 2  # Perry 11-12
    fsbp = lbc * lbb / sm                                             # Perry 11-11

    re = do * m / (shell["viscosity_Pa_s"] * sm)                     # Perry 11-20
    pr = shell["cp_J_kgK"] * shell["viscosity_Pa_s"] / shell["k_W_mK"]
    a = 1.450 / (1 + 0.14 * re ** 0.519)
    j = 0.321 * (1.33 / 1.25) ** a * re ** -0.388                    # Re > 1000
    h_ideal = j * shell["cp_J_kgK"] * m / sm * pr ** (-2 / 3)         # Perry 11-21, phi = 1

    jc = 0.55 + 0.72 * fc
    rs, rlm = ssb / (ssb + stb), (ssb + stb) / sm
    jl = 0.44 * (1 - rs) + (1 - 0.44 * (1 - rs)) * math.exp(-2.2 * rlm)
    jb = math.exp(-1.25 * fsbp)                                       # no sealing strips

    report = data["bell_delaware"]
    assert re > 1000
    assert report["re_shell"] == pytest.approx(re, rel=1e-9)
    assert report["geometry"]["Fc"] == pytest.approx(fc, rel=1e-9)
    assert report["geometry"]["Sm_m2"] == pytest.approx(sm, rel=1e-9)
    assert report["geometry"]["Ssb_m2"] == pytest.approx(ssb, rel=1e-9)
    assert report["geometry"]["Stb_m2"] == pytest.approx(stb, rel=1e-9)
    assert data["h_shell_ideal"] == pytest.approx(h_ideal, rel=1e-9)
    assert data["bell_factors"] == pytest.approx({"Jc": jc, "Jl": jl, "Jb": jb, "Jr": 1.0, "Js": 1.0}, rel=1e-9)
    assert _value(data["h_shell"]) == pytest.approx(h_ideal * jc * jl * jb, rel=1e-9)
    # Typical corrected-to-ideal ratio for a TEMA R bundle without sealing strips.
    assert 0.4 < jc * jl * jb < 0.7


def test_rating_with_bell_delaware_is_no_longer_kern():
    bell = _rating()
    kern = _run(method="kern", mode="rate", streams=_streams(cold_out_c=25), **_RATE_GEOMETRY)
    assert bell["method"] == "bell_delaware"
    assert "bell_factors" not in kern
    assert _value(bell["h_shell"]) != pytest.approx(_value(kern["h_shell"]), rel=1e-3)
    # The tube side does not depend on the shell-side method.
    assert _value(bell["h_tube"]) == pytest.approx(_value(kern["h_tube"]), rel=1e-12)


# ----------------------------------------------------------------------------
# Design sizes the area for the Bell U
# ----------------------------------------------------------------------------

def test_bell_design_area_covers_its_own_u():
    """Without a user U the loop sizes on the calculated U. The Bell area used to
    be the Kern one, about 57% of what the Bell U needed."""
    data = _run()
    q_w = _value(data["Q"].to("W"))
    u = _value(data["U_calculated"])
    required = q_w / (u * data["ft"] * _value(data["LMTD"]))
    assert data["converged"] is True
    assert _value(data["Area"]) >= required * (1 - 1e-6)
    assert _value(data["Area_required"]) == pytest.approx(required, rel=1e-6)
    kern = _run(method="kern")
    # Taborek's corrected coefficient is lower than Kern's here, so the area is larger.
    assert u < _value(kern["U_calculated"])
    assert _value(data["Area_required"]) > _value(kern["Area_required"])


def test_the_settled_pass_reports_its_own_factors():
    data = _run()
    factors = data["bell_factors"]
    assert _value(data["h_shell"]) == pytest.approx(data["h_shell_ideal"] * math.prod(factors.values()), rel=1e-12)
    assert data["bell_delaware"]["geometry"]["baffles"] >= 1


# ----------------------------------------------------------------------------
# Construction inputs
# ----------------------------------------------------------------------------

def test_sealing_strips_reduce_the_bypass_penalty():
    none = _rating()
    some = _rating(sealing_strip_pairs=2)
    enough = _rating(sealing_strip_pairs=20)
    assert none["bell_factors"]["Jb"] < some["bell_factors"]["Jb"] < 1.0
    # rss = Nss / Ntcc >= 1/2: no bypass penalty at all.
    assert enough["bell_factors"]["Jb"] == 1.0


def test_tighter_clearances_raise_the_leakage_factor():
    loose = _rating(shell_baffle_clearance=0.008, tube_baffle_clearance=0.0016)
    tight = _rating(shell_baffle_clearance=0.002, tube_baffle_clearance=0.0004)
    assert tight["bell_factors"]["Jl"] > loose["bell_factors"]["Jl"]


def test_baffle_cut_outside_the_fitted_range_is_warned():
    data = _rating(baffle_cut=0.5)
    assert any("Baffle cut 0.50 is outside 0.15-0.45" in w for w in data["warnings"])


@pytest.mark.parametrize("layout, key", [("square", "square"), ("rotated_square", "rotated_square"),
                                         ("triangular", "triangular")])
def test_layout_picks_its_j_table(layout, key):
    hx = ShellAndTubeHX(method="bell_delaware", tube_layout=layout, **_streams())
    assert hx._bell_layout() == key
