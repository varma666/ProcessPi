"""PressureVessel: the fit/run engine, low design temperatures, the UG-27
validity range and the head areas in the weight.

Reference case (as in test_pressure_vessel_asme_formulas.py): ID 2000 mm,
6 m straight length, 10 bar, SA-516-70, E = 0.85, CA 3 mm.
"""

from math import cos, pi, sin, sqrt

import pytest

from processpi.equipment import PressureVessel, PressureVesselEngine
from processpi.equipment.pressure_vessel import (
    PressureVesselResults,
    asme_material_stress_data,
    get_allowable_stress,
)
from processpi.units import Length, Pressure, Temperature


def _inputs(**overrides):
    values = {
        "design_pressure": Pressure(10, "bar"),
        "design_temperature": Temperature(150, "C"),
        "diameter": Length(2, "m"),
        "length": Length(6, "m"),
        "material": "SA516-70",
        "joint_efficiency": 0.85,
        "corrosion_allowance": Length(3, "mm"),
    }
    values.update(overrides)
    return values


def _value(x, unit):
    return float(x.to(unit).original_value) if hasattr(x, "to") else float(x)


# ----------------------------------------------------------------------------
# Engine
# ----------------------------------------------------------------------------

def test_engine_fit_run_gives_the_vessel_design():
    engine = PressureVesselEngine()
    assert engine.fit(**_inputs()) is engine
    results = engine.run()
    assert isinstance(results, PressureVesselResults)
    assert engine.results() is results
    direct = PressureVessel(**_inputs()).design()
    for key in ("shell_required_thickness", "head_required_thickness", "selected_thickness",
                "estimated_weight_kg", "hydrotest_pressure"):
        assert results[key] == direct[key] or _value(results[key], "m") == pytest.approx(_value(direct[key], "m"))
    text = engine.summary()
    assert "Selected thickness" in text and "12 mm" in text


def test_engine_before_run_and_without_inputs():
    engine = PressureVesselEngine()
    assert engine.summary() is None
    with pytest.raises(RuntimeError):
        engine.results()
    with pytest.raises(RuntimeError):
        engine.run()
    with pytest.raises(ValueError):
        engine.fit()


def test_engine_constructor_kwargs_fit_and_nozzles():
    engine = PressureVesselEngine(
        name="V-101", **_inputs(),
        nozzles=[{"name": "N1", "diameter": Length(0.1, "m")}],
        manholes=[{"name": "M1", "diameter": Length(0.6, "m")}],
    )
    results = engine.run()
    assert engine.name == "V-101"
    assert "N1" in engine.vessel.nozzles and "M1" in engine.vessel.manholes
    assert any("reinforcement" in w for w in results.warnings)
    with pytest.raises(TypeError):
        PressureVesselEngine().fit(**_inputs(), nozzles=["N1"])


def test_a_new_fit_clears_the_previous_results():
    engine = PressureVesselEngine(**_inputs())
    engine.run()
    engine.fit(**_inputs(design_pressure=Pressure(5, "bar")))
    with pytest.raises(RuntimeError):
        engine.results()


# ----------------------------------------------------------------------------
# Low design temperatures (ASME II-D Table 1A: "-20 to 100 F" column)
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("temperature", [Temperature(20, "C"), Temperature(-20, "F"), Temperature(0, "C")])
def test_ambient_and_chilled_vessels_take_the_first_column(temperature):
    """The module's own default design temperature, 20 C, used to raise."""
    stress = get_allowable_stress("SA516-70", temperature)
    assert _value(stress, "psi") == pytest.approx(asme_material_stress_data["SA516-70"][100] * 1000.0)
    PressureVessel(**_inputs(design_temperature=temperature)).design()


def test_below_minus_20_f_is_refused_and_says_why():
    with pytest.raises(ValueError, match="UCS-66"):
        get_allowable_stress("SA516-70", Temperature(-30, "F"))


# ----------------------------------------------------------------------------
# UG-27(c)(1) range
# ----------------------------------------------------------------------------

def test_reference_shell_is_within_the_ug27_range():
    data = PressureVessel(**_inputs()).design()
    assert data["ug27_validity"]["valid"] is True
    assert not any("UG-27(c)(1) range" in w for w in data["warnings"])


