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
- Material densities
- Cylindrical shell sizing
- 2:1 ellipsoidal head sizing
- Hemispherical head sizing
- Flat-head preliminary sizing
- Torispherical / conical preliminary sizing
- Corrosion allowance
- Joint efficiency
- Vessel volume calculation
- Volume adequacy check
- Nozzles
- Manholes
- Hydrotest pressure
- Estimated external area
- Estimated vessel weight
- Expanded result dictionary
- CalculationBase.calculate() implementation
- Backward-compatible PressureVessels alias

IMPORTANT
---------
This module is intended for preliminary engineering calculations.

It is NOT a replacement for:
- ASME Section VIII detailed design
- ASME Section II, Part D allowable-stress tables
- Complete nozzle reinforcement calculations
- External-pressure / vacuum calculations
- Saddle/support design
- Wind/seismic calculations
- Fatigue analysis
- MDMT evaluation
- PWHT evaluation
- Flange design
- Detailed fabrication drawings
- Code-stamped design

All final engineering designs must be independently verified against
the applicable ASME code edition and project design basis.
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
# Verify these values against the applicable ASME Section II,
# Part D tables before code-stamped design or fabrication.
# ============================================================================

asme_material_stress_data: Dict[str, Dict[int, float]] = {

    # ------------------------------------------------------------------------
    # CARBON STEELS / LOW ALLOY STEELS
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
    # STAINLESS STEELS
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
    # NICKEL / SPECIALTY ALLOYS
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
    # TITANIUM / ZIRCONIUM
    # ------------------------------------------------------------------------

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
# MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES: Dict[str, str] = {

    # Carbon / low-alloy steels
    "sa515-55": "SA515-55",
    "sa515 55": "SA515-55",

    "sa515-70": "SA515-70",
    "sa515 70": "SA515-70",

    "sa516-55": "SA516-55",
    "sa516 55": "SA516-55",

    "sa516-70": "SA516-70",
    "sa516 70": "SA516-70",
    "sa-516-70": "SA516-70",

    "sa256-a": "SA256-A",
    "sa256 a": "SA256-A",

    "sa285-b": "SA285-B",
    "sa285 b": "SA285-B",

    "sa285-c": "SA285-C",
    "sa285 c": "SA285-C",

    "sa202-a": "SA202-A",
    "sa202 a": "SA202-A",

    "sa202-b": "SA202-B",
    "sa202 b": "SA202-B",

    "sa387-d": "SA387-D",
    "sa387 d": "SA387-D",

    # Stainless steels
    "304": "SA240-304",
    "304 stainless": "SA240-304",
    "ss304": "SA240-304",
    "sa240-304": "SA240-304",

    "304l": "SA240-304L",
    "304l stainless": "SA240-304L",
    "ss304l": "SA240-304L",
    "sa240-304l": "SA240-304L",

    "309s": "SA240-309S",
    "sa240-309s": "SA240-309S",

    "310": "SA240-310",
    "sa240-310": "SA240-310",

    "316": "SA240-316",
    "316 stainless": "SA240-316",
    "ss316": "SA240-316",
    "sa240-316": "SA240-316",

    "316l": "SA240-316L",
    "316l stainless": "SA240-316L",
    "ss316l": "SA240-316L",
    "sa240-316l": "SA240-316L",

    "317l": "SA240-317L",
    "sa240-317l": "SA240-317L",

    "347": "SA240-347",
    "sa240-347": "SA240-347",

    # Nickel / specialty
    "b162": "B162",
    "201": "201",
    "b127": "B127",
    "b168": "B168",
    "b443": "B443",

    "c22": "C-22 alloy",
    "c-22": "C-22 alloy",
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
    "904": "A240 904",
    "904l": "A240 904",

    "g-30": "G-30 Alloy",
    "g-30 alloy": "G-30 Alloy",
    "g30 alloy": "G-30 Alloy",

    # Titanium / zirconium
    "titanium grade 2": "Titanium Grade 2",
    "ti grade 2": "Titanium Grade 2",
    "grade 2 titanium": "Titanium Grade 2",

    "zirconium 702": "Zinccronium 702",
    "zinccronium 702": "Zinccronium 702",
    "zr702": "Zinccronium 702",

    # Generic ProcessPI names
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",

    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",

    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
}


