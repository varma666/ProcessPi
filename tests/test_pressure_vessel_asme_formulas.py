"""
ASME VIII-1 thickness formulas for PressureVessel.

Every expected value is recomputed here from the code formula with explicit
numbers, never by calling the library, and is also pinned to the hand
calculation to four decimal places in millimetres.

Reference case used throughout:

    inside diameter D = 2.000 m (ID 2000 mm)
    design pressure  P = 10 bar  -> 1.0e6 Pa
    design temperature 150 C     -> 302 F, so the 400 F band is selected
    material SA-516-70           -> S = 20.0 ksi = 137.895 MPa
    joint efficiency E = 0.85
    corrosion allowance   = 3 mm, added after the pressure thickness
"""

from math import cos, radians

import pytest

from processpi.equipment import PressureVessel
from processpi.units import Diameter, Length, Pressure, Temperature


# Explicit inputs of the reference case, in SI base units.
P_PA = 10.0 * 1.0e5
D_M = 2.0
R_M = D_M / 2.0
CA_M = 3.0e-3
E = 0.85

# 20.0 ksi expressed in Pa: 20.0 * 1000 psi * 6894.757293168 Pa/psi.
S_PA = 20.0 * 1000.0 * 6894.757293168
SE_PA = S_PA * E


def vessel(**overrides):
    values = {
        "design_pressure": Pressure(10, "bar"),
        "design_temperature": Temperature(150, "C"),
        "diameter": Diameter(2.0),
        "length": Length(6),
        "corrosion_allowance": Length(3, "mm"),
        "material": "sa-516-70",
        "joint_efficiency": 0.85,
    }
    values.update(overrides)
    return PressureVessel(**values)


def mm(thickness):
    return thickness.to("m").value * 1000.0


# Length stores its magnitude as round(value_in_m, 6), so every thickness the
# library returns is quantized to 0.001 mm. Compare to one quantum.
TOL_MM = 1.0e-3


def test_reference_case_inputs_are_what_the_hand_calculation_assumes():
    """Guard the unit conventions the expected values depend on."""

    item = vessel()

    # The design pressure is used as supplied: 10 bar is 1.0e6 Pa, with no
    # atmospheric offset applied anywhere in the thickness equations.
    assert item.design().get("design_pressure").to("Pa").value == pytest.approx(P_PA)

    # 150 C selects the 400 F allowable-stress band, which is 20.0 ksi.
    assert item.allowable_stress().to("psi").value == pytest.approx(20.0 * 1000.0)
    assert S_PA / 1.0e6 == pytest.approx(137.895, abs=5e-4)


def test_torispherical_head_matches_ug_32_e():
    """UG-32(e) standard F&D head: t = 0.885 P L / (S E - 0.1 P), L = D."""

    expected_m = 0.885 * P_PA * D_M / (SE_PA - 0.1 * P_PA) + CA_M

    assert round(expected_m * 1000.0, 4) == 18.1139

    actual_mm = mm(vessel(head_type="torispherical").head_thickness())
    assert actual_mm == pytest.approx(expected_m * 1000.0, abs=TOL_MM)


def test_torispherical_head_uses_an_explicit_crown_radius():
    """A crown radius other than D must scale the pressure thickness."""

    crown_radius_m = 1.6

    expected_m = (
        0.885 * P_PA * crown_radius_m / (SE_PA - 0.1 * P_PA) + CA_M
    )

    assert round(expected_m * 1000.0, 4) == 15.0911

    actual_mm = mm(
        vessel(
            head_type="torispherical",
            crown_radius=Length(crown_radius_m, "m"),
        ).head_thickness()
    )
    assert actual_mm == pytest.approx(expected_m * 1000.0, abs=TOL_MM)


def test_conical_head_matches_ug_32_g_at_30_degrees():
    """UG-32(g): t = P D / (2 cos(alpha) (S E - 0.6 P))."""

    alpha_deg = 30.0

    expected_m = (
        P_PA
        * D_M
        / (2.0 * cos(radians(alpha_deg)) * (SE_PA - 0.6 * P_PA))
        + CA_M
    )

    assert round(expected_m * 1000.0, 4) == 12.9022

    actual_mm = mm(
        vessel(
            head_type="conical",
            cone_half_angle=alpha_deg,
        ).head_thickness()
    )
    assert actual_mm == pytest.approx(expected_m * 1000.0, abs=TOL_MM)


