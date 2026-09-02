import pytest

from processpi.calculations import CalculationEngine
from processpi.equipment import PressureVessel, PressureVessels
from processpi.equipment.pressure_vessel import (
    CylindricalHorizontalDishEnd,
    CylindricalHorizontalFlatEnd,
)
from processpi.units import Diameter, Length, Pressure, Temperature, Volume


def vessel(**overrides):
    values = {
        "design_pressure": Pressure(10, "bar"),
        "design_temperature": Temperature(150, "C"),
        "diameter": Diameter(1.2),
        "length": Length(4),
        "corrosion_allowance": Length(3, "mm"),
        "material": "sa-516-70",
        "joint_efficiency": 0.85,
    }
    values.update(overrides)
    return PressureVessel(**values)


@pytest.mark.parametrize("vessel_type", ["horizontal", "vertical", "spherical"])
def test_designs_vessel_geometries(vessel_type):
    kwargs = {"vessel_type": vessel_type}
    if vessel_type == "spherical":
        kwargs.pop("length", None)
    result = vessel(**kwargs).design()
    assert result["internal_volume"].value > 0
    assert result["selected_thickness"].value >= result["shell_required_thickness"].value


@pytest.mark.parametrize("head_type", ["flat", "ellipsoidal", "torispherical", "hemispherical", "conical"])
def test_designs_supported_heads(head_type):
    result = vessel(head_type=head_type).design()
    assert result["head_required_thickness"].value > 0


def test_nozzles_manhole_weight_hydrotest_and_level():
    item = vessel()
    item.add_nozzle("feed", Diameter(100, "mm"), location="top")
    item.add_manhole("access", Diameter(450, "mm"))
    result = item.design()
    assert result["estimated_weight_kg"] > 0
    assert result["hydrotest_pressure"].to("bar").value == pytest.approx(13)
    assert result["nozzles"]["feed"]["location"] == "top"
    assert item.volume(Length(0.6)).value < result["internal_volume"].value


def test_compatibility_classes_and_calculation_engine():
    assert PressureVessels is PressureVessel
    assert CylindricalHorizontalFlatEnd(**vessel().inputs).inputs["head_type"] == "flat"
    assert CylindricalHorizontalDishEnd(**vessel().inputs).inputs["head_type"] == "2:1_ellipsoidal"
    result = CalculationEngine().calculate("vessel_design", **vessel().inputs)
    assert result["vessel_type"] == "horizontal"


@pytest.mark.parametrize("key, value", [("design_pressure", Pressure(0)), ("diameter", Diameter(0)), ("joint_efficiency", 1.1)])
def test_rejects_invalid_inputs(key, value):
    with pytest.raises(ValueError):
        vessel(**{key: value})


def automatic_vessel(**overrides):
    values = {
        "volume": Volume(25, "m3"),
        "design_pressure": Pressure(10, "bar"),
        "design_temperature": Temperature(150, "C"),
        "vessel_type": "horizontal",
        "head_type": "2:1_ellipsoidal",
        "material": "SA-240-304",
        "corrosion_allowance": Length(3, "mm"),
        "joint_efficiency": 0.85,
    }
    values.update(overrides)
    return PressureVessel(**values)


def test_auto_sizing_accepts_documented_user_example_and_reports_geometry():
    item = automatic_vessel()
    item.add_nozzle("N1", Diameter(100, "mm"), service="Feed")
    item.add_manhole("MH1", Diameter(450, "mm"))
    result = item.design()

    assert result["material"]["key"] == "SS304"
    assert result["geometry"]["mode"] == "AUTO_SIZED"
    assert result["geometry"]["inside_diameter"].value > 0
    assert result["geometry"]["straight_length"].value > 0
    assert result["volume"]["total_internal_volume"].value >= 25
    assert result["volume"]["excess_volume"].value >= 0
    assert result["nozzle_reinforcement"]["N1"]["status"] == "INCOMPLETE"
    assert "INCOMPLETE" in " ".join(result["warnings"])


def test_diameter_only_retains_diameter_and_selects_length():
    result = automatic_vessel(diameter=Diameter(2200, "mm")).design()
    geometry = result["geometry"]
    assert geometry["mode"] == "DIAMETER_SPECIFIED"
    assert geometry["inside_diameter"].to("mm").original_value == pytest.approx(2200)
    assert geometry["straight_length"].value > 0
    assert result["volume"]["total_internal_volume"].value >= 25


def test_length_only_retains_length_and_selects_diameter():
    result = automatic_vessel(length=Length(8000, "mm")).design()
    geometry = result["geometry"]
    assert geometry["mode"] == "LENGTH_SPECIFIED"
    assert geometry["straight_length"].to("mm").original_value == pytest.approx(8000)
    assert geometry["inside_diameter"].value > 0


def test_fully_specified_geometry_is_never_replaced_and_volume_is_checked():
    result = automatic_vessel(diameter=Diameter(2200, "mm"), length=Length(8000, "mm")).design()
    geometry = result["geometry"]
    assert geometry["mode"] == "USER_SPECIFIED"
    assert geometry["inside_diameter"].to("mm").original_value == pytest.approx(2200)
    assert geometry["straight_length"].to("mm").original_value == pytest.approx(8000)
    assert result["design_checks"]["volume"]["status"] == "PASS"


@pytest.mark.parametrize("vessel_type", ["vertical", "spherical"])
def test_automatic_sizing_supports_vertical_and_spherical_vessels(vessel_type):
    result = automatic_vessel(vessel_type=vessel_type).design()
    assert result["geometry"]["mode"] == "AUTO_SIZED"
    assert result["volume"]["total_internal_volume"].value >= 25


def test_design_check_weight_and_hydrotest_are_traceable():
    item = automatic_vessel()
    item.add_nozzle("N1", Diameter(100, "mm"))
    result = item.design()
    checks = item.design_check()
    assert result["weight"]["shell_weight_kg"] > 0
    assert result["weight"]["total_empty_weight_kg"] > result["weight"]["shell_weight_kg"]
    assert result["hydrotest"]["liquid_weight_kg"] > 0
    assert checks["opening:N1"]["status"] == "INCOMPLETE"
    assert {"design_pressure", "material", "shell_thickness", "head_thickness", "hydrotest"} <= checks.keys()


@pytest.mark.parametrize(
    "overrides",
    [
        {"volume": Volume(0, "m3")},
        {"material": "not-a-material"},
        {"vessel_type": "diagonal"},
        {"head_type": "unknown"},
        {"diameter": Diameter(0, "mm")},
    ],
)
def test_auto_sizing_validation_distinguishes_missing_and_invalid_geometry(overrides):
    with pytest.raises(ValueError):
        automatic_vessel(**overrides)
