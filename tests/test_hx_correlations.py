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


# ----------------------------------------------------------------------------
# Tube-side friction factor
# ----------------------------------------------------------------------------

def _tube_dp(hx, v=1.5, rho=995.0, mu=8.0e-4):
    water = {"density": rho, "viscosity": mu}
    geometry = {"tube_od": 0.019, "tube_pitch": 0.02375, "baffle_spacing": 0.2, "tube_count": 100}
    tube_dp, _ = hx._calculate_pressure_drop(
        geometry=geometry, tube=water, shell=water, shell_velocity=0.5, tube_velocity=v,
        shell_diameter=0.5, tube_length=4.88, tube_id=0.016, tube_passes=2,
    )
    return tube_dp


def test_tube_roughness_uses_colebrook_white():
    """Water at 1.5 m/s in 16 mm tubes, 4.88 m, 2 passes, roughness 0.046 mm.

      Re        = 995 x 1.5 x 0.016 / 8e-4                  = 29 850
      Colebrook 1/sqrt(f) = -2 log10(e/3.7d + 2.51/(Re sqrt f)), e/d = 0.002875
                f_Darcy                                     = 0.029765  (Fanning 0.0074413)
      head      = 995 x 1.5^2 / 2                           = 1119.375 Pa
      dP        = f_D (L Np / di) head + 4 Np head
                = 0.029765 x 610 x 1119.375 + 8 x 1119.375  = 29 279 Pa

    The smooth-tube Blasius factor gives 25 371 Pa for the same tube.
    """
    rough = _tube_dp(_hx(_benzene_cooler(), tube_roughness=4.6e-5))
    smooth = _tube_dp(_hx(_benzene_cooler()))
    assert rough == pytest.approx(29_279.3, rel=1e-4)
    assert smooth == pytest.approx(25_370.6, rel=1e-4)


def test_tube_roughness_accepts_a_length():
    from processpi.units import Length

    as_length = _tube_dp(_hx(_benzene_cooler(), tube_roughness=Length(0.046, "mm")))
    as_metres = _tube_dp(_hx(_benzene_cooler(), tube_roughness=4.6e-5))
    assert as_length == pytest.approx(as_metres, rel=1e-9)
    assert as_metres > _tube_dp(_hx(_benzene_cooler()))


def test_negative_tube_roughness_is_refused():
    with pytest.raises(ValueError, match="tube_roughness"):
        _tube_dp(_hx(_benzene_cooler(), tube_roughness=-1e-5))


def test_laminar_tube_friction_is_hagen_poiseuille():
    """Re < 2100 keeps the Fanning 16/Re, which with the Fanning form
    4 f (L/d) rho v^2/2 is Hagen-Poiseuille, dP = 32 mu v L / d^2, whatever the
    roughness. A guard: this held before as well."""
    rho, mu, v = 900.0, 0.05, 1.0
    re = rho * v * 0.016 / mu
    assert re < 2100
    expected = 32.0 * mu * v * 4.88 * 2 / 0.016 ** 2 + 4 * 2 * rho * v ** 2 / 2.0
    for hx in (_hx(_benzene_cooler()), _hx(_benzene_cooler(), tube_roughness=4.6e-5)):
        assert _tube_dp(hx, v=v, rho=rho, mu=mu) == pytest.approx(expected, rel=1e-9)


def test_tube_friction_model_is_reported():
    smooth = _run(_benzene_cooler())
    rough = _run(_benzene_cooler(), tube_roughness=4.6e-5)
    assert smooth["tube_friction_model"].startswith("Blasius")
    assert rough["tube_friction_model"].startswith("Colebrook-White")
    assert _value(rough["tube_dp"]) > _value(smooth["tube_dp"])


# ----------------------------------------------------------------------------
# Sieder-Tate viscosity correction
# ----------------------------------------------------------------------------

_RATE_GEOMETRY = dict(tube_od=0.01905, tube_id=0.016, tube_length=4.88, tube_count=200,
                      tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18)