def test_thick_shell_is_flagged():
    """500 bar: P = 50 MPa > 0.385 S E = 0.385 x 137.895 x 0.85 = 45.13 MPa,
    and the pressure thickness 573 mm > R/2 = 500 mm. It used to be reported
    as a valid 576 mm wall."""
    data = PressureVessel(**_inputs(design_pressure=Pressure(500, "bar"))).design()
    validity = data["ug27_validity"]
    s_e = 20.0 * 1000.0 * 6894.757293168 * 0.85
    assert validity["pressure_limit_Pa"] == pytest.approx(0.385 * s_e)
    assert validity["thickness_limit_m"] == pytest.approx(0.5)
    assert validity["pressure_thickness_m"] == pytest.approx(50e6 * 1.0 / (s_e - 0.6 * 50e6))
    assert validity["valid"] is False
    assert any("UG-27(c)(1) range" in w and "Appendix 1-2" in w for w in data["warnings"])


def test_the_range_ends_at_0_385_s_e():
    """With t = P R / (S E - 0.6 P), t = R/2 exactly when P = S E / 2.6 =
    0.3846 S E, so the two limits end the range at the same pressure."""
    s_e = 20.0 * 1000.0 * 6894.757293168 * 0.85
    over = PressureVessel(**_inputs(design_pressure=Pressure(0.386 * s_e, "Pa"))).ug27_cylinder_validity()
    under = PressureVessel(**_inputs(design_pressure=Pressure(0.384 * s_e, "Pa"))).ug27_cylinder_validity()
    assert over["valid"] is False and under["valid"] is True
    assert under["pressure_thickness_m"] < under["thickness_limit_m"] < over["pressure_thickness_m"]


# ----------------------------------------------------------------------------
# Head surface areas and weight
# ----------------------------------------------------------------------------

def _meridian_area(points):
    """2 pi * integral of rho ds along a meridian given as (rho, z) points."""
    area = 0.0
    for (r1, z1), (r2, z2) in zip(points, points[1:]):
        area += 2.0 * pi * 0.5 * (r1 + r2) * sqrt((r2 - r1) ** 2 + (z2 - z1) ** 2)
    return area


N = 20000


def _ellipsoid_points(a, c):
    return [(a * cos(t), c * sin(t)) for t in (i * (pi / 2) / N for i in range(N + 1))]


def _torisphere_points(radius, crown, knuckle):
    """Knuckle arc from the shell (rho = R) to the tangent point, then the crown."""
    beta = __import__("math").asin((radius - knuckle) / (crown - knuckle))
    theta_k = pi / 2 - beta
    pts = [((radius - knuckle) + knuckle * cos(t), knuckle * sin(t))
           for t in (i * theta_k / N for i in range(N + 1))]
    z_centre = pts[-1][1] - crown * cos(beta)
    pts += [(crown * sin(b), z_centre + crown * cos(b))
            for b in (beta - i * beta / N for i in range(1, N + 1))]
    return pts


@pytest.mark.parametrize("head, expected", [
    ("flat", lambda r: pi * r ** 2),
    ("hemispherical", lambda r: 2 * pi * r ** 2),
    ("ellipsoidal", lambda r: _meridian_area(_ellipsoid_points(r, r / 2))),
    ("torispherical", lambda r: _meridian_area(_torisphere_points(r, 2 * r, 0.12 * r))),
])
def test_head_area_against_numerical_integration(head, expected):
    vessel = PressureVessel(**_inputs(head_type=head))
    assert vessel._head_surface_area(1.0, head) == pytest.approx(expected(1.0), rel=1e-6)


def test_conical_head_area_is_its_lateral_area():
    vessel = PressureVessel(**_inputs(head_type="conical", cone_half_angle=30))
    assert vessel._head_surface_area(1.0, "conical") == pytest.approx(pi / sin(pi / 6))


def test_ellipsoidal_weight_counts_the_dished_heads():
    """pi D L + 2 x 1.380 pi R^2 = 37.699 + 8.672 = 46.371 m2; at 12 mm and
    7850 kg/m3 that is 4368 kg. Both heads used to be flat discs: 43.982 m2,
    4143 kg (-5.2%)."""
    data = PressureVessel(**_inputs()).design()
    area = _value(data["external_area"], "m2")
    assert area == pytest.approx(46.371, abs=5e-4)
    assert data["estimated_weight_kg"] == pytest.approx(area * 0.012 * 7850.0, rel=1e-9)
    assert data["estimated_weight_kg"] == pytest.approx(4368, abs=1)
