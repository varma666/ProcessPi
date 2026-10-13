"""Fitting losses: the higher of the K-factor and Le/D methods (#108).

The engine used to reach only the equivalent-length (Le/D) data for a
`Fitting`, because `Fitting.equivalent_length` always exists; the K_FACTORS
table was used only for fittings missing from EQUIVALENT_LENGTHS, and then
without the quantity. The two tables disagree by up to about 60% (one 90 deg
elbow in 4 in STD, water 50 m3/h: 794 Pa by Le/D, 1280 Pa by K). The
maintainer's rule on #108: check both and use the higher. It is applied per
fitting, and every route (single pipe, sizing, series and parallel networks)
goes through `_pipe_calculation`, so they agree.

Hand calculation used throughout (4 in STD, water at 25 C, 50 m3/h):

    D   = 0.10226 m                     (4 in STD bore)
    A   = pi/4 * D^2 = 0.0082130 m2
    v   = (50/3600) / A = 1.69109 m/s
    rho = 994.679 kg/m3                 (Water() at 25 C)
    rho v^2 / 2 = 1422.28 Pa
    Re  = 188 498, f = 0.0186171        (Colebrook-White, CS 0.045 mm)
"""

import contextlib
import io
import math

import pytest

from processpi.components import Water
from processpi.pipelines import standards
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, Pressure, Velocity, VolumetricFlowRate

Q = VolumetricFlowRate(50, "m3/h")
D_4IN_STD = 0.10226


def _engine(**specs):
    return PipelineEngine().fit(fluid=Water(), flowrate=Q, length=Length(100, "m"), **specs)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _pipe(name="P", length=100.0, fittings=(), nominal_in=4):
    pipe = Pipe(name, nominal_diameter=Diameter(nominal_in, "in"), length=Length(length, "m"))
    pipe.fittings = list(fittings)
    return pipe


def _dynamic_pressure():
    """rho v^2 / 2 in 4 in STD at 50 m3/h, worked out here, not by the engine."""
    rho = Water().density().to("kg/m3").value
    v = Q.to("m3/s").value / (math.pi / 4.0 * D_4IN_STD ** 2)
    return 0.5 * rho * v * v


def _pipe_f():
    """The Darcy f of the bare 4 in pipe (the Le/D method uses the pipe's f)."""
    calc = _engine()._pipe_calculation(_pipe(), Q)
    return calc["friction_factor"].value


# ----------------------------------------------------------------------------
# Each method on its own, and the higher one counted
# ----------------------------------------------------------------------------

def test_elbow_both_methods_by_hand_and_k_governs():
    # K:    0.9 * 1422.28              = 1280.05 Pa
    # Le/D: 0.0186171 * 30 * 1422.28   =  794.36 Pa  -> K governs
    calc = _engine()._pipe_calculation(_pipe(fittings=[Fitting("standard_elbow_90_deg")]), Q)
    loss = calc["fitting_losses"][0]
    dyn, f = _dynamic_pressure(), _pipe_f()

    assert loss["dp_k_Pa"] == pytest.approx(0.9 * dyn, rel=1e-4)
    assert loss["dp_le_Pa"] == pytest.approx(f * 30 * dyn, rel=1e-4)
    assert loss["dp_k_Pa"] == pytest.approx(1280.05, rel=1e-4)
    assert loss["dp_le_Pa"] == pytest.approx(794.36, rel=1e-4)
    assert loss["fitting_method"] == "K"
    assert loss["dp_Pa"] == loss["dp_k_Pa"]
    assert loss["k_factor"] == 0.9
    assert loss["le_over_d"] == 30
    assert calc["minor_dp_pa"] == pytest.approx(loss["dp_k_Pa"], rel=1e-12)


