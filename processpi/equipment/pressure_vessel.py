"""
ProcessPI - Pressure Vessel Equipment Module
============================================

Preliminary pressure-vessel sizing based on ASME Section VIII Division 1.

Implemented
-----------
- Complete supplied preliminary material allowable-stress database
- Temperature-specific allowable stresses
- Conservative temperature-band selection
- Material aliases
- Cylindrical shell sizing
- 2:1 ellipsoidal head sizing
- Hemispherical head sizing
- Flat-head preliminary sizing
- Corrosion allowance
- Joint efficiency
- Vessel volume calculation
- Volume requirement check
- Nozzles
- Manholes
- Hydrotest pressure
- Material density
- Approximate vessel weight
- Expanded result dictionary
- CalculationBase compatibility
- Backward-compatible PressureVessels alias

IMPORTANT
---------
This module is intended for preliminary engineering calculations only.

It is NOT a replacement for:
- ASME Section VIII design verification
- ASME Section II, Part D allowable-stress tables
- Complete nozzle reinforcement calculations
- External-pressure/vacuum calculations
- Saddle/support design
- Wind/seismic calculations
- Fatigue analysis
- MDMT evaluation
- PWHT requirements
- Flange design
- Detailed fabrication drawings
- Code-stamped design

All final engineering designs must be independently verified against the
applicable ASME code edition and project design basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, pi, sqrt
from typing import Any, Dict, List, Optional

from processpi.calculations.base import CalculationBase
from processpi.units import (
    Area,
    Diameter,
    Length,
    Pressure,
    Temperature,
    Volume,
)


# ============================================================================
# ASME PRELIMINARY MATERIAL ALLOWABLE-STRESS DATABASE
# ============================================================================
#
# Temperature keys : °F
# Stress values    : ksi
#
# These are the values originally supplied for ProcessPI.
#
# IMPORTANT:
# Preliminary application database only.
# Verify against the applicable ASME Section II, Part D table before
# code-stamped design or fabrication.
# ============================================================================

asme_material_stress_data: Dict[str, Dict[int, float]] = {

    "SA515-55": {
        100: 13.7,
        200: 13.7,
        300: 13.7,
        400: 13.7,
        500: 13.7,
        600: 13.7,
        700: 13.2,
        800: 10.2,
    },

    "SA515-70": {
        100: 17.5,
        200: 17.5,
        300: 17.5,
        400: 17.5,
        500: 17.5,
        600: 17.5,
        700: 16.6,
        800: 12.0,
    },

    "SA516-55": {
        100: 13.7,
        200: 13.7,
        300: 13.7,
        400: 13.7,
        500: 13.7,
        600: 13.7,
        700: 13.2,
        800: 10.2,
    },

    "SA516-70": {
        100: 20.0,
        200: 20.0,
        300: 20.0,
        400: 20.0,
        500: 20.0,
        600: 19.4,
        700: 18.1,
        800: 12.0,
    },

    "SA256-A": {
        100: 11.2,
        200: 11.2,
        300: 11.2,
        400: 11.2,
        500: 11.2,
        600: 11.2,
        700: 11.0,
        800: 9.0,
    },

    "SA285-B": {
        100: 1.2,
        200: 1.2,
        300: 1.2,
        400: 1.2,
        500: 1.2,
        600: 1.2,
        700: 12.1,
        800: 9.6,
    },

    "SA285-C": {
        100: 13.7,
        200: 13.7,
        300: 13.7,
        400: 13.7,
        500: 13.7,
        600: 13.7,
        700: 13.2,
        800: 10.2,
    },

    "SA202-A": {
        100: 18.7,
        200: 18.7,
        300: 18.7,
        400: 18.7,
        500: 18.7,
        600: 18.7,
        700: 17.7,
        800: 12.6,
    },

    "SA202-B": {
        100: 21.2,
        200: 21.2,
        300: 21.2,
        400: 21.2,
        500: 21.2,
        600: 21.2,
        700: 19.8,
        800: 12.9,
    },

    "SA387-D": {
        100: 15.0,
        200: 15.0,
        300: 15.0,
        400: 15.0,
        500: 15.0,
        600: 15.0,
        700: 15.0,
        800: 15.0,
    },

    "SA240-304": {
        100: 20.0,
        200: 20.0,
        300: 18.9,
        400: 18.3,
        500: 17.5,
        600: 16.6,
        700: 15.8,
        800: 15.2,
    },

    "SA240-304L": {
        100: 16.7,
        200: 16.7,
        300: 16.7,
        400: 15.8,
        500: 14.7,
        600: 14.0,
        700: 13.5,
        800: 13.0,
    },

    "SA240-309S": {
        100: 20.0,
        200: 20.0,
        300: 20.0,
        400: 20.0,
        500: 19.4,
        600: 18.8,
        700: 18.2,
        800: 17.7,
    },

    "SA240-310": {
        100: 20.0,
        200: 20.0,
        300: 20.0,
        400: 19.9,
        500: 19.3,
        600: 18.5,
        700: 17.9,
        800: 17.4,
    },

    "SA240-316": {
        100: 20.0,
        200: 20.0,
        300: 20.0,
        400: 19.3,
        500: 18.0,
        600: 17.0,
        700: 16.3,
        800: 15.9,
    },

    "SA240-316L": {
        100: 16.7,
        200: 16.7,
        300: 16.7,
        400: 15.7,
        500: 14.8,
        600: 14.0,
        700: 13.5,
        800: 12.9,
    },

    "SA240-317L": {
        100: 20.0,
        200: 20.0,
        300: 19.6,
        400: 18.9,
        500: 17.7,
        600: 16.9,
        700: 16.2,
        800: 15.5,
    },

    "SA240-347": {
        100: 20.0,
        200: 20.0,
        300: 18.8,
        400: 17.8,
        500: 17.2,
        600: 16.9,
        700: 16.8,
        800: 16.8,
    },

    "B162": {
        100: 10.0,
        200: 10.0,
        300: 10.0,
        400: 10.0,
        500: 10.0,
        600: 10.0,
        700: 0.0,
        800: 0.0,
    },

    "201": {
        100: 8.0,
        200: 7.7,
        300: 7.5,
        400: 7.5,
        500: 7.5,
        600: 7.5,
        700: 7.4,
        800: 7.2,
    },

    "B127": {
        100: 18.7,
        200: 16.4,
        300: 15.2,
        400: 14.7,
        500: 14.7,
        600: 14.7,
        700: 14.6,
        800: 14.3,
    },

    "B168": {
        100: 22.9,
        200: 22.9,
        300: 22.9,
        400: 22.9,
        500: 22.9,
        600: 22.9,
        700: 22.9,
        800: 22.9,
    },

    "B443": {
        100: 34.3,
        200: 34.3,
        300: 34.3,
        400: 33.6,
        500: 32.9,
        600: 32.4,
        700: 31.8,
        800: 31.2,
    },

    "C-22 alloy": {
        100: 28.6,
        200: 28.6,
        300: 28.2,
        400: 27.2,
        500: 26.5,
        600: 26.0,
        700: 25.6,
        800: 25.3,
    },

    "B575": {
        100: 27.3,
        200: 27.3,
        300: 27.3,
        400: 27.3,
        500: 26.5,
        600: 26.0,
        700: 25.6,
        800: 25.3,
    },

    "B333": {
        100: 31.4,
        200: 31.4,
        300: 31.4,
        400: 31.4,
        500: 31.4,
        600: 31.2,
        700: 30.9,
        800: 30.6,
    },

    "B463": {
        100: 22.9,
        200: 22.9,
        300: 22.6,
        400: 22.2,
        500: 22.1,
        600: 22.1,
        700: 21.9,
        800: 21.8,
    },

    "B409": {
        100: 20.0,
        200: 20.0,
        300: 20.0,
        400: 20.0,
        500: 20.0,
        600: 20.0,
        700: 20.0,
        800: 20.0,
    },

    "B424": {
        100: 23.3,
        200: 23.3,
        300: 23.3,
        400: 23.3,
        500: 23.3,
        600: 23.3,
        700: 23.2,
        800: 23.0,
    },

    "B688": {
        100: 27.1,
        200: 27.1,
        300: 25.7,
        400: 24.6,
        500: 23.8,
        600: 23.3,
        700: 22.9,
        800: 22.6,
    },

    "A240 904": {
        100: 20.3,
        200: 16.7,
        300: 15.1,
        400: 13.8,
        500: 12.7,
        600: 11.9,
        700: 11.4,
        800: 0.0,
    },

    "G-30 Alloy": {
        100: 23.3,
        200: 23.3,
        300: 23.2,
        400: 22.5,
        500: 21.9,
        600: 21.3,
        700: 20.5,
        800: 19.7,
    },

    "Titanium Grade 2": {
        100: 14.3,
        200: 12.4,
        300: 10.3,
        400: 8.8,
        500: 7.6,
        600: 6.5,
        700: 0.0,
        800: 0.0,
    },

    "Zinccronium 702": {
        100: 15.7,
        200: 13.7,
        300: 11.2,
        400: 9.1,
        500: 7.4,
        600: 6.4,
        700: 5.2,
        800: 0.0,
    },
}


# ============================================================================
# TEMPERATURE CONSTANTS
# ============================================================================

ASME_STRESS_TEMPERATURES_F = (
    100,
    200,
    300,
    400,
    500,
    600,
    700,
    800,
)

MIN_SUPPORTED_TEMPERATURE_F = -20.0
MAX_SUPPORTED_TEMPERATURE_F = 800.0

TEMPERATURE_TOLERANCE_F = 1.0e-9


# ============================================================================
# MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES: Dict[str, str] = {

    # Carbon steel
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "carbonsteel": "SA516-70",
    "sa516-70": "SA516-70",
    "sa-516-70": "SA516-70",

    # Other common SA grades
    "sa515-55": "SA515-55",
    "sa-515-55": "SA515-55",

    "sa515-70": "SA515-70",
    "sa-515-70": "SA515-70",

    "sa516-55": "SA516-55",
    "sa-516-55": "SA516-55",

    "sa256-a": "SA256-A",
    "sa-256-a": "SA256-A",

    "sa285-b": "SA285-B",
    "sa-285-b": "SA285-B",

    "sa285-c": "SA285-C",
    "sa-285-c": "SA285-C",

    "sa202-a": "SA202-A",
    "sa-202-a": "SA202-A",

    "sa202-b": "SA202-B",
    "sa-202-b": "SA202-B",

    "sa387-d": "SA387-D",
    "sa-387-d": "SA387-D",

    # Stainless steels
    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",
    "stainless304": "SA240-304",
    "sa240-304": "SA240-304",

    "stainless_304l": "SA240-304L",
    "stainless 304l": "SA240-304L",
    "sa240-304l": "SA240-304L",

    "stainless_309s": "SA240-309S",
    "stainless 309s": "SA240-309S",
    "sa240-309s": "SA240-309S",

    "stainless_310": "SA240-310",
    "stainless 310": "SA240-310",
    "sa240-310": "SA240-310",

    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
    "sa240-316": "SA240-316",

    "stainless_316l": "SA240-316L",
    "stainless 316l": "SA240-316L",
    "sa240-316l": "SA240-316L",

    "stainless_317l": "SA240-317L",
    "stainless 317l": "SA240-317L",
    "sa240-317l": "SA240-317L",

    "stainless_347": "SA240-347",
    "stainless 347": "SA240-347",
    "sa240-347": "SA240-347",

    # Nickel / special alloys
    "c22 alloy": "C-22 alloy",
    "c-22 alloy": "C-22 alloy",
    "c-22": "C-22 alloy",

    "b575": "B575",
    "b333": "B333",
    "b463": "B463",
    "b409": "B409",
    "b424": "B424",
    "b688": "B688",
    "b162": "B162",
    "b127": "B127",
    "b168": "B168",
    "b443": "B443",

    "a240 904": "A240 904",
    "a240-904": "A240 904",
    "a240_904": "A240 904",

    "g-30 alloy": "G-30 Alloy",
    "g30 alloy": "G-30 Alloy",
    "g30": "G-30 Alloy",

    "titanium grade 2": "Titanium Grade 2",
    "titanium_grade_2": "Titanium Grade 2",
    "ti grade 2": "Titanium Grade 2",

    "zirconium 702": "Zinccronium 702",
    "zirconium_702": "Zinccronium 702",
    "zinccronium 702": "Zinccronium 702",
    "zinccronium_702": "Zinccronium 702",
}


# ============================================================================
# VALUE / UNIT HELPERS
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from a ProcessPI unit object or plain number.

    Important:
    Conversion is performed FIRST. Therefore:

        Temperature(150, "C") -> _value(..., "F") -> 302.0

    and:

        Pressure(10, "bar") -> _value(..., "Pa") -> 1,000,000

    The helper supports both ProcessPI ``value`` and ``original_value``
    representations.
    """

    if value is None:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value"
        )

    converted = value

    if hasattr(converted, "to") and unit:
        converted = converted.to(unit)

    # Prefer the public value representation after conversion.
    if hasattr(converted, "value"):
        raw = converted.value
    elif hasattr(converted, "original_value"):
        raw = converted.original_value
    else:
        raw = converted

    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value"
        ) from exc


