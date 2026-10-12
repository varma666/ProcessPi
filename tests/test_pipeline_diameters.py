"""Nominal and internal diameter are separate inputs; bare numbers warn (#108).

The maintainer's answer on varma666/ProcessPi#108: "yes i prefer nominal and
internal dia separate, and bare numbers are warned".

Before this change `fit()` took `nominal_diameter` and `internal_diameter` as
aliases of `diameter` and used the value as the bore, so a nominal 4 in pipe
was calculated on 101.6 mm instead of its 102.26 mm STD bore, and a bare
number was read as millimetres without a word.

Table values used here, ASME B36.10M-2015 Table 1:

    NPS 4 (DN 100): outside diameter 114.3 mm
        STD / schedule 40 wall 6.02 mm -> bore 114.3 - 2 x 6.02 = 102.26 mm
        XS  / schedule 80 wall 8.56 mm -> bore 114.3 - 2 x 8.56 =  97.18 mm

Hand calculation (NPS 4 STD, water at 25 C, 50 m3/h, 100 m of carbon steel):

    v  = (50/3600) / (pi/4 x 0.10226^2) = 1.69109 m/s
    Re = 188 498, f = 0.0186171 (Colebrook-White, 0.045 mm)
    dp = f (L/D) rho v^2 / 2 = 25 894 Pa
    on the nominal 101.6 mm taken as the bore it was 26 750 Pa (+3.3 %)
"""

import contextlib
import io
import math
import warnings

import pytest

from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, VolumetricFlowRate

Q = VolumetricFlowRate(50, "m3/h")
BORE_4IN_STD = 0.10226   # m, B36.10M: 114.3 - 2 x 6.02 mm
BORE_4IN_XS = 0.09718    # m, B36.10M: 114.3 - 2 x 8.56 mm
OD_4IN = 0.1143          # m


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _fit(**specs):
    return PipelineEngine().fit(fluid=Water(), flowrate=Q, **specs)


def _run(**specs):
    specs.setdefault("length", Length(100, "m"))
    return _quiet(_fit(**specs).run).results


