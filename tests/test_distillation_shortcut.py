"""
Shortcut distillation methods, McCabe-Thiele stepping and tray hydraulics.

Reference values:
- OEP: OpenExamPrep PE Chemical guide 11.4,
  https://open-exam-prep.com/study-guides/pe-chemical/distillation-operations/multicomponent-distillation
  (worked example: ethane/propane/n-butane/n-pentane, and its Fenske question).
- Duss and Taylor, Chem. Eng. Prog. July 2018, eq. (2) (O'Connell).
- Souza et al., Ind. Eng. Chem. Res. 64 (2025) 2256, eqs. (2), (5), Table 1 (Fair flooding).
"""

import math

import pytest

from processpi.equipment.distillation import hydraulics, mccabe_thiele, shortcut

# OEP worked example, alpha relative to n-butane, 100 kmol/h saturated liquid.
ALPHA = {"C2": 5.00, "C3": 2.20, "nC4": 1.00, "nC5": 0.40}
Z = {"C2": 0.100, "C3": 0.400, "nC4": 0.350, "nC5": 0.150}
FEED = {n: 100.0 * z for n, z in Z.items()}


def _oep_split():
    n_min = shortcut.fenske_minimum_stages(39.20, 0.80, 0.70, 34.30, ALPHA["C3"])
    d, b = shortcut.fenske_split(FEED, ALPHA, "nC4", 0.70, 34.30, n_min)
    d["C3"], b["C3"] = 39.20, 0.80
    return n_min, d, b


# ----------------------------------------------------------------------
# Fenske
# ----------------------------------------------------------------------
def test_fenske_oep_question():
    # 99 % recoveries of both keys, alpha 2.25 -> 11.333 stages.
    assert shortcut.fenske_minimum_stages(99.0, 1.0, 1.0, 99.0, 2.25) == pytest.approx(11.333, abs=1e-3)


def test_fenske_oep_worked_example():
    n_min, d, b = _oep_split()
    assert n_min == pytest.approx(9.872, abs=1e-3)
    # The light non-key goes overhead and the heavy non-key to the bottoms.
    assert d["C2"] == pytest.approx(10.0, abs=1e-3)
    assert d["nC5"] == pytest.approx(0.0, abs=1e-3)
    assert sum(d.values()) == pytest.approx(49.90, abs=1e-2)
    assert sum(b.values()) == pytest.approx(50.10, abs=1e-2)


def test_fenske_split_conserves_every_component():
    _, d, b = _oep_split()
    for name, f in FEED.items():
        assert d[name] + b[name] == pytest.approx(f)


def test_fenske_rejects_reversed_keys_and_no_separation():
    with pytest.raises(ValueError):
        shortcut.fenske_minimum_stages(99, 1, 1, 99, 0.9)
    with pytest.raises(ValueError):
        shortcut.fenske_minimum_stages(1, 99, 99, 1, 2.0)


# ----------------------------------------------------------------------
# Underwood
# ----------------------------------------------------------------------
def test_underwood_oep_worked_example():
    _, d, _ = _oep_split()
    uw = shortcut.underwood_minimum_reflux(ALPHA, Z, 1.0, d, "C3", "nC4")
    assert uw["theta"] == [pytest.approx(1.3250, abs=1e-4)]
    assert uw["V_min"] == pytest.approx(110.011, abs=0.01)
    assert uw["R_min"] == pytest.approx(1.2046, abs=1e-4)


def test_underwood_binary_matches_the_mccabe_thiele_pinch():
    # Two independent routes to R_min: Underwood, and the reflux at which the
    # McCabe-Thiele operating lines touch the equilibrium curve.
    alpha, x_d, x_b, z_f, q = 2.5, 0.95, 0.05, 0.5, 1.0
    uw = shortcut.underwood_minimum_reflux({"A": alpha, "B": 1.0}, {"A": z_f, "B": 1 - z_f}, q,
                                           {"A": 0.5 * x_d, "B": 0.5 * (1 - x_d)}, "A", "B")
    y_eq, x_eq = mccabe_thiele.constant_alpha_curves(alpha)
    # Binary, saturated liquid: the pinch is at x = z_F.
    y_star = y_eq(z_f)
    r_pinch = (x_d - y_star) / (y_star - z_f)
    assert uw["R_min"] == pytest.approx(r_pinch, rel=1e-9)
    mccabe_thiele.step_stages(x_d, x_b, z_f, q, 1.01 * r_pinch, y_eq, x_eq)
    with pytest.raises(ValueError, match="minimum"):
        mccabe_thiele.step_stages(x_d, x_b, z_f, q, 0.99 * r_pinch, y_eq, x_eq)