def _pressure_pa(value: Any) -> float:
    return _value(value, "pressure", "Pa")


def _length_m(value: Any) -> float:
    return _value(value, "length", "m")


def _diameter_m(value: Any) -> float:
    return _value(value, "diameter", "m")


# ============================================================================
# MATERIAL FUNCTIONS
# ============================================================================

def normalize_material(material: Any) -> str:
    """
    Normalize a material name to the canonical database key.
    """

    if material is None:
        raise ValueError("Material must be specified.")

    key = str(material).strip()

    # Exact database key
    if key in asme_material_stress_data:
        return key

    # Case-insensitive direct database lookup
    lower_key = key.lower()

    for material_name in asme_material_stress_data:
        if material_name.lower() == lower_key:
            return material_name

    # Alias lookup
    if lower_key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[lower_key]

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: "
        f"{', '.join(asme_material_stress_data.keys())}"
    )


def set_temperature_range(
    temperature: Any,
) -> Temperature:
    """
    Select the conservative ASME allowable-stress temperature band.

    The supplied database is tabulated at:

        100°F
        200°F
        300°F
        400°F
        500°F
        600°F
        700°F
        800°F

    Conservative selection:

        T <= 100°F  -> 100°F
        T <= 200°F  -> 200°F
        T <= 300°F  -> 300°F
        T <= 400°F  -> 400°F
        T <= 500°F  -> 500°F
        T <= 600°F  -> 600°F
        T <= 700°F  -> 700°F
        T <= 800°F  -> 800°F

    Example:

        533°F -> 600°F

    This is the critical fix for the previous KeyError/ValueError.

    Temperatures below -20°F are rejected.

    Temperatures above 800°F are rejected.
    """

    fahrenheit = _value(
        temperature,
        "temperature",
        "F",
    )

    # Minimum supported temperature.
    if fahrenheit < (
        MIN_SUPPORTED_TEMPERATURE_F
        - TEMPERATURE_TOLERANCE_F
    ):
        raise ValueError(
            "Design temperature is below the available "
            "allowable-stress database. "
            "Minimum supported temperature is -20°F."
        )

    # Conservative upward band selection.
    for band in ASME_STRESS_TEMPERATURES_F:
        if fahrenheit <= (
            band + TEMPERATURE_TOLERANCE_F
        ):
            return Temperature(
                band,
                "F",
            )

    # Above maximum.
    raise ValueError(
        "Design temperature exceeds the available "
        "allowable-stress database. "
        "Maximum supported temperature is 800°F."
    )


