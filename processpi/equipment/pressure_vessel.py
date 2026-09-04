"""
ProcessPI Pressure Vessel Module
--------------------------------

Preliminary ASME Section VIII Division 1 internal-pressure sizing.

This module includes:
- Complete supplied temperature-specific preliminary allowable-stress database
- Conservative ASME temperature-band selection
- Material aliases / normalization
- Cylindrical shell sizing
- Preliminary head sizing
- Volume calculation and volume check
- Nozzle and manhole storage
- Hydrotest pressure
- Estimated external area and weight
- Expanded design result dictionary
- CalculationBase.calculate() implementation
- Backward-compatible PressureVessels / legacy classes

IMPORTANT:
The stress values below are the supplied preliminary database and are NOT a
replacement for the applicable ASME Section II, Part D tables. Verify all
values before code-stamped design or fabrication.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, pi, sqrt
from typing import Any, Dict, List, Optional

from processpi.calculations.base import CalculationBase
from processpi.units import Area, Diameter, Length, Pressure, Temperature, Volume


# ============================================================================
# ASME MATERIAL ALLOWABLE-STRESS DATABASE
# ============================================================================
#
# Values are ksi.
# Temperature keys are °F.
#
# The supplied database is intentionally retained exactly as provided,
# including zero values. A zero value means that no allowable stress is
# available for that material at that temperature.
# ============================================================================

asme_material_stress_data: Dict[str, Dict[int, float]] = {

    "SA515-55": {
        100: 13.7, 200: 13.7, 300: 13.7, 400: 13.7,
        500: 13.7, 600: 13.7, 700: 13.2, 800: 10.2,
    },

    "SA515-70": {
        100: 17.5, 200: 17.5, 300: 17.5, 400: 17.5,
        500: 17.5, 600: 17.5, 700: 16.6, 800: 12.0,
    },

    "SA516-55": {
        100: 13.7, 200: 13.7, 300: 13.7, 400: 13.7,
        500: 13.7, 600: 13.7, 700: 13.2, 800: 10.2,
    },

    "SA516-70": {
        100: 20.0, 200: 20.0, 300: 20.0, 400: 20.0,
        500: 20.0, 600: 19.4, 700: 18.1, 800: 12.0,
    },

    "SA256-A": {
        100: 11.2, 200: 11.2, 300: 11.2, 400: 11.2,
        500: 11.2, 600: 11.2, 700: 11.0, 800: 9.0,
    },

    # Retained exactly as originally supplied.
    "SA285-B": {
        100: 1.2, 200: 1.2, 300: 1.2, 400: 1.2,
        500: 1.2, 600: 1.2, 700: 12.1, 800: 9.6,
    },

    "SA285-C": {
        100: 13.7, 200: 13.7, 300: 13.7, 400: 13.7,
        500: 13.7, 600: 13.7, 700: 13.2, 800: 10.2,
    },

    "SA202-A": {
        100: 18.7, 200: 18.7, 300: 18.7, 400: 18.7,
        500: 18.7, 600: 18.7, 700: 17.7, 800: 12.6,
    },

    "SA202-B": {
        100: 21.2, 200: 21.2, 300: 21.2, 400: 21.2,
        500: 21.2, 600: 21.2, 700: 19.8, 800: 12.9,
    },

    "SA387-D": {
        100: 15.0, 200: 15.0, 300: 15.0, 400: 15.0,
        500: 15.0, 600: 15.0, 700: 15.0, 800: 15.0,
    },

    "SA240-304": {
        100: 20.0, 200: 20.0, 300: 18.9, 400: 18.3,
        500: 17.5, 600: 16.6, 700: 15.8, 800: 15.2,
    },

    "SA240-304L": {
        100: 16.7, 200: 16.7, 300: 16.7, 400: 15.8,
        500: 14.7, 600: 14.0, 700: 13.5, 800: 13.0,
    },

    "SA240-309S": {
        100: 20.0, 200: 20.0, 300: 20.0, 400: 20.0,
        500: 19.4, 600: 18.8, 700: 18.2, 800: 17.7,
    },

    "SA240-310": {
        100: 20.0, 200: 20.0, 300: 20.0, 400: 19.9,
        500: 19.3, 600: 18.5, 700: 17.9, 800: 17.4,
    },

    "SA240-316": {
        100: 20.0, 200: 20.0, 300: 20.0, 400: 19.3,
        500: 18.0, 600: 17.0, 700: 16.3, 800: 15.9,
    },

    "SA240-316L": {
        100: 16.7, 200: 16.7, 300: 16.7, 400: 15.7,
        500: 14.8, 600: 14.0, 700: 13.5, 800: 12.9,
    },

    "SA240-317L": {
        100: 20.0, 200: 20.0, 300: 19.6, 400: 18.9,
        500: 17.7, 600: 16.9, 700: 16.2, 800: 15.5,
    },

    "SA240-347": {
        100: 20.0, 200: 20.0, 300: 18.8, 400: 17.8,
        500: 17.2, 600: 16.9, 700: 16.8, 800: 16.8,
    },

    "B162": {
        100: 10.0, 200: 10.0, 300: 10.0, 400: 10.0,
        500: 10.0, 600: 10.0, 700: 0.0, 800: 0.0,
    },

    "201": {
        100: 8.0, 200: 7.7, 300: 7.5, 400: 7.5,
        500: 7.5, 600: 7.5, 700: 7.4, 800: 7.2,
    },

    "B127": {
        100: 18.7, 200: 16.4, 300: 15.2, 400: 14.7,
        500: 14.7, 600: 14.7, 700: 14.6, 800: 14.3,
    },

    "B168": {
        100: 22.9, 200: 22.9, 300: 22.9, 400: 22.9,
        500: 22.9, 600: 22.9, 700: 22.9, 800: 22.9,
    },

    "B443": {
        100: 34.3, 200: 34.3, 300: 34.3, 400: 33.6,
        500: 32.9, 600: 32.4, 700: 31.8, 800: 31.2,
    },

    "C-22 alloy": {
        100: 28.6, 200: 28.6, 300: 28.2, 400: 27.2,
        500: 26.5, 600: 26.0, 700: 25.6, 800: 25.3,
    },

    "B575": {
        100: 27.3, 200: 27.3, 300: 27.3, 400: 27.3,
        500: 26.5, 600: 26.0, 700: 25.6, 800: 25.3,
    },

    "B333": {
        100: 31.4, 200: 31.4, 300: 31.4, 400: 31.4,
        500: 31.4, 600: 31.2, 700: 30.9, 800: 30.6,
    },

    "B463": {
        100: 22.9, 200: 22.9, 300: 22.6, 400: 22.2,
        500: 22.1, 600: 22.1, 700: 21.9, 800: 21.8,
    },

    "B409": {
        100: 20.0, 200: 20.0, 300: 20.0, 400: 20.0,
        500: 20.0, 600: 20.0, 700: 20.0, 800: 20.0,
    },

    "B424": {
        100: 23.3, 200: 23.3, 300: 23.3, 400: 23.3,
        500: 23.3, 600: 23.3, 700: 23.2, 800: 23.0,
    },

    "B688": {
        100: 27.1, 200: 27.1, 300: 25.7, 400: 24.6,
        500: 23.8, 600: 23.3, 700: 22.9, 800: 22.6,
    },

    "A240 904": {
        100: 20.3, 200: 16.7, 300: 15.1, 400: 13.8,
        500: 12.7, 600: 11.9, 700: 11.4, 800: 0.0,
    },

    "G-30 Alloy": {
        100: 23.3, 200: 23.3, 300: 23.2, 400: 22.5,
        500: 21.9, 600: 21.3, 700: 20.5, 800: 19.7,
    },

    "Titanium Grade 2": {
        100: 14.3, 200: 12.4, 300: 10.3, 400: 8.8,
        500: 7.6, 600: 6.5, 700: 0.0, 800: 0.0,
    },

    "Zinccronium 702": {
        100: 15.7, 200: 13.7, 300: 11.2, 400: 9.1,
        500: 7.4, 600: 6.4, 700: 5.2, 800: 0.0,
    },
}


# ============================================================================
# MATERIAL DENSITIES
# ============================================================================

MATERIAL_DENSITIES: Dict[str, float] = {
    "SA515-55": 7850.0,
    "SA515-70": 7850.0,
    "SA516-55": 7850.0,
    "SA516-70": 7850.0,
    "SA256-A": 7850.0,
    "SA285-B": 7850.0,
    "SA285-C": 7850.0,
    "SA202-A": 7850.0,
    "SA202-B": 7850.0,
    "SA387-D": 7850.0,

    "SA240-304": 8000.0,
    "SA240-304L": 8000.0,
    "SA240-309S": 8000.0,
    "SA240-310": 8000.0,
    "SA240-316": 8000.0,
    "SA240-316L": 8000.0,
    "SA240-317L": 8000.0,
    "SA240-347": 8000.0,

    "B162": 8900.0,
    "201": 8000.0,
    "B127": 8850.0,
    "B168": 8900.0,
    "B443": 8440.0,
    "C-22 alloy": 8690.0,
    "B575": 8690.0,
    "B333": 8890.0,
    "B463": 8000.0,
    "B409": 8000.0,
    "B424": 8000.0,
    "B688": 8900.0,
    "A240 904": 8000.0,
    "G-30 Alloy": 8690.0,

    "Titanium Grade 2": 4510.0,
    "Zinccronium 702": 6500.0,
}


# ============================================================================
# MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES: Dict[str, str] = {

    "sa515-55": "SA515-55",
    "sa515-70": "SA515-70",
    "sa516": "SA516-70",
    "sa516-55": "SA516-55",
    "sa516-70": "SA516-70",
    "sa-516-70": "SA516-70",
    "sa256-a": "SA256-A",
    "sa285-b": "SA285-B",
    "sa285-c": "SA285-C",
    "sa202-a": "SA202-A",
    "sa202-b": "SA202-B",
    "sa387-d": "SA387-D",

    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "cs": "SA516-70",

    "sa240-304": "SA240-304",
    "304": "SA240-304",
    "304 stainless": "SA240-304",
    "ss304": "SA240-304",
    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",

    "sa240-304l": "SA240-304L",
    "304l": "SA240-304L",
    "304l stainless": "SA240-304L",
    "ss304l": "SA240-304L",

    "sa240-309s": "SA240-309S",
    "309s": "SA240-309S",

    "sa240-310": "SA240-310",
    "310": "SA240-310",

    "sa240-316": "SA240-316",
    "316": "SA240-316",
    "316 stainless": "SA240-316",
    "ss316": "SA240-316",
    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",

    "sa240-316l": "SA240-316L",
    "316l": "SA240-316L",
    "316l stainless": "SA240-316L",
    "ss316l": "SA240-316L",

    "sa240-317l": "SA240-317L",
    "317l": "SA240-317L",

    "sa240-347": "SA240-347",

    "b162": "B162",
    "201": "201",
    "b127": "B127",
    "b168": "B168",
    "b443": "B443",
    "c-22 alloy": "C-22 alloy",
    "c22 alloy": "C-22 alloy",
    "b575": "B575",
    "b333": "B333",
    "b463": "B463",
    "b409": "B409",
    "b424": "B424",
    "b688": "B688",

    "a240 904": "A240 904",
    "a240-904": "A240 904",

    "g-30 alloy": "G-30 Alloy",
    "g30 alloy": "G-30 Alloy",

    "titanium grade 2": "Titanium Grade 2",

    "zirconium 702": "Zinccronium 702",
    "zinccronium 702": "Zinccronium 702",
}


# ============================================================================
# TEMPERATURE DATABASE LIMITS
# ============================================================================

ASME_STRESS_TEMPERATURES_F = (
    100, 200, 300, 400, 500, 600, 700, 800
)

ASME_TEMPERATURE_BANDS = ASME_STRESS_TEMPERATURES_F

MIN_SUPPORTED_TEMPERATURE_F = -20.0
MAX_SUPPORTED_TEMPERATURE_F = 800.0
TEMPERATURE_TOLERANCE_F = 1.0e-6


# ============================================================================
# GENERAL HELPERS
# ============================================================================

def _value(value: Any, name: str, unit: Optional[str] = None) -> float:
    """
    Extract a numeric value from a ProcessPI unit object or a plain number.

    If a unit is requested, conversion is attempted first.
    ProcessPI unit implementations may expose the converted magnitude through
    either ``original_value`` or ``value``.
    """
    converted = value

    if hasattr(converted, "to") and unit:
        converted = converted.to(unit)

    # Prefer original_value because ProcessPI's unit classes may retain the
    # converted magnitude there.
    converted = getattr(
        converted,
        "original_value",
        getattr(converted, "value", converted),
    )

    try:
        return float(converted)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a compatible ProcessPI unit value"
        ) from exc


def _normalize_material_key(material: Any) -> str:
    if material is None:
        raise ValueError("Material must be specified.")

    text = str(material).strip()

    if not text:
        raise ValueError("Material must not be empty.")

    if text in asme_material_stress_data:
        return text

    lowered = text.lower()

    if lowered in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[lowered]

    for key in asme_material_stress_data:
        if key.lower() == lowered:
            return key

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: {', '.join(asme_material_stress_data.keys())}"
    )


def normalize_material(material: Any) -> str:
    """Public material normalization helper."""
    return _normalize_material_key(material)


def _temperature_to_f(temperature: Any) -> float:
    if not isinstance(temperature, Temperature):
        raise TypeError("Design temperature must be a Temperature object.")

    temperature_f = _value(temperature, "temperature", "F")
    return round(temperature_f, 6)


# ============================================================================
# TEMPERATURE-BAND SELECTION
# ============================================================================

def set_temperature_range(temperature: Any) -> Temperature:
    """
    Select the conservative allowable-stress temperature band.

    Examples
    --------
    25 C  -> 100 F
    150 C -> 400 F
    175 C -> 400 F
    225 C -> 500 F
    425 C -> 800 F

    A temperature between table values uses the NEXT HIGHER band.

    The important implementation detail is that the selected band is returned
    and later used as the DATABASE KEY. The actual design temperature is never
    used directly as a dictionary key.

    This fixes the previous failure:

        KeyError: 533

    for a design temperature of 150 C = 302 F.
    """
    temperature_f = _temperature_to_f(temperature)

    if temperature_f < MIN_SUPPORTED_TEMPERATURE_F - TEMPERATURE_TOLERANCE_F:
        raise ValueError(
            "Design temperature is below the available "
            "allowable-stress database. "
            f"Minimum supported temperature is "
            f"{MIN_SUPPORTED_TEMPERATURE_F:g}°F."
        )

    for band in ASME_STRESS_TEMPERATURES_F:
        if temperature_f <= band + TEMPERATURE_TOLERANCE_F:
            return Temperature(band, "F")

    raise ValueError(
        "Design temperature exceeds the available "
        "allowable-stress database. "
        f"Maximum supported temperature is "
        f"{MAX_SUPPORTED_TEMPERATURE_F:g}°F."
    )


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return preliminary allowable stress as a ProcessPI Pressure in psi.

    Numeric material input is supported for backward compatibility and is
    interpreted as an explicit allowable stress in ksi.

    For database materials, the temperature is first converted to the
    conservative temperature band and THAT band is used for the lookup.
    """
    # Explicit numerical allowable stress in ksi.
    if isinstance(material, (int, float)):
        stress_ksi = float(material)

        if stress_ksi <= 0:
            raise ValueError("Allowable stress must be greater than zero.")

        return Pressure(stress_ksi * 1000.0, "psi")

    material_key = _normalize_material_key(material)

    temperature_band = set_temperature_range(temperature)
    temperature_band_f = int(
        round(_value(temperature_band, "temperature band", "F"))
    )

    stress_table = asme_material_stress_data[material_key]

    if temperature_band_f not in stress_table:
        raise ValueError(
            f"No allowable stress temperature band is available "
            f"for material '{material_key}' at {temperature_band_f}°F."
        )

    stress_ksi = float(stress_table[temperature_band_f])

    if stress_ksi <= 0:
        raise ValueError(
            f"No allowable stress is available for material "
            f"'{material_key}' at {temperature_band_f}°F."
        )

    return Pressure(stress_ksi * 1000.0, "psi")


