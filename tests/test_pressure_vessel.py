import pytest

from processpi.calculations import CalculationEngine
from processpi.equipment import PressureVessel, PressureVessels
from processpi.equipment.pressure_vessel import (
    CylindricalHorizontalDishEnd,
    CylindricalHorizontalFlatEnd,
)
from processpi.units import Diameter, Length, Pressure, Temperature


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
    assert CylindricalHorizontalDishEnd(**vessel().inputs).inputs["head_type"] == "ellipsoidal"
    result = CalculationEngine().calculate("vessel_design", **vessel().inputs)
    assert result["vessel_type"] == "horizontal"


@pytest.mark.parametrize("key, value", [("design_pressure", Pressure(0)), ("diameter", Diameter(0)), ("joint_efficiency", 1.1)])
def test_rejects_invalid_inputs(key, value):
    with pytest.raises(ValueError):
        vessel(**{key: value})