def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return allowable stress as a ProcessPI Pressure object in psi.

    Numeric material values are interpreted as explicit allowable stress
    in ksi.

    For material database lookup, the design temperature is first converted
    to Fahrenheit and then mapped to the NEXT HIGHER available temperature
    band.

    Example:

        302°F -> 400°F
        533°F -> 600°F
        797°F -> 800°F
    """

    # ------------------------------------------------------------------
    # Explicit numerical allowable stress
    # ------------------------------------------------------------------

    if isinstance(material, (int, float)):
        stress_ksi = float(material)

        if stress_ksi <= 0.0:
            raise ValueError(
                "Allowable stress must be greater than zero."
            )

        return Pressure(
            stress_ksi * 1000.0,
            "psi",
        )

    # ------------------------------------------------------------------
    # Normalize material
    # ------------------------------------------------------------------

    material_key = normalize_material(material)

    # ------------------------------------------------------------------
    # Select temperature BAND
    # ------------------------------------------------------------------

    temperature_band = set_temperature_range(
        temperature
    )

    temperature_band_f = int(
        round(
            _value(
                temperature_band,
                "temperature band",
                "F",
            )
        )
    )

    # ------------------------------------------------------------------
    # IMPORTANT:
    # Use the BAND as the database key.
    #
    # Do NOT use actual design temperature here.
    #
    # 533°F -> 600°F -> database[600]
    # ------------------------------------------------------------------

    stress_table = asme_material_stress_data[
        material_key
    ]

    if temperature_band_f not in stress_table:
        raise ValueError(
            f"No allowable stress temperature band is "
            f"available for material '{material_key}' "
            f"at {temperature_band_f}°F."
        )

    stress_ksi = float(
        stress_table[temperature_band_f]
    )

    # ------------------------------------------------------------------
    # Zero means no allowable stress available.
    # ------------------------------------------------------------------

    if stress_ksi <= 0.0:
        raise ValueError(
            f"No allowable stress is available for "
            f"material '{material_key}' at "
            f"{temperature_band_f}°F."
        )

    return Pressure(
        stress_ksi * 1000.0,
        "psi",
    )


# ============================================================================
# RESULTS
# ============================================================================

@dataclass
class PressureVesselResults:
    """
    Structured pressure-vessel calculation results.
    """

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
    """
    Preliminary ASME VIII-1 pressure vessel sizing model.

    Supported vessel types:

        horizontal
        vertical
        spherical

    Supported head types:

        2:1_ellipsoidal
        ellipsoidal
        hemispherical
        flat
    """

    STANDARD_THICKNESSES_MM = (
        3,
        4,
        5,
        6,
        8,
        10,
        12,
        16,
        20,
        25,
        32,
        40,
        50,
    )

    _HEADS = {
        "flat",
        "ellipsoidal",
        "torispherical",
        "hemispherical",
        "conical",
    }

    _TYPES = {
        "horizontal",
        "vertical",
        "spherical",
    }

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        # CalculationBase requires validate_inputs().
        super().__init__(**kwargs)

        self.nozzles: Dict[
            str,
            Dict[str, Any]
        ] = {}

        self.manholes: Dict[
            str,
            Dict[str, Any]
        ] = {}

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def validate_inputs(self) -> None:
        """
        Validate pressure-vessel inputs.

        This method is intentionally compatible with ProcessPI's
        CalculationBase initialization workflow.
        """

        inputs = self.inputs

        # ------------------------------------------------------------------
        # Vessel type
        # ------------------------------------------------------------------

        vessel_type = str(
            inputs.get(
                "vessel_type",
                inputs.get(
                    "orientation",
                    "horizontal",
                ),
            )
        ).strip().lower()

        if vessel_type not in self._TYPES:
            raise ValueError(
                f"vessel_type must be one of "
                f"{sorted(self._TYPES)}"
            )

        # ------------------------------------------------------------------
        # Pressure
        # ------------------------------------------------------------------

        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        if pressure is None:
            raise ValueError(
                "design_pressure must be specified."
            )

        pressure_pa = _pressure_pa(
            pressure
        )

        if pressure_pa <= 0.0:
            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # ------------------------------------------------------------------
        # Diameter
        # ------------------------------------------------------------------

        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None:
            raise ValueError(
                "diameter must be specified."
            )

        diameter_m = _diameter_m(
            diameter
        )

        if diameter_m <= 0.0:
            raise ValueError(
                "diameter must be greater than zero."
            )

        # ------------------------------------------------------------------
        # Length
        # ------------------------------------------------------------------

        if vessel_type != "spherical":

            length = inputs.get(
                "length",
                inputs.get(
                    "tangent_to_tangent_length"
                ),
            )

            if length is None:
                raise ValueError(
                    "length must be specified for "
                    "cylindrical vessels."
                )

            length_m = _length_m(
                length
            )

            if length_m <= 0.0:
                raise ValueError(
                    "length must be greater than zero "
                    "for cylindrical vessels."
                )

        # ------------------------------------------------------------------
        # Joint efficiency
        # ------------------------------------------------------------------

        try:
            joint_efficiency = float(
                inputs.get(
                    "joint_efficiency",
                    1.0,
                )
            )
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "joint_efficiency must be numeric."
            ) from exc

        if not 0.0 < joint_efficiency <= 1.0:
            raise ValueError(
                "joint_efficiency must be greater than "
                "zero and no more than one."
            )

        # ------------------------------------------------------------------
        # Corrosion allowance
        # ------------------------------------------------------------------

        corrosion_allowance = inputs.get(
            "corrosion_allowance",
            Length(0, "mm"),
        )

        corrosion_allowance_m = _length_m(
            corrosion_allowance
        )

        if corrosion_allowance_m < 0.0:
            raise ValueError(
                "corrosion_allowance must be non-negative."
            )

        # ------------------------------------------------------------------
        # Head type
        # ------------------------------------------------------------------

        head_type = str(
            inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

        supported_head_types = {
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
            "hemispherical",
            "hemisphere",
            "flat",
            "flat_head",
        }

        if head_type not in supported_head_types:
            raise ValueError(
                f"Unsupported head_type '{head_type}'. "
                "Supported types: "
                "2:1_ellipsoidal, hemispherical, flat."
            )

        # ------------------------------------------------------------------
        # Temperature / material validation
        # ------------------------------------------------------------------

        material = inputs.get(
            "material",
            "SA516-70",
        )

        design_temperature = inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

        # This validates:
        #  - minimum temperature
        #  - maximum temperature
        #  - temperature band
        #  - material
        #  - zero-stress entries
        get_allowable_stress(
            material,
            design_temperature,
        )

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def vessel_type(self) -> str:
        return str(
            self.inputs.get(
                "vessel_type",
                self.inputs.get(
                    "orientation",
                    "horizontal",
                ),
            )
        ).strip().lower()

    @property
    def material(self) -> str:
        return normalize_material(
            self.inputs.get(
                "material",
                "SA516-70",
            )
        )

    @property
    def design_temperature(self) -> Any:
        return self.inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

    # ========================================================================
    # ALLOWABLE STRESS
    # ========================================================================

    def allowable_stress(self) -> Pressure:
        """
        Return allowable stress at the design temperature.
        """

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # ========================================================================
    # NOZZLES
    # ========================================================================

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Add a nozzle.

        Currently stored for reporting only.

        Nozzle reinforcement calculation is NOT performed.
        """

        if not name:
            raise ValueError(
                "Nozzle name must not be empty."
            )

        diameter_m = _diameter_m(
            diameter
        )

        if diameter_m <= 0.0:
            raise ValueError(
                "nozzle diameter must be greater than zero."
            )

        self.nozzles[str(name)] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # ========================================================================
    # MANHOLES
    # ========================================================================

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Add a manhole.

        Currently stored for reporting only.

        Manhole reinforcement calculation is NOT performed.
        """

        if not name:
            raise ValueError(
                "Manhole name must not be empty."
            )

        diameter_m = _diameter_m(
            diameter
        )

        if diameter_m <= 0.0:
            raise ValueError(
                "manhole diameter must be greater than zero."
            )

        self.manholes[str(name)] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # ========================================================================
    # SHELL THICKNESS
    # ========================================================================

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical-shell thickness.

        Based on ASME VIII-1 UG-27(c)(1):

            t = PR / (SE - 0.6P)

        Corrosion allowance is added after pressure thickness.
        """

        pressure_pa = _pressure_pa(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            )
        )

        diameter_m = _diameter_m(
            self.inputs.get(
                "diameter",
                self.inputs.get(
                    "inside_diameter"
                ),
            )
        )

        radius_m = diameter_m / 2.0

        allowable_stress_pa = _value(
            self.allowable_stress(),
            "allowable stress",
            "Pa",
        )

        joint_efficiency = float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        corrosion_allowance_m = _length_m(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            )
        )

        denominator = (
            allowable_stress_pa
            * joint_efficiency
            - 0.6 * pressure_pa
        )

        if denominator <= 0.0:
            raise ValueError(
                "Shell thickness equation has a "
                "non-positive denominator. "
                "Check pressure, allowable stress, "
                "and joint efficiency."
            )

        pressure_thickness_m = (
            pressure_pa
            * radius_m
            / denominator
        )

        return Length(
            pressure_thickness_m
            + corrosion_allowance_m,
            "m",
        )

    # ========================================================================
    # HEAD THICKNESS
    # ========================================================================

    def head_thickness(self) -> Length:
        """
        Preliminary vessel-head thickness.

        2:1 ellipsoidal:

            t = PD / (2SE - 0.2P)

        Hemispherical:

            t = PR / (2SE - 0.2P)

        Flat head:

            preliminary screening equation only.

        Corrosion allowance is added to all cases.
        """

        pressure_pa = _pressure_pa(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            )
        )

        diameter_m = _diameter_m(
            self.inputs.get(
                "diameter",
                self.inputs.get(
                    "inside_diameter"
                ),
            )
        )

        radius_m = diameter_m / 2.0

        allowable_stress_pa = _value(
            self.allowable_stress(),
            "allowable stress",
            "Pa",
        )

        joint_efficiency = float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        corrosion_allowance_m = _length_m(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            )
        )

        head_type = str(
            self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

        # Normalize head aliases.
        if head_type in {
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
        }:
            normalized = "2:1_ellipsoidal"

        elif head_type in {
            "hemisphere",
        }:
            normalized = "hemispherical"

        elif head_type in {
            "flat_head",
        }:
            normalized = "flat"

        else:
            normalized = head_type

        # ---------------------------------------------------------------
        # 2:1 ellipsoidal
        # ---------------------------------------------------------------

        if normalized == "2:1_ellipsoidal":

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure_pa
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Ellipsoidal-head thickness equation "
                    "has a non-positive denominator."
                )

            pressure_thickness_m = (
                pressure_pa
                * diameter_m
                / denominator
            )

        # ---------------------------------------------------------------
        # Hemispherical
        # ---------------------------------------------------------------

        elif normalized == "hemispherical":

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure_pa
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Hemispherical-head thickness equation "
                    "has a non-positive denominator."
                )

            pressure_thickness_m = (
                pressure_pa
                * radius_m
                / denominator
            )

        # ---------------------------------------------------------------
        # Flat
        # ---------------------------------------------------------------

        elif normalized == "flat":

            # Preliminary screening equation only.
            #
            # Final flat-head design requires detailed evaluation of:
            # - geometry
            # - attachment
            # - bending
            # - edge conditions
            # - gasket seating
            # - construction details

            denominator = (
                allowable_stress_pa
                * joint_efficiency
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Flat-head thickness calculation has "
                    "a non-positive denominator."
                )

            pressure_thickness_m = (
                0.55
                * diameter_m
                * sqrt(
                    pressure_pa
                    / denominator
                )
            )

        else:
            raise ValueError(
                f"Unsupported head type '{head_type}'."
            )

        return Length(
            pressure_thickness_m
            + corrosion_allowance_m,
            "m",
        )

    # ========================================================================
    # STANDARD THICKNESS
    # ========================================================================

    def select_standard_thickness(
        self,
        required: Any,
    ) -> Length:
        """
        Select the next standard plate thickness.

        If the required thickness exceeds the largest standard value,
        the calculated required thickness is returned.
        """

        required_mm = _value(
            required,
            "required thickness",
            "mm",
        )

        for thickness_mm in self.STANDARD_THICKNESSES_MM:

            if thickness_mm >= required_mm:
                return Length(
                    thickness_mm,
                    "mm",
                )

        return Length(
            required_mm,
            "mm",
        )

    # ========================================================================
    # HEAD VOLUME
    # ========================================================================

    def _head_volume(
        self,
        radius_m: float,
        head_type: str,
    ) -> float:
        """
        Approximate volume of BOTH heads, m³.

        2:1 ellipsoidal:
            total = πD³/12 = 2/3 πr³

        Hemispherical:
            total = 4/3 πr³

        Flat:
            zero

        These are preliminary geometric approximations.
        """

        normalized = str(
            head_type
        ).strip().lower()

        if normalized in {
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
        }:
            factor = 2.0 / 3.0

        elif normalized in {
            "hemispherical",
            "hemisphere",
        }:
            factor = 4.0 / 3.0

        elif normalized in {
            "flat",
            "flat_head",
        }:
            factor = 0.0

        elif normalized == "torispherical":
            factor = 0.5

        elif normalized == "conical":
            factor = 1.0 / 3.0

        else:
            raise ValueError(
                f"Unsupported head type '{head_type}'."
            )

        return (
            factor
            * pi
            * radius_m ** 3
        )

    # ========================================================================
    # INTERNAL VOLUME
    # ========================================================================

    def volume(
        self,
        liquid_level: Any = None,
    ) -> Volume:
        """
        Calculate preliminary internal vessel volume.

        For cylindrical vessels:

            V = cylindrical volume + head volume

        ``length`` is treated as the straight cylindrical length.

        If ``liquid_level`` is supplied, a cylindrical segment approximation
        is used for screening purposes.
        """

        diameter_m = _diameter_m(
            self.inputs.get(
                "diameter",
                self.inputs.get(
                    "inside_diameter"
                ),
            )
        )

        radius_m = diameter_m / 2.0

        head_type = str(
            self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

        if self.vessel_type == "spherical":

            full_volume = (
                4.0
                / 3.0
                * pi
                * radius_m ** 3
            )

        else:

            length_m = _length_m(
                self.inputs.get(
                    "length",
                    self.inputs.get(
                        "tangent_to_tangent_length"
                    ),
                )
            )

            cylinder_volume = (
                pi
                * radius_m ** 2
                * length_m
            )

            head_volume = self._head_volume(
                radius_m,
                head_type,
            )

            full_volume = (
                cylinder_volume
                + head_volume
            )

        if liquid_level is None:
            return Volume(
                full_volume,
                "m3",
            )

        level_m = _length_m(
            liquid_level
        )

        if not 0.0 <= level_m <= diameter_m:
            raise ValueError(
                "liquid_level must be between zero "
                "and vessel diameter."
            )

        # Only cylindrical liquid volume is represented by this
        # simple segment calculation.
        if self.vessel_type == "spherical":
            h = level_m
            sphere_segment = (
                pi
                * h ** 2
                * (
                    radius_m
                    - h / 3.0
                )
            )

            return Volume(
                sphere_segment,
                "m3",
            )

        theta_term = acos(
            (
                radius_m - level_m
            )
            / radius_m
        )

        segment_area = (
            radius_m ** 2
            * theta_term
            - (
                radius_m
                - level_m
            )
            * sqrt(
                max(
                    0.0,
                    2.0
                    * radius_m
                    * level_m
                    - level_m ** 2,
                )
            )
        )

        length_m = _length_m(
            self.inputs.get(
                "length",
                self.inputs.get(
                    "tangent_to_tangent_length"
                ),
            )
        )

        liquid_volume = (
            segment_area
            * length_m
        )

        return Volume(
            liquid_volume,
            "m3",
        )

    # ========================================================================
    # EXTERNAL AREA
    # ========================================================================

    def _ellipsoidal_head_area(
        self,
        diameter_m: float,
    ) -> float:
        """
        Approximate external area of ONE 2:1 ellipsoidal head.

        Numerical integration is used for preliminary weight estimation.
        """

        a = diameter_m / 2.0
        c = diameter_m / 4.0

        n = 200
        total = 0.0

        dtheta = (
            pi / 2.0
        ) / n

        for i in range(n):

            theta = (
                i + 0.5
            ) * dtheta

            sin_theta = sqrt(
                max(
                    0.0,
                    1.0
                    - (
                        __import__("math").cos(
                            theta
                        ) ** 2
                    ),
                )
            )

            cos_theta = __import__(
                "math"
            ).cos(theta)

            element = (
                2.0
                * pi
                * a
                * sin_theta
                * sqrt(
                    c ** 2
                    * sin_theta ** 2
                    + a ** 2
                    * cos_theta ** 2
                )
            )

            total += (
                element
                * dtheta
            )

        return total

    def _external_area(
        self,
        diameter_m: float,
        length_m: float,
        head_type: str,
    ) -> float:
        """
        Approximate vessel external surface area, m².
        """

        normalized = str(
            head_type
        ).strip().lower()

        if self.vessel_type == "spherical":

            radius_m = diameter_m / 2.0

            return (
                4.0
                * pi
                * radius_m ** 2
            )

        cylindrical_area = (
            pi
            * diameter_m
            * length_m
        )

        if normalized in {
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
        }:

            head_area = (
                2.0
                * self._ellipsoidal_head_area(
                    diameter_m
                )
            )

        elif normalized in {
            "hemispherical",
            "hemisphere",
        }:

            radius_m = diameter_m / 2.0

            head_area = (
                4.0
                * pi
                * radius_m ** 2
            )

        elif normalized in {
            "flat",
            "flat_head",
        }:

            head_area = (
                2.0
                * pi
                * (
                    diameter_m ** 2
                    / 4.0
                )
            )

        else:
            raise ValueError(
                f"Unsupported head type '{head_type}'."
            )

        return (
            cylindrical_area
            + head_area
        )

    # ========================================================================
    # DESIGN
    # ========================================================================

    def design(self) -> Dict[str, Any]:
        """
        Execute the complete preliminary pressure-vessel design.
        """

        # Revalidate because attachments may have been added after
        # construction and because this provides a predictable public API.
        self.validate_inputs()

        # ------------------------------------------------------------------
        # Geometry
        # ------------------------------------------------------------------

        diameter_m = _diameter_m(
            self.inputs.get(
                "diameter",
                self.inputs.get(
                    "inside_diameter"
                ),
            )
        )

        if self.vessel_type == "spherical":
            length_m = 0.0
        else:
            length_m = _length_m(
                self.inputs.get(
                    "length",
                    self.inputs.get(
                        "tangent_to_tangent_length"
                    ),
                )
            )

        # ------------------------------------------------------------------
        # Material / temperature
        # ------------------------------------------------------------------

        material = self.material

        design_temperature = (
            self.design_temperature
        )

        design_temperature_f = _value(
            design_temperature,
            "design temperature",
            "F",
        )

        temperature_band = (
            set_temperature_range(
                design_temperature
            )
        )

        temperature_band_f = _value(
            temperature_band,
            "temperature band",
            "F",
        )

        allowable_stress = (
            self.allowable_stress()
        )

        allowable_stress_psi = _value(
            allowable_stress,
            "allowable stress",
            "psi",
        )

        allowable_stress_ksi = (
            allowable_stress_psi
            / 1000.0
        )

        # ------------------------------------------------------------------
        # Shell / head thickness
        # ------------------------------------------------------------------

        if self.vessel_type == "spherical":
            shell_required = (
                self.head_thickness()
            )
        else:
            shell_required = (
                self.shell_thickness()
            )

        head_required = (
            self.head_thickness()
        )

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

        selected_thickness = (
            self.select_standard_thickness(
                Length(
                    governing_required_mm,
                    "mm",
                )
            )
        )

        selected_thickness_mm = _value(
            selected_thickness,
            "selected thickness",
            "mm",
        )

        # ------------------------------------------------------------------
        # Design pressure
        # ------------------------------------------------------------------

        design_pressure = self.inputs.get(
            "design_pressure",
            self.inputs.get(
                "pressure"
            ),
        )

        design_pressure_pa = _pressure_pa(
            design_pressure
        )

        design_pressure_obj = Pressure(
            design_pressure_pa,
            "Pa",
        )

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

        # ------------------------------------------------------------------
        # Hydrotest
        # ------------------------------------------------------------------

        # Preliminary project-level assumption retained from previous
        # ProcessPI implementation.
        hydrotest_pressure = Pressure(
            1.3
            * design_pressure_pa,
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

        # ------------------------------------------------------------------
        # Volume
        # ------------------------------------------------------------------

        specified_volume = (
            self.inputs.get(
                "volume"
            )
        )

        specified_volume_obj = None

        if specified_volume is not None:

            specified_volume_m3 = _value(
                specified_volume,
                "volume",
                "m3",
            )

            if specified_volume_m3 <= 0.0:
                raise ValueError(
                    "volume must be greater than zero."
                )

            specified_volume_obj = Volume(
                specified_volume_m3,
                "m3",
            )

        internal_volume = self.volume()

        internal_volume_m3 = _value(
            internal_volume,
            "internal volume",
            "m3",
        )

        if specified_volume_obj is not None:

            specified_volume_m3 = _value(
                specified_volume_obj,
                "specified volume",
                "m3",
            )

            volume_margin_m3 = (
                internal_volume_m3
                - specified_volume_m3
            )

            volume_check = (
                internal_volume_m3
                >= specified_volume_m3
            )

            if specified_volume_m3 > 0.0:
                volume_margin_percent = (
                    volume_margin_m3
                    / specified_volume_m3
                    * 100.0
                )
            else:
                volume_margin_percent = None

        else:

            specified_volume_m3 = None
            volume_margin_m3 = None
            volume_check = None
            volume_margin_percent = None

        # ------------------------------------------------------------------
        # External area
        # ------------------------------------------------------------------

        head_type = self.inputs.get(
            "head_type",
            "2:1_ellipsoidal",
        )

        external_area_m2 = (
            self._external_area(
                diameter_m,
                length_m,
                head_type,
            )
        )

        external_area = Area(
            external_area_m2,
            "m2",
        )

        # ------------------------------------------------------------------
        # Material density
        # ------------------------------------------------------------------

        density = float(
            self.inputs.get(
                "material_density",
                7850.0,
            )
        )

        if density <= 0.0:
            raise ValueError(
                "material_density must be greater than zero."
            )

        # ------------------------------------------------------------------
        # Estimated weight
        # ------------------------------------------------------------------

        selected_thickness_m = (
            selected_thickness_mm
            / 1000.0
        )

        estimated_weight_kg = (
            external_area_m2
            * selected_thickness_m
            * density
        )

        # ------------------------------------------------------------------
        # Warnings
        # ------------------------------------------------------------------

        warnings = [

            "Preliminary ASME Section VIII Division 1 "
            "internal-pressure sizing only.",

            "Allowable stresses are taken from the supplied "
            "temperature-specific preliminary material database.",

            "Verify all material allowable stresses against "
            "the applicable ASME Section II, Part D tables "
            "before code-stamped design or fabrication.",

            "External pressure/vacuum, complete nozzle "
            "reinforcement, supports, wind, seismic, fatigue, "
            "MDMT, PWHT, and flanges are not evaluated.",
        ]

        if self.nozzles or self.manholes:

            warnings.append(
                "Nozzle and manhole reinforcement calculations "
                "are not included."
            )

        # ------------------------------------------------------------------
        # Head-specific warning
        # ------------------------------------------------------------------

        normalized_head = str(
            head_type
        ).strip().lower()

        if normalized_head in {
            "flat",
            "flat_head",
        }:

            warnings.append(
                "Flat-head thickness is a preliminary "
                "screening calculation and requires detailed "
                "ASME VIII verification."
            )

        # ------------------------------------------------------------------
        # Design basis
        # ------------------------------------------------------------------

        design_basis = (
            "ASME VIII-1 preliminary: "
            "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
        )

        # ------------------------------------------------------------------
        # Result dictionary
        # ------------------------------------------------------------------

        result = {

            # --------------------------------------------------------------
            # Identification
            # --------------------------------------------------------------

            "vessel_type":
                self.vessel_type,

            "head_type":
                head_type,

            "material":
                material,

            # --------------------------------------------------------------
            # Pressure
            # --------------------------------------------------------------

            "design_pressure":
                design_pressure_obj,

            "design_pressure_bar":
                design_pressure_bar,

            "design_pressure_psi":
                design_pressure_psi,

            # --------------------------------------------------------------
            # Temperature
            # --------------------------------------------------------------

            "design_temperature":
                design_temperature,

            "design_temperature_F":
                Temperature(
                    design_temperature_f,
                    "F",
                ),

            "allowable_stress_temperature_band":
                temperature_band,

            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            # --------------------------------------------------------------
            # Dimensions
            # --------------------------------------------------------------

            "diameter":
                Diameter(
                    diameter_m,
                    "m",
                ),

            "length":
                Length(
                    length_m,
                    "m",
                ),

            "joint_efficiency":
                float(
                    self.inputs.get(
                        "joint_efficiency",
                        1.0,
                    )
                ),

            "corrosion_allowance":
                Length(
                    _length_m(
                        self.inputs.get(
                            "corrosion_allowance",
                            Length(0, "mm"),
                        )
                    ),
                    "m",
                ),

            # --------------------------------------------------------------
            # Thickness
            # --------------------------------------------------------------

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
                selected_thickness,

            # --------------------------------------------------------------
            # Volume
            # --------------------------------------------------------------

            "specified_volume":
                specified_volume_obj,

            "internal_volume":
                internal_volume,

            "volume_check":
                volume_check,

            "volume_margin":
                (
                    Volume(
                        volume_margin_m3,
                        "m3",
                    )
                    if volume_margin_m3
                    is not None
                    else None
                ),

            "volume_margin_percent":
                volume_margin_percent,

            # --------------------------------------------------------------
            # Area / weight
            # --------------------------------------------------------------

            "external_area":
                external_area,

            "material_density_kg_m3":
                density,

            "estimated_weight_kg":
                estimated_weight_kg,

            # --------------------------------------------------------------
            # Hydrotest
            # --------------------------------------------------------------

            "hydrotest_pressure":
                hydrotest_pressure,

            "hydrotest_pressure_bar":
                hydrotest_pressure_bar,

            "hydrotest_pressure_psi":
                hydrotest_pressure_psi,

            # --------------------------------------------------------------
            # Attachments
            # --------------------------------------------------------------

            "nozzles":
                self.nozzles.copy(),

            "manholes":
                self.manholes.copy(),

            # --------------------------------------------------------------
            # Status
            # --------------------------------------------------------------

            "warnings":
                warnings,

            "design_basis":
                design_basis,
        }

        return result

    # ========================================================================
    # CALCULATIONBASE COMPATIBILITY
    # ========================================================================

    def calculate(self) -> Dict[str, Any]:
        """
        Required concrete implementation of CalculationBase.calculate().

        ``design()`` remains the public pressure-vessel method.

        ``calculate()`` provides the standard ProcessPI CalculationBase
        interface and prevents:

            TypeError:
            Can't instantiate abstract class PressureVessel
            without an implementation for abstract method 'calculate'
        """

        return self.design()


# ============================================================================
# BACKWARD-COMPATIBLE CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(
    PressureVessel
):
    """
    Backward-compatible horizontal cylindrical vessel
    with flat ends.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        kwargs.setdefault(
            "vessel_type",
            "horizontal",
        )

        kwargs.setdefault(
            "head_type",
            "flat",
        )

        super().__init__(
            **kwargs
        )


class CylindricalHorizontalDishEnd(
    PressureVessel
):
    """
    Backward-compatible horizontal cylindrical vessel
    with ellipsoidal/dished ends.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        kwargs.setdefault(
            "vessel_type",
            "horizontal",
        )

        kwargs.setdefault(
            "head_type",
            "ellipsoidal",
        )

        super().__init__(
            **kwargs
        )


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

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

    "MATERIAL_ALIASES",

    "ASME_STRESS_TEMPERATURES_F",

    "MIN_SUPPORTED_TEMPERATURE_F",

    "MAX_SUPPORTED_TEMPERATURE_F",

    "normalize_material",

    "get_allowable_stress",

    "set_temperature_range",
]
