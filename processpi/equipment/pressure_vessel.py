"""Preliminary ASME VIII-1 internal-pressure pressure-vessel design.

This module is intentionally an equipment module (rather than a calculation in
``equipment.base``), in the same way that the heat-exchanger implementations
live below :mod:`processpi.equipment`.  It provides preliminary sizing only;
the warnings returned by :meth:`PressureVessel.design` are part of that scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from typing import Any, Dict, List, Mapping, Optional

from processpi.calculations.base import CalculationBase
from processpi.units import Area, Diameter, Length, Pressure, Temperature, Volume


# Typical room-temperature allowable stresses (MPa).  These are deliberately a
# small preliminary-design table, not a replacement for the ASME code tables.
asme_material_stress_data: Dict[str, float] = {
    "carbon_steel": 138.0,
    "sa-516-70": 138.0,
    "stainless_304": 129.0,
    "stainless_316": 115.0,
}


def set_temperature_range(temperature: Any) -> str:
    """Return the preliminary material-table temperature band for *temperature*."""
    celsius = _value(temperature, "temperature", "C")
    if celsius <= 100:
        return "ambient_to_100C"
    if celsius <= 400:
        return "100C_to_400C"
    return "above_400C"


def get_allowable_stress(material: str, temperature: Any = Temperature(20, "C")) -> float:
    """Get a preliminary allowable stress in MPa.

    A numerical ``material`` is accepted as an explicit allowable stress for
    projects which already perform their own code-material lookup.
    """
    if isinstance(material, (int, float)):
        stress = float(material)
    else:
        key = str(material).strip().lower().replace(" ", "_")
        if key not in asme_material_stress_data:
            raise ValueError(f"Unsupported pressure-vessel material: {material!r}")
        stress = asme_material_stress_data[key]
    # Simple, conservative derating outside the supplied ambient table band.
    return stress * (0.85 if _value(temperature, "temperature", "C") > 400 else 1.0)


def _value(value: Any, name: str, unit: Optional[str] = None) -> float:
    if hasattr(value, "to") and unit:
        value = value.to(unit)
    # Several ProcessPI length-like units retain SI in ``value`` even after
    # ``to()``; their converted magnitude is exposed as ``original_value``.
    # Pressure uses the same public attribute, so use it consistently.
    value = getattr(value, "original_value", getattr(value, "value", value))
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be numeric or a ProcessPI unit value") from exc


@dataclass
class PressureVesselResults:
    """Structured results returned by the pressure-vessel design workflow."""

    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()

    @property
    def warnings(self) -> List[str]:
        return self.data["warnings"]


class PressureVessel(CalculationBase):
    """A preliminary ASME VIII-1 vessel with cylindrical or spherical geometry.

    Dimensions are SI when plain numbers are supplied (m, Pa, and kg/m3).
    ProcessPI :class:`~processpi.units.Pressure`, :class:`Length`,
    :class:`Diameter`, and :class:`Temperature` inputs are accepted directly.
    """

    STANDARD_THICKNESSES_MM = (3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 40, 50)
    _HEADS = {"flat", "ellipsoidal", "torispherical", "hemispherical", "conical"}
    _TYPES = {"horizontal", "vertical", "spherical"}

    def __init__(self, **kwargs: Any):
        # Retain the CalculationBase input/result convention used by ProcessPI.
        super().__init__(**kwargs)
        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    def validate_inputs(self) -> None:
        inputs = self.inputs
        vessel_type = str(inputs.get("vessel_type", inputs.get("orientation", "horizontal"))).lower()
        if vessel_type not in self._TYPES:
            raise ValueError(f"vessel_type must be one of {sorted(self._TYPES)}")
        pressure = inputs.get("design_pressure", inputs.get("pressure"))
        if pressure is None or _value(pressure, "design_pressure", "Pa") <= 0:
            raise ValueError("design_pressure must be greater than zero")
        diameter = inputs.get("diameter", inputs.get("inside_diameter"))
        if diameter is None or _value(diameter, "diameter", "m") <= 0:
            raise ValueError("diameter must be greater than zero")
        if vessel_type != "spherical":
            length = inputs.get("length", inputs.get("tangent_to_tangent_length"))
            if length is None or _value(length, "length", "m") <= 0:
                raise ValueError("length must be greater than zero for cylindrical vessels")
        if not 0 < float(inputs.get("joint_efficiency", 1.0)) <= 1:
            raise ValueError("joint_efficiency must be greater than zero and no more than one")
        if _value(inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m") < 0:
            raise ValueError("corrosion_allowance must be non-negative")

    @property
    def vessel_type(self) -> str:
        return str(self.inputs.get("vessel_type", self.inputs.get("orientation", "horizontal"))).lower()

    def add_nozzle(self, name: str, diameter: Any, **details: Any) -> None:
        diameter_m = _value(diameter, "nozzle diameter", "m")
        if diameter_m <= 0:
            raise ValueError("nozzle diameter must be greater than zero")
        self.nozzles[name] = {"diameter": Diameter(diameter_m), **details}

    def add_manhole(self, name: str, diameter: Any, **details: Any) -> None:
        diameter_m = _value(diameter, "manhole diameter", "m")
        if diameter_m <= 0:
            raise ValueError("manhole diameter must be greater than zero")
        self.manholes[name] = {"diameter": Diameter(diameter_m), **details}

    def shell_thickness(self) -> Length:
        """UG-27(c)(1) cylindrical-shell thickness, including corrosion allowance."""
        p = _value(self.inputs.get("design_pressure", self.inputs.get("pressure")), "design_pressure", "Pa")
        radius = _value(self.inputs.get("diameter", self.inputs.get("inside_diameter")), "diameter", "m") / 2
        s = get_allowable_stress(self.inputs.get("material", "carbon_steel"), self.inputs.get("design_temperature", Temperature(20, "C"))) * 1e6
        e = float(self.inputs.get("joint_efficiency", 1.0))
        return Length((p * radius / (s * e - 0.6 * p)) + _value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m"))

    def head_thickness(self) -> Length:
        """Preliminary UG-34/UG-32 head thickness, including corrosion allowance."""
        p = _value(self.inputs.get("design_pressure", self.inputs.get("pressure")), "design_pressure", "Pa")
        d = _value(self.inputs.get("diameter", self.inputs.get("inside_diameter")), "diameter", "m")
        s = get_allowable_stress(self.inputs.get("material", "carbon_steel"), self.inputs.get("design_temperature", Temperature(20, "C"))) * 1e6
        e = float(self.inputs.get("joint_efficiency", 1.0))
        head = str(self.inputs.get("head_type", "ellipsoidal")).lower().replace("2:1_", "").replace("2:1 ", "")
        if head not in self._HEADS:
            raise ValueError(f"head_type must be one of {sorted(self._HEADS)}")
        factors = {"flat": 0.50, "ellipsoidal": 0.25, "torispherical": 0.885, "hemispherical": 0.125, "conical": 0.35}
        t = factors[head] * p * d / (s * e - 0.1 * p)
        return Length(t + _value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m"))

    def volume(self, liquid_level: Optional[Any] = None) -> Volume:
        d = _value(self.inputs.get("diameter", self.inputs.get("inside_diameter")), "diameter", "m")
        r = d / 2
        if self.vessel_type == "spherical":
            full = 4 * pi * r**3 / 3
        else:
            length = _value(self.inputs.get("length", self.inputs.get("tangent_to_tangent_length")), "length", "m")
            full = pi * r**2 * length + self._head_volume(r)
        if liquid_level is None:
            return Volume(full)
        level = _value(liquid_level, "liquid_level", "m")
        if not 0 <= level <= d:
            raise ValueError("liquid_level must be between zero and vessel diameter")
        fraction = (r * r * __import__("math").acos((r - level) / r) - (r - level) * sqrt(max(0, 2 * r * level - level * level))) / (pi * r * r)
        return Volume(full * fraction)

    def _head_volume(self, radius: float) -> float:
        head = str(self.inputs.get("head_type", "ellipsoidal")).lower()
        factors = {"flat": 0.0, "ellipsoidal": 2 / 3, "torispherical": 0.5, "hemispherical": 4 / 3, "conical": 1 / 3}
        return factors.get(head, 2 / 3) * pi * radius**3

    def select_standard_thickness(self, required: Any) -> Length:
        required_mm = _value(required, "required thickness", "mm")
        for thickness in self.STANDARD_THICKNESSES_MM:
            if thickness >= required_mm:
                return Length(thickness, "mm")
        return Length(required_mm, "mm")

    def design(self) -> Dict[str, Any]:
        shell_required = self.shell_thickness() if self.vessel_type != "spherical" else self.head_thickness()
        head_required = self.head_thickness()
        selected = self.select_standard_thickness(
            Length(max(shell_required.value, head_required.value))
        )
        p = _value(self.inputs.get("design_pressure", self.inputs.get("pressure")), "design_pressure", "Pa")
        hydrotest = Pressure(1.3 * p)
        d = _value(self.inputs.get("diameter", self.inputs.get("inside_diameter")), "diameter", "m")
        length = 0.0 if self.vessel_type == "spherical" else _value(self.inputs.get("length", self.inputs.get("tangent_to_tangent_length")), "length", "m")
        area = pi * d * length + 2 * pi * (d / 2) ** 2
        density = float(self.inputs.get("material_density", 7850.0))
        weight = area * selected.value * density
        warnings = [
            "Preliminary ASME Section VIII Division 1 internal-pressure sizing only.",
            "External pressure/vacuum, complete nozzle reinforcement, supports, wind, seismic, fatigue, MDMT, PWHT, and flanges are not evaluated.",
        ]
        if self.nozzles or self.manholes:
            warnings.append("Nozzle and manhole reinforcement calculations are not included.")
        return PressureVesselResults({
            "vessel_type": self.vessel_type,
            "head_type": self.inputs.get("head_type", "ellipsoidal"),
            "shell_required_thickness": shell_required,
            "head_required_thickness": head_required,
            "selected_thickness": selected,
            "internal_volume": self.volume(),
            "external_area": Area(area),
            "estimated_weight_kg": weight,
            "hydrotest_pressure": hydrotest,
            "nozzles": self.nozzles.copy(),
            "manholes": self.manholes.copy(),
            "warnings": warnings,
            "design_basis": "ASME VIII-1 preliminary: UG-27(c)(1), UG-34, UG-32, UG-99(b)",
        }).to_dict()

    calculate = design


class CylindricalHorizontalFlatEnd(PressureVessel):
    """Backward-compatible horizontal cylindrical vessel with flat heads."""
    def __init__(self, **kwargs: Any):
        super().__init__(vessel_type="horizontal", head_type="flat", **kwargs)


class CylindricalHorizontalDishEnd(PressureVessel):
    """Backward-compatible horizontal cylindrical vessel with dished heads."""
    def __init__(self, **kwargs: Any):
        super().__init__(vessel_type="horizontal", head_type="ellipsoidal", **kwargs)


PressureVessels = PressureVessel

__all__ = ["PressureVessel", "PressureVessels", "PressureVesselResults", "CylindricalHorizontalFlatEnd", "CylindricalHorizontalDishEnd", "asme_material_stress_data", "get_allowable_stress", "set_temperature_range"]