def test_underwood_with_a_component_between_the_keys():
    alpha = {"A": 4.0, "LK": 2.0, "M": 1.5, "HK": 1.0, "H": 0.5}
    z = {"A": 0.1, "LK": 0.3, "M": 0.2, "HK": 0.3, "H": 0.1}
    d = {"A": 0.1, "LK": 0.29, "M": 0.1, "HK": 0.01, "H": 0.0}
    q = 0.6
    uw = shortcut.underwood_minimum_reflux(alpha, z, q, d, "LK", "HK")
    assert uw["distributing_components"] == ["M"]
    assert len(uw["theta"]) == 2
    assert 1.5 < uw["theta"][0] < 2.0 and 1.0 < uw["theta"][1] < 1.5
    # Each root satisfies the feed equation...
    for theta in uw["theta"]:
        assert sum(alpha[n] * z[n] / (alpha[n] - theta) for n in z) == pytest.approx(1 - q, abs=1e-9)
    # ...and the distillate equation gives the same V_min for both.
    for theta in uw["theta"]:
        dd = uw["distillate"]
        assert sum(alpha[n] * dd[n] / (alpha[n] - theta) for n in dd) == pytest.approx(uw["V_min"], rel=1e-9)
    assert 0.0 < uw["distillate"]["M"] < z["M"]


# ----------------------------------------------------------------------
# Gilliland and Kirkbride
# ----------------------------------------------------------------------
def test_gilliland_eduljee_oep_worked_example():
    out = shortcut.gilliland_stages(9.872, 1.2046, 1.5660, "eduljee")
    assert out["X"] == pytest.approx(0.1408, abs=1e-4)
    assert out["Y"] == pytest.approx(0.75 * (1 - out["X"] ** 0.5668))
    # OEP prints 0.1408^0.5668 = 0.3299 and Y = 0.5026; the power is in fact
    # 0.3292, so Y = 0.5031 and N moves by 0.02 from OEP's 20.86.
    assert out["Y"] == pytest.approx(0.5026, abs=1e-3)
    assert out["N"] == pytest.approx(20.86, abs=0.05)


def test_gilliland_molokanov_formula_and_limits():
    out = shortcut.gilliland_stages(10.0, 1.0, 1.5)
    x = 0.5 / 2.5
    y = 1 - math.exp(((1 + 54.4 * x) / (11 + 117.2 * x)) * ((x - 1) / math.sqrt(x)))
    assert out["Y"] == pytest.approx(y)
    assert out["N"] == pytest.approx((10.0 + y) / (1 - y))
    # Near total reflux N approaches N_min; near minimum reflux it grows without bound.
    assert shortcut.gilliland_stages(10.0, 1.0, 1e6)["N"] == pytest.approx(10.0, abs=0.01)
    assert shortcut.gilliland_stages(10.0, 1.0, 1.0001)["N"] > 100
    # Molokanov and Eduljee are two fits of the same chart.
    for r in (1.2, 1.5, 2.0, 3.0):
        m = shortcut.gilliland_stages(10.0, 1.0, r, "molokanov")["N"]
        e = shortcut.gilliland_stages(10.0, 1.0, r, "eduljee")["N"]
        assert m == pytest.approx(e, rel=0.10)


def test_gilliland_rejects_reflux_at_or_below_minimum():
    with pytest.raises(ValueError):
        shortcut.gilliland_stages(10.0, 1.2, 1.2)
    with pytest.raises(ValueError):
        shortcut.gilliland_stages(10.0, 1.2, 1.5, "fair")


def test_kirkbride_oep_worked_example():
    ratio = shortcut.kirkbride_ratio(0.400, 0.350, 0.80 / 50.10, 0.70 / 49.90, 50.10, 49.90)
    assert ratio == pytest.approx(1.0271, abs=1e-4)


