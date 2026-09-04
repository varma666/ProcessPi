"""
ProcessPI Pressure Vessel Module
================================

Preliminary ASME Section VIII Division 1 pressure-vessel sizing.

Scope
-----
This module provides preliminary internal-pressure sizing for pressure
vessels. It is NOT a replacement for a complete ASME code calculation.

Implemented:
    - Complete supplied preliminary allowable-stress database
    - Temperature-specific allowable stress selection
    - Conservative temperature-band selection
    - Material aliases
    - Material density lookup
    - Cylindrical shell sizing
    - 2:1 ellipsoidal head sizing
    - Hemispherical head sizing
    - Torispherical head sizing
    - Flat-head preliminary sizing
    - Conical-head preliminary sizing
    - Horizontal / vertical / spherical vessels
    - Volume calculation
    - Volume requirement check
    - Nozzle storage
    - Manhole storage
    - Hydrotest pressure
    - Standard thickness selection
    - Expanded result dictionary
    - CalculationBase compatibility
    - Backward-compatible PressureVessels alias

Important
---------
The material stresses below are the supplied preliminary database. They must
be verified against the applicable ASME Section II, Part D tables before
code-stamped design, fabrication, or certification.
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
# ASME PRELIMINARY ALLOWABLE-STRESS DATABASE
# ============================================================================
#
# Stress values are in ksi.
#
# Temperature keys are Fahrenheit.
#
# These are the values supplied for the ProcessPI preliminary database.
# ============================================================================

asme_material_stress_data: Dict[str, Dict[int, float]] = {

    # ------------------------------------------------------------------------
    # CARBON / LOW-ALLOY STEELS
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

    # ------------------------------------------------------------------------
    # SPECIAL ALLOYS
    # ------------------------------------------------------------------------

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
# MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES: Dict[str, str] = {

    # Carbon / low alloy steels
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "carbonsteel": "SA516-70",
    "cs": "SA516-70",

    "sa515-55": "SA515-55",
    "sa515 55": "SA515-55",
    "sa515-70": "SA515-70",
    "sa515 70": "SA515-70",

    "sa516": "SA516-70",
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
    "sa202 b": "SA202-B",
    "sa202-b": "SA202-B",

    "sa387-d": "SA387-D",
    "sa387 d": "SA387-D",

    # Stainless steels
    "304": "SA240-304",
    "304 stainless": "SA240-304",
    "ss304": "SA240-304",
    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",
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
    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
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
    "c22 alloy": "C-22 alloy",
    "c-22 alloy": "C-22 alloy",

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

    "zinccronium 702": "Zinccronium 702",
    "zirconium 702": "Zinccronium 702",
    "zr702": "Zinccronium 702",
}


# ============================================================================
# MATERIAL DENSITIES
# ============================================================================
#
# kg/m3
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
# TEMPERATURE DATABASE LIMITS
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

ASME_TEMPERATURE_BANDS = ASME_STRESS_TEMPERATURES_F

MIN_SUPPORTED_TEMPERATURE_F = -20.0
MAX_SUPPORTED_TEMPERATURE_F = 800.0

TEMPERATURE_TOLERANCE_F = 1.0e-6


# ============================================================================
# GENERAL UNIT HELPERS
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from a ProcessPI unit or plain numeric value.

    For most ProcessPI units, the normal ``to()`` mechanism is used.

    Temperature is intentionally NOT handled through this generic helper.
    Temperature conversion has its own explicit implementation below because
    the pressure-vessel material database requires reliable C/F conversion.
    """

    if value is None:
        raise ValueError(f"{name} must be provided.")

    if hasattr(value, "to") and unit:
        try:
            converted = value.to(unit)

            # ProcessPI units expose value.
            if hasattr(converted, "value"):
                return float(converted.value)

            if hasattr(converted, "original_value"):
                return float(converted.original_value)

        except Exception:
            # Fall through to direct extraction.
            pass

    if hasattr(value, "original_value"):
        try:
            return float(value.original_value)
        except (TypeError, ValueError):
            pass

    if hasattr(value, "value"):
        try:
            return float(value.value)
        except (TypeError, ValueError):
            pass

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value."
        ) from exc


def _length_m(value: Any, name: str = "length") -> float:
    return _value(value, name, "m")


def _diameter_m(value: Any, name: str = "diameter") -> float:
    return _value(value, name, "m")


