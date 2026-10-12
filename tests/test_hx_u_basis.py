"""specified_U (fixed) and assumed_U (starting guess) for the heat exchangers.

9f419f2 made a user `U` the design basis: the area was sized at it and U was
not iterated. The maintainer's answer on #98 is that a user U is "just a
starting point for the calculation of area", and that the two meanings should
be two keywords:

- ``specified_U`` fixes U. The area is sized at it and U is not iterated; the
  U calculated from the film coefficients is still reported, and a warning
  says when the two disagree enough to matter.
- ``assumed_U`` is the first guess of the U iteration, which then resizes the
  area at the calculated U until it converges, as without any U.

The plain ``U`` is read as ``assumed_U`` and warns with a DeprecationWarning.
The results say which basis was used in ``u_basis``.
"""

import contextlib
import functools
import io
import warnings

import pytest

from processpi.components import Benzene, OrganicLiquid, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import (
    HeatTransferCoefficient,
    MassFlowRate,
    Pressure,
    SpecificHeat,
    Temperature,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _streams():
    """docs/examples benzene cooler: benzene 21 000 kg/h 90 to 30 C, water 60 500 kg/h from 15 C."""
    return dict(
        hot_in=MaterialStream("hot_in", component=Benzene(),
                              temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(),
                               temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(),
                               temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
    )


def _engine(**specs):
    return HeatExchangerEngine(method="kern").fit(
        **_streams(), shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
        mode="design", **specs,
    )


@functools.lru_cache(maxsize=None)
def _design(keyword=None, u=None):
    """Design results of the benzene cooler with `keyword`=u W/m2K (None: no U)."""
    specs = {} if keyword is None else {keyword: HeatTransferCoefficient(u, "W/m2K")}
    return _quiet(_engine(**specs).run).data


def _w(value, unit):
    return value.to(unit).value


def _geometry(data):
    return (
        data["tube_count"],
        round(_w(data["tube_length"], "m"), 6),
        round(_w(data["shell_diameter"], "m"), 6),
        data["tube_passes"],
    )


def _q_watts(data):
    return _w(data["Q"], "W")


# ----------------------------------------------------------------------------
# specified_U: U fixed
# ----------------------------------------------------------------------------

def test_specified_u_sizes_the_area_at_q_over_u_f_lmtd():
    data = _design("specified_U", 575.0)
    required = _q_watts(data) / (575.0 * data["corrected_lmtd"])
    assert _w(data["Area_required"], "m2") == pytest.approx(required, rel=1e-9)
    # Every pass of the loop sized the area at the same U.
    areas = [row["value"] for row in data["calculation_trace"] if row["name"] == "Area required"]
    assert len(areas) >= 2
    assert areas == pytest.approx([required] * len(areas), rel=1e-9)


def test_specified_u_is_not_iterated():
    data = _design("specified_U", 575.0)
    assert _w(data["U_assumed"], "W/m2K") == pytest.approx(575.0)
    # The film coefficients give another U, reported beside the fixed one.
    u_calc = _w(data["U_calculated"], "W/m2K")
    assert abs(u_calc - 575.0) / 575.0 > 0.05
    # Each pass compares U_calc with the fixed U; none moves towards U_calc.
    history = data["convergence_history"]
    assert history[-1] == pytest.approx(abs(u_calc - 575.0) / 575.0 * 100.0, rel=1e-9)


def test_specified_u_is_reported():
    data = _design("specified_U", 575.0)
    assert data["u_basis"] == "specified"
    assert _w(data["U_specified"], "W/m2K") == pytest.approx(575.0)
    # U_user is the older name of the fixed U.
    assert _w(data["U_user"], "W/m2K") == pytest.approx(575.0)
    assert _w(data["U_initial"], "W/m2K") == pytest.approx(575.0)


def test_specified_u_reports_the_area_at_the_calculated_u():
    data = _design("specified_U", 575.0)
    u_calc = _w(data["U_calculated"], "W/m2K")
    at_u_calc = _q_watts(data) / (u_calc * data["corrected_lmtd"])
    assert _w(data["Area_required_at_U_calculated"], "m2") == pytest.approx(at_u_calc, rel=1e-9)
    assert data["thermal_ok_at_U_calculated"] == (_w(data["Area"], "m2") >= at_u_calc)


def test_specified_u_above_the_calculated_u_warns_and_keeps_its_basis():
    """At 1200 W/m2K the area is sized well short of what the film coefficients
    need. The status still judges the area against the U the user fixed, and a
    warning gives the area the calculated U needs."""
    data = _design("specified_U", 1200.0)
    u_calc = _w(data["U_calculated"], "W/m2K")
    assert u_calc < 1200.0
    assert data["thermal_ok_at_U_calculated"] is False
    assert _w(data["Area"], "m2") >= _w(data["Area_required"], "m2")
    assert data["status"] != "THERMAL_FAILURE"
    basis = [w for w in data["warnings"] if w.startswith("[U_BASIS_WARNING]")]
    assert len(basis) == 1
    assert "below specified_U 1200.0 W/m2K" in basis[0]
    assert {"category": "U_BASIS_WARNING", "message": basis[0].split("] ", 1)[1]} in data["warning_details"]


def test_specified_u_far_below_the_calculated_u_warns_of_the_extra_area():
    data = _design("specified_U", 300.0)
    assert _w(data["Area"], "m2") > 1.35 * _w(data["Area_required_at_U_calculated"], "m2")
    basis = [w for w in data["warnings"] if w.startswith("[U_BASIS_WARNING]")]
    assert len(basis) == 1
    assert "above specified_U 300.0 W/m2K" in basis[0]


def test_no_u_basis_warning_without_specified_u():
    for data in (_design(), _design("assumed_U", 575.0)):
        assert not [w for w in data["warnings"] if "U_BASIS_WARNING" in w]


# ----------------------------------------------------------------------------
# assumed_U: starting guess
# ----------------------------------------------------------------------------

def test_assumed_u_converges_to_the_design_without_u():
    free = _design()
    for start in (300.0, 1200.0):
        data = _design("assumed_U", start)
        assert data["converged"] is True
        assert _geometry(data) == _geometry(free)
        assert _w(data["U_calculated"], "W/m2K") == pytest.approx(
            _w(free["U_calculated"], "W/m2K"), rel=1e-9)
        assert _w(data["Area"], "m2") == pytest.approx(_w(free["Area"], "m2"), rel=1e-9)


def test_assumed_u_result_does_not_depend_on_the_start():
    low, high = _design("assumed_U", 300.0), _design("assumed_U", 1200.0)
    assert _w(low["U_initial"], "W/m2K") == pytest.approx(300.0)
    assert _w(high["U_initial"], "W/m2K") == pytest.approx(1200.0)
    # Different starting points, different paths ...
    assert low["convergence_history"] != high["convergence_history"]
    # ... to the same design.
    assert _geometry(low) == _geometry(high)
    assert _w(low["U_calculated"], "W/m2K") == pytest.approx(
        _w(high["U_calculated"], "W/m2K"), rel=1e-9)


def test_assumed_u_sizes_the_area_at_the_calculated_u():
    data = _design("assumed_U", 1200.0)
    u_calc = _w(data["U_calculated"], "W/m2K")
    required = _q_watts(data) / (u_calc * data["corrected_lmtd"])
    assert _w(data["Area_required"], "m2") == pytest.approx(required, rel=1e-9)
    assert _w(data["Area_required_at_U_calculated"], "m2") == pytest.approx(required, rel=1e-9)
    # The iteration left the starting guess.
    assert data["convergence_history"][-1] < 1.0
    assert _w(data["U_assumed"], "W/m2K") == pytest.approx(u_calc, rel=0.01)


def test_assumed_u_and_specified_u_give_different_designs():
    assumed, specified = _design("assumed_U", 575.0), _design("specified_U", 575.0)
    assert _geometry(assumed) != _geometry(specified)
    assert _w(assumed["Area_required"], "m2") != pytest.approx(
        _w(specified["Area_required"], "m2"), rel=1e-3)


def test_assumed_u_is_reported():
    data = _design("assumed_U", 575.0)
    assert data["u_basis"] == "assumed"
    assert data["U_specified"] is None
    assert data["U_user"] is None
    assert _w(data["U_initial"], "W/m2K") == pytest.approx(575.0)


def test_no_u_is_reported_as_calculated():
    data = _design()
    assert data["u_basis"] == "calculated"
    assert data["U_specified"] is None
    # The first pass starts from the tabulated U for the service.
    assert data["U_initial"] is not None


# ----------------------------------------------------------------------------
# The deprecated U
# ----------------------------------------------------------------------------

def test_plain_u_warns_and_names_both_keywords():
    with pytest.warns(DeprecationWarning) as record:
        engine = _engine(U=HeatTransferCoefficient(575, "W/m2K"))
    message = str(record[0].message)
    assert "assumed_U" in message and "specified_U" in message
    # Stored under its new name, so the exchanger built in run() does not warn again.
    assert "U" not in engine.data["specs"]
    assert engine.data["specs"]["assumed_U"].to("W/m2K").value == pytest.approx(575.0)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        _quiet(engine.run)


def test_plain_u_behaves_as_assumed_u():
    with pytest.warns(DeprecationWarning):
        engine = _engine(U=HeatTransferCoefficient(575, "W/m2K"))
    data = _quiet(engine.run).data
    assumed = _design("assumed_U", 575.0)
    assert data["u_basis"] == "assumed"
    assert _geometry(data) == _geometry(assumed)
    assert _w(data["U_calculated"], "W/m2K") == pytest.approx(
        _w(assumed["U_calculated"], "W/m2K"), rel=1e-12)
    assert data["convergence_history"] == pytest.approx(assumed["convergence_history"], rel=1e-12)


def test_plain_u_warns_on_the_exchanger_class_too():
    with pytest.warns(DeprecationWarning, match="assumed_U"):
        hx = ShellAndTubeHX(**_streams(), U=HeatTransferCoefficient(575, "W/m2K"))
    assert hx.specs.get("U") is None
    assert hx._u_basis() == "assumed"


def test_the_deprecation_points_at_the_caller():
    with pytest.warns(DeprecationWarning) as record:
        HeatExchangerEngine(**_streams(), U=HeatTransferCoefficient(575, "W/m2K"))
    assert record[0].filename == __file__


# ----------------------------------------------------------------------------
# Conflicts and values
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("pair", [
    ("specified_U", "assumed_U"),
    ("U", "specified_U"),
    ("U", "assumed_U"),
])
def test_two_u_keywords_raise(pair):
    specs = {key: HeatTransferCoefficient(575, "W/m2K") for key in pair}
    with pytest.raises(ValueError, match="only one of specified_U"):
        _engine(**specs)
    with pytest.raises(ValueError, match="only one of specified_U"):
        ShellAndTubeHX(**_streams(), **specs)


def test_a_none_u_keyword_is_not_a_conflict():
    engine = _engine(specified_U=HeatTransferCoefficient(575, "W/m2K"), assumed_U=None)
    assert engine.data["specs"]["specified_U"].to("W/m2K").value == pytest.approx(575.0)


def test_a_plain_number_is_read_in_w_per_m2k():
    data = _quiet(_engine(specified_U=575.0).run).data
    assert _geometry(data) == _geometry(_design("specified_U", 575.0))


@pytest.mark.parametrize("value", [0.0, -100.0])
def test_a_non_positive_u_raises(value):
    with pytest.raises(ValueError, match="specified_U must be a positive"):
        _quiet(_engine(specified_U=value).run)


# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------

def _line(summary, label):
    for line in summary.splitlines():
        if line.startswith(label):
            return line.split(":", 1)[1].strip()
    return None


def test_summary_shows_the_u_basis():
    engine = _engine(specified_U=HeatTransferCoefficient(575, "W/m2K"))
    summary = _quiet(engine.run).summary()
    assert _line(summary, "U Basis") == "specified"
    assert _line(summary, "U Specified") == "575.000 W/m2K"

    engine = _engine(assumed_U=HeatTransferCoefficient(575, "W/m2K"))
    summary = _quiet(engine.run).summary()
    assert _line(summary, "U Basis") == "assumed"
    assert _line(summary, "U Specified") is None


def test_debug_summary_carries_the_u_basis():
    engine = _engine(specified_U=HeatTransferCoefficient(575, "W/m2K"))
    debug = _quiet(engine.run).debug_summary()
    assert debug["u_basis"] == "specified"
    assert debug["u_values"]["U_specified"].to("W/m2K").value == pytest.approx(575.0)


# ----------------------------------------------------------------------------
# Rating
# ----------------------------------------------------------------------------

def _rate(**specs):
    streams = _streams()
    streams["cold_out"] = MaterialStream("cold_out", component=Water(),
                                         temperature=Temperature(25, "C"))
    engine = HeatExchangerEngine().fit(
        **streams, mode="rate", tube_od=0.01905, tube_id=0.016, tube_length=4.88,
        tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18, **specs,
    )
    return _quiet(engine.run).data


def test_rating_holds_the_area_to_specified_u():
    data = _rate(specified_U=HeatTransferCoefficient(575, "W/m2K"))
    assert data["u_basis"] == "specified"
    assert _w(data["U_specified"], "W/m2K") == pytest.approx(575.0)
    required = _q_watts(data) / (575.0 * data["corrected_lmtd"])
    assert _w(data["Area_required"], "m2") == pytest.approx(required, rel=1e-9)


def test_rating_with_assumed_u_does_not_report_a_fixed_u():
    data = _rate(assumed_U=HeatTransferCoefficient(575, "W/m2K"))
    assert data["u_basis"] == "assumed"
    assert data["U_specified"] is None
    assert data["U_user"] is None
    # The tube count still follows from the area at the U it was given.
    required = _q_watts(data) / (575.0 * data["corrected_lmtd"])
    assert _w(data["Area_required"], "m2") == pytest.approx(required, rel=1e-9)


# ----------------------------------------------------------------------------
# Double pipe
# ----------------------------------------------------------------------------

def _double_pipe(mode="design", **specs):
    """Kerosene 2 kg/s 120 to 80 C against water 1.5 kg/s from 20 C (test_unit_system H10)."""
    rate_geometry = dict(tube_od=0.0254, tube_id=0.021, tube_length=6.0,
                         annulus_diameter=0.05, area=10.0) if mode == "rate" else {}
    engine = HeatExchangerEngine(method="kern").fit(
        hot_in=MaterialStream("kerosene_in", component=OrganicLiquid(),
                              temperature=Temperature(120, "C"),
                              mass_flow=MassFlowRate(2, "kg/s"),
                              specific_heat=SpecificHeat(2470, "J/kgK")),
        hot_out=MaterialStream("kerosene_out", component=OrganicLiquid(),
                               temperature=Temperature(80, "C")),
        cold_in=MaterialStream("water_in", component=Water(),
                               temperature=Temperature(20, "C"),
                               mass_flow=MassFlowRate(1.5, "kg/s"),
                               specific_heat=SpecificHeat(4180, "J/kgK")),
        hx_type="double_pipe", mode=mode, **rate_geometry, **specs,
    )
    return _quiet(engine.run).data


def test_double_pipe_sizes_the_area_at_specified_u():
    data = _double_pipe(specified_U=HeatTransferCoefficient(500, "W/m2K"))
    assert data["u_basis"] == "specified"
    assert _w(data["U_specified"], "W/m2K") == pytest.approx(500.0)
    assert _w(data["Area"], "m2") == pytest.approx(_q_watts(data) / (500.0 * data["LMTD"]), rel=1e-9)
    assert not [w for w in data["warnings"] if "U_BASIS_WARNING" in w]


def test_double_pipe_says_assumed_u_is_not_iterated():
    data = _double_pipe(assumed_U=HeatTransferCoefficient(500, "W/m2K"))
    assert data["u_basis"] == "assumed"
    assert data["U_specified"] is None
    # No film-coefficient model in the double-pipe design: the area is sized at it.
    assert _w(data["Area"], "m2") == pytest.approx(_q_watts(data) / (500.0 * data["LMTD"]), rel=1e-9)
    assert any(w.startswith("[U_BASIS_WARNING]") and "not iterated" in w for w in data["warnings"])


def test_double_pipe_without_u_uses_its_default():
    data = _double_pipe()
    assert data["u_basis"] == "default"
    assert _w(data["U_calculated"], "W/m2K") == pytest.approx(350.0)


def test_double_pipe_rating_says_a_given_u_is_not_used():
    data = _double_pipe(mode="rate", specified_U=HeatTransferCoefficient(500, "W/m2K"))
    assert data["u_basis"] == "calculated"
    assert any("specified_U is not used" in w for w in data["warnings"])