# ----------------------------------------------------------------------
# McCabe-Thiele
# ----------------------------------------------------------------------
def test_mccabe_thiele_total_reflux_approaches_fenske():
    alpha, x_d, x_b = 2.5, 0.95, 0.05
    n_min = shortcut.fenske_minimum_stages(x_d, x_b, 1 - x_d, 1 - x_b, alpha)
    y_eq, x_eq = mccabe_thiele.constant_alpha_curves(alpha)
    mt = mccabe_thiele.step_stages(x_d, x_b, 0.5, 1.0, 1e6, y_eq, x_eq)
    assert mt["N"] == math.ceil(n_min)


def test_mccabe_thiele_textbook_case_terminates():
    y_eq, x_eq = mccabe_thiele.constant_alpha_curves(2.5)
    mt = mccabe_thiele.step_stages(0.95, 0.05, 0.5, 1.0, 2.0, y_eq, x_eq)
    assert mt["N"] == 11
    assert 10.0 < mt["N_fractional"] <= 11.0
    assert mt["feed_stage"] == 5
    # Every stage is on the equilibrium curve.
    for x, y in mt["stages"]:
        assert y == pytest.approx(y_eq(x))


@pytest.mark.parametrize("q", [1.2, 0.5, 0.0, -0.2])
def test_mccabe_thiele_other_feed_conditions(q):
    y_eq, x_eq = mccabe_thiele.constant_alpha_curves(2.5)
    x_int, y_int = mccabe_thiele.operating_lines_intersection(0.95, 0.5, q, 3.0)
    # The intersection lies on the q-line.
    if abs(q - 1) > 1e-12:
        assert y_int == pytest.approx(q / (q - 1) * x_int - 0.5 / (q - 1))
    mt = mccabe_thiele.step_stages(0.95, 0.05, 0.5, q, 3.0, y_eq, x_eq)
    assert mt["N"] > 0


# ----------------------------------------------------------------------
# Hydraulics
# ----------------------------------------------------------------------
def test_csb_is_the_lygeros_magoulas_fit():
    for lt, flv in ((0.3048, 0.05), (0.6096, 0.2), (0.9144, 1.0)):
        expected = 0.0105 + 0.1496 * lt ** 0.755 * math.exp(-1.463 * flv ** 0.842)
        assert hydraulics.souders_brown_csb(lt, flv) == pytest.approx(expected)
    # The mm form quoted elsewhere, 8.127e-4 * lt[mm]^0.755, is the same constant.
    assert 8.127e-4 * 1000 ** 0.755 == pytest.approx(0.1496, rel=1e-3)
    # More spacing, more capacity; more liquid, less.
    assert hydraulics.souders_brown_csb(0.6, 0.1) > hydraulics.souders_brown_csb(0.45, 0.1)
    assert hydraulics.souders_brown_csb(0.6, 0.5) < hydraulics.souders_brown_csb(0.6, 0.1)


def test_flooding_velocity_surface_tension_correction():
    base = hydraulics.flooding_velocity(0.1, 800.0, 3.0, 0.020)
    assert base == pytest.approx(0.1 * math.sqrt(797.0 / 3.0))
    assert hydraulics.flooding_velocity(0.1, 800.0, 3.0, 0.040) == pytest.approx(base * 2 ** 0.2)


def test_tray_diameter_scales_with_vapour_flow_and_flags_extrapolation():
    one = hydraulics.tray_diameter(2.0, 2.0, 3.0, 800.0, 0.6, 0.02, 0.8, 0.12)
    two = hydraulics.tray_diameter(4.0, 4.0, 3.0, 800.0, 0.6, 0.02, 0.8, 0.12)
    assert two["area"] == pytest.approx(2 * one["area"])
    assert one["net_area"] == pytest.approx(one["area"] * 0.88)
    assert one["warnings"] == []
    far = hydraulics.tray_diameter(2.0, 2.0, 3.0, 800.0, 1.2, 0.02, 0.8, 0.12)
    assert any("Tray spacing" in w for w in far["warnings"])


def test_oconnell_duss_taylor_eq2():
    assert hydraulics.oconnell_efficiency(1.0, 1.0) == pytest.approx(0.503)
    assert hydraulics.oconnell_efficiency(0.3, 2.5) == pytest.approx(0.503 * 0.75 ** -0.226)