# ============================================================================
# MATERIAL DENSITIES
# ============================================================================
#
# kg/m3
# ============================================================================

MATERIAL_DENSITIES: Dict[str, float] = {

    # Carbon / low-alloy steels
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

    # Stainless
    "SA240-304": 8000.0,
    "SA240-304L": 8000.0,
    "SA240-309S": 8000.0,
    "SA240-310": 8000.0,
    "SA240-316": 8000.0,
    "SA240-316L": 8000.0,
    "SA240-317L": 8000.0,
    "SA240-347": 8000.0,

    # Specialty
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

    # Titanium / zirconium
    "Titanium Grade 2": 4510.0,
    "Zinccronium 702": 6500.0,
}


# ============================================================================
# TEMPERATURE SETTINGS
# ============================================================================

ASME_TEMPERATURE_BANDS = (
    100,
    200,
    300,
    400,
    500,
    600,
    700,
    800,
)

# Public/backward-compatible name
ASME_STRESS_TEMPERATURES_F = ASME_TEMPERATURE_BANDS

MIN_SUPPORTED_TEMPERATURE_F = -20.0
MAX_SUPPORTED_TEMPERATURE_F = 800.0

TEMPERATURE_TOLERANCE_F = 1.0e-6


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

    IMPORTANT:
    The conversion is performed BEFORE extracting .value.

    This avoids the previous temperature-band bug where the converted
    ProcessPI value could be confused with the original value.
    """

    if value is None:
        raise ValueError(f"{name} must be specified.")

    converted = value

    if hasattr(converted, "to") and unit:
        converted = converted.to(unit)

    if hasattr(converted, "value"):
        converted = converted.value
    elif hasattr(converted, "original_value"):
        converted = converted.original_value

    try:
        return float(converted)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value."
        ) from exc


def _temperature_to_f(
    temperature: Any,
) -> float:
    """
    Convert a temperature to °F.

    ProcessPI Temperature objects are converted through their public
    .to('F') interface.

    Plain numeric temperatures are interpreted as °F.
    """

    if isinstance(temperature, Temperature):
        try:
            converted = temperature.to("F")
            value = getattr(converted, "value", converted)
            return round(float(value), 6)
        except Exception as exc:
            raise TypeError(
                "Unable to convert design temperature to Fahrenheit."
            ) from exc

    if isinstance(temperature, (int, float)):
        return round(float(temperature), 6)

    raise TypeError(
        "Design temperature must be a ProcessPI Temperature "
        "or a numeric Fahrenheit value."
    )


# ============================================================================
# MATERIAL NORMALIZATION
# ============================================================================

def normalize_material(material: Any) -> str:
    """
    Normalize a user material name to the canonical database key.
    """

    if material is None:
        raise ValueError("Material must be specified.")

    material_text = str(material).strip()

    if not material_text:
        raise ValueError("Material must not be empty.")

    # Exact match
    if material_text in asme_material_stress_data:
        return material_text

    lowered = material_text.lower()

    # Case-insensitive canonical match
    for key in asme_material_stress_data:
        if key.lower() == lowered:
            return key

    # Alias match
    if lowered in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[lowered]

    raise ValueError(
        f"Unsupported material '{material}'. "
        f"Available materials: "
        f"{', '.join(asme_material_stress_data.keys())}"
    )


# Backward-compatible private alias
_normalize_material_key = normalize_material


# ============================================================================
# TEMPERATURE-BAND SELECTION
# ============================================================================

def set_temperature_range(
    temperature: Any,
) -> Temperature:
    """
    Select the next higher available allowable-stress temperature band.

    Examples
    --------
    77°F   -> 100°F
    150°F  -> 200°F
    302°F  -> 400°F
    533°F  -> 600°F
    797°F  -> 800°F
    800°F  -> 800°F

    Temperatures below -20°F are rejected.

    Temperatures above 800°F are rejected.
    """

    temperature_f = _temperature_to_f(temperature)

    # Minimum-temperature validation
    if (
        temperature_f
        < MIN_SUPPORTED_TEMPERATURE_F
        - TEMPERATURE_TOLERANCE_F
    ):
        raise ValueError(
            "Design temperature is below the available "
            "allowable-stress database. "
            f"Minimum supported temperature is "
            f"{MIN_SUPPORTED_TEMPERATURE_F:g}°F."
        )

    # IMPORTANT:
    # Select the FIRST available database temperature >= actual temperature.
    #
    # This is the critical correction for the previous:
    #
    #     KeyError: 533
    #
    # because 533°F itself is not a database key.
    for band in ASME_TEMPERATURE_BANDS:

        if temperature_f <= (
            band + TEMPERATURE_TOLERANCE_F
        ):
            return Temperature(
                band,
                "F",
            )

    raise ValueError(
        "Design temperature exceeds the available "
        "allowable-stress database. "
        f"Maximum supported temperature is "
        f"{MAX_SUPPORTED_TEMPERATURE_F:g}°F."
    )


def _get_temperature_band_f(
    temperature: Any,
) -> int:
    """
    Return selected allowable-stress temperature band as integer °F.
    """

    band = set_temperature_range(temperature)

    return int(
        round(
            _value(
                band,
                "temperature band",
                "F",
            )
        )
    )


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return allowable stress for the material at the selected temperature band.

    Database:
        stress = ksi

    Return:
        ProcessPI Pressure in psi.

    Temperature selection is conservative.

    Example
    -------
    533°F -> 600°F table value
    """

    # ------------------------------------------------------------------------
    # Explicit numerical allowable stress
    # ------------------------------------------------------------------------

    if isinstance(material, (int, float)):

        stress_ksi = float(material)

        if stress_ksi <= 0:
            raise ValueError(
                "Allowable stress must be greater than zero."
            )

        return Pressure(
            stress_ksi * 1000,
            "psi",
        )

    # ------------------------------------------------------------------------
    # Normalize material
    # ------------------------------------------------------------------------

    material_key = normalize_material(material)

    # ------------------------------------------------------------------------
    # Select temperature band
    # ------------------------------------------------------------------------

    temperature_f = _temperature_to_f(
        temperature
    )

    temperature_band_f = _get_temperature_band_f(
        temperature
    )

    # ------------------------------------------------------------------------
    # Retrieve table
    # ------------------------------------------------------------------------

    stress_table = asme_material_stress_data[
        material_key
    ]

    # ------------------------------------------------------------------------
    # Ensure selected band exists
    # ------------------------------------------------------------------------

    if temperature_band_f not in stress_table:

        raise ValueError(
            "No allowable stress temperature band is "
            "available for material "
            f"'{material_key}' at "
            f"{temperature_band_f}°F."
        )

    stress_ksi = float(
        stress_table[
            temperature_band_f
        ]
    )

    # ------------------------------------------------------------------------
    # Zero means unavailable
    # ------------------------------------------------------------------------

    if stress_ksi <= 0:

        raise ValueError(
            "No allowable stress is available for material "
            f"'{material_key}' at "
            f"{temperature_band_f}°F."
        )

    # ------------------------------------------------------------------------
    # ksi -> psi
    # ------------------------------------------------------------------------

    return Pressure(
        stress_ksi * 1000,
        "psi",
    )