def _pressure_pa(value: Any, name: str = "pressure") -> float:
    return _value(value, name, "Pa")


def _pressure_bar(value: Any, name: str = "pressure") -> float:
    return _value(value, name, "bar")


def _pressure_psi(value: Any, name: str = "pressure") -> float:
    return _value(value, name, "psi")


# ============================================================================
# ROBUST TEMPERATURE CONVERSION
# ============================================================================

def _temperature_unit_name(temperature: Any) -> Optional[str]:
    """
    Attempt to identify the original unit of a Temperature object.

    Different ProcessPI versions may expose the unit under different
    attribute names. This helper intentionally checks several possibilities.
    """

    for attr in (
        "unit",
        "units",
        "original_unit",
        "_unit",
        "_units",
    ):
        if hasattr(temperature, attr):
            unit = getattr(temperature, attr)

            if unit is not None:
                text = str(unit).strip().upper()

                if text in {"C", "°C", "CELSIUS"}:
                    return "C"

                if text in {"F", "°F", "FAHRENHEIT"}:
                    return "F"

                if text in {"K", "KELVIN"}:
                    return "K"

    # Some implementations expose a textual representation.
    try:
        text = str(temperature).upper()

        if "°C" in text or text.endswith(" C"):
            return "C"

        if "°F" in text or text.endswith(" F"):
            return "F"

        if text.endswith(" K"):
            return "K"

    except Exception:
        pass

    return None


def _temperature_raw_value(temperature: Any) -> float:
    """
    Obtain the original numerical temperature magnitude.
    """

    for attr in (
        "original_value",
        "value",
    ):
        if hasattr(temperature, attr):

            candidate = getattr(temperature, attr)

            try:
                return float(candidate)
            except (TypeError, ValueError):
                pass

    try:
        return float(temperature)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            "Temperature must be a ProcessPI Temperature object "
            "or a numeric value."
        ) from exc


def _temperature_to_f(temperature: Any) -> float:
    """
    Convert temperature to Fahrenheit.

    IMPORTANT:
    This function intentionally performs the C/F conversion explicitly
    instead of trusting Temperature.to("F"), because the pressure-vessel
    stress lookup must not be affected by implementation differences in the
    generic ProcessPI unit conversion layer.

    ProcessPI Temperature:
        Temperature(150, "C") -> 302°F
        Temperature(302, "F") -> 302°F
    """

    # Plain numbers are interpreted as Fahrenheit.
    if not isinstance(temperature, Temperature):
        return round(float(temperature), 6)

    raw = _temperature_raw_value(temperature)
    unit = _temperature_unit_name(temperature)

    if unit == "C":
        fahrenheit = raw * 9.0 / 5.0 + 32.0

    elif unit == "F":
        fahrenheit = raw

    elif unit == "K":
        fahrenheit = (raw - 273.15) * 9.0 / 5.0 + 32.0

    else:
        # Last-resort attempt using the ProcessPI conversion.
        try:
            converted = temperature.to("F")

            if hasattr(converted, "value"):
                fahrenheit = float(converted.value)
            elif hasattr(converted, "original_value"):
                fahrenheit = float(converted.original_value)
            else:
                fahrenheit = float(converted)

        except Exception as exc:
            raise ValueError(
                "Unable to determine the temperature unit. "
                "Use Temperature(value, 'C'), Temperature(value, 'F'), "
                "or Temperature(value, 'K')."
            ) from exc

    return round(fahrenheit, 6)


def _temperature_to_c(temperature: Any) -> float:
    """
    Convert temperature to Celsius using the same robust logic.
    """

    fahrenheit = _temperature_to_f(temperature)

    return round(
        (fahrenheit - 32.0) * 5.0 / 9.0,
        6,
    )


# ============================================================================
# MATERIAL NORMALIZATION
# ============================================================================

def normalize_material(material: Any) -> str:
    """
    Resolve a material name or alias to the canonical database key.
    """

    if material is None:
        raise ValueError("Material must be specified.")

    text = str(material).strip()

    if not text:
        raise ValueError("Material must not be empty.")

    # Exact match.
    if text in asme_material_stress_data:
        return text

    lowered = text.lower()

    # Case-insensitive canonical match.
    for key in asme_material_stress_data:

        if key.lower() == lowered:
            return key

    # Alias.
    if lowered in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[lowered]

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: "
        f"{', '.join(asme_material_stress_data.keys())}"
    )