# ============================================================================
# RESULTS
# ============================================================================

@dataclass
class PressureVesselResults:
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()

    @property
    def warnings(self) -> List[str]:
        return self.data["warnings"]


# ============================================================================
# PRESSURE VESSEL
# ============================================================================

class PressureVessel(CalculationBase):

    STANDARD_THICKNESSES_MM = (
        3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 40, 50
    )

    _TYPES = {
        "horizontal",
        "vertical",
        "spherical",
    }

    _HEADS = {
        "flat",
        "ellipsoidal",
        "torispherical",
        "hemispherical",
        "conical",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------------
    # INPUT VALIDATION
    # ------------------------------------------------------------------------

    def validate_inputs(self) -> None:
        inputs = self.inputs

        vessel_type = str(
            inputs.get(
                "vessel_type",
                inputs.get("orientation", "horizontal"),
            )
        ).strip().lower()

        if vessel_type not in self._TYPES:
            raise ValueError(
                f"vessel_type must be one of {sorted(self._TYPES)}"
            )

        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        if pressure is None:
            raise ValueError("design_pressure must be specified.")

        if _value(pressure, "design_pressure", "Pa") <= 0:
            raise ValueError("design_pressure must be greater than zero.")

        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None:
            raise ValueError("diameter must be specified.")

        if _value(diameter, "diameter", "m") <= 0:
            raise ValueError("diameter must be greater than zero.")

        if vessel_type != "spherical":
            length = inputs.get(
                "length",
                inputs.get("tangent_to_tangent_length"),
            )

            if length is None:
                raise ValueError(
                    "length must be specified for cylindrical vessels."
                )

            if _value(length, "length", "m") <= 0:
                raise ValueError("length must be greater than zero.")

        head_type = str(
            inputs.get("head_type", "2:1_ellipsoidal")
        ).strip().lower()

        if head_type not in {
            "flat",
            "flat_head",
            "ellipsoidal",
            "elliptical",
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "torispherical",
            "hemispherical",
            "hemisphere",
            "conical",
        }:
            raise ValueError(
                f"Unsupported head_type: {inputs.get('head_type')!r}."
            )

        joint_efficiency = float(
            inputs.get("joint_efficiency", 1.0)
        )

        if not 0.0 < joint_efficiency <= 1.0:
            raise ValueError(
                "joint_efficiency must be greater than zero and no more than one."
            )

        corrosion_allowance = _value(
            inputs.get("corrosion_allowance", Length(0, "mm")),
            "corrosion_allowance",
            "m",
        )

        if corrosion_allowance < 0:
            raise ValueError(
                "corrosion_allowance must be non-negative."
            )

        design_temperature = inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

        if not isinstance(design_temperature, Temperature):
            raise TypeError(
                "design_temperature must be a Temperature object."
            )

        # This validates both the temperature range and zero-stress materials.
        get_allowable_stress(
            inputs.get("material", "SA516-70"),
            design_temperature,
        )

        density = float(
            inputs.get(
                "material_density",
                MATERIAL_DENSITIES.get(
                    _normalize_material_key(
                        inputs.get("material", "SA516-70")
                    ),
                    7850.0,
                ),
            )
        )

        if density <= 0:
            raise ValueError("material_density must be greater than zero.")

    # ------------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------------

    @property
    def vessel_type(self) -> str:
        return str(
            self.inputs.get(
                "vessel_type",
                self.inputs.get("orientation", "horizontal"),
            )
        ).strip().lower()

    @property
    def head_type(self) -> str:
        return str(
            self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

    @property
    def material(self) -> str:
        return _normalize_material_key(
            self.inputs.get("material", "SA516-70")
        )

    @property
    def design_temperature(self) -> Temperature:
        return self.inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

    # ------------------------------------------------------------------------
    # ATTACHMENTS
    # ------------------------------------------------------------------------

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        if not name:
            raise ValueError("Nozzle name must not be empty.")

        diameter_m = _value(
            diameter,
            "nozzle diameter",
            "m",
        )

        if diameter_m <= 0:
            raise ValueError(
                "nozzle diameter must be greater than zero."
            )

        self.nozzles[str(name)] = {
            "diameter": Diameter(diameter_m, "m"),
            **details,
        }

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        if not name:
            raise ValueError("Manhole name must not be empty.")

        diameter_m = _value(
            diameter,
            "manhole diameter",
            "m",
        )

        if diameter_m <= 0:
            raise ValueError(
                "manhole diameter must be greater than zero."
            )

        self.manholes[str(name)] = {
            "diameter": Diameter(diameter_m, "m"),
            **details,
        }

    # ------------------------------------------------------------------------
    # ALLOWABLE STRESS
    # ------------------------------------------------------------------------

    def allowable_stress(self) -> Pressure:
        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # ------------------------------------------------------------------------
    # SHELL THICKNESS
    # ------------------------------------------------------------------------

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical-shell internal-pressure thickness.

        UG-27(c)(1):

            t = P R / (S E - 0.6 P)

        Corrosion allowance is added after pressure thickness.
        """
        pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        allowable_stress_psi = _value(
            self.allowable_stress(),
            "allowable stress",
            "psi",
        )

        # psi -> Pa
        allowable_stress_pa = allowable_stress_psi * 6894.757293168

        joint_efficiency = float(
            self.inputs.get("joint_efficiency", 1.0)
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        radius = diameter / 2.0

        denominator = (
            allowable_stress_pa * joint_efficiency
            - 0.6 * pressure
        )

        if denominator <= 0:
            raise ValueError(
                "Shell thickness equation has a non-positive denominator. "
                "Check pressure, allowable stress, and joint efficiency."
            )

        pressure_thickness = (
            pressure * radius / denominator
        )

        return Length(
            pressure_thickness + corrosion_allowance,
            "m",
        )

    # ------------------------------------------------------------------------
    # HEAD THICKNESS
    # ------------------------------------------------------------------------

    def head_thickness(self) -> Length:
        """
        Preliminary pressure thickness for vessel heads.

        Factors retained from the ProcessPI preliminary implementation:

            flat           = 0.50
            ellipsoidal    = 0.25
            torispherical  = 0.885
            hemispherical  = 0.125
            conical        = 0.35

        t_pressure =
            factor * P * D / (S E - 0.1 P)

        This is a preliminary screening calculation only.
        """
        pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        allowable_stress_psi = _value(
            self.allowable_stress(),
            "allowable stress",
            "psi",
        )

        allowable_stress_pa = allowable_stress_psi * 6894.757293168

        joint_efficiency = float(
            self.inputs.get("joint_efficiency", 1.0)
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        head = self.head_type

        aliases = {
            "2:1_ellipsoidal": "ellipsoidal",
            "2:1 ellipsoidal": "ellipsoidal",
            "elliptical": "ellipsoidal",
            "flat_head": "flat",
            "hemisphere": "hemispherical",
        }

        head = aliases.get(head, head)

        factors = {
            "flat": 0.50,
            "ellipsoidal": 0.25,
            "torispherical": 0.885,
            "hemispherical": 0.125,
            "conical": 0.35,
        }

        if head not in factors:
            raise ValueError(
                f"Unsupported head type '{self.head_type}'."
            )

        denominator = (
            allowable_stress_pa * joint_efficiency
            - 0.1 * pressure
        )

        if denominator <= 0:
            raise ValueError(
                "Head thickness equation has a non-positive denominator. "
                "Check pressure, allowable stress, and joint efficiency."
            )

        pressure_thickness = (
            factors[head]
            * pressure
            * diameter
            / denominator
        )

        return Length(
            pressure_thickness + corrosion_allowance,
            "m",
        )

    # ------------------------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------------------------

    def _head_volume(self, radius: float) -> float:
        """
        Approximate total volume of both heads.

        For a 2:1 ellipsoidal pair:
            V = 2/3 * pi * r^3

        The values are preliminary geometry estimates.
        """
        head = self.head_type

        aliases = {
            "2:1_ellipsoidal": "ellipsoidal",
            "2:1 ellipsoidal": "ellipsoidal",
            "elliptical": "ellipsoidal",
            "flat_head": "flat",
            "hemisphere": "hemispherical",
        }

        head = aliases.get(head, head)

        factors = {
            "flat": 0.0,
            "ellipsoidal": 2.0 / 3.0,
            "torispherical": 0.5,
            "hemispherical": 4.0 / 3.0,
            "conical": 1.0 / 3.0,
        }

        if head not in factors:
            raise ValueError(
                f"Unsupported head type '{self.head_type}'."
            )

        return factors[head] * pi * radius ** 3

    def volume(
        self,
        liquid_level: Optional[Any] = None,
    ) -> Volume:
        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        radius = diameter / 2.0

        if self.vessel_type == "spherical":
            full_volume = (
                4.0 * pi * radius ** 3 / 3.0
            )
        else:
            length = _value(
                self.inputs.get(
                    "length",
                    self.inputs.get(
                        "tangent_to_tangent_length"
                    ),
                ),
                "length",
                "m",
            )

            full_volume = (
                pi * radius ** 2 * length
                + self._head_volume(radius)
            )

        if liquid_level is None:
            return Volume(full_volume, "m3")

        level = _value(
            liquid_level,
            "liquid_level",
            "m",
        )

        if not 0.0 <= level <= diameter:
            raise ValueError(
                "liquid_level must be between zero and vessel diameter."
            )

        if self.vessel_type == "spherical":
            # Spherical-cap fraction.
            cap_volume = (
                pi * level ** 2
                * (radius - level / 3.0)
            )
            return Volume(cap_volume, "m3")

        fraction = (
            (
                radius ** 2
                * acos(
                    (radius - level) / radius
                )
                -
                (radius - level)
                * sqrt(
                    max(
                        0.0,
                        2.0 * radius * level - level ** 2,
                    )
                )
            )
            / (pi * radius ** 2)
        )

        return Volume(
            full_volume * fraction,
            "m3",
        )

    # ------------------------------------------------------------------------
    # STANDARD THICKNESS
    # ------------------------------------------------------------------------

    def select_standard_thickness(
        self,
        required: Any,
    ) -> Length:
        required_mm = _value(
            required,
            "required thickness",
            "mm",
        )

        if required_mm <= 0:
            raise ValueError(
                "required thickness must be greater than zero."
            )

        for thickness in self.STANDARD_THICKNESSES_MM:
            if thickness >= required_mm:
                return Length(thickness, "mm")

        # If above the standard list, return the exact calculated requirement
        # rather than silently pretending it is a standard plate size.
        return Length(required_mm, "mm")

    # ------------------------------------------------------------------------
    # EXTERNAL AREA
    # ------------------------------------------------------------------------

    def _ellipsoidal_head_area(
        self,
        diameter_m: float,
    ) -> float:
        """
        Approximate area of ONE 2:1 ellipsoidal head.

        Numerical integration is used for preliminary weight estimation.
        """
        a = diameter_m / 2.0
        c = diameter_m / 4.0

        n = 200
        total = 0.0
        dtheta = (pi / 2.0) / n

        for i in range(n):
            theta = (i + 0.5) * dtheta

            sin_theta = __import__("math").sin(theta)
            cos_theta = __import__("math").cos(theta)

            element = (
                2.0
                * pi
                * a
                * sin_theta
                * sqrt(
                    c ** 2 * sin_theta ** 2
                    + a ** 2 * cos_theta ** 2
                )
            )

            total += element * dtheta

        return total

    def _external_area(
        self,
        diameter_m: float,
        length_m: float,
    ) -> float:
        """
        Preliminary external surface area in m².

        The cylindrical shell plus two circular end projections are retained
        for continuity with the previous ProcessPI result dictionary.
        """
        if self.vessel_type == "spherical":
            radius = diameter_m / 2.0
            return 4.0 * pi * radius ** 2

        cylindrical_area = (
            pi * diameter_m * length_m
        )

        end_area = (
            2.0 * pi * (diameter_m / 2.0) ** 2
        )

        return cylindrical_area + end_area

    # ------------------------------------------------------------------------
    # DESIGN
    # ------------------------------------------------------------------------

    def design(self) -> Dict[str, Any]:
        """
        Run the complete preliminary pressure-vessel design calculation.
        """

        # ---- Geometry / inputs ---------------------------------------------

        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        if self.vessel_type == "spherical":
            length = 0.0
        else:
            length = _value(
                self.inputs.get(
                    "length",
                    self.inputs.get(
                        "tangent_to_tangent_length"
                    ),
                ),
                "length",
                "m",
            )

        pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        design_pressure_obj = Pressure(
            pressure,
            "Pa",
        )

        design_temperature = self.design_temperature

        material = self.material

        # ---- Allowable stress ----------------------------------------------

        temperature_band = set_temperature_range(
            design_temperature
        )

        allowable_stress = get_allowable_stress(
            material,
            design_temperature,
        )

        allowable_stress_psi = _value(
            allowable_stress,
            "allowable stress",
            "psi",
        )

        allowable_stress_ksi = (
            allowable_stress_psi / 1000.0
        )

        # ---- Thickness ------------------------------------------------------

        if self.vessel_type == "spherical":
            shell_required = self.head_thickness()
        else:
            shell_required = self.shell_thickness()

        head_required = self.head_thickness()

        shell_required_mm = _value(
            shell_required,
            "shell thickness",
            "mm",
        )

        head_required_mm = _value(
            head_required,
            "head thickness",
            "mm",
        )

        governing_required_mm = max(
            shell_required_mm,
            head_required_mm,
        )

        selected = self.select_standard_thickness(
            Length(
                governing_required_mm,
                "mm",
            )
        )

        selected_thickness_mm = _value(
            selected,
            "selected thickness",
            "mm",
        )

        # ---- Volume ---------------------------------------------------------

        internal_volume = self.volume()

        internal_volume_m3 = _value(
            internal_volume,
            "internal volume",
            "m3",
        )

        specified_volume = self.inputs.get("volume")

        volume_check = None
        volume_margin_m3 = None
        volume_margin_percent = None

        if specified_volume is not None:
            specified_volume_m3 = _value(
                specified_volume,
                "volume",
                "m3",
            )

            if specified_volume_m3 <= 0:
                raise ValueError(
                    "volume must be greater than zero."
                )

            volume_margin_m3 = (
                internal_volume_m3
                - specified_volume_m3
            )

            volume_margin_percent = (
                volume_margin_m3
                / specified_volume_m3
                * 100.0
            )

            volume_check = (
                internal_volume_m3
                >= specified_volume_m3
            )

        # ---- Area / weight --------------------------------------------------

        external_area = self._external_area(
            diameter,
            length,
        )

        density_default = MATERIAL_DENSITIES.get(
            material,
            7850.0,
        )

        density = float(
            self.inputs.get(
                "material_density",
                density_default,
            )
        )

        selected_thickness_m = (
            selected_thickness_mm / 1000.0
        )

        estimated_weight_kg = (
            external_area
            * selected_thickness_m
            * density
        )

        # ---- Hydrotest ------------------------------------------------------

        hydrotest_pressure = Pressure(
            1.3 * pressure,
            "Pa",
        )

        hydrotest_pressure_bar = _value(
            hydrotest_pressure,
            "hydrotest pressure",
            "bar",
        )

        hydrotest_pressure_psi = _value(
            hydrotest_pressure,
            "hydrotest pressure",
            "psi",
        )

        # ---- Design-condition conversions ----------------------------------

        design_pressure_bar = _value(
            design_pressure_obj,
            "design pressure",
            "bar",
        )

        design_pressure_psi = _value(
            design_pressure_obj,
            "design pressure",
            "psi",
        )

        design_temperature_f = _value(
            design_temperature,
            "design temperature",
            "F",
        )

        # ---- Warnings -------------------------------------------------------

        warnings = [
            (
                "Preliminary ASME Section VIII Division 1 "
                "internal-pressure sizing only."
            ),
            (
                "Allowable stresses are taken from the supplied "
                "temperature-specific preliminary material database."
            ),
            (
                "Verify all material allowable stresses against the "
                "applicable ASME Section II, Part D tables before "
                "code-stamped design or fabrication."
            ),
            (
                "External pressure/vacuum, complete nozzle reinforcement, "
                "supports, wind, seismic, fatigue, MDMT, PWHT, and flanges "
                "are not evaluated."
            ),
        ]

        if self.nozzles or self.manholes:
            warnings.append(
                "Nozzle and manhole reinforcement calculations are not included."
            )

        if (
            specified_volume is not None
            and not volume_check
        ):
            warnings.append(
                "Calculated internal vessel volume is less than "
                "the specified design volume."
            )

        # ---- Design basis ---------------------------------------------------

        design_basis = (
            "ASME VIII-1 preliminary: "
            "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
        )

        # ---- Result dictionary ----------------------------------------------

        result = {
            "vessel_type": self.vessel_type,

            "head_type": self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            ),

            "material": material,

            "design_pressure": design_pressure_obj,
            "design_pressure_bar": design_pressure_bar,
            "design_pressure_psi": design_pressure_psi,

            "design_temperature": design_temperature,
            "design_temperature_F": Temperature(
                design_temperature_f,
                "F",
            ),

            "allowable_stress_temperature_band":
                temperature_band,

            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            "diameter": Diameter(
                diameter,
                "m",
            ),

            "length": (
                Length(length, "m")
                if self.vessel_type != "spherical"
                else Length(0.0, "m")
            ),

            "joint_efficiency": float(
                self.inputs.get(
                    "joint_efficiency",
                    1.0,
                )
            ),

            "corrosion_allowance": Length(
                _value(
                    self.inputs.get(
                        "corrosion_allowance",
                        Length(0, "mm"),
                    ),
                    "corrosion_allowance",
                    "m",
                ),
                "m",
            ),

            "shell_required_thickness":
                shell_required,

            "head_required_thickness":
                head_required,

            "governing_required_thickness":
                Length(
                    governing_required_mm,
                    "mm",
                ),

            "selected_thickness":
                selected,

            "specified_volume":
                specified_volume,

            "internal_volume":
                internal_volume,

            "volume_check":
                volume_check,

            "volume_margin": (
                Volume(
                    volume_margin_m3,
                    "m3",
                )
                if volume_margin_m3 is not None
                else None
            ),

            "volume_margin_percent":
                volume_margin_percent,

            "external_area":
                Area(
                    external_area,
                    "m2",
                ),

            "material_density_kg_m3":
                density,

            "estimated_weight_kg":
                estimated_weight_kg,

            "hydrotest_pressure":
                hydrotest_pressure,

            "hydrotest_pressure_bar":
                hydrotest_pressure_bar,

            "hydrotest_pressure_psi":
                hydrotest_pressure_psi,

            "nozzles":
                self.nozzles.copy(),

            "manholes":
                self.manholes.copy(),

            "warnings":
                warnings,

            "design_basis":
                design_basis,
        }

        return result

    # ------------------------------------------------------------------------
    # CALCULATIONBASE COMPATIBILITY
    # ------------------------------------------------------------------------

    def calculate(self) -> Dict[str, Any]:
        """
        Concrete CalculationBase implementation.

        This is intentionally a method rather than:

            calculate = design

        so that PressureVessel explicitly satisfies the abstract base class.
        """
        return self.design()


# ============================================================================
# BACKWARD-COMPATIBLE CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(PressureVessel):
    """Backward-compatible horizontal cylindrical vessel with flat ends."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("vessel_type", "horizontal")
        kwargs.setdefault("head_type", "flat")
        super().__init__(**kwargs)


class CylindricalHorizontalDishEnd(PressureVessel):
    """Backward-compatible horizontal cylindrical vessel with ellipsoidal ends."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("vessel_type", "horizontal")
        kwargs.setdefault("head_type", "ellipsoidal")
        super().__init__(**kwargs)


# Backward-compatible alias expected by processpi.equipment.__init__
PressureVessels = PressureVessel


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "PressureVessel",
    "PressureVessels",
    "PressureVesselResults",
    "CylindricalHorizontalFlatEnd",
    "CylindricalHorizontalDishEnd",
    "asme_material_stress_data",
    "MATERIAL_DENSITIES",
    "MATERIAL_ALIASES",
    "ASME_STRESS_TEMPERATURES_F",
    "ASME_TEMPERATURE_BANDS",
    "MIN_SUPPORTED_TEMPERATURE_F",
    "MAX_SUPPORTED_TEMPERATURE_F",
    "normalize_material",
    "get_allowable_stress",
    "set_temperature_range",
]
