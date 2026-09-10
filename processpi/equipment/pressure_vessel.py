"""
ProcessPI Pressure Vessel Module
--------------------------------

Preliminary pressure-vessel sizing module.

The module supports:
- Supplied ASME-style preliminary allowable-stress data in ksi / °F.
- Supplied IS 2825:1969 reference-scan data originally expressed in
  kgf/mm² / °C, converted once to ksi / °F and stored in the same dictionary.
- Material-specific temperature grids.
- Conservative selection of the first available temperature point at or above
  the design temperature.
- Cylindrical shell sizing.
- Preliminary 2:1 ellipsoidal, hemispherical and flat-head sizing.
- Volume and volume-check calculations.
- Nozzle / manhole storage.
- Hydrotest pressure.
- Estimated external area and weight.
- CalculationBase compatibility.

IMPORTANT:
These data and equations are preliminary engineering aids. They are not a
replacement for the applicable ASME Section II, Part D / Section VIII or
other governing code requirements. The supplied historical IS 2825 values
must be independently verified against the governing edition and product
form before design/fabrication use.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, pi, sqrt
from typing import Any, Dict, List, Optional

from processpi.calculations.base import CalculationBase
from processpi.units import Area, Diameter, Length, Pressure, Temperature, Volume


# ============================================================================
# UNIT CONVERSION CONSTANTS
# ============================================================================

# 1 kgf/mm² = 9.80665 MPa; 1 ksi = 6.894757293 MPa.
# Therefore 1 kgf/mm² = 1.4223343307 ksi.
# This correction is important: the earlier project draft used 14.223...
# which is 10x too high and materially understates required thickness.
KGF_MM2_TO_KSI = 1.4223343307

# The IS 2825 values supplied in the project are printed in kgf/mm².
# Keep the explicit conversion here so the database is auditable.


# ============================================================================
# UNIFIED MATERIAL ALLOWABLE-STRESS DATABASE
# ============================================================================
#
# ALL entries are stored in:
#
#     temperature -> °F
#     allowable stress -> ksi
#
# This is intentionally one dictionary, as requested.
#
# For the original ProcessPI/ASME preliminary entries, the supplied values
# are already ksi / °F.
#
# For the IS 2825 entries, the source table is kgf/mm² / °C and the values
# are converted to ksi / °F.
#
# Zero stress values are retained exactly where they were supplied.
# A zero value is treated as "no allowable stress available".
# ============================================================================

asme_material_stress_data: Dict[str, Dict[int, float]] = {

    # ------------------------------------------------------------------------
    # ASME / ProcessPI preliminary data originally supplied
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
    # IS 2825:1969 TABLE A.1 / A.2 REFERENCE DATA SUPPLIED BY USER
    #
    # Source units: kgf/mm² at °C.
    # Stored units: ksi at °F.
    #
    # IMPORTANT: the conversion factor is 1.4223343307 ksi per kgf/mm².
    # ------------------------------------------------------------------------

    "IS 2002-1962 Grade I": {
        482: 9.5 * KGF_MM2_TO_KSI,
        572: 8.7 * KGF_MM2_TO_KSI,
        662: 7.8 * KGF_MM2_TO_KSI,
        707: 7.5 * KGF_MM2_TO_KSI,
        752: 7.2 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 2002-1962 Grade 2A": {
        482: 9.0 * KGF_MM2_TO_KSI,
        572: 9.0 * KGF_MM2_TO_KSI,
        662: 8.0 * KGF_MM2_TO_KSI,
        707: 7.7 * KGF_MM2_TO_KSI,
        752: 7.7 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 2002-1962 Grade 2B": {
        482: 12.1 * KGF_MM2_TO_KSI,
        572: 11.1 * KGF_MM2_TO_KSI,
        662: 10.0 * KGF_MM2_TO_KSI,
        707: 9.5 * KGF_MM2_TO_KSI,
        752: 8.3 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 2004-1962 Class 1": {
        482: 8.6 * KGF_MM2_TO_KSI,
        572: 7.9 * KGF_MM2_TO_KSI,
        662: 7.1 * KGF_MM2_TO_KSI,
        707: 6.8 * KGF_MM2_TO_KSI,
        752: 6.5 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 2004-1962 Class 2": {
        482: 10.2 * KGF_MM2_TO_KSI,
        572: 9.3 * KGF_MM2_TO_KSI,
        662: 8.5 * KGF_MM2_TO_KSI,
        707: 8.0 * KGF_MM2_TO_KSI,
        752: 7.7 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 2004-1962 Class 3": {
        482: 11.7 * KGF_MM2_TO_KSI,
        572: 10.7 * KGF_MM2_TO_KSI,
        662: 9.6 * KGF_MM2_TO_KSI,
        707: 9.1 * KGF_MM2_TO_KSI,
        752: 8.3 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 2004-1962 Class 4": {
        482: 14.7 * KGF_MM2_TO_KSI,
        572: 13.4 * KGF_MM2_TO_KSI,
        662: 12.2 * KGF_MM2_TO_KSI,
        707: 11.9 * KGF_MM2_TO_KSI,
        752: 11.5 * KGF_MM2_TO_KSI,
        797: 5.9 * KGF_MM2_TO_KSI,
        842: 4.3 * KGF_MM2_TO_KSI,
        887: 3.6 * KGF_MM2_TO_KSI,
    },

    "IS 1570-1961 04Cr19Ni9": {
        122: 16.00 * KGF_MM2_TO_KSI,
        212: 14.20 * KGF_MM2_TO_KSI,
        302: 12.40 * KGF_MM2_TO_KSI,
        392: 10.60 * KGF_MM2_TO_KSI,
        482: 9.97 * KGF_MM2_TO_KSI,
        572: 9.35 * KGF_MM2_TO_KSI,
        662: 8.70 * KGF_MM2_TO_KSI,
        752: 8.07 * KGF_MM2_TO_KSI,
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

    "IS 2002-1962 Grade I": 7850.0,
    "IS 2002-1962 Grade 2A": 7850.0,
    "IS 2002-1962 Grade 2B": 7850.0,
    "IS 2004-1962 Class 1": 7850.0,
    "IS 2004-1962 Class 2": 7850.0,
    "IS 2004-1962 Class 3": 7850.0,
    "IS 2004-1962 Class 4": 7850.0,
    "IS 1570-1961 04Cr19Ni9": 8000.0,
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

    # IS 2825 / historical material aliases
    "is 2002-1962 grade i": "IS 2002-1962 Grade I",
    "is2002 grade i": "IS 2002-1962 Grade I",
    "is 2002-1962 grade 2a": "IS 2002-1962 Grade 2A",
    "is2002 grade 2a": "IS 2002-1962 Grade 2A",
    "is 2002-1962 grade 2b": "IS 2002-1962 Grade 2B",
    "is2002 grade 2b": "IS 2002-1962 Grade 2B",

    "is 2004-1962 class 1": "IS 2004-1962 Class 1",
    "is 2004-1962 class 2": "IS 2004-1962 Class 2",
    "is 2004-1962 class 3": "IS 2004-1962 Class 3",
    "is 2004-1962 class 4": "IS 2004-1962 Class 4",

    "is 1570-1961 04cr19ni9": "IS 1570-1961 04Cr19Ni9",
    "is1570 04cr19ni9": "IS 1570-1961 04Cr19Ni9",
}


# ============================================================================
# DESIGN-STANDARD SELECTION
# ============================================================================

STANDARD_ALIASES: Dict[str, str] = {
    "asme": "ASME",
    "asme viii": "ASME",
    "asme viii-1": "ASME",
    "asme section viii": "ASME",
    "asme section viii division 1": "ASME",
    "is2825": "IS2825",
    "is 2825": "IS2825",
    "is 2825:1969": "IS2825",
}

SUPPORTED_STANDARDS = {
    "ASME": "ASME Section VIII Division 1",
    "IS2825": "IS 2825:1969",
}

# The unified stress dictionary above stores every temperature key in °F.
# IS 2825 source temperatures are converted from °C to °F once when the
# dictionary is built. The standard selector below determines which grid is
# applicable; it does not mix ASME and IS 2825 material families.
MATERIAL_STANDARD: Dict[str, str] = {
    key: ("IS2825" if key.startswith("IS ") else "ASME")
    for key in asme_material_stress_data
}


# ============================================================================
# TEMPERATURE CONSTANTS
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

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """Extract a numeric magnitude from a ProcessPI unit or plain number."""

    converted = value

    if hasattr(converted, "to") and unit:
        converted = converted.to(unit)

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


def _normalize_standard(std: Any = "ASME") -> str:
    """Normalize a pressure-vessel design standard name."""

    if std is None:
        std = "ASME"

    text = str(std).strip()
    if not text:
        raise ValueError(
            "Design standard must be specified as 'ASME' or 'IS2825'."
        )

    if text in SUPPORTED_STANDARDS:
        return text

    lowered = text.lower()
    if lowered in STANDARD_ALIASES:
        return STANDARD_ALIASES[lowered]

    raise ValueError(
        f"Unsupported pressure-vessel design standard {std!r}. "
        "Supported standards: ASME, IS2825."
    )


def normalize_standard(std: Any = "ASME") -> str:
    """Public design-standard normalization helper."""
    return _normalize_standard(std)


def _validate_standard_material(material_key: str, std: Any) -> str:
    """Validate that a material belongs to the selected design standard."""

    standard = _normalize_standard(std)
    material_standard = MATERIAL_STANDARD.get(material_key)

    if material_standard is None:
        raise ValueError(
            f"No design-standard mapping is available for material "
            f"'{material_key}'."
        )

    if material_standard != standard:
        expected = SUPPORTED_STANDARDS[material_standard]
        selected = SUPPORTED_STANDARDS[standard]
        raise ValueError(
            f"Material '{material_key}' belongs to {expected}, but std="
            f"'{standard}' selects {selected}. Select a material compatible "
            f"with the chosen design standard."
        )

    return standard


def _normalize_material_key(material: Any) -> str:
    """Resolve material names and aliases to the canonical dictionary key."""

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

    return round(
        _value(temperature, "temperature", "F"),
        6,
    )


def _material_temperature_bands(material_key: str) -> List[int]:
    return sorted(
        int(key)
        for key in asme_material_stress_data[material_key].keys()
    )


# ============================================================================
# TEMPERATURE-BAND SELECTION
# ============================================================================

def set_temperature_range(
    temperature: Any,
    material: Optional[Any] = None,
    std: Any = "ASME",
) -> Temperature:
    """
    Select the first applicable allowable-stress temperature point at or
    above the design temperature.

    ASME uses the supplied ProcessPI preliminary 100°F grid.
    IS2825 uses the actual material-specific temperature points represented
    in the unified dictionary. The selected standard is explicit when the
    class is used and may be supplied directly to this helper.
    """

    standard = _normalize_standard(std)
    temperature_f = _temperature_to_f(temperature)

    if material is None:
        if standard != "ASME":
            raise ValueError(
                "material must be provided when std='IS2825' is selected."
            )
        bands = list(ASME_STRESS_TEMPERATURES_F)
        minimum = MIN_SUPPORTED_TEMPERATURE_F
        maximum = MAX_SUPPORTED_TEMPERATURE_F
    else:
        material_key = _normalize_material_key(material)
        _validate_standard_material(material_key, standard)
        bands = _material_temperature_bands(material_key)
        if not bands:
            raise ValueError(
                f"No allowable-stress temperature data exists for material "
                f"'{material_key}'."
            )
        minimum = bands[0]
        maximum = bands[-1]

    if temperature_f < minimum - TEMPERATURE_TOLERANCE_F:
        raise ValueError(
            f"Design temperature is below the available allowable-stress "
            f"database. Minimum supported temperature is {minimum:g}°F."
        )

    for band in bands:
        if temperature_f <= band + TEMPERATURE_TOLERANCE_F:
            return Temperature(band, "F")

    raise ValueError(
        "Design temperature exceeds the available allowable-stress "
        f"database. Maximum supported temperature is {maximum:g}°F."
    )


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
    std: Any = "ASME",
) -> Pressure:
    """
    Return allowable stress as a ProcessPI Pressure in psi.

    ``std`` explicitly selects the design standard. Numeric material values
    remain supported as an explicit allowable stress in ksi for backward
    compatibility; standard validation is not applicable to that form.
    """

    if isinstance(material, (int, float)):
        stress_ksi = float(material)
        if stress_ksi <= 0:
            raise ValueError("Allowable stress must be greater than zero.")
        return Pressure(stress_ksi * 1000.0, "psi")

    standard = _normalize_standard(std)
    material_key = _normalize_material_key(material)
    _validate_standard_material(material_key, standard)

    temperature_band = set_temperature_range(
        temperature,
        material_key,
        standard,
    )

    temperature_f = int(round(_value(temperature_band, "temperature band", "F")))
    stress_table = asme_material_stress_data[material_key]

    if temperature_f not in stress_table:
        raise ValueError(
            f"No allowable stress temperature band is available for "
            f"material '{material_key}' at {temperature_f}°F."
        )

    stress_ksi = float(stress_table[temperature_f])

    if stress_ksi <= 0.0:
        raise ValueError(
            f"No allowable stress is available for material "
            f"'{material_key}' at {temperature_f}°F."
        )

    return Pressure(stress_ksi * 1000.0, "psi")


# ============================================================================
# RESULTS
# ============================================================================

@dataclass
class PressureVesselResults:
    """Structured results returned by the pressure-vessel design workflow."""

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
    Preliminary pressure vessel with explicit design-standard selection.

    Use ``std="ASME"`` for the supplied ASME preliminary database or
    ``std="IS2825"`` for the supplied IS 2825:1969 reference data.

    Plain numeric dimensions use SI:
        diameter -> m
        length -> m
        pressure -> Pa
        density -> kg/m³

    ProcessPI Pressure, Temperature, Length, Diameter and Volume objects are
    also accepted.
    """

    STANDARD_THICKNESSES_MM = (
        3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 40, 50
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
            raise ValueError("design_pressure must be provided.")

        if _value(pressure, "design_pressure", "Pa") <= 0.0:
            raise ValueError(
                "design_pressure must be greater than zero."
            )

        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None:
            raise ValueError("diameter must be provided.")

        if _value(diameter, "diameter", "m") <= 0.0:
            raise ValueError(
                "diameter must be greater than zero."
            )

        if vessel_type != "spherical":
            length = inputs.get(
                "length",
                inputs.get("tangent_to_tangent_length"),
            )

            if length is None:
                raise ValueError(
                    "length must be provided for cylindrical vessels."
                )

            if _value(length, "length", "m") <= 0.0:
                raise ValueError(
                    "length must be greater than zero for cylindrical vessels."
                )

        joint_efficiency = float(
            inputs.get("joint_efficiency", 1.0)
        )

        if not 0.0 < joint_efficiency <= 1.0:
            raise ValueError(
                "joint_efficiency must be greater than zero and no more "
                "than one."
            )

        corrosion_allowance = _value(
            inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        if corrosion_allowance < 0.0:
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

        std = _normalize_standard(
            inputs.get("std", "ASME")
        )

        material = inputs.get(
            "material",
            "SA516-70",
        )

        material_key = _normalize_material_key(material)

        # Validate standard/material compatibility and the selected
        # temperature-specific allowable stress now.
        _validate_standard_material(
            material_key,
            std,
        )

        get_allowable_stress(
            material_key,
            design_temperature,
            std,
        )

        head_type = str(
            inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

        head_aliases = {
            "2:1_ellipsoidal": "ellipsoidal",
            "2:1 ellipsoidal": "ellipsoidal",
            "elliptical": "ellipsoidal",
            "hemisphere": "hemispherical",
            "flat_head": "flat",
        }

        normalized_head = head_aliases.get(
            head_type,
            head_type,
        )

        if normalized_head not in self._HEADS:
            raise ValueError(
                f"Unsupported head_type '{head_type}'. "
                f"Supported types: {sorted(self._HEADS)}"
            )

        density = float(
            inputs.get(
                "material_density",
                MATERIAL_DENSITIES.get(
                    _normalize_material_key(material),
                    7850.0,
                ),
            )
        )

        if density <= 0.0:
            raise ValueError(
                "material_density must be greater than zero."
            )

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
            self.inputs.get(
                "material",
                "SA516-70",
            )
        )

    @property
    def std(self) -> str:
        """Normalized design standard selected for this vessel."""
        return _normalize_standard(
            self.inputs.get("std", "ASME")
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
            raise ValueError(
                "Nozzle name must not be empty."
            )

        diameter_m = _value(
            diameter,
            "nozzle diameter",
            "m",
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

    # ------------------------------------------------------------------------
    # ALLOWABLE STRESS
    # ------------------------------------------------------------------------

    def allowable_stress(self) -> Pressure:
        return get_allowable_stress(
            self.material,
            self.design_temperature,
            self.std,
        )

    # ------------------------------------------------------------------------
    # SHELL THICKNESS
    # ------------------------------------------------------------------------

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical-shell internal-pressure thickness.

        UG-27(c)(1) form:

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

        allowable_stress_pa = (
            allowable_stress_psi
            * 6894.757293168
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
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        radius = diameter / 2.0

        denominator = (
            allowable_stress_pa
            * joint_efficiency
            - 0.6 * pressure
        )

        if denominator <= 0.0:
            raise ValueError(
                "Shell thickness equation has a non-positive denominator. "
                "Check pressure, allowable stress, and joint efficiency."
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

        2:1 ellipsoidal:
            t = P D / (2 S E - 0.2 P)

        Hemispherical:
            t = P R / (2 S E - 0.2 P)

        Flat:
            preliminary screening expression only.
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

        allowable_stress_pa = (
            allowable_stress_psi
            * 6894.757293168
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
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        head = self.head_type

        normalized = {
            "2:1_ellipsoidal": "ellipsoidal",
            "2:1 ellipsoidal": "ellipsoidal",
            "elliptical": "ellipsoidal",
            "hemisphere": "hemispherical",
            "flat_head": "flat",
        }.get(
            head,
            head,
        )

        radius = diameter / 2.0

        if normalized == "ellipsoidal":

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Ellipsoidal-head thickness equation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                pressure
                * diameter
                / denominator
            )

        elif normalized == "hemispherical":

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Hemispherical-head thickness equation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                pressure
                * radius
                / denominator
            )

        elif normalized == "flat":

            denominator = (
                allowable_stress_pa
                * joint_efficiency
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Flat-head thickness calculation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                0.55
                * diameter
                * sqrt(
                    pressure
                    / denominator
                )
            )

        elif normalized == "torispherical":

            # Preliminary screening factor only.
            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Torispherical-head thickness equation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                0.885
                * pressure
                * diameter
                / denominator
            )

        elif normalized == "conical":

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Conical-head thickness equation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                pressure
                * diameter
                / denominator
            )

        else:
            raise ValueError(
                f"Unsupported head type '{self.head_type}'."
            )

        return Length(
            pressure_thickness
            + corrosion_allowance,
            "m",
        )

    # ------------------------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------------------------

    def _head_volume(
        self,
        radius_m: float,
        head_type: str,
    ) -> float:
        normalized = {
            "2:1_ellipsoidal": "ellipsoidal",
            "2:1 ellipsoidal": "ellipsoidal",
            "elliptical": "ellipsoidal",
            "hemisphere": "hemispherical",
            "flat_head": "flat",
        }.get(
            str(head_type).strip().lower(),
            str(head_type).strip().lower(),
        )

        factors = {
            "flat": 0.0,
            "ellipsoidal": 2.0 / 3.0,
            "torispherical": 0.5,
            "hemispherical": 4.0 / 3.0,
            "conical": 1.0 / 3.0,
        }

        return (
            factors.get(normalized, 2.0 / 3.0)
            * pi
            * radius_m ** 3
        )

    def _calculate_internal_volume(
        self,
        diameter_m: float,
        length_m: float,
        head_type: str,
    ) -> float:
        radius = diameter_m / 2.0

        if self.vessel_type == "spherical":
            return (
                4.0
                / 3.0
                * pi
                * radius ** 3
            )

        cylindrical_volume = (
            pi
            * radius ** 2
            * length_m
        )

        total_head_volume = self._head_volume(
            radius,
            head_type,
        )

        return (
            cylindrical_volume
            + total_head_volume
        )

    def volume(
        self,
        liquid_level: Any = None,
    ) -> Volume:
        """
        Return preliminary internal vessel volume.

        For cylindrical vessels the supplied length is treated as the straight
        cylindrical length and the two heads are added.

        If liquid_level is supplied, a simple cylindrical-segment fraction is
        applied to the complete vessel volume for preliminary use.
        """

        diameter_m = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        radius = diameter_m / 2.0

        if self.vessel_type == "spherical":
            full_volume = (
                4.0
                / 3.0
                * pi
                * radius ** 3
            )
        else:
            length_m = _value(
                self.inputs.get(
                    "length",
                    self.inputs.get("tangent_to_tangent_length"),
                ),
                "length",
                "m",
            )

            full_volume = self._calculate_internal_volume(
                diameter_m,
                length_m,
                self.head_type,
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

        if not 0.0 <= level <= diameter_m:
            raise ValueError(
                "liquid_level must be between zero and vessel diameter."
            )

        if self.vessel_type == "spherical":
            h = level
            fraction = (
                pi * h ** 2 * (3.0 * radius - h) / 3.0
            ) / full_volume

        else:
            segment = (
                radius ** 2
                * acos((radius - level) / radius)
                - (radius - level)
                * sqrt(
                    max(
                        0.0,
                        2.0 * radius * level - level ** 2,
                    )
                )
            )

            fraction = (
                segment
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

        for thickness in self.STANDARD_THICKNESSES_MM:
            if thickness >= required_mm:
                return Length(
                    thickness,
                    "mm",
                )

        return Length(
            required_mm,
            "mm",
        )

    # ------------------------------------------------------------------------
    # DESIGN
    # ------------------------------------------------------------------------

    def design(self) -> Dict[str, Any]:

        shell_required = (
            self.shell_thickness()
            if self.vessel_type != "spherical"
            else self.head_thickness()
        )

        head_required = self.head_thickness()

        governing_required_mm = max(
            _value(
                shell_required,
                "shell required thickness",
                "mm",
            ),
            _value(
                head_required,
                "head required thickness",
                "mm",
            ),
        )

        selected = self.select_standard_thickness(
            Length(
                governing_required_mm,
                "mm",
            )
        )

        pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        pressure_bar = pressure / 100000.0
        pressure_psi = pressure / 6894.757293168

        hydrotest_pressure = Pressure(
            1.3 * pressure,
            "Pa",
        )

        hydrotest_pressure_bar = (
            1.3 * pressure_bar
        )

        hydrotest_pressure_psi = (
            1.3 * pressure_psi
        )

        diameter_m = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        length_m = (
            0.0
            if self.vessel_type == "spherical"
            else _value(
                self.inputs.get(
                    "length",
                    self.inputs.get("tangent_to_tangent_length"),
                ),
                "length",
                "m",
            )
        )

        head_type = self.head_type

        if self.vessel_type == "spherical":
            external_area = (
                4.0
                * pi
                * (diameter_m / 2.0) ** 2
            )
        else:
            external_area = (
                pi
                * diameter_m
                * length_m
                + 2.0
                * pi
                * (diameter_m / 2.0) ** 2
            )

        density = float(
            self.inputs.get(
                "material_density",
                MATERIAL_DENSITIES.get(
                    self.material,
                    7850.0,
                ),
            )
        )

        selected_thickness_m = _value(
            selected,
            "selected thickness",
            "m",
        )

        estimated_weight_kg = (
            external_area
            * selected_thickness_m
            * density
        )

        internal_volume = self.volume()

        specified_volume_input = self.inputs.get(
            "volume",
            None,
        )

        if specified_volume_input is None:
            specified_volume = None
            volume_check = None
            volume_margin_m3 = None
            volume_margin_percent = None
        else:
            specified_volume_m3 = _value(
                specified_volume_input,
                "volume",
                "m3",
            )

            specified_volume = Volume(
                specified_volume_m3,
                "m3",
            )

            internal_volume_m3 = _value(
                internal_volume,
                "internal volume",
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

        temperature_band = set_temperature_range(
            self.design_temperature,
            self.material,
            self.std,
        )

        allowable_stress = self.allowable_stress()

        allowable_stress_psi = _value(
            allowable_stress,
            "allowable stress",
            "psi",
        )

        allowable_stress_ksi = (
            allowable_stress_psi / 1000.0
        )

        design_temperature_f = _value(
            self.design_temperature,
            "design temperature",
            "F",
        )

        selected_temperature_band_f = _value(
            temperature_band,
            "temperature band",
            "F",
        )

        source_note = (
            "Supplied ProcessPI preliminary stress database."
        )

        if self.material.startswith("IS "):
            source_note = (
                "Supplied IS 2825:1969 reference-scan data; "
                "original kgf/mm² values converted to ksi."
            )

        warnings = [
            "Preliminary pressure-vessel internal-pressure sizing only.",
            "Allowable stresses are taken from the supplied "
            "temperature-specific preliminary material database for the "
            f"selected standard ({self.std}).",
            "Verify allowable stresses against the applicable governing "
            "code/material tables before code-stamped design or fabrication.",
            "External pressure/vacuum, complete nozzle reinforcement, "
            "supports, wind, seismic, fatigue, MDMT, PWHT, and flanges "
            "are not evaluated.",
        ]

        if self.material.startswith("IS "):
            warnings.append(
                "IS 2825 values are historical reference-scan data supplied "
                "for ProcessPI development and must be independently verified "
                "against the applicable material/product form and edition."
            )

        if self.nozzles or self.manholes:
            warnings.append(
                "Nozzle and manhole reinforcement calculations are not included."
            )

        if self.std == "ASME":
            design_basis = (
                "Preliminary ASME VIII-1 internal-pressure screening: "
                "UG-27(c)(1), UG-32, UG-34, UG-99(b)."
            )
        else:
            design_basis = (
                "Preliminary pressure-vessel internal-pressure screening "
                "using the supplied IS 2825:1969 material allowable-stress "
                "data. Geometry equations remain preliminary ProcessPI "
                "screening equations and are not a complete IS 2825 code check."
            )

        result = {
            "std": self.std,
            "design_standard": self.std,
            "design_standard_reference": SUPPORTED_STANDARDS[self.std],
            "vessel_type": self.vessel_type,
            "head_type": head_type,
            "material": self.material,

            "design_pressure": Pressure(
                pressure,
                "Pa",
            ),
            "design_pressure_bar": pressure_bar,
            "design_pressure_psi": pressure_psi,

            "design_temperature": self.design_temperature,
            "design_temperature_F": Temperature(
                design_temperature_f,
                "F",
            ),

            "allowable_stress_temperature_band": temperature_band,
            "allowable_stress_temperature_band_F": selected_temperature_band_f,
            "allowable_stress_temperature_band_C": (
                (selected_temperature_band_f - 32.0) * 5.0 / 9.0
                if self.std == "IS2825"
                else None
            ),

            "allowable_stress": allowable_stress,
            "allowable_stress_ksi": allowable_stress_ksi,

            "allowable_stress_source": source_note,

            "diameter": Diameter(
                diameter_m,
                "m",
            ),

            "length": (
                Length(
                    length_m,
                    "m",
                )
                if self.vessel_type != "spherical"
                else Length(
                    0.0,
                    "m",
                )
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

            "shell_required_thickness": shell_required,
            "head_required_thickness": head_required,

            "governing_required_thickness": Length(
                governing_required_mm,
                "mm",
            ),

            "selected_thickness": selected,

            "specified_volume": specified_volume,
            "internal_volume": internal_volume,
            "volume_check": volume_check,

            "volume_margin": (
                Volume(
                    volume_margin_m3,
                    "m3",
                )
                if volume_margin_m3 is not None
                else None
            ),

            "volume_margin_percent": volume_margin_percent,

            "external_area": Area(
                external_area,
                "m2",
            ),

            "material_density_kg_m3": density,
            "estimated_weight_kg": estimated_weight_kg,

            "hydrotest_pressure": hydrotest_pressure,
            "hydrotest_pressure_bar": hydrotest_pressure_bar,
            "hydrotest_pressure_psi": hydrotest_pressure_psi,

            "nozzles": self.nozzles.copy(),
            "manholes": self.manholes.copy(),

            "warnings": warnings,
            "design_basis": design_basis,
        }

        return PressureVesselResults(result).to_dict()

    # ------------------------------------------------------------------------
    # CALCULATIONBASE COMPATIBILITY
    # ------------------------------------------------------------------------

    def calculate(self) -> Dict[str, Any]:
        """Concrete CalculationBase implementation."""
        return self.design()


# ============================================================================
# BACKWARD-COMPATIBLE CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(PressureVessel):
    """Backward-compatible horizontal cylindrical vessel with flat heads."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("vessel_type", "horizontal")
        kwargs.setdefault("head_type", "flat")
        super().__init__(**kwargs)


class CylindricalHorizontalDishEnd(PressureVessel):
    """Backward-compatible horizontal cylindrical vessel with ellipsoidal heads."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("vessel_type", "horizontal")
        kwargs.setdefault("head_type", "ellipsoidal")
        super().__init__(**kwargs)


# Expected by processpi.equipment.__init__
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
    "KGF_MM2_TO_KSI",
    "SUPPORTED_STANDARDS",
    "STANDARD_ALIASES",
    "MATERIAL_STANDARD",
    "normalize_standard",
]