def _rating(**specs):
    streams = _benzene_cooler()
    streams["cold_out"] = MaterialStream("cold_out", component=Water(),
                                         temperature=Temperature(25, "C"))
    return _run(streams, mode="rate", **dict(_RATE_GEOMETRY, **specs))


def test_without_a_wall_viscosity_phi_is_one_and_says_so():
    data = _rating()
    correction = data["viscosity_correction"]
    assert correction["tube"]["phi"] == 1.0
    assert correction["shell"]["phi"] == 1.0
    assert correction["tube"]["mu_wall"] is None
    assert "assumed" in correction["shell"]["basis"]
    assumptions = [w for w in data["warnings"] if w.startswith("[ASSUMPTION_WARNING]")]
    # Water (cold) is in the tubes and benzene (hot) in the shell here.
    assert any("tube side: no cold_wall_viscosity" in w for w in assumptions)
    assert any("shell side: no hot_wall_viscosity" in w for w in assumptions)


def test_wall_viscosity_corrects_the_kern_shell_film_and_both_pressure_drops():
    """Fixed geometry, so only phi changes between the two ratings.

    Water in the tubes, mu = 9.1253e-4 Pa.s, given mu_w = 6.0e-4:
      phi_t = (9.1253e-4 / 6.0e-4)^0.14 = 1.0605
    Benzene in the shell, mu = 5.9973e-4 Pa.s, given mu_w = 7.0e-4:
      phi_s = (5.9973e-4 / 7.0e-4)^0.14 = 0.97859

    Kern: h_s carries phi_s, the shell dP is divided by phi_s, and the tube
    friction (not the 4 Np return losses) is divided by phi_t.
    """
    plain = _rating()
    corrected = _rating(cold_wall_viscosity=6.0e-4, hot_wall_viscosity=7.0e-4)

    streams = _benzene_cooler()
    hx = _hx(streams)
    water = hx._stream_props(streams["cold_in"])
    benzene = hx._stream_props(streams["hot_in"])
    phi_t = (water["viscosity"] / 6.0e-4) ** 0.14
    phi_s = (benzene["viscosity"] / 7.0e-4) ** 0.14
    assert phi_t == pytest.approx(1.0605, abs=1e-4)
    assert phi_s == pytest.approx(0.97859, abs=1e-5)
    assert corrected["viscosity_correction"]["tube"]["phi"] == pytest.approx(phi_t)
    assert corrected["viscosity_correction"]["shell"]["phi"] == pytest.approx(phi_s)
    assert not any(w.startswith("[ASSUMPTION_WARNING]") for w in corrected["warnings"])

    assert _value(corrected["h_shell"]) == pytest.approx(_value(plain["h_shell"]) * phi_s, rel=1e-9)
    assert _value(corrected["h_tube"]) == pytest.approx(_value(plain["h_tube"]), rel=1e-12)
    assert _value(corrected["shell_dp"]) == pytest.approx(_value(plain["shell_dp"]) / phi_s, rel=1e-9)

    v = _value(plain["tube_velocity"])
    returns = 4.0 * 2 * water["density"] * v ** 2 / 2.0
    friction = _value(plain["tube_dp"]) - returns
    assert _value(corrected["tube_dp"]) == pytest.approx(friction / phi_t + returns, rel=1e-9)


def test_wall_viscosity_follows_its_stream_to_its_side():
    """The spec is per stream, so it lands on whichever side the stream is on."""
    data = _run(_benzene_cooler(), force_hot_in_tubes=True, hot_wall_viscosity=7.0e-4)
    correction = data["viscosity_correction"]
    assert correction["tube"]["mu_wall"] == pytest.approx(7.0e-4)
    assert correction["shell"]["mu_wall"] is None


def test_non_positive_wall_viscosity_is_refused():
    with pytest.raises(ValueError, match="hot_wall_viscosity"):
        _rating(hot_wall_viscosity=0.0)


# ----------------------------------------------------------------------------
# rate() applies the LMTD correction factor
# ----------------------------------------------------------------------------