# ============================================================================
# RESULTS
# ============================================================================

@dataclass
class PressureVesselResults:
    """
    Structured pressure-vessel result container.
    """

    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()

    @property
    def warnings(self) -> List[str]:
        return self.data.get(
            "warnings",
            [],
        )


# ============================================================================
# PRESSURE VESSEL
# ============================================================================

class PressureVessel(CalculationBase):
    """
    Preliminary ASME VIII-1 pressure vessel.

    Plain numeric inputs use SI units:

        diameter            -> m
        length              -> m
        pressure             -> Pa
        corrosion allowance  -> m

    ProcessPI unit objects are accepted directly.
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

    # ------------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------------

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        # CalculationBase.validate_inputs() is called here.
        super().__init__(**kwargs)

        self.nozzles: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self.manholes: Dict[
            str,
            Dict[str, Any],
        ] = {}

    # ------------------------------------------------------------------------
    # INPUT VALIDATION
    # ------------------------------------------------------------------------

    def validate_inputs(self) -> None:

        inputs = self.inputs

        # Vessel type
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
                "vessel_type must be one of "
                f"{sorted(self._TYPES)}"
            )

        # Pressure
        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        if pressure is None:

            raise ValueError(
                "design_pressure must be specified."
            )

        if _value(
            pressure,
            "design_pressure",
            "Pa",
        ) <= 0:

            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # Diameter
        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None:

            raise ValueError(
                "diameter must be specified."
            )

        if _value(
            diameter,
            "diameter",
            "m",
        ) <= 0:

            raise ValueError(
                "diameter must be greater than zero."
            )

        # Length
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

            if _value(
                length,
                "length",
                "m",
            ) <= 0:

                raise ValueError(
                    "length must be greater than zero "
                    "for cylindrical vessels."
                )

        # Joint efficiency
        joint_efficiency = float(
            inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        if not 0 < joint_efficiency <= 1:

            raise ValueError(
                "joint_efficiency must be greater than "
                "zero and no more than one."
            )

        # Corrosion allowance
        corrosion_allowance = _value(
            inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

        if corrosion_allowance < 0:

            raise ValueError(
                "corrosion_allowance must be non-negative."
            )

        # Head type
        head_type = str(
            inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).strip().lower()

        allowed_head_types = {
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
            "hemispherical",
            "hemisphere",
            "flat",
            "flat_head",
            "torispherical",
            "conical",
        }

        if head_type not in allowed_head_types:

            raise ValueError(
                f"Unsupported head_type '{head_type}'. "
                "Supported types: "
                "2:1_ellipsoidal, hemispherical, "
                "flat, torispherical, conical."
            )

        # Material + temperature
        material = inputs.get(
            "material",
            "SA516-70",
        )

        design_temperature = inputs.get(
            "design_temperature",
            Temperature(
                20,
                "C",
            ),
        )

        # This validates the material, temperature band and
        # zero-stress protection.
        get_allowable_stress(
            material,
            design_temperature,
        )

    # ------------------------------------------------------------------------
    # VESSEL TYPE
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
    # MATERIAL
    # ------------------------------------------------------------------------

    @property
    def material(self) -> str:

        return normalize_material(
            self.inputs.get(
                "material",
                "SA516-70",
            )
        )

    # ------------------------------------------------------------------------
    # DESIGN TEMPERATURE
    # ------------------------------------------------------------------------

    @property
    def design_temperature(self) -> Any:

        return self.inputs.get(
            "design_temperature",
            Temperature(
                20,
                "C",
            ),
        )

    # ------------------------------------------------------------------------
    # ALLOWABLE STRESS
    # ------------------------------------------------------------------------

    def allowable_stress(self) -> Pressure:

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # ------------------------------------------------------------------------
    # NOZZLES
    # ------------------------------------------------------------------------

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:

        if not name:

            raise ValueError(
                "Nozzle name must not be empty."
            )

        diameter_m = _value(
            diameter,
            "nozzle diameter",
            "m",
        )

        if diameter_m <= 0:

            raise ValueError(
                "Nozzle diameter must be greater than zero."
            )

        self.nozzles[str(name)] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # ------------------------------------------------------------------------
    # MANHOLES
    # ------------------------------------------------------------------------

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:

        if not name:

            raise ValueError(
                "Manhole name must not be empty."
            )

        diameter_m = _value(
            diameter,
            "manhole diameter",
            "m",
        )

        if diameter_m <= 0:

            raise ValueError(
                "Manhole diameter must be greater than zero."
            )

        self.manholes[str(name)] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # ------------------------------------------------------------------------
    # SHELL THICKNESS
    # ------------------------------------------------------------------------

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical-shell internal-pressure thickness.

        ASME VIII-1 UG-27(c)(1) form:

            t = PR / (SE - 0.6P)

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

        radius = diameter / 2.0

        allowable_stress_pa = _value(
            self.allowable_stress().to("Pa"),
            "allowable stress",
            "Pa",
        )

        joint_efficiency = float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

        denominator = (
            allowable_stress_pa
            * joint_efficiency
            - 0.6 * pressure
        )

        if denominator <= 0:

            raise ValueError(
                "Shell thickness equation has a "
                "non-positive denominator. Check "
                "pressure, allowable stress and "
                "joint efficiency."
            )

        pressure_thickness = (
            pressure
            * radius
            / denominator
        )

        return Length(
            pressure_thickness
            + corrosion_allowance,
            "m",
        )

    # ------------------------------------------------------------------------
    # HEAD THICKNESS
    # ------------------------------------------------------------------------

    def head_thickness(self) -> Length:
        """
        Preliminary pressure thickness for vessel heads.

        The supplied ProcessPI preliminary factors are retained.

        Factors:

            flat            = 0.500
            ellipsoidal     = 0.250
            torispherical   = 0.885
            hemispherical   = 0.125
            conical         = 0.350

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

        allowable_stress_pa = _value(
            self.allowable_stress().to("Pa"),
            "allowable stress",
            "Pa",
        )

        joint_efficiency = float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

        head = str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).strip().lower()

        head = (
            head
            .replace("2:1_", "")
            .replace("2:1 ", "")
        )

        if head == "elliptical":
            head = "ellipsoidal"

        if head == "hemisphere":
            head = "hemispherical"

        if head == "flat_head":
            head = "flat"

        if head not in self._HEADS:

            raise ValueError(
                "head_type must be one of "
                f"{sorted(self._HEADS)}"
            )

        factors = {
            "flat": 0.50,
            "ellipsoidal": 0.25,
            "torispherical": 0.885,
            "hemispherical": 0.125,
            "conical": 0.35,
        }

        denominator = (
            allowable_stress_pa
            * joint_efficiency
            - 0.1 * pressure
        )

        if denominator <= 0:

            raise ValueError(
                "Head thickness equation has a "
                "non-positive denominator. Check "
                "pressure, allowable stress and "
                "joint efficiency."
            )

        pressure_thickness = (
            factors[head]
            * pressure
            * diameter
            / denominator
        )

        return Length(
            pressure_thickness
            + corrosion_allowance,
            "m",
        )

    # ------------------------------------------------------------------------
    # HEAD VOLUME
    # ------------------------------------------------------------------------

    def _head_volume(
        self,
        radius: float,
    ) -> float:
        """
        Approximate total volume contribution of both heads.

        For the preliminary geometry model:

            flat            -> 0
            ellipsoidal     -> 2/3 πr³
            torispherical   -> 1/2 πr³
            hemispherical   -> 4/3 πr³
            conical         -> 1/3 πr³
        """

        head = str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).strip().lower()

        head = (
            head
            .replace("2:1_", "")
            .replace("2:1 ", "")
        )

        if head == "elliptical":
            head = "ellipsoidal"

        if head == "hemisphere":
            head = "hemispherical"

        if head == "flat_head":
            head = "flat"

        factors = {
            "flat": 0.0,
            "ellipsoidal": 2.0 / 3.0,
            "torispherical": 0.5,
            "hemispherical": 4.0 / 3.0,
            "conical": 1.0 / 3.0,
        }

        if head not in factors:

            raise ValueError(
                f"Unsupported head type '{head}'."
            )

        return (
            factors[head]
            * pi
            * radius**3
        )

    # ------------------------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------------------------

    def volume(
        self,
        liquid_level: Optional[Any] = None,
    ) -> Volume:
        """
        Calculate vessel internal volume.

        For horizontal/vertical cylindrical vessels:

            V = πr²L + head volume

        For spherical vessels:

            V = 4/3 πr³

        If liquid_level is supplied, a preliminary cylindrical segment
        fraction is applied.
        """

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
                4.0
                * pi
                * radius**3
                / 3.0
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
                pi
                * radius**2
                * length
                + self._head_volume(radius)
            )

        if liquid_level is None:

            return Volume(
                full_volume,
                "m3",
            )

        level = _value(
            liquid_level,
            "liquid_level",
            "m",
        )

        if not 0 <= level <= diameter:

            raise ValueError(
                "liquid_level must be between "
                "zero and vessel diameter."
            )

        segment_volume = (
            radius**2
            * acos(
                (radius - level)
                / radius
            )
            -
            (radius - level)
            * sqrt(
                max(
                    0.0,
                    2.0 * radius * level
                    - level**2,
                )
            )
        )

        fraction = (
            segment_volume
            / (pi * radius**2)
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
        """
        Select the next available standard thickness.
        """

        required_mm = _value(
            required,
            "required thickness",
            "mm",
        )

        for thickness in self.STANDARD_THICKNESSES_MM:

            if thickness >= required_mm:

                return Length(
                    thickness,
                    "mm",
                )

        # If above the standard list, return the exact calculated
        # requirement rather than silently undersizing.
        return Length(
            required_mm,
            "mm",
        )

    # ------------------------------------------------------------------------
    # EXTERNAL AREA
    # ------------------------------------------------------------------------

    def _external_area(
        self,
        diameter_m: float,
        length_m: float,
    ) -> float:
        """
        Preliminary external surface area.

        Cylindrical shell:
            πDL

        Two projected circular head areas:
            2π(D/2)²

        This is an estimation for preliminary weight calculations.
        """

        if self.vessel_type == "spherical":

            return (
                4.0
                * pi
                * (diameter_m / 2.0) ** 2
            )

        return (
            pi
            * diameter_m
            * length_m
            +
            2.0
            * pi
            * (diameter_m / 2.0) ** 2
        )

    # ------------------------------------------------------------------------
    # DESIGN
    # ------------------------------------------------------------------------

    def design(self) -> Dict[str, Any]:
        """
        Perform complete preliminary pressure-vessel design.

        Returns an expanded ProcessPI result dictionary.
        """

        # --------------------------------------------------------------------
        # Geometry
        # --------------------------------------------------------------------

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

        # --------------------------------------------------------------------
        # Design conditions
        # --------------------------------------------------------------------

        design_pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        design_pressure_obj = Pressure(
            design_pressure,
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

        design_temperature = (
            self.design_temperature
        )

        design_temperature_f = (
            _temperature_to_f(
                design_temperature
            )
        )

        design_temperature_f_obj = (
            Temperature(
                design_temperature_f,
                "F",
            )
        )

        # --------------------------------------------------------------------
        # Temperature band
        # --------------------------------------------------------------------

        temperature_band = (
            set_temperature_range(
                design_temperature
            )
        )

        temperature_band_f = (
            _get_temperature_band_f(
                design_temperature
            )
        )

        # --------------------------------------------------------------------
        # Material / allowable stress
        # --------------------------------------------------------------------

        material = self.material

        allowable_stress = (
            self.allowable_stress()
        )

        allowable_stress_psi = _value(
            allowable_stress,
            "allowable stress",
            "psi",
        )

        allowable_stress_ksi = (
            allowable_stress_psi / 1000.0
        )

        # --------------------------------------------------------------------
        # Joint efficiency / corrosion allowance
        # --------------------------------------------------------------------

        joint_efficiency = float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

        corrosion_allowance_obj = (
            Length(
                corrosion_allowance,
                "m",
            )
        )

        # --------------------------------------------------------------------
        # Thickness
        # --------------------------------------------------------------------

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

        selected = (
            self.select_standard_thickness(
                Length(
                    governing_required_mm,
                    "mm",
                )
            )
        )

        selected_thickness_mm = _value(
            selected,
            "selected thickness",
            "mm",
        )

        # --------------------------------------------------------------------
        # Volume
        # --------------------------------------------------------------------

        internal_volume = (
            self.volume()
        )

        internal_volume_m3 = _value(
            internal_volume,
            "internal volume",
            "m3",
        )

        specified_volume = (
            self.inputs.get("volume")
        )

        volume_check = None
        volume_margin_m3 = None
        volume_margin_percent = None

        specified_volume_obj = None

        if specified_volume is not None:

            specified_volume_m3 = _value(
                specified_volume,
                "volume",
                "m3",
            )

            specified_volume_obj = (
                Volume(
                    specified_volume_m3,
                    "m3",
                )
            )

            volume_margin_m3 = (
                internal_volume_m3
                - specified_volume_m3
            )

            if specified_volume_m3 > 0:

                volume_margin_percent = (
                    volume_margin_m3
                    / specified_volume_m3
                    * 100.0
                )

            volume_check = (
                internal_volume_m3
                >= specified_volume_m3
            )

        # --------------------------------------------------------------------
        # External area
        # --------------------------------------------------------------------

        external_area = (
            self._external_area(
                diameter,
                length,
            )
        )

        # --------------------------------------------------------------------
        # Material density
        # --------------------------------------------------------------------

        if "material_density" in self.inputs:

            density = float(
                self.inputs[
                    "material_density"
                ]
            )

        else:

            density = MATERIAL_DENSITIES.get(
                material,
                7850.0,
            )

        # --------------------------------------------------------------------
        # Weight
        # --------------------------------------------------------------------

        selected_thickness_m = (
            selected_thickness_mm / 1000.0
        )

        estimated_weight_kg = (
            external_area
            * selected_thickness_m
            * density
        )

        # --------------------------------------------------------------------
        # Hydrotest
        # --------------------------------------------------------------------

        hydrotest_pressure = Pressure(
            1.3 * design_pressure,
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

        # --------------------------------------------------------------------
        # Warnings
        # --------------------------------------------------------------------

        warnings = [

            (
                "Preliminary ASME Section VIII "
                "Division 1 internal-pressure "
                "sizing only."
            ),

            (
                "Allowable stresses are taken from "
                "the supplied temperature-specific "
                "preliminary material database."
            ),

            (
                "Verify all material allowable stresses "
                "against the applicable ASME Section II, "
                "Part D tables before code-stamped "
                "design or fabrication."
            ),

            (
                "External pressure/vacuum, complete "
                "nozzle reinforcement, supports, wind, "
                "seismic, fatigue, MDMT, PWHT, and "
                "flanges are not evaluated."
            ),
        ]

        if self.nozzles or self.manholes:

            warnings.append(
                "Nozzle and manhole reinforcement "
                "calculations are not included."
            )

        if (
            specified_volume is not None
            and not volume_check
        ):

            warnings.append(
                "Calculated internal vessel volume "
                "is less than the specified design "
                "volume."
            )

        # --------------------------------------------------------------------
        # Design basis
        # --------------------------------------------------------------------

        design_basis = (
            "ASME VIII-1 preliminary: "
            "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
        )

        # --------------------------------------------------------------------
        # Result dictionary
        # --------------------------------------------------------------------

        result = {

            # Identification
            "vessel_type":
                self.vessel_type,

            "head_type":
                self.inputs.get(
                    "head_type",
                    "ellipsoidal",
                ),

            "material":
                material,

            # Design conditions
            "design_pressure":
                design_pressure_obj,

            "design_pressure_bar":
                design_pressure_bar,

            "design_pressure_psi":
                design_pressure_psi,

            "design_temperature":
                design_temperature,

            "design_temperature_F":
                design_temperature_f_obj,

            # Temperature band
            "allowable_stress_temperature_band":
                temperature_band,

            "allowable_stress_temperature_band_F":
                temperature_band_f,

            # Stress
            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            "allowable_stress_psi":
                allowable_stress_psi,

            # Dimensions
            "diameter":
                Diameter(
                    diameter,
                    "m",
                ),

            "length":
                (
                    Length(
                        length,
                        "m",
                    )
                    if self.vessel_type != "spherical"
                    else Length(
                        0.0,
                        "m",
                    )
                ),

            "joint_efficiency":
                joint_efficiency,

            "corrosion_allowance":
                corrosion_allowance_obj,

            # Thickness
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

            # Volume
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
                    if volume_margin_m3 is not None
                    else None
                ),

            "volume_margin_percent":
                volume_margin_percent,

            # Area / weight
            "external_area":
                Area(
                    external_area,
                    "m2",
                ),

            "material_density_kg_m3":
                density,

            "estimated_weight_kg":
                estimated_weight_kg,

            # Hydrotest
            "hydrotest_pressure":
                hydrotest_pressure,

            "hydrotest_pressure_bar":
                hydrotest_pressure_bar,

            "hydrotest_pressure_psi":
                hydrotest_pressure_psi,

            # Attachments
            "nozzles":
                self.nozzles.copy(),

            "manholes":
                self.manholes.copy(),

            # Status
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
        Required concrete implementation of CalculationBase.calculate().

        This method fixes the previous:

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
    with flat heads.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        super().__init__(
            vessel_type="horizontal",
            head_type="flat",
            **kwargs,
        )


class CylindricalHorizontalDishEnd(
    PressureVessel
):
    """
    Backward-compatible horizontal cylindrical vessel
    with ellipsoidal/dished heads.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        super().__init__(
            vessel_type="horizontal",
            head_type="ellipsoidal",
            **kwargs,
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
    "MATERIAL_DENSITIES",
    "ASME_TEMPERATURE_BANDS",
    "ASME_STRESS_TEMPERATURES_F",
    "MIN_SUPPORTED_TEMPERATURE_F",
    "MAX_SUPPORTED_TEMPERATURE_F",
    "normalize_material",
    "get_allowable_stress",
    "set_temperature_range",
]