def test_lift_check_valve_le_over_d_governs():
    # K:    10 * 1422.28               = 14222.8 Pa
    # Le/D: 0.0186171 * 600 * 1422.28  = 15887.3 Pa  -> Le/D governs
    calc = _engine()._pipe_calculation(_pipe(fittings=[Fitting("lift_check_valve")]), Q)
    loss = calc["fitting_losses"][0]
    dyn, f = _dynamic_pressure(), _pipe_f()

    assert loss["dp_k_Pa"] == pytest.approx(10.0 * dyn, rel=1e-4)
    assert loss["dp_le_Pa"] == pytest.approx(f * 600 * dyn, rel=1e-4)
    assert loss["dp_le_Pa"] == pytest.approx(15887.3, rel=1e-4)
    assert loss["fitting_method"] == "Le/D"
    assert calc["minor_dp_pa"] == pytest.approx(loss["dp_le_Pa"], rel=1e-12)


def test_the_choice_is_made_per_fitting():
    # Four elbows (K: 4 * 1280.05 = 5120.2 Pa, Le/D 3177.5 Pa) plus one lift
    # check valve (Le/D 15887.3 Pa, K 14222.8 Pa):
    #   per fitting: 5120.2 + 15887.3 = 21007.5 Pa
    #   (K on the total would give 19343.0 Pa, Le/D on the total 19064.7 Pa)
    fittings = [Fitting("standard_elbow_90_deg", quantity=4), Fitting("lift_check_valve")]
    calc = _engine()._pipe_calculation(_pipe(fittings=fittings), Q)
    elbows, check = calc["fitting_losses"]
    dyn, f = _dynamic_pressure(), _pipe_f()

    assert elbows["fitting_method"] == "K"
    assert check["fitting_method"] == "Le/D"
    expected = 4 * 0.9 * dyn + f * 600 * dyn
    assert calc["minor_dp_pa"] == pytest.approx(expected, rel=1e-4)
    assert calc["minor_dp_pa"] == pytest.approx(21007.5, rel=1e-4)
    assert calc["pressure_drop"].to("Pa").value == pytest.approx(
        calc["major_dp_pa"] + calc["minor_dp_pa"] + calc["elevation_dp_pa"], rel=1e-12)


def test_the_comparison_uses_the_friction_factor_given():
    # Same elbow and velocity, laminar-like f = 0.064 (64/Re at Re = 1000):
    # Le/D: 0.064 * 30 * 1422.28 = 2730.8 Pa > K 1280.05 Pa -> Le/D governs.
    eng = _engine()
    v = Velocity(Q.to("m3/s").value / (math.pi / 4.0 * D_4IN_STD ** 2), "m/s")
    loss = eng._fitting_loss(Fitting("standard_elbow_90_deg"), v, 0.064, Diameter(D_4IN_STD, "m"))
    assert loss["dp_le_Pa"] == pytest.approx(0.064 * 30 * _dynamic_pressure(), rel=1e-6)
    assert loss["fitting_method"] == "Le/D"
    dp = eng._minor_dp_pa(Fitting("standard_elbow_90_deg"), v, 0.064, Diameter(D_4IN_STD, "m"))
    assert dp.to("Pa").value == pytest.approx(loss["dp_le_Pa"], rel=1e-12)


# ----------------------------------------------------------------------------
# Data in one table only, quantity, user values
# ----------------------------------------------------------------------------

def test_k_only_fitting_uses_k_times_the_quantity():
    # "exit" is in K_FACTORS (1.0) only: 2 * 1.0 * 1422.28 = 2844.56 Pa.
    # The quantity used to be dropped on this route (1422.28 Pa).
    assert "exit" not in standards.EQUIVALENT_LENGTHS
    calc = _engine()._pipe_calculation(_pipe(fittings=[Fitting("exit", quantity=2)]), Q)
    loss = calc["fitting_losses"][0]
    assert loss["dp_le_Pa"] is None
    assert loss["fitting_method"] == "K"
    assert calc["minor_dp_pa"] == pytest.approx(2 * 1.0 * _dynamic_pressure(), rel=1e-4)
    assert calc["minor_dp_pa"] == pytest.approx(2844.56, rel=1e-4)