@contextlib.contextmanager
def _record():
    """Every warning, recorded, with the default filters (once per call site)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("default")
        yield caught


def _messages(caught, category=Warning):
    return [str(w.message) for w in caught if issubclass(w.category, category)]


def _hand_dp(d_m, length_m=100.0):
    """Darcy-Weisbach with Colebrook-White, worked out here, not by the engine."""
    water = Water()
    rho = water.density().to("kg/m3").value
    mu = water.viscosity().value   # Pa s (the base unit)
    q = Q.to("m3/s").value
    v = q / (math.pi / 4.0 * d_m ** 2)
    re = rho * v * d_m / mu
    eps = 0.045e-3
    f = 0.02
    for _ in range(200):
        f = (-2.0 * math.log10(eps / (3.7 * d_m) + 2.51 / (re * math.sqrt(f)))) ** -2
    return f * (length_m / d_m) * rho * v * v / 2.0


# ---------------------------------------------------------------------------
# Nominal size: looked up through the schedule table
# ---------------------------------------------------------------------------

def test_pipe_nominal_resolves_to_the_tabulated_bore():
    std = Pipe("P", nominal_diameter=Diameter(4, "in"))
    xs = Pipe("P", nominal_diameter=Diameter(4, "in"), schedule="XS")
    assert std.nominal_diameter == Diameter(4, "in")
    assert std.internal_diameter.to("m").value == pytest.approx(BORE_4IN_STD, abs=1e-9)
    assert xs.internal_diameter.to("m").value == pytest.approx(BORE_4IN_XS, abs=1e-9)


def test_fit_nominal_resolves_with_the_schedule():
    # Was: the nominal 4 in itself, 101.6 mm, whatever the schedule.
    results = _run(nominal_diameter=Diameter(4, "in"), schedule="XS")
    assert results["summary"]["calculated_diameter_m"] == pytest.approx(BORE_4IN_XS, abs=1e-9)
    assert results["summary"]["nominal_diameter"] == Diameter(4, "in")


def test_nominal_size_given_as_dn_or_in_millimetres():
    from processpi.pipelines.standards import find_nominal_size

    assert find_nominal_size(Diameter(100, "mm")) == Diameter(4, "in")    # DN 100
    assert find_nominal_size(Diameter(101.6, "mm")) == Diameter(4, "in")  # NPS 4 in mm
    assert find_nominal_size(Diameter(15, "mm")) == Diameter(0.5, "in")   # DN 15
    assert find_nominal_size(Diameter(100.5, "mm")) is None
    pipe = Pipe("P", nominal_diameter=Diameter(100, "mm"))
    assert pipe.nominal_diameter == Diameter(4, "in")
    assert pipe.internal_diameter.to("m").value == pytest.approx(BORE_4IN_STD, abs=1e-9)


def test_every_tabulated_size_has_one_dn_and_no_dn_equals_an_nps():
    from processpi.pipelines import standards

    assert set(standards._NPS_TO_DN) == set(standards._PIPE_DIMENSIONS_MM)
    nps_mm = {round(nps * 25.4, 6) for nps in standards._NPS_TO_DN}
    assert not nps_mm & {float(dn) for dn in standards._NPS_TO_DN.values()}


def test_fit_nominal_with_an_untabulated_schedule_raises():
    with pytest.raises(ValueError, match="not tabulated"):
        _fit(nominal_diameter=Diameter(4, "in"), schedule="S35")


def test_non_standard_nominal_is_used_as_the_bore_with_a_warning():
    with _record() as caught:
        pipe = Pipe("P", nominal_diameter=Diameter(110, "mm"))
    assert pipe.internal_diameter == Diameter(110, "mm")   # as before
    assert any("not a standard pipe size" in m for m in _messages(caught, UserWarning))


# ---------------------------------------------------------------------------
# Internal diameter: used as given
# ---------------------------------------------------------------------------

def test_internal_diameter_is_used_as_is():
    pipe = Pipe("P", internal_diameter=Diameter(100, "mm"))
    assert pipe.nominal_diameter is None
    assert pipe.internal_diameter == Diameter(100, "mm")

    results = _run(internal_diameter=Diameter(100, "mm"))
    assert results["summary"]["calculated_diameter_m"] == pytest.approx(0.1, abs=1e-12)
    assert results["summary"]["nominal_diameter"] is None


# ---------------------------------------------------------------------------
# Both reported
# ---------------------------------------------------------------------------

def test_single_pipe_results_report_nominal_and_internal():
    results = _run(nominal_diameter=Diameter(4, "in"))
    comp = results["components"][0]
    assert comp["nominal_diameter"] == Diameter(4, "in")
    assert comp["diameter"].to("m").value == pytest.approx(BORE_4IN_STD, abs=1e-9)
    assert results["summary"]["calculated_diameter_m"] == pytest.approx(BORE_4IN_STD, abs=1e-9)


def test_summary_prints_and_returns_nominal_and_internal():
    results = _quiet(_fit(nominal_diameter=Diameter(4, "in"), length=Length(100, "m")).run)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        row = results.summary()[0]
    assert "Nominal Pipe Size: 4 in" in out.getvalue()
    assert "Internal Diameter: 102.26 mm" in out.getvalue()
    assert row["nominal_diameter_in"] == pytest.approx(4)
    assert row["pipe_diameter_m"] == pytest.approx(BORE_4IN_STD, abs=1e-9)


def test_network_element_reports_carry_the_nominal_size():
    p1 = Pipe("P1", nominal_diameter=Diameter(4, "in"), length=Length(100, "m"))
    p2 = Pipe("P2", internal_diameter=Diameter(100, "mm"), length=Length(50, "m"))
    results = _quiet(_fit(network=PipelineNetwork.series("S", p1, p2)).run).results
    comps = {c["name"]: c for c in results["components"]}
    assert comps["P1"]["nominal_diameter"] == Diameter(4, "in")
    assert comps["P1"]["diameter"].to("m").value == pytest.approx(BORE_4IN_STD, abs=1e-9)
    assert comps["P2"]["nominal_diameter"] is None
    assert comps["P2"]["diameter"] == Diameter(100, "mm")


def test_pipe_describe_to_dict_and_surface_area_use_the_right_diameter():
    pipe = Pipe("P", nominal_diameter=Diameter(4, "in"), length=Length(10, "m"))
    net = PipelineNetwork("N")
    net.add_node("A")
    net.add_node("B")
    net.add_edge(pipe, "A", "B")
    # Was "Pipe: 4 in mm, L=10 m m".
    assert "Pipe: nominal 4 in, ID 102.26 mm, L=10 m" in net.describe()
    # Was AttributeError: the unit classes have no to_dict.
    d = pipe.to_dict()
    assert d["nominal_diameter"] == {"value": 4, "units": "in"}
    assert d["internal_diameter"]["value"] == pytest.approx(102.26)
    # External area on the 114.3 mm outside diameter (was the 101.6 mm nominal).
    assert pipe.surface_area().value == pytest.approx(3.14159 * OD_4IN * 10.0)


# ---------------------------------------------------------------------------
# Nominal and internal both given
# ---------------------------------------------------------------------------

def test_both_given_the_internal_diameter_is_used():
    # A lined 4 in pipe: the bore given replaces the tabulated one.
    pipe = Pipe("P", nominal_diameter=Diameter(4, "in"), internal_diameter=Diameter(95, "mm"))
    assert pipe.nominal_diameter == Diameter(4, "in")
    assert pipe.internal_diameter == Diameter(95, "mm")

    results = _run(nominal_diameter=Diameter(4, "in"), internal_diameter=Diameter(95, "mm"))
    assert results["summary"]["calculated_diameter_m"] == pytest.approx(0.095, abs=1e-12)
    assert results["summary"]["nominal_diameter"] == Diameter(4, "in")


def test_both_given_a_bore_that_does_not_fit_the_size_raises():
    # 120 mm cannot be the bore of a 114.3 mm OD pipe; the usual cause is a
    # nominal size given as the internal diameter or the other way round.
    with pytest.raises(ValueError, match="does not fit"):
        Pipe("P", nominal_diameter=Diameter(4, "in"), internal_diameter=Diameter(120, "mm"))
    with pytest.raises(ValueError, match="does not fit"):
        _fit(nominal_diameter=Diameter(4, "in"), internal_diameter=Diameter(OD_4IN, "m"))


def test_diameter_and_internal_diameter_that_disagree_raise():
    with _record() as caught, pytest.raises(ValueError, match="disagree"):
        _fit(diameter=Diameter(100, "mm"), internal_diameter=Diameter(102, "mm"))
    assert _messages(caught, DeprecationWarning)


# ---------------------------------------------------------------------------
# The old `diameter` keyword
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", ["diameter", "dia", "D"])
def test_fit_diameter_keeps_meaning_the_bore_and_is_deprecated(key):
    with _record() as caught:
        engine = _fit(length=Length(100, "m"), **{key: Diameter(4, "in")})
    assert any("taken as the internal diameter" in m
               for m in _messages(caught, DeprecationWarning))
    # The bore, not a nominal size: 4 in = 101.6 mm, as before.
    assert engine.internal_diameter.to("m").value == pytest.approx(0.1016, abs=1e-12)
    assert engine.nominal_diameter is None
    results = _quiet(engine.run).results
    assert results["summary"]["calculated_diameter_m"] == pytest.approx(0.1016, abs=1e-12)


def test_pipe_diameter_keyword_is_still_ignored_but_warns():
    with _record() as caught:
        pipe = Pipe("P", diameter=Diameter(4, "in"))
    assert pipe.internal_diameter is None and pipe.nominal_diameter is None
    assert pipe.is_optimization_target
    assert pipe.params["diameter"] == Diameter(4, "in")
    assert any("has no `diameter` input" in m for m in _messages(caught, UserWarning))


# ---------------------------------------------------------------------------
# Bare numbers: the old unit, with a warning that names it
# ---------------------------------------------------------------------------

def test_fit_bare_diameter_is_millimetres_with_a_warning():
    with _record() as caught:
        engine = _fit(internal_diameter=102.26, length=Length(100, "m"))
    assert engine.internal_diameter.to("m").value == pytest.approx(BORE_4IN_STD, abs=1e-12)
    assert any("bare number" in m and "millimetres" in m
               for m in _messages(caught, UserWarning))


def test_fit_bare_diameter_is_metres_when_assume_mm_is_off():
    with _record() as caught:
        engine = _fit(internal_diameter=0.10226, assume_mm_for_numbers=False,
                      length=Length(100, "m"))
    assert engine.internal_diameter.to("m").value == pytest.approx(BORE_4IN_STD, abs=1e-12)
    assert any("bare number" in m and "metres" in m for m in _messages(caught, UserWarning))


def test_fit_bare_length_is_metres_with_a_warning():
    with _record() as caught:
        results = _run(internal_diameter=Diameter(BORE_4IN_STD, "m"), length=100)
    assert any("length was given as a bare number" in m and "metres" in m
               for m in _messages(caught, UserWarning))
    assert results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        _hand_dp(BORE_4IN_STD), rel=1e-4)


def test_pipe_bare_numbers_are_metres_with_a_warning():
    with _record() as caught:
        pipe = Pipe("P", internal_diameter=0.1, length=10)
    msgs = _messages(caught, UserWarning)
    assert any("Pipe internal_diameter" in m and "metres" in m for m in msgs)
    assert any("Pipe length" in m and "metres" in m for m in msgs)
    assert pipe.internal_diameter == Diameter(0.1, "m")
    assert pipe.length == Length(10, "m")


def test_bare_number_warning_is_once_per_call_site_and_points_at_it():
    with _record() as caught:
        for _ in range(5):
            Pipe("P", length=3)
    lengths = [w for w in caught if "Pipe length" in str(w.message)]
    assert len(lengths) == 1
    assert lengths[0].filename == __file__


def test_unit_objects_raise_no_warning():
    with _record() as caught:
        _run(nominal_diameter=Diameter(4, "in"))
        Pipe("P", nominal_diameter=Diameter(4, "in"), length=Length(10, "m"))
    assert _messages(caught, UserWarning) == []
    assert _messages(caught, DeprecationWarning) == []


# ---------------------------------------------------------------------------
# The calculations use the bore
# ---------------------------------------------------------------------------

def test_pressure_drop_is_calculated_on_the_bore():
    results = _run(nominal_diameter=Diameter(4, "in"))
    dp = results["summary"]["total_pressure_drop_Pa"]
    assert dp == pytest.approx(_hand_dp(BORE_4IN_STD), rel=1e-4)
    assert dp == pytest.approx(25894, rel=1e-4)
    # The nominal size taken as the bore (the old behaviour) is 3.3 % higher.
    assert _hand_dp(0.1016) == pytest.approx(26750, rel=1e-4)


def test_flow_from_velocity_uses_the_bore():
    engine = PipelineEngine().fit(fluid=Water(), velocity=2.0,
                                  nominal_diameter=Diameter(4, "in"))
    q = engine._infer_flowrate().to("m3/s").value
    assert q == pytest.approx(2.0 * math.pi / 4.0 * BORE_4IN_STD ** 2, rel=1e-12)


def test_nominal_set_on_a_pipe_after_it_is_built_is_looked_up():
    pipe = Pipe("P", length=Length(100, "m"))
    pipe.nominal_diameter = Diameter(4, "in")
    pipe.schedule = "XS"
    bore = _fit()._resolve_internal_diameter(pipe)
    assert bore.to("m").value == pytest.approx(BORE_4IN_XS, abs=1e-9)