def test_conical_head_thickness_depends_on_the_cone_angle():
    """A shallower cone must be thinner than a 30 degree cone."""

    alpha_deg = 15.0

    expected_m = (
        P_PA
        * D_M
        / (2.0 * cos(radians(alpha_deg)) * (SE_PA - 0.6 * P_PA))
        + CA_M
    )

    assert round(expected_m * 1000.0, 4) == 11.8780

    actual_mm = mm(
        vessel(
            head_type="conical",
            cone_half_angle=alpha_deg,
        ).head_thickness()
    )
    assert actual_mm == pytest.approx(expected_m * 1000.0, abs=TOL_MM)
    assert actual_mm < 12.9022


def test_conical_head_requires_a_half_apex_angle():
    with pytest.raises(ValueError, match="cone_half_angle"):
        vessel(head_type="conical")


@pytest.mark.parametrize("alpha_deg", [30.001, 45.0, 60.0])
def test_conical_head_rejects_a_half_apex_angle_above_30_degrees(alpha_deg):
    """UG-32(g) stops at 30 degrees; beyond it a toriconical head is needed."""

    with pytest.raises(ValueError, match="30 degrees"):
        vessel(head_type="conical", cone_half_angle=alpha_deg)


@pytest.mark.parametrize("alpha_deg", [0.0, -10.0])
def test_conical_head_rejects_a_non_positive_half_apex_angle(alpha_deg):
    with pytest.raises(ValueError, match="cone_half_angle"):
        vessel(head_type="conical", cone_half_angle=alpha_deg)


def test_spherical_shell_matches_ug_27_d():
    """UG-27(d) sphere: t = P R / (2 S E - 0.2 P)."""

    expected_m = P_PA * R_M / (2.0 * SE_PA - 0.2 * P_PA) + CA_M

    assert round(expected_m * 1000.0, 4) == 7.2695

    item = vessel(vessel_type="spherical")

    assert mm(item.spherical_shell_thickness()) == pytest.approx(
        expected_m * 1000.0, abs=TOL_MM
    )

    result = item.design()
    assert mm(result["shell_required_thickness"]) == pytest.approx(
        expected_m * 1000.0, abs=TOL_MM
    )
    assert mm(result["governing_required_thickness"]) == pytest.approx(
        expected_m * 1000.0, abs=TOL_MM
    )
    assert mm(result["selected_thickness"]) == pytest.approx(8.0)


@pytest.mark.parametrize(
    "head_type", ["flat", "ellipsoidal", "torispherical", "hemispherical"]
)
def test_spherical_shell_is_independent_of_head_type(head_type):
    """A sphere has no heads, so head_type must not change its wall."""

    expected_mm = (P_PA * R_M / (2.0 * SE_PA - 0.2 * P_PA) + CA_M) * 1000.0

    item = vessel(vessel_type="spherical", head_type=head_type)

    assert mm(item.design()["shell_required_thickness"]) == pytest.approx(
        expected_mm, abs=TOL_MM
    )


def test_ellipsoidal_head_is_unchanged():
    """Guard: the 2:1 ellipsoidal head was already correct, UG-32(d)."""

    expected_m = P_PA * D_M / (2.0 * SE_PA - 0.2 * P_PA) + CA_M

    assert round(expected_m * 1000.0, 4) == 11.5389

    actual_mm = mm(vessel(head_type="ellipsoidal").head_thickness())
    assert actual_mm == pytest.approx(expected_m * 1000.0, abs=TOL_MM)


def test_cylindrical_shell_is_unchanged():
    """Guard: UG-27(c)(1) shell, t = P R / (S E - 0.6 P)."""

    expected_m = P_PA * R_M / (SE_PA - 0.6 * P_PA) + CA_M

    assert round(expected_m * 1000.0, 4) == 11.5755

    actual_mm = mm(vessel().shell_thickness())
    assert actual_mm == pytest.approx(expected_m * 1000.0, abs=TOL_MM)