# Backward-compatible internal name.
_normalize_material_key = normalize_material


# ============================================================================
# TEMPERATURE BAND SELECTION
# ============================================================================

def set_temperature_range(temperature: Any) -> Temperature:
    """
    Select the conservative allowable-stress temperature band.

    Examples
    --------
    25°C  -> 77°F  -> 100°F
    50°C  -> 122°F -> 200°F
    150°C -> 302°F -> 400°F
    175°C -> 347°F -> 400°F
    275°C -> 527°F -> 600°F
    375°C -> 707°F -> 800°F
    425°C -> 797°F -> 800°F

    Temperatures above 800°F are rejected.

    Temperatures below -20°F are rejected.
    """

    temperature_f = _temperature_to_f(temperature)

    if (
        temperature_f
        < MIN_SUPPORTED_TEMPERATURE_F - TEMPERATURE_TOLERANCE_F
    ):
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


def _get_temperature_band_f(temperature: Any) -> int:
    """
    Return the selected temperature band as an integer Fahrenheit value.
    """

    band = set_temperature_range(temperature)

    # We know this object was created by this module as Temperature(band, F).
    return int(round(_temperature_to_f(band)))


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return allowable stress as a ProcessPI Pressure object in psi.

    Stress database values are in ksi.

    A numerical material value is interpreted as an explicit allowable
    stress in ksi.

    Temperature selection is conservative:
        between table temperatures -> next higher band.
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
            stress_ksi * 1000.0,
            "psi",
        )

    # ------------------------------------------------------------------------
    # Material
    # ------------------------------------------------------------------------

    material_key = normalize_material(material)

    # ------------------------------------------------------------------------
    # Temperature
    # ------------------------------------------------------------------------

    temperature_f = _temperature_to_f(temperature)

    # Explicit upper limit.
    if temperature_f > (
        MAX_SUPPORTED_TEMPERATURE_F
        + TEMPERATURE_TOLERANCE_F
    ):
        raise ValueError(
            "Design temperature exceeds the available "
            "allowable-stress database. "
            f"Maximum supported temperature is "
            f"{MAX_SUPPORTED_TEMPERATURE_F:g}°F."
        )

    temperature_band = _get_temperature_band_f(
        temperature
    )

    stress_table = asme_material_stress_data[
        material_key
    ]

    if temperature_band not in stress_table:

        raise ValueError(
            "No allowable stress temperature band is available "
            f"for material '{material_key}' at "
            f"{temperature_band}°F."
        )

    stress_ksi = float(
        stress_table[temperature_band]
    )

    # Zero means unavailable in supplied database.
    if stress_ksi <= 0.0:

        raise ValueError(
            "No allowable stress is available for material "
            f"'{material_key}' at {temperature_band}°F."
        )

    return Pressure(
        stress_ksi * 1000.0,
        "psi",
    )


# ============================================================================
# MATERIAL DENSITY
# ============================================================================

def get_material_density(material: Any) -> float:
    """
    Return approximate material density in kg/m3.
    """

    material_key = normalize_material(material)

    return MATERIAL_DENSITIES.get(
        material_key,
        7850.0,
    )


# ============================================================================
# RESULT CONTAINER
# ============================================================================