def test_le_over_d_only_fitting_uses_le_over_d(monkeypatch):
    # Every EQUIVALENT_LENGTHS entry is also in K_FACTORS today, so add one:
    # Le/D = 50 -> 0.0186171 * 50 * 1422.28 = 1323.9 Pa.
    monkeypatch.setitem(standards.EQUIVALENT_LENGTHS, "le_only_test_fitting", 50)
    calc = _engine()._pipe_calculation(_pipe(fittings=[Fitting("le_only_test_fitting")]), Q)
    loss = calc["fitting_losses"][0]
    assert loss["dp_k_Pa"] is None
    assert loss["fitting_method"] == "Le/D"
    assert calc["minor_dp_pa"] == pytest.approx(_pipe_f() * 50 * _dynamic_pressure(), rel=1e-4)


def test_unknown_fitting_reports_no_method():
    with pytest.warns(UserWarning, match="no_such_fitting"):
        calc = _engine()._pipe_calculation(_pipe(fittings=[Fitting("no_such_fitting")]), Q)
    loss = calc["fitting_losses"][0]
    assert loss["fitting_method"] is None
    assert loss["dp_Pa"] == 0.0
    assert calc["minor_dp_pa"] == 0.0


def test_a_k_set_on_the_fitting_overrides_the_tables():
    # K = 0.3 given: 0.3 * 1422.28 = 426.7 Pa, used even though the tables give
    # more (K 1280.05, Le/D 794.4 Pa).
    elbow = Fitting("standard_elbow_90_deg", quantity=2)
    elbow.K = 0.3
    calc = _engine()._pipe_calculation(_pipe(fittings=[elbow]), Q)
    loss = calc["fitting_losses"][0]
    assert loss["data_source"] == "given"
    assert loss["fitting_method"] == "K"
    assert loss["dp_le_Pa"] is None
    # K is per unit, so the quantity applies: 2 * 426.7 = 853.4 Pa.
    assert calc["minor_dp_pa"] == pytest.approx(2 * 0.3 * _dynamic_pressure(), rel=1e-4)


def test_a_given_k_and_le_take_the_higher():
    # K = 0.3 (426.7 Pa) and Le = 3 m (Le/D = 29.34, 0.0186171 * 29.34 * 1422.28
    # = 776.8 Pa) both given: Le/D governs.
    elbow = Fitting("standard_elbow_90_deg")
    elbow.K = 0.3
    elbow.Le = Length(3.0, "m")
    calc = _engine()._pipe_calculation(_pipe(fittings=[elbow]), Q)
    loss = calc["fitting_losses"][0]
    assert loss["fitting_method"] == "Le/D"
    assert loss["le_over_d"] == pytest.approx(3.0 / D_4IN_STD, rel=1e-9)
    assert calc["minor_dp_pa"] == pytest.approx(
        _pipe_f() * (3.0 / D_4IN_STD) * _dynamic_pressure(), rel=1e-4)


# ----------------------------------------------------------------------------
# Every route counts the same loss
# ----------------------------------------------------------------------------

def _sizing_fittings():
    return [Fitting("globe_valve", quantity=2), Fitting("standard_elbow_90_deg", quantity=6)]


