"""Regression tests for the Kern shell-side geometry and the overall U build-up.

The shell side was described by three different cross-flow areas and by the
square-pitch equivalent diameter while the default layout is triangular, so the
velocity fed to a correlation was not the velocity that correlation assumes.
The overall U used the plane-wall resistance, put the fouling factors on the
wrong sides, and left the tube fouling un-referred to the outside area.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import (
    HeatTransferCoefficient,
    MassFlowRate,
    Pressure,
    Temperature,
)

TUBE_OD = 0.019
TUBE_ID = 0.015
TUBE_PITCH = 1.25 * TUBE_OD
TUBE_WALL_K = 45.0

GEOMETRY = {
    "tube_od": TUBE_OD,
    "tube_id": TUBE_ID,
    "tube_pitch": TUBE_PITCH,
    "tube_count": 138,
    "tube_length": 3.0,
}


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _hx(hot_flow_kg_h=21000.0, cold_flow_kg_h=60500.0, **specs):
    """The benzene cooler from docs/examples, with adjustable flows."""
    hot_in = MaterialStream("hot_in", component=Benzene(),
                            temperature=Temperature(90, "C"),
                            mass_flow=MassFlowRate(hot_flow_kg_h, "kg/h"))
    hot_out = MaterialStream("hot_out", component=Benzene(),
                             temperature=Temperature(30, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(15, "C"),
                             mass_flow=MassFlowRate(cold_flow_kg_h, "kg/h"))
    cold_out = MaterialStream("cold_out", component=Water())
    defaults = dict(U=HeatTransferCoefficient(575, "W/m2K"),
                    shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
                    mode="design")
    defaults.update(specs)
    return ShellAndTubeHX(hot_in=hot_in, cold_in=cold_in, hot_out=hot_out,
                          cold_out=cold_out, method="kern", **defaults)


def _kern_de_triangular(pitch, od):
    return 4.0 * (math.sqrt(3.0) / 4.0 * pitch ** 2 - math.pi * od ** 2 / 8.0) / (math.pi * od / 2.0)


def _kern_de_square(pitch, od):
    return 4.0 * (pitch ** 2 - math.pi * od ** 2 / 4.0) / (math.pi * od)


def _kern_crossflow_area(ds, baffle, pitch, od):
    return (pitch - od) * ds * baffle / pitch


def test_equivalent_diameter_follows_the_bundle_layout():
    hx = _hx()
    assert hx._shell_equivalent_diameter(TUBE_PITCH, TUBE_OD, "triangular") == pytest.approx(
        _kern_de_triangular(TUBE_PITCH, TUBE_OD)
    )
    assert hx._shell_equivalent_diameter(TUBE_PITCH, TUBE_OD, "square") == pytest.approx(
        _kern_de_square(TUBE_PITCH, TUBE_OD)
    )
    # The two differ by more than a third, so picking the wrong one matters.
    assert _kern_de_square(TUBE_PITCH, TUBE_OD) > 1.3 * _kern_de_triangular(TUBE_PITCH, TUBE_OD)


def test_default_layout_is_triangular_and_is_used():
    """The default layout is triangular, so the correlations must use its De."""
    hx = _hx()
    assert hx._get_standard_layout() == "triangular"

    dimless = _quiet(
        hx._calculate_dimensionless,
        dict(GEOMETRY, shell_diameter=0.5),
        hx._stream_props(hx.hot_in),
        hx._stream_props(hx.cold_in),
        1.5,
        1.0,
    )
    assert dimless["de_shell"] == pytest.approx(_kern_de_triangular(TUBE_PITCH, TUBE_OD))


def test_square_layout_is_honoured():
    hx = _hx(tube_layout="square")
    dimless = _quiet(
        hx._calculate_dimensionless,
        dict(GEOMETRY, shell_diameter=0.5),
        hx._stream_props(hx.hot_in),
        hx._stream_props(hx.cold_in),
        1.5,
        1.0,
    )
    assert dimless["de_shell"] == pytest.approx(_kern_de_square(TUBE_PITCH, TUBE_OD))


def test_one_shell_crossflow_area_everywhere():
    """The velocity check and the pressure drop routine must agree on the area."""
    hx = _hx()
    shell_diameter = 0.9532
    baffle = 0.4 * shell_diameter
    expected = _kern_crossflow_area(shell_diameter, baffle, TUBE_PITCH, TUBE_OD)

    assert hx._shell_crossflow_area(shell_diameter, baffle, TUBE_PITCH, TUBE_OD) == pytest.approx(
        expected
    )

    cold = hx._stream_props(hx.cold_in)
    _, v_shell, _, ds_out, _ = _quiet(
        hx._check_velocities, GEOMETRY, hx._stream_props(hx.hot_in), cold, 2, 1, shell_diameter
    )
    area_used = (cold["m_dot"] / cold["density"]) / v_shell
    assert area_used == pytest.approx(
        _kern_crossflow_area(ds_out, 0.4 * ds_out, TUBE_PITCH, TUBE_OD), rel=1e-9
    )


def test_shell_velocity_belongs_to_the_shell_diameter_returned():
    """A shell diameter adjustment must carry its velocity with it."""
    # A very large cold flow keeps the velocity above the limit for all 10 passes,
    # so the loop ends on an adjustment rather than on a break.
    hx = _hx(cold_flow_kg_h=6_000_000.0)
    cold = hx._stream_props(hx.cold_in)

    _, v_shell, _, ds_out, _ = _quiet(
        hx._check_velocities, GEOMETRY, hx._stream_props(hx.hot_in), cold, 2, 1, 0.5
    )

    area = hx._shell_crossflow_area(ds_out, 0.4 * ds_out, TUBE_PITCH, TUBE_OD)
    assert v_shell == pytest.approx((cold["m_dot"] / cold["density"]) / area, rel=1e-9)
    assert ds_out > 0.5  # it did adjust
    assert any("HYDRAULIC_WARNING" in w for w in hx._warnings)


def test_tube_wall_resistance_is_the_cylindrical_form():
    hx = _hx()
    result = _quiet(
        hx._calculate_overall_U,
        h_t=2000.0,
        h_s=3000.0,
        geometry={"tube_od": TUBE_OD, "tube_id": TUBE_ID},
    )
    r_wall_cylindrical = TUBE_OD * math.log(TUBE_OD / TUBE_ID) / (2.0 * TUBE_WALL_K)
    r_wall_plane = (TUBE_OD - TUBE_ID) / 2.0 / TUBE_WALL_K
    r_tube = 1.0 / (2000.0 * TUBE_ID / TUBE_OD)
    r_shell = 1.0 / 3000.0

    assert result["R_total_clean"] == pytest.approx(r_tube + r_shell + r_wall_cylindrical)
    assert r_wall_cylindrical != pytest.approx(r_wall_plane)


def test_tube_fouling_is_referred_to_the_outside_area():
    hx = _hx()
    result = _quiet(
        hx._calculate_overall_U,
        h_t=2000.0,
        h_s=3000.0,
        geometry={"tube_od": TUBE_OD, "tube_id": TUBE_ID},
    )
    from processpi.equipment.heatexchangers.standards import get_fouling_factor

    assert result["R_total_dirty"] == pytest.approx(
        result["R_total_clean"] + result["Rf_tube"] + result["Rf_shell"]
    )

    raw = get_fouling_factor(
        fluid_key=hx.hot_in.component.hx_data()["fouling_key"],
        velocity=None,
        temperature=hx._safe_float(hx.hot_in.temperature.to("C"), "t"),
    )
    # The tube-side film already carries do/di; its fouling must too.
    assert result["Rf_tube"] == pytest.approx(raw * TUBE_OD / TUBE_ID)
    assert result["Rf_tube"] != pytest.approx(raw)


def test_fouling_factors_sit_on_the_side_that_carries_the_fluid():
    """The calculation models the hot stream in the tubes, so its fouling is Rf_tube."""
    from processpi.equipment.heatexchangers.standards import get_fouling_factor

    hx = _hx()
    result = _quiet(
        hx._calculate_overall_U,
        h_t=2000.0,
        h_s=3000.0,
        geometry={"tube_od": TUBE_OD, "tube_id": TUBE_ID},
    )
    hot_fouling = get_fouling_factor(
        fluid_key=hx.hot_in.component.hx_data()["fouling_key"],
        velocity=None,
        temperature=hx._safe_float(hx.hot_in.temperature.to("C"), "t"),
    )
    cold_fouling = get_fouling_factor(
        fluid_key=hx.cold_in.component.hx_data()["fouling_key"],
        velocity=None,
        temperature=hx._safe_float(hx.cold_in.temperature.to("C"), "t"),
    )
    assert result["Rf_tube"] == pytest.approx(hot_fouling * TUBE_OD / TUBE_ID)
    assert result["Rf_shell"] == pytest.approx(cold_fouling)


def test_tube_side_pressure_drop_includes_the_return_losses():
    hx = _hx()
    hot = hx._stream_props(hx.hot_in)
    v_tube, tube_passes = 1.5, 2

    tube_dp, _ = _quiet(
        hx._calculate_pressure_drop,
        geometry=GEOMETRY, tube=hot, shell=hx._stream_props(hx.cold_in),
        shell_velocity=1.0, tube_velocity=v_tube, tube_passes=tube_passes,
        shell_diameter=0.5, tube_length=3.0, tube_id=TUBE_ID,
    )

    velocity_head = hot["density"] * v_tube ** 2 / 2.0
    re = hot["density"] * v_tube * TUBE_ID / hot["viscosity"]
    f = 16.0 / re if re < 2100 else 0.079 / re ** 0.25
    friction = 4.0 * f * (3.0 * tube_passes / TUBE_ID) * velocity_head

    assert tube_dp == pytest.approx(friction + 4.0 * tube_passes * velocity_head)
    assert tube_dp > friction


def test_dittus_boelter_exponent_is_the_cooling_one():
    """The tube side carries the stream being cooled, so n = 0.3."""
    from processpi.calculations.heat_transfer import DittusBoelter

    hx = _hx()
    hot = hx._stream_props(hx.hot_in)
    dimless = _quiet(
        hx._calculate_dimensionless,
        dict(GEOMETRY, shell_diameter=0.5), hot, hx._stream_props(hx.cold_in), 1.5, 1.0,
    )
    expected = DittusBoelter(
        reynolds=max(dimless["re_t"], 1.0), prandtl=dimless["pr_t"], n=0.3
    ).calculate()
    assert dimless["nu_t"] == pytest.approx(expected)


def test_reported_sides_are_the_sides_that_were_modelled():
    """The report must not name a tube-side fluid the calculation did not use.

    The scoring puts the water in the tubes here, and the assignment now drives
    the calculation, so the water is both the reported and the modelled
    tube-side fluid and there is no disagreement to warn about.
    """
    hx = _hx()
    hot = hx._stream_props(hx.hot_in)
    cold = hx._stream_props(hx.cold_in)
    assignment = _quiet(hx._assign_fluids_to_sides, hot, cold)
    assert assignment["tube_side_fluid"] == hx.cold_in.component.name
    assert assignment["shell_side_fluid"] == hx.hot_in.component.name
    assert assignment["recommended_tube_side_fluid"] == assignment["tube_side_fluid"]
    tube, shell = hx._side_props(hot, cold)
    assert tube is cold and shell is hot
    assert not any("ASSIGNMENT_WARNING" in w for w in hx._warnings)
