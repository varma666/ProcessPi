"""Preliminary ASME VIII-1 internal-pressure vessel design equipment.

The module uses ProcessPI units and the shared material-property database.  It
is deliberately limited to traceable preliminary sizing, not certified code
design; every omitted code calculation is reported in the design result.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, pi, radians, sqrt
from typing import Any, Dict, Iterable, List, Optional, Tuple

from processpi.calculations.base import CalculationBase
from processpi.pipelines.materials import MATERIAL_PROPERTIES, get_material_data
from processpi.units import Area, Diameter, Length, Pressure, Temperature, Volume


# Compatibility exports point to the ProcessPI material database; no vessel-
# specific copy of material data is maintained here.
asme_material_stress_data = MATERIAL_PROPERTIES
_MATERIAL_ALIASES = {
    "carbon-steel": "CS", "cs": "CS", "sa-516-70": "CS", "sa51670": "CS",
    "stainless-304": "SS304", "ss304": "SS304", "sa-240-304": "SS304",
    "sa240304": "SS304", "stainless-316": "SS316", "ss316": "SS316",
    "sa-240-316": "SS316", "sa240316": "SS316",
}


def _value(value: Any, name: str, unit: Optional[str] = None) -> float:
    if hasattr(value, "to") and unit:
        value = value.to(unit)
    value = getattr(value, "original_value", getattr(value, "value", value))
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be numeric or a ProcessPI unit value") from exc


def _material_key(material: str) -> str:
    key = str(material).strip().lower().replace("_", "-").replace(" ", "")
    key = _MATERIAL_ALIASES.get(key, str(material).strip().upper())
    if not get_material_data(key):
        raise ValueError(f"Unsupported ProcessPI material: {material!r}")
    return key


def set_temperature_range(temperature: Any) -> str:
    """Compatibility helper describing the supplied design-temperature band."""
    celsius = _value(temperature, "temperature", "C")
    return "ambient_to_100C" if celsius <= 100 else "100C_to_400C" if celsius <= 400 else "above_400C"


def get_allowable_stress(material: str, temperature: Any = Temperature(20, "C")) -> float:
    """Return the shared ProcessPI material allowable stress in MPa.

    The pipeline material table is currently the repository's common material
    infrastructure.  It supplies a representative allowable stress and a
    maximum temperature; no independent pressure-vessel derating is applied.
    """
    data = get_material_data(_material_key(material))
    if _value(temperature, "design_temperature", "C") > data["max_temp"]:
        raise ValueError(f"Design temperature exceeds the {data['max_temp']} C limit for {material}")
    return float(data["allowable_stress"])


@dataclass
class PressureVesselResults:
    """Heat-exchanger-style result wrapper with a readable engineering summary."""

    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()

    @property
    def warnings(self) -> List[str]:
        return self.data["warnings"]

    def summary(self) -> str:
        geometry = self.data["geometry"]
        volume = self.data["volume"]
        return (
            "PRESSURE VESSEL DESIGN\n"
            "======================\n"
            f"Vessel Type       : {self.data['vessel_type'].title()}\n"
            f"Head Type         : {self.data['head_type']}\n"
            f"Geometry Mode     : {geometry['mode']}\n"
            f"Inside Diameter   : {geometry['inside_diameter'].to('mm')}\n"
            f"{geometry['axial_label'].title():<18}: {geometry['straight_length'].to('mm')}\n"
            f"Required Volume   : {volume['required_volume']}\n"
            f"Design Volume     : {volume['total_internal_volume']}\n"
            f"Excess Volume     : {volume['excess_volume']}\n"
            f"Shell Thickness   : {self.data['shell']['selected_nominal_thickness'].to('mm')}\n"
            f"Head Thickness    : {self.data['heads']['selected_nominal_thickness'].to('mm')}\n"
            f"Hydrotest Pressure: {self.data['hydrotest']['pressure'].to('bar')}\n"
            f"Sizing Basis      : {geometry['selection_basis']}"
        )


class PressureVessel(CalculationBase):
    """A configurable preliminary ASME VIII-1 pressure-vessel equipment model.

    ``volume`` is required only when one or more geometric dimensions are
    omitted.  Plain numeric dimensions are SI metres and pressures are Pa.
    Candidate lists are preliminary fabrication choices in millimetres and can
    be overridden through ``standard_diameters``, ``standard_lengths``, and
    ``standard_thicknesses``.
    """

    STANDARD_VESSEL_DIAMETERS = (1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800, 4000, 4500, 5000, 5500, 6000)
    STANDARD_VESSEL_LENGTHS = (2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 9000, 10000, 12000)
    STANDARD_THICKNESSES_MM = (6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40, 45, 50)
    _TYPES = {"horizontal", "vertical", "spherical"}
    _HEAD_ALIASES = {"flat": "flat", "ellipsoidal": "2:1_ellipsoidal", "2:1 ellipsoidal": "2:1_ellipsoidal", "2:1_ellipsoidal": "2:1_ellipsoidal", "torispherical": "torispherical", "hemispherical": "hemispherical", "conical": "conical"}
    _HEAD_VOLUME_FACTORS = {"flat": 0.0, "2:1_ellipsoidal": 2 / 3, "torispherical": 0.5, "hemispherical": 4 / 3, "conical": 1 / 3}

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    def validate_inputs(self) -> None:
        if self.vessel_type not in self._TYPES:
            raise ValueError(f"vessel_type must be one of {sorted(self._TYPES)}")
        if self.head_type not in self._HEAD_VOLUME_FACTORS:
            raise ValueError(f"head_type must be one of {sorted(self._HEAD_VOLUME_FACTORS)}")
        pressure = self.inputs.get("design_pressure")
        if pressure is None or _value(pressure, "design_pressure", "Pa") <= 0:
            raise ValueError("design_pressure must be greater than zero")
        if self.inputs.get("design_temperature") is None:
            raise ValueError("design_temperature is required")
        required_volume = self.inputs.get("volume")
        if required_volume is not None and _value(required_volume, "volume", "m3") <= 0:
            raise ValueError("volume must be greater than zero")
        for name in ("diameter", "inside_diameter", "length", "height", "tangent_to_tangent_length"):
            if self.inputs.get(name) is not None and _value(self.inputs[name], name, "m") <= 0:
                raise ValueError(f"{name} must be greater than zero when provided")
        if required_volume is None and not self._has_complete_geometry():
            raise ValueError("volume is required when geometry is not fully specified")
        if not 0 < float(self.inputs.get("joint_efficiency", 1.0)) <= 1:
            raise ValueError("joint_efficiency must be greater than zero and no more than one")
        if _value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m") < 0:
            raise ValueError("corrosion_allowance must be non-negative")
        get_allowable_stress(self.inputs.get("material", "CS"), self.inputs["design_temperature"])

    @property
    def vessel_type(self) -> str:
        return str(self.inputs.get("vessel_type", self.inputs.get("orientation", "horizontal"))).lower()

    @property
    def head_type(self) -> str:
        value = str(self.inputs.get("head_type", "2:1_ellipsoidal")).lower().replace("-", "_")
        return self._HEAD_ALIASES.get(value, value)

    def _diameter_input(self) -> Optional[float]:
        value = self.inputs.get("diameter", self.inputs.get("inside_diameter"))
        return None if value is None else _value(value, "diameter", "m")

    def _axial_input(self) -> Optional[float]:
        key = "height" if self.vessel_type == "vertical" else "length"
        # ``length`` remains accepted for vertical-vessel compatibility; new
        # results consistently label the same tangent-to-tangent dimension as
        # ``height``.
        value = self.inputs.get(key)
        if value is None and self.vessel_type == "vertical":
            value = self.inputs.get("length")
        if value is None:
            value = self.inputs.get("tangent_to_tangent_length")
        return None if value is None else _value(value, key, "m")

    def _has_complete_geometry(self) -> bool:
        return self._diameter_input() is not None and (self.vessel_type == "spherical" or self._axial_input() is not None)

    def _required_volume(self) -> Optional[float]:
        value = self.inputs.get("volume")
        return None if value is None else _value(value, "volume", "m3")

    def _candidates(self, name: str, default: Iterable[int]) -> Tuple[float, ...]:
        values = self.inputs.get(name, default)
        result = tuple(sorted(_value(item, name, "mm") / 1000 for item in values))
        if not result or result[0] <= 0:
            raise ValueError(f"{name} must contain positive candidate dimensions")
        return result

    def _head_volume(self, radius: float) -> float:
        return self._HEAD_VOLUME_FACTORS[self.head_type] * pi * radius**3

    def _volume_parts(self, diameter: float, axial: float = 0.0) -> Tuple[float, float, float]:
        radius = diameter / 2
        if self.vessel_type == "spherical":
            total = 4 * pi * radius**3 / 3
            return 0.0, total, total
        shell = pi * radius**2 * axial
        head = self._head_volume(radius)
        return shell, head, shell + head

    def _aspect_limits(self) -> Tuple[float, float]:
        prefix = "height" if self.vessel_type == "vertical" else "length"
        return float(self.inputs.get(f"min_{prefix}_to_diameter", 1.0)), float(self.inputs.get(f"max_{prefix}_to_diameter", 6.0))

    def _select_length(self, diameter: float, required: float) -> float:
        radius = diameter / 2
        theoretical = max(0.0, (required - self._head_volume(radius)) / (pi * radius**2))
        for candidate in self._candidates("standard_lengths", self.STANDARD_VESSEL_LENGTHS):
            if candidate >= theoretical:
                return candidate
        return theoretical

    def _select_diameter(self, axial: float, required: float) -> float:
        candidates = self._candidates("standard_diameters", self.STANDARD_VESSEL_DIAMETERS)
        feasible = [d for d in candidates if self._volume_parts(d, axial)[2] >= required]
        if not feasible:
            raise ValueError("Configured standard diameters cannot satisfy the required volume")
        return min(feasible)

    def _geometry(self) -> Dict[str, Any]:
        diameter, axial, required = self._diameter_input(), self._axial_input(), self._required_volume()
        label = "height" if self.vessel_type == "vertical" else "length"
        if self.vessel_type == "spherical":
            if diameter is None:
                candidates = self._candidates("standard_diameters", self.STANDARD_VESSEL_DIAMETERS)
                diameter = next((d for d in candidates if self._volume_parts(d)[2] >= required), None)
                if diameter is None:
                    raise ValueError("Configured standard diameters cannot satisfy the required volume")
                mode, basis = "AUTO_SIZED", "Smallest configured spherical diameter satisfying required volume."
            else:
                mode, basis = "USER_SPECIFIED", "User-specified spherical diameter retained."
            axial = 0.0
        elif diameter is not None and axial is not None:
            mode, basis = "USER_SPECIFIED", "User-specified diameter and straight dimension retained."
        elif diameter is not None:
            axial = self._select_length(diameter, required)
            mode, basis = "DIAMETER_SPECIFIED", "Specified diameter retained; smallest configured straight dimension satisfying volume selected."
        elif axial is not None:
            diameter = self._select_diameter(axial, required)
            mode, basis = "LENGTH_SPECIFIED", "Specified straight dimension retained; smallest configured diameter satisfying volume selected."
        else:
            low, high = self._aspect_limits()
            choices = []
            for d in self._candidates("standard_diameters", self.STANDARD_VESSEL_DIAMETERS):
                for candidate_axial in self._candidates("standard_lengths", self.STANDARD_VESSEL_LENGTHS):
                    total = self._volume_parts(d, candidate_axial)[2]
                    ratio = candidate_axial / d
                    if total >= required and low <= ratio <= high:
                        choices.append((total - required, abs(ratio - 3.0), d, candidate_axial))
            if not choices:
                raise ValueError("No configured candidate geometry satisfies volume and aspect-ratio constraints")
            _, _, diameter, axial = min(choices)
            mode = "AUTO_SIZED"
            basis = "Configured candidate geometry satisfying volume and aspect-ratio limits with minimum excess volume."
        shell, heads, total = self._volume_parts(diameter, axial)
        return {"mode": mode, "inside_diameter": Diameter(diameter), "straight_length": Length(axial), "axial_label": label, "shell_volume": Volume(shell), "head_volume": Volume(heads), "total_internal_volume": Volume(total), "required_volume": None if required is None else Volume(required), "excess_volume": None if required is None else Volume(total - required), "volume_margin_percent": None if required is None else (total - required) / required * 100, "aspect_ratio": None if self.vessel_type == "spherical" else axial / diameter, "selection_basis": basis}

    def add_nozzle(self, name: str, diameter: Any, **details: Any) -> None:
        d = _value(diameter, "nozzle diameter", "m")
        if d <= 0:
            raise ValueError("nozzle diameter must be greater than zero")
        self.nozzles[name] = {"diameter": Diameter(d), **details}

    def add_manhole(self, name: str, diameter: Any, **details: Any) -> None:
        d = _value(diameter, "manhole diameter", "m")
        if d <= 0:
            raise ValueError("manhole diameter must be greater than zero")
        self.manholes[name] = {"diameter": Diameter(d), **details}

    def _thicknesses(self, diameter: float) -> Tuple[Length, Length, float, float, float]:
        pressure = _value(self.inputs["design_pressure"], "design_pressure", "Pa")
        stress = get_allowable_stress(self.inputs.get("material", "CS"), self.inputs["design_temperature"]) * 1e6
        efficiency = float(self.inputs.get("joint_efficiency", 1.0))
        allowance = _value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m")
        radius = diameter / 2
        shell_pressure = pressure * radius / (stress * efficiency - 0.6 * pressure)
        if self.head_type == "flat":
            # UG-34 uses a geometry/boundary-condition coefficient C.  Keep
            # it explicit rather than disguising a project assumption.
            coefficient = float(self.inputs.get("flat_head_coefficient", 0.30))
            head_pressure = diameter * sqrt(coefficient * pressure / (stress * efficiency))
        elif self.head_type == "2:1_ellipsoidal":
            # UG-32(d), K = 1 for a standard 2:1 ellipsoidal head.
            head_pressure = pressure * diameter / (2 * stress * efficiency - 0.2 * pressure)
        elif self.head_type == "torispherical":
            # UG-32(e), standard flanged-and-dished preliminary form, L = D.
            head_pressure = 0.885 * pressure * diameter / (stress * efficiency - 0.1 * pressure)
        elif self.head_type == "hemispherical":
            head_pressure = pressure * diameter / (4 * stress * efficiency - 0.4 * pressure)
        else:
            # Conical heads require an angle; retain it as an explicit,
            # reviewable input for this preliminary internal-pressure form.
            half_angle = radians(float(self.inputs.get("conical_half_angle", 30.0)))
            head_pressure = pressure * diameter / (2 * cos(half_angle) * (stress * efficiency - 0.6 * pressure))
        return Length(shell_pressure + allowance), Length(head_pressure + allowance), shell_pressure, head_pressure, stress

    def select_standard_thickness(self, required: Any) -> Length:
        required_mm = _value(required, "required thickness", "mm")
        for thickness in self._candidates("standard_thicknesses", self.STANDARD_THICKNESSES_MM):
            if thickness * 1000 >= required_mm:
                return Length(thickness)
        return Length(required_mm, "mm")

    def _weights(self, geometry: Dict[str, Any], shell_t: Length, head_t: Length, density: float) -> Dict[str, float]:
        d, axial = geometry["inside_diameter"].value, geometry["straight_length"].value
        shell_area = 0.0 if self.vessel_type == "spherical" else pi * d * axial
        head_area = 4 * pi * (d / 2) ** 2 if self.vessel_type == "spherical" else 2 * pi * (d / 2) ** 2
        shell = shell_area * shell_t.value * density
        heads = head_area * head_t.value * density
        accessory = sum(pi * item["diameter"].value ** 2 / 4 * shell_t.value * density for item in self.nozzles.values())
        manholes = sum(pi * item["diameter"].value ** 2 / 4 * head_t.value * density for item in self.manholes.values())
        return {"shell_weight_kg": shell, "head_weight_kg": heads, "nozzle_weight_kg": accessory, "manhole_weight_kg": manholes, "reinforcement_weight_kg": 0.0, "total_empty_weight_kg": shell + heads + accessory + manholes}

    def design_check(self) -> Dict[str, Dict[str, Any]]:
        """Return traceable PASS/WARNING/INCOMPLETE preliminary design checks."""
        return self.design()["design_checks"]

    def design(self) -> Dict[str, Any]:
        geometry = self._geometry()
        d = geometry["inside_diameter"].value
        shell_required, head_required, shell_pressure, head_pressure, stress = self._thicknesses(d)
        shell_nominal, head_nominal = self.select_standard_thickness(shell_required), self.select_standard_thickness(head_required)
        material_key = _material_key(self.inputs.get("material", "CS"))
        material = get_material_data(material_key)
        weights = self._weights(geometry, shell_nominal, head_nominal, float(material["density"]))
        test_pressure = Pressure(1.3 * _value(self.inputs["design_pressure"], "design_pressure", "Pa"))
        test_volume = geometry["total_internal_volume"]
        test_weight = test_volume.value * float(self.inputs.get("hydrotest_liquid_density", 1000.0))
        reinforcement = {name: {"status": "INCOMPLETE", "required_opening_area": Area(pi * item["diameter"].value ** 2 / 4), "available_reinforcement_area": None, "nozzle_neck_contribution": None, "shell_contribution": None, "reinforcement_pad_contribution": None} for name, item in self.nozzles.items()}
        warnings = ["Preliminary ASME VIII-1 internal-pressure sizing only; it is not certified code compliance.", "INCOMPLETE: external pressure/vacuum, supports, wind, seismic, fatigue, MDMT, PWHT, flanges, and other load cases are not evaluated."]
        if self.nozzles or self.manholes:
            warnings.append("INCOMPLETE: UG-37 nozzle/manhole reinforcement is reported as a framework only and must be completed.")
        result = {"inputs": self.inputs.copy(), "vessel_type": self.vessel_type, "head_type": self.head_type, "design_conditions": {"design_pressure": self.inputs["design_pressure"], "design_temperature": self.inputs["design_temperature"], "operating_pressure": self.inputs.get("operating_pressure"), "operating_temperature": self.inputs.get("operating_temperature"), "corrosion_allowance": Length(_value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m")), "joint_efficiency": self.inputs.get("joint_efficiency", 1.0)}, "material": {"input": self.inputs.get("material", "CS"), "key": material_key, "allowable_stress_mpa": stress / 1e6, "maximum_temperature_c": material["max_temp"], "density_kg_m3": material["density"]}, "geometry": geometry, "volume": {key: geometry[key] for key in ("required_volume", "shell_volume", "head_volume", "total_internal_volume", "excess_volume", "volume_margin_percent")}, "shell": {"pressure_thickness": Length(shell_pressure), "corrosion_allowance": Length(_value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m")), "required_thickness": shell_required, "selected_nominal_thickness": shell_nominal}, "heads": {"pressure_thickness": Length(head_pressure), "corrosion_allowance": Length(_value(self.inputs.get("corrosion_allowance", 0.0), "corrosion_allowance", "m")), "required_thickness": head_required, "selected_nominal_thickness": head_nominal}, "nozzles": self.nozzles.copy(), "manholes": self.manholes.copy(), "nozzle_reinforcement": reinforcement, "weight": weights, "hydrotest": {"pressure": test_pressure, "basis": "Preliminary UG-99(b) 1.3 × design-pressure reporting; final code test pressure requires stress-ratio review.", "liquid_volume": test_volume, "liquid_weight_kg": test_weight, "estimated_test_condition_weight_kg": weights["total_empty_weight_kg"] + test_weight}, "warnings": warnings, "limitations": warnings[1:], "design_basis": "Preliminary ASME VIII-1: UG-27(c)(1), UG-32, UG-34, UG-99(b)"}
        # Retain compact keys used by the first public implementation.
        result.update({"shell_required_thickness": shell_required, "head_required_thickness": head_required, "selected_thickness": max(shell_nominal, head_nominal, key=lambda x: x.value), "internal_volume": geometry["total_internal_volume"], "hydrotest_pressure": test_pressure, "estimated_weight_kg": weights["total_empty_weight_kg"]})
        result["design_checks"] = self._design_checks_from_result(result)
        return result

    def _design_checks_from_result(self, result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        # Avoid recursive design_check() while retaining a public standalone API.
        volume = result["volume"]
        checks = {
            "design_pressure": {"status": "PASS", "actual": result["design_conditions"]["design_pressure"], "required": "positive", "margin": None},
            "design_temperature": {"status": "PASS", "actual": result["design_conditions"]["design_temperature"], "required": f"<= {result['material']['maximum_temperature_c']} C", "margin": None},
            "material": {"status": "PASS", "actual": result["material"]["key"], "required": "ProcessPI material database", "margin": None},
            "corrosion_allowance": {"status": "PASS", "actual": result["design_conditions"]["corrosion_allowance"], "required": ">= 0", "margin": None},
            "joint_efficiency": {"status": "PASS", "actual": result["design_conditions"]["joint_efficiency"], "required": "0 < E <= 1", "margin": None},
            "geometry": {"status": "PASS", "actual": result["geometry"]["mode"], "required": "valid final geometry", "margin": None},
            "volume": {"status": "WARNING" if volume["required_volume"] is None else ("PASS" if volume["excess_volume"].value >= 0 else "FAIL"), "actual": volume["total_internal_volume"], "required": volume["required_volume"], "margin": volume["excess_volume"]},
            "shell_thickness": {"status": "PASS", "actual": result["shell"]["selected_nominal_thickness"], "required": result["shell"]["required_thickness"], "margin": result["shell"]["selected_nominal_thickness"].value - result["shell"]["required_thickness"].value},
            "head_thickness": {"status": "PASS", "actual": result["heads"]["selected_nominal_thickness"], "required": result["heads"]["required_thickness"], "margin": result["heads"]["selected_nominal_thickness"].value - result["heads"]["required_thickness"].value},
            "hydrotest": {"status": "WARNING", "actual": result["hydrotest"]["pressure"], "required": "final UG-99(b) stress-ratio review", "margin": None},
        }
        checks.update({f"opening:{name}": {"status": "INCOMPLETE", "actual": item["diameter"], "required": "UG-37 reinforcement", "margin": None} for name, item in {**self.nozzles, **self.manholes}.items()})
        return checks

    def volume(self, liquid_level: Optional[Any] = None) -> Volume:
        geometry = self._geometry()
        full = geometry["total_internal_volume"].value
        if liquid_level is None:
            return Volume(full)
        d = geometry["inside_diameter"].value
        level = _value(liquid_level, "liquid_level", "m")
        if not 0 <= level <= d:
            raise ValueError("liquid_level must be between zero and vessel diameter")
        r = d / 2
        fraction = (r * r * acos((r - level) / r) - (r - level) * sqrt(max(0, 2 * r * level - level * level))) / (pi * r * r)
        return Volume(full * fraction)

    calculate = design


class CylindricalHorizontalFlatEnd(PressureVessel):
    def __init__(self, **kwargs: Any):
        kwargs.setdefault("vessel_type", "horizontal")
        kwargs.setdefault("head_type", "flat")
        super().__init__(**kwargs)


class CylindricalHorizontalDishEnd(PressureVessel):
    def __init__(self, **kwargs: Any):
        kwargs.setdefault("vessel_type", "horizontal")
        kwargs.setdefault("head_type", "2:1_ellipsoidal")
        super().__init__(**kwargs)


PressureVessels = PressureVessel

__all__ = ["PressureVessel", "PressureVessels", "PressureVesselResults", "CylindricalHorizontalFlatEnd", "CylindricalHorizontalDishEnd", "asme_material_stress_data", "get_allowable_stress", "set_temperature_range"]