def test_rating_applies_the_lmtd_correction_factor():
    """Benzene 90 to 30 C against water 15 to 25 C, 1 shell pass, 2 tube passes.

      LMTD = (65 - 15) / ln(65 / 15)                       = 34.0986 K
      R    = (90 - 30) / (25 - 15) = 6,  S = 10 / 75        = 0.13333
      F    = sqrt(R^2+1) ln[(1-S)/(1-RS)]
             / ((R-1) ln[(2 - S(R+1-sqrt(R^2+1))) / (2 - S(R+1+sqrt(R^2+1)))])
                                                            = 0.894592
    rate() used the bare LMTD; design() has always used F x LMTD. The area the
    duty needs is Q / (U F LMTD).
    """
    data = _rating()
    lmtd = (65.0 - 15.0) / math.log(65.0 / 15.0)
    assert data["LMTD"] == pytest.approx(lmtd, rel=1e-4)
    assert data["ft"] == pytest.approx(0.894592, abs=1e-6)
    assert data["corrected_lmtd"] == pytest.approx(data["ft"] * data["LMTD"], rel=1e-12)
    q = _value(data["Q"])
    assert _value(data["Area_required"]) == pytest.approx(q / (575.0 * data["corrected_lmtd"]), rel=1e-9)


def test_rating_ft_matches_the_review_kerosene_case():
    """#86 scenario 16: 200 to 90 C against 30 to 40 C gives R = 11,
    S = 0.0588 and F = 0.9812; the rating reported no F at all."""
    hot_in = MaterialStream("hot_in", component=Benzene(), temperature=Temperature(200, "C"),
                            mass_flow=MassFlowRate(5000, "kg/h"))
    hot_out = MaterialStream("hot_out", component=Benzene(), temperature=Temperature(90, "C"))
    cold_in = MaterialStream("cold_in", component=Water(), temperature=Temperature(30, "C"),
                             mass_flow=MassFlowRate(50000, "kg/h"))
    cold_out = MaterialStream("cold_out", component=Water(), temperature=Temperature(40, "C"))
    data = _run(dict(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out),
                mode="rate", **_RATE_GEOMETRY)
    assert data["ft"] == pytest.approx(0.981201, abs=1e-6)


def test_rating_one_tube_pass_is_counter_current():
    data = _rating(tube_passes=1)
    assert data["ft"] == 1.0
    assert data["corrected_lmtd"] == pytest.approx(data["LMTD"])


def test_rating_refuses_shell_passes_without_an_ft_expression():
    with pytest.raises(ValueError, match="1 and 2 shell"):
        _rating(shell_passes=3, tube_passes=6)


def test_rating_refuses_an_undefined_ft(monkeypatch):
    monkeypatch.setattr(ShellAndTubeHX, "_calculate_ft", lambda self, *args: 0.0)
    with pytest.raises(ValueError, match="temperature cross"):
        _rating()


# ----------------------------------------------------------------------------
# Bell-Delaware results carry units like Kern's
# ----------------------------------------------------------------------------

def test_bell_results_carry_units_like_kern():
    """_design_bell_delaware overwrote the unit-wrapped Kern U_calculated with a
    bare float and added U_clean as one. The Bell U itself is unchanged: it is
    still the Kern design corrected by the Bell factors after sizing (the Bell
    area is not resized in this change)."""
    from processpi.units import Pressure as P
    from processpi.units.heat_transfer_coefficient import HeatTransferCoefficient as HTC

    kern = _run(_benzene_cooler())
    bell = _run(_benzene_cooler(), method="bell_delaware")
    assert bell["method"] == "bell_delaware"
    assert isinstance(kern["U_calculated"], HTC)
    assert isinstance(bell["U_calculated"], HTC)
    assert isinstance(bell["U_clean"], HTC)
    assert isinstance(bell["shell_dp"], P)
    assert isinstance(bell["tube_dp"], P)
    # Same value as the bare float before: the Bell-corrected U of the Kern geometry.
    assert bell["tube_count"] == kern["tube_count"]
    assert _value(bell["U_calculated"]) < _value(kern["U_calculated"])
    assert _value(bell["U_clean"]) > _value(bell["U_calculated"])