@dataclass
class PressureVesselResults:
    """
    Structured pressure-vessel calculation result.
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

    Supported vessel types
    ----------------------
    horizontal
    vertical
    spherical

    Supported heads
    ---------------
    flat
    ellipsoidal
    2:1_ellipsoidal
    torispherical
    hemispherical
    conical
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
        "2:1_ellipsoidal",
        "torispherical",
        "hemispherical",
        "conical",
    }

    _TYPES = {
        "horizontal",
        "vertical",
        "spherical",
    }

    def __init__(self, **kwargs: Any) -> None:

        # CalculationBase calls validate_inputs().
        super().__init__(**kwargs)

        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def validate_inputs(self) -> None:

        inputs = self.inputs

        vessel_type = str(
            inputs.get(
                "vessel_type",
                inputs.get(
                    "orientation",
                    "horizontal",
                ),
            )
        ).lower()

        if vessel_type not in self._TYPES:

            raise ValueError(
                "vessel_type must be one of "
                f"{sorted(self._TYPES)}"
            )

        # --------------------------------------------------------------------
        # Pressure
        # --------------------------------------------------------------------

        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        if pressure is None:

            raise ValueError(
                "design_pressure must be provided."
            )

        if _pressure_pa(
            pressure,
            "design_pressure",
        ) <= 0:

            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Diameter
        # --------------------------------------------------------------------

        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None:

            raise ValueError(
                "diameter must be provided."
            )

        if _diameter_m(
            diameter,
            "diameter",
        ) <= 0:

            raise ValueError(
                "diameter must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Length
        # --------------------------------------------------------------------

        if vessel_type != "spherical":

            length = inputs.get(
                "length",
                inputs.get(
                    "tangent_to_tangent_length"
                ),
            )

            if length is None:

                raise ValueError(
                    "length must be provided for "
                    "cylindrical vessels."
                )

            if _length_m(
                length,
                "length",
            ) <= 0:

                raise ValueError(
                    "length must be greater than zero "
                    "for cylindrical vessels."
                )

        # --------------------------------------------------------------------
        # Joint efficiency
        # --------------------------------------------------------------------

        try:
            joint_efficiency = float(
                inputs.get(
                    "joint_efficiency",
                    1.0,
                )
            )

        except (TypeError, ValueError) as exc:

            raise ValueError(
                "joint_efficiency must be numeric."
            ) from exc

        if not (
            0.0
            < joint_efficiency
            <= 1.0
        ):

            raise ValueError(
                "joint_efficiency must be greater than zero "
                "and no more than one."
            )

        # --------------------------------------------------------------------
        # Corrosion allowance
        # --------------------------------------------------------------------

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

        # --------------------------------------------------------------------
        # Material
        # --------------------------------------------------------------------

        material = inputs.get(
            "material",
            "SA516-70",
        )

        # --------------------------------------------------------------------
        # Temperature
        # --------------------------------------------------------------------

        design_temperature = inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

        if not isinstance(
            design_temperature,
            Temperature,
        ):

            # Accept numeric temperatures as Fahrenheit.
            try:
                design_temperature = Temperature(
                    float(design_temperature),
                    "F",
                )

            except Exception as exc:

                raise TypeError(
                    "design_temperature must be a ProcessPI "
                    "Temperature object or numeric Fahrenheit value."
                ) from exc

        # --------------------------------------------------------------------
        # Material database validation
        # --------------------------------------------------------------------

        get_allowable_stress(
            material,
            design_temperature,
        )

        # --------------------------------------------------------------------
        # Head validation
        # --------------------------------------------------------------------

        head_type = str(
            inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).lower()

        if head_type not in self._HEADS:

            raise ValueError(
                "head_type must be one of "
                f"{sorted(self._HEADS)}"
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
        ).lower()

    @property
    def head_type(self) -> str:

        return str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).lower()

    @property
    def material(self) -> str:

        return normalize_material(
            self.inputs.get(
                "material",
                "SA516-70",
            )
        )

    @property
    def design_temperature(self) -> Temperature:

        return self.inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

    # ========================================================================
    # ATTACHMENTS
    # ========================================================================

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Add a nozzle definition.

        Nozzle reinforcement is NOT calculated in this preliminary module.
        """

        if not name:
            raise ValueError(
                "Nozzle name must not be empty."
            )

        diameter_m = _diameter_m(
            diameter,
            "nozzle diameter",
        )

        if diameter_m <= 0:

            raise ValueError(
                "nozzle diameter must be greater than zero."
            )

        self.nozzles[name] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Add a manhole definition.

        Manhole reinforcement is NOT calculated in this preliminary module.
        """

        if not name:
            raise ValueError(
                "Manhole name must not be empty."
            )

        diameter_m = _diameter_m(
            diameter,
            "manhole diameter",
        )

        if diameter_m <= 0:

            raise ValueError(
                "manhole diameter must be greater than zero."
            )

        self.manholes[name] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # ========================================================================
    # BASIC INPUT ACCESS
    # ========================================================================

    def _pressure(self) -> float:

        return _pressure_pa(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
        )

    def _diameter(self) -> float:

        return _diameter_m(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
        )

    def _radius(self) -> float:

        return self._diameter() / 2.0

    def _length(self) -> float:

        if self.vessel_type == "spherical":
            return 0.0

        return _length_m(
            self.inputs.get(
                "length",
                self.inputs.get(
                    "tangent_to_tangent_length"
                ),
            ),
            "length",
        )

    def _joint_efficiency(self) -> float:

        return float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

    def _corrosion_allowance(self) -> float:

        return _value(
            self.inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

    def _allowable_stress_pa(self) -> float:

        stress = get_allowable_stress(
            self.material,
            self.design_temperature,
        )

        return _pressure_pa(
            stress,
            "allowable stress",
        )

    # ========================================================================
    # SHELL THICKNESS
    # ========================================================================

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical shell thickness.

        Based on the ASME VIII-1 UG-27(c)(1) internal-pressure form:

            t = P R / (S E - 0.6 P)

        Corrosion allowance is then added.
        """

        if self.vessel_type == "spherical":

            return self.head_thickness()

        p = self._pressure()
        r = self._radius()
        s = self._allowable_stress_pa()
        e = self._joint_efficiency()
        ca = self._corrosion_allowance()

        denominator = (
            s * e
            - 0.6 * p
        )

        if denominator <= 0:

            raise ValueError(
                "Pressure is too high for the available allowable "
                "stress and joint efficiency."
            )

        required = (
            p * r / denominator
        ) + ca

        return Length(
            required,
            "m",
        )

    # ========================================================================
    # HEAD THICKNESS
    # ========================================================================

    def head_thickness(self) -> Length:
        """
        Preliminary pressure thickness for the selected head.

        The head equations are preliminary sizing relationships and are not
        a substitute for complete ASME VIII-1 head design.
        """

        p = self._pressure()
        d = self._diameter()
        s = self._allowable_stress_pa()
        e = self._joint_efficiency()
        ca = self._corrosion_allowance()

        head = self.head_type

        # Normalize 2:1 notation.
        if head in {
            "2:1",
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "2:1-ellipsoidal",
        }:

            head = "ellipsoidal"

        # --------------------------------------------------------------------
        # 2:1 Ellipsoidal
        #
        # Preliminary form:
        #
        # t = P D / (2 S E - 0.2 P)
        # --------------------------------------------------------------------

        if head == "ellipsoidal":

            denominator = (
                2.0 * s * e
                - 0.2 * p
            )

            if denominator <= 0:

                raise ValueError(
                    "Pressure is too high for ellipsoidal-head sizing."
                )

            pressure_thickness = (
                p * d / denominator
            )

        # --------------------------------------------------------------------
        # Hemispherical
        # --------------------------------------------------------------------

        elif head == "hemispherical":

            denominator = (
                4.0 * s * e
                - 0.4 * p
            )

            if denominator <= 0:

                raise ValueError(
                    "Pressure is too high for hemispherical-head sizing."
                )

            pressure_thickness = (
                p * d / denominator
            )

        # --------------------------------------------------------------------
        # Torispherical
        #
        # Preliminary conservative multiplier.
        # --------------------------------------------------------------------

        elif head == "torispherical":

            denominator = (
                2.0 * s * e
                - 0.2 * p
            )

            if denominator <= 0:

                raise ValueError(
                    "Pressure is too high for torispherical-head sizing."
                )

            pressure_thickness = (
                0.885
                * p
                * d
                / denominator
            )

        # --------------------------------------------------------------------
        # Conical
        # --------------------------------------------------------------------

        elif head == "conical":

            denominator = (
                2.0 * s * e
                - 0.2 * p
            )

            if denominator <= 0:

                raise ValueError(
                    "Pressure is too high for conical-head sizing."
                )

            pressure_thickness = (
                p * d / denominator
            )

        # --------------------------------------------------------------------
        # Flat head
        #
        # Preliminary UG-34-style form.
        # --------------------------------------------------------------------

        elif head == "flat":

            c = float(
                self.inputs.get(
                    "flat_head_factor",
                    0.30,
                )
            )

            if s * e <= 0:

                raise ValueError(
                    "Invalid allowable stress or joint efficiency."
                )

            pressure_thickness = (
                c
                * d
                * sqrt(
                    p
                    / (s * e)
                )
            )

        else:

            raise ValueError(
                "Unsupported head type: "
                f"{self.head_type!r}"
            )

        required = (
            pressure_thickness
            + ca
        )

        return Length(
            required,
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
        Select the next available standard plate thickness.
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

        # If the requirement exceeds the predefined table, preserve the
        # calculated value rather than silently undersizing.
        return Length(
            required_mm,
            "mm",
        )

    # ========================================================================
    # VOLUME
    # ========================================================================

    def _head_volume_one(self) -> float:
        """
        Approximate volume of one head, m3.
        """

        r = self._radius()
        head = self.head_type

        if head in {
            "2:1",
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "2:1-ellipsoidal",
            "ellipsoidal",
        }:

            # One 2:1 ellipsoidal head.
            return (
                (2.0 / 3.0)
                * pi
                * r ** 3
            )

        if head == "hemispherical":

            return (
                (2.0 / 3.0)
                * pi
                * r ** 3
            )

        if head == "torispherical":

            return (
                0.5
                * pi
                * r ** 3
            )

        if head == "conical":

            return (
                (1.0 / 3.0)
                * pi
                * r ** 3
            )

        if head == "flat":

            return 0.0

        return (
            (2.0 / 3.0)
            * pi
            * r ** 3
        )

    def volume(
        self,
        liquid_level: Any = None,
    ) -> Volume:
        """
        Calculate approximate internal vessel volume.

        For cylindrical vessels:
            cylindrical volume + two head volumes

        For spherical vessels:
            sphere volume

        If liquid_level is supplied, a cylindrical liquid-volume estimate is
        returned for horizontal vessels.
        """

        d = self._diameter()
        r = d / 2.0

        # --------------------------------------------------------------------
        # Spherical vessel
        # --------------------------------------------------------------------

        if self.vessel_type == "spherical":

            full = (
                4.0
                / 3.0
                * pi
                * r ** 3
            )

            if liquid_level is None:

                return Volume(
                    full,
                    "m3",
                )

            level = _length_m(
                liquid_level,
                "liquid_level",
            )

            if not 0 <= level <= d:

                raise ValueError(
                    "liquid_level must be between zero "
                    "and vessel diameter."
                )

            # Spherical-cap volume.
            cap = (
                pi
                * level ** 2
                * (r - level / 3.0)
            )

            return Volume(
                cap,
                "m3",
            )

        # --------------------------------------------------------------------
        # Cylindrical vessel
        # --------------------------------------------------------------------

        length = self._length()

        cylindrical = (
            pi
            * r ** 2
            * length
        )

        head_volume = (
            2.0
            * self._head_volume_one()
        )

        full = (
            cylindrical
            + head_volume
        )

        # Full volume.
        if liquid_level is None:

            return Volume(
                full,
                "m3",
            )

        # --------------------------------------------------------------------
        # Horizontal liquid-level estimate
        # --------------------------------------------------------------------

        level = _length_m(
            liquid_level,
            "liquid_level",
        )

        if not 0 <= level <= d:

            raise ValueError(
                "liquid_level must be between zero "
                "and vessel diameter."
            )

        # Circular-segment fraction.
        theta_argument = (
            (r - level) / r
        )

        # Numerical protection.
        theta_argument = max(
            -1.0,
            min(
                1.0,
                theta_argument,
            ),
        )

        segment_area = (
            r ** 2
            * acos(theta_argument)
            - (
                r - level
            )
            * sqrt(
                max(
                    0.0,
                    2.0 * r * level
                    - level ** 2,
                )
            )
        )

        fraction = (
            segment_area
            / (pi * r ** 2)
        )

        liquid_volume = (
            cylindrical
            * fraction
        )

        return Volume(
            liquid_volume,
            "m3",
        )

    # ========================================================================
    # EXTERNAL AREA
    # ========================================================================

    def external_area(self) -> float:
        """
        Approximate external surface area in m2.

        Used only for preliminary weight estimation.
        """

        d = self._diameter()
        r = d / 2.0

        if self.vessel_type == "spherical":

            return (
                4.0
                * pi
                * r ** 2
            )

        length = self._length()

        shell_area = (
            pi
            * d
            * length
        )

        # Approximate both head areas using projected area.
        head_area = (
            2.0
            * pi
            * r ** 2
        )

        return (
            shell_area
            + head_area
        )

    # ========================================================================
    # ALLOWABLE STRESS INSTANCE METHOD
    # ========================================================================

    def allowable_stress(self) -> Pressure:
        """
        Return allowable stress for this vessel.
        """

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # ========================================================================
    # DESIGN
    # ========================================================================

    def design(self) -> Dict[str, Any]:
        """
        Execute the complete preliminary pressure-vessel design.
        """

        # --------------------------------------------------------------------
        # Revalidate
        # --------------------------------------------------------------------

        self.validate_inputs()

        # --------------------------------------------------------------------
        # Basic design quantities
        # --------------------------------------------------------------------

        pressure = self._pressure()

        pressure_obj = Pressure(
            pressure,
            "Pa",
        )

        pressure_bar = _pressure_bar(
            pressure_obj,
            "design pressure",
        )

        pressure_psi = _pressure_psi(
            pressure_obj,
            "design pressure",
        )

        # --------------------------------------------------------------------
        # Temperature
        # --------------------------------------------------------------------

        design_temperature_f = _temperature_to_f(
            self.design_temperature
        )

        design_temperature_c = _temperature_to_c(
            self.design_temperature
        )

        temperature_band = set_temperature_range(
            self.design_temperature
        )

        temperature_band_f = _temperature_to_f(
            temperature_band
        )

        # --------------------------------------------------------------------
        # Stress
        # --------------------------------------------------------------------

        allowable_stress = self.allowable_stress()

        allowable_stress_psi = _pressure_psi(
            allowable_stress,
            "allowable stress",
        )

        allowable_stress_ksi = (
            allowable_stress_psi
            / 1000.0
        )

        allowable_stress_mpa = (
            allowable_stress_psi
            * 0.006894757293168
        )

        # --------------------------------------------------------------------
        # Thickness
        # --------------------------------------------------------------------

        shell_required = (
            self.shell_thickness()
            if self.vessel_type != "spherical"
            else self.head_thickness()
        )

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

        # --------------------------------------------------------------------
        # Volume
        # --------------------------------------------------------------------

        internal_volume = self.volume()

        internal_volume_m3 = _value(
            internal_volume,
            "internal volume",
            "m3",
        )

        specified_volume_obj = self.inputs.get(
            "volume",
            None,
        )

        if specified_volume_obj is None:

            specified_volume = None
            volume_check = True
            volume_margin = None
            volume_margin_percent = None

        else:

            specified_volume = _value(
                specified_volume_obj,
                "volume",
                "m3",
            )

            volume_margin = (
                internal_volume_m3
                - specified_volume
            )

            volume_margin_percent = (
                volume_margin
                / specified_volume
                * 100.0
                if specified_volume > 0
                else None
            )

            volume_check = (
                internal_volume_m3
                >= specified_volume
            )

        # --------------------------------------------------------------------
        # Geometry
        # --------------------------------------------------------------------

        diameter_m = self._diameter()

        length_m = (
            self._length()
            if self.vessel_type != "spherical"
            else None
        )

        # --------------------------------------------------------------------
        # Area / weight
        # --------------------------------------------------------------------

        external_area_m2 = self.external_area()

        density = float(
            self.inputs.get(
                "material_density",
                get_material_density(
                    self.material
                ),
            )
        )

        selected_thickness_m = (
            selected_thickness_mm
            / 1000.0
        )

        estimated_weight_kg = (
            external_area_m2
            * selected_thickness_m
            * density
        )

        # --------------------------------------------------------------------
        # Hydrotest
        # --------------------------------------------------------------------
        #
        # Preliminary project convention retained from the previous module:
        #
        #     Ptest = 1.3 x Design Pressure
        #
        # This is NOT a complete UG-99 hydrotest verification.
        # --------------------------------------------------------------------

        hydrotest_pressure = Pressure(
            1.3 * pressure,
            "Pa",
        )

        hydrotest_pressure_bar = _pressure_bar(
            hydrotest_pressure,
            "hydrotest pressure",
        )

        hydrotest_pressure_psi = _pressure_psi(
            hydrotest_pressure,
            "hydrotest pressure",
        )

        # --------------------------------------------------------------------
        # Warnings
        # --------------------------------------------------------------------

        warnings = [

            "Preliminary ASME Section VIII Division 1 "
            "internal-pressure sizing only.",

            "Allowable stresses are taken from the supplied "
            "temperature-specific preliminary material database.",

            "Verify all material allowable stresses against the "
            "applicable ASME Section II, Part D tables before "
            "code-stamped design or fabrication.",

            "External pressure/vacuum, complete nozzle reinforcement, "
            "supports, wind, seismic, fatigue, MDMT, PWHT, and flanges "
            "are not evaluated.",

            "Head geometry and reinforcement details are treated "
            "as preliminary sizing relationships.",

        ]

        if self.nozzles or self.manholes:

            warnings.append(
                "Nozzle and manhole reinforcement calculations "
                "are not included."
            )

        if (
            specified_volume is not None
            and not volume_check
        ):

            warnings.append(
                "Specified vessel volume exceeds the calculated "
                "internal geometric volume."
            )

        # --------------------------------------------------------------------
        # Design basis
        # --------------------------------------------------------------------

        design_basis = (
            "ASME VIII-1 preliminary: "
            "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
        )

        # --------------------------------------------------------------------
        # Result
        # --------------------------------------------------------------------

        result = PressureVesselResults({

            # ---------------------------------------------------------------
            # Vessel
            # ---------------------------------------------------------------

            "vessel_type":
                self.vessel_type,

            "head_type":
                self.inputs.get(
                    "head_type",
                    "ellipsoidal",
                ),

            "material":
                self.material,

            # ---------------------------------------------------------------
            # Pressure
            # ---------------------------------------------------------------

            "design_pressure":
                pressure_obj,

            "design_pressure_bar":
                pressure_bar,

            "design_pressure_psi":
                pressure_psi,

            # ---------------------------------------------------------------
            # Temperature
            # ---------------------------------------------------------------

            "design_temperature":
                self.design_temperature,

            "design_temperature_C":
                design_temperature_c,

            "design_temperature_F":
                design_temperature_f,

            "allowable_stress_temperature_band":
                temperature_band_f,

            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            "allowable_stress_MPa":
                allowable_stress_mpa,

            # ---------------------------------------------------------------
            # Geometry
            # ---------------------------------------------------------------

            "diameter":
                Diameter(
                    diameter_m,
                    "m",
                ),

            "length":
                (
                    Length(
                        length_m,
                        "m",
                    )
                    if length_m is not None
                    else None
                ),

            "joint_efficiency":
                self._joint_efficiency(),

            "corrosion_allowance":
                Length(
                    self._corrosion_allowance(),
                    "m",
                ),

            # ---------------------------------------------------------------
            # Thickness
            # ---------------------------------------------------------------

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

            # ---------------------------------------------------------------
            # Volume
            # ---------------------------------------------------------------

            "specified_volume":
                specified_volume,

            "internal_volume":
                internal_volume,

            "volume_check":
                volume_check,

            "volume_margin":
                (
                    Volume(
                        volume_margin,
                        "m3",
                    )
                    if volume_margin is not None
                    else None
                ),

            "volume_margin_percent":
                volume_margin_percent,

            # ---------------------------------------------------------------
            # Area / Weight
            # ---------------------------------------------------------------

            "external_area":
                Area(
                    external_area_m2,
                    "m2",
                ),

            "material_density_kg_m3":
                density,

            "estimated_weight_kg":
                estimated_weight_kg,

            # ---------------------------------------------------------------
            # Hydrotest
            # ---------------------------------------------------------------

            "hydrotest_pressure":
                hydrotest_pressure,

            "hydrotest_pressure_bar":
                hydrotest_pressure_bar,

            "hydrotest_pressure_psi":
                hydrotest_pressure_psi,

            # ---------------------------------------------------------------
            # Attachments
            # ---------------------------------------------------------------

            "nozzles":
                self.nozzles.copy(),

            "manholes":
                self.manholes.copy(),

            # ---------------------------------------------------------------
            # Status
            # ---------------------------------------------------------------

            "warnings":
                warnings,

            "design_basis":
                design_basis,

        })

        return result.to_dict()

    # ========================================================================
    # CALCULATIONBASE COMPATIBILITY
    # ========================================================================

    def calculate(self) -> Dict[str, Any]:
        """
        Required concrete implementation of CalculationBase.calculate().
        """

        return self.design()


# ============================================================================
# BACKWARD-COMPATIBLE CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(PressureVessel):
    """
    Backward-compatible horizontal cylindrical vessel with flat heads.
    """

    def __init__(self, **kwargs: Any) -> None:

        super().__init__(
            vessel_type="horizontal",
            head_type="flat",
            **kwargs,
        )


class CylindricalHorizontalDishEnd(PressureVessel):
    """
    Backward-compatible horizontal cylindrical vessel with ellipsoidal heads.
    """

    def __init__(self, **kwargs: Any) -> None:

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

    "ASME_STRESS_TEMPERATURES_F",

    "ASME_TEMPERATURE_BANDS",

    "MIN_SUPPORTED_TEMPERATURE_F",

    "MAX_SUPPORTED_TEMPERATURE_F",

    "normalize_material",

    "get_allowable_stress",

    "get_material_density",

    "set_temperature_range",

]