def test_sizing_and_run_agree_and_use_the_higher_loss():
    # 2 globe valves + 6 elbows, available 50 kPa. Per fitting K governs:
    #   globe 10 > 340 * 0.0186 = 6.33, elbow 0.9 > 30 * 0.0186 = 0.56
    #   4 in: major 25 893.6 + minor 25.4 * 1422.28 = 36 125.9 -> 62 019.5 Pa > 50 kPa
    #   5 in: (D = 0.12819 m, v = 1.0762 m/s, rho v^2/2 = 575.8 Pa)
    #         major 8 367.4 + minor 25.4 * 575.8 = 14 624.8 -> 22 992.2 Pa
    sized = _quiet(_engine(available_dp=Pressure(50000, "Pa"), fittings=_sizing_fittings()).run)
    s = sized.results["summary"]
    comp = sized.results["components"][0]
    assert s["nominal_diameter"] == Diameter(5, "in")
    assert s["total_pressure_drop_Pa"] == pytest.approx(22992.2, rel=1e-4)
    assert [x["fitting_method"] for x in comp["fitting_losses"]] == ["K", "K"]

    ran = _quiet(_engine(internal_diameter=Diameter(s["calculated_diameter_m"], "m"),
                         fittings=_sizing_fittings()).run)
    r = ran.results
    assert r["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        s["total_pressure_drop_Pa"], rel=1e-9)
    assert r["components"][0]["minor_dp"].to("Pa").value == pytest.approx(
        comp["minor_dp"].to("Pa").value, rel=1e-9)
    assert [x["fitting_method"] for x in r["components"][0]["fitting_losses"]] == ["K", "K"]


def test_series_network_total_includes_the_higher_losses():
    # P1: 100 m, 4 elbows   -> K governs,    minor 5 120.2 Pa
    # P2:  50 m, 1 lift check -> Le/D governs, minor 15 887.3 Pa
    # Network total = sum of element totals, each with its own minor loss.
    p1 = _pipe("P1", 100.0, [Fitting("standard_elbow_90_deg", quantity=4)])
    p2 = _pipe("P2", 50.0, [Fitting("lift_check_valve")])
    net = PipelineNetwork.series("S", p1, p2)
    res = _quiet(_engine(network=net).run).results
    comps = {c["name"]: c for c in res["components"]}
    dyn, f = _dynamic_pressure(), _pipe_f()

    assert comps["P1"]["fitting_losses"][0]["fitting_method"] == "K"
    assert comps["P2"]["fitting_losses"][0]["fitting_method"] == "Le/D"
    assert comps["P1"]["minor_dp"].to("Pa").value == pytest.approx(4 * 0.9 * dyn, rel=1e-4)
    assert comps["P2"]["minor_dp"].to("Pa").value == pytest.approx(f * 600 * dyn, rel=1e-4)
    total = sum(c["total_dp"].to("Pa").value for c in res["components"])
    assert res["summary"]["total_pressure_drop_Pa"] == pytest.approx(total, rel=1e-9)

    # Single-pipe run of P1 alone gives the same element drop.
    single = _quiet(_engine(internal_diameter=Diameter(D_4IN_STD, "m"),
                            fittings=[Fitting("standard_elbow_90_deg", quantity=4)]).run)
    assert single.results["summary"]["total_pressure_drop_Pa"] == pytest.approx(
        comps["P1"]["total_dp"].to("Pa").value, rel=1e-6)


def test_parallel_branches_use_the_higher_loss_at_their_own_flow():
    # Two 4 in branches, one with a globe valve (K governs: 10 > 340 f), one with
    # a lift check valve (Le/D governs: 600 f > 10). Each branch's minor loss is
    # the higher one at the flow the solver gives that branch.
    a = _pipe("A", 100.0, [Fitting("globe_valve")])
    b = _pipe("B", 100.0, [Fitting("lift_check_valve")])
    net = PipelineNetwork.parallel("PAR", a, b)
    eng = PipelineEngine().fit(fluid=Water(), flowrate=VolumetricFlowRate(100, "m3/h"), network=net)
    res = _quiet(eng.run).results
    comps = {c["name"]: c for c in res["components"]}
    rho = Water().density().to("kg/m3").value

    for name, k, le_d, method in (("A", 10.0, 340, "K"), ("B", 10.0, 600, "Le/D")):
        c = comps[name]
        v = c["flow_m3s"] / (math.pi / 4.0 * D_4IN_STD ** 2)
        dyn = 0.5 * rho * v * v
        f = c["friction_factor"].value
        loss = c["fitting_losses"][0]
        assert loss["fitting_method"] == method
        assert c["minor_dp"].to("Pa").value == pytest.approx(max(k * dyn, f * le_d * dyn), rel=1e-4)
