"""
ProcessPI Pressure Vessel Module
================================

Preliminary pressure-vessel design utilities based on ASME Section VIII
Division 1 internal-pressure equations.

Scope
-----
This module provides preliminary sizing for:
    - Cylindrical pressure vessels
    - Horizontal pressure vessels
    - Spherical pressure vessels
    - 2:1 ellipsoidal heads
    - Flat heads
    - Nozzle/manhole bookkeeping
    - Hydrotest pressure
    - Approximate vessel volume
    - Approximate external area
    - Approximate vessel weight
    - Temperature-dependent allowable stress selection

IMPORTANT
---------
This module is intended for preliminary engineering calculations.

It is NOT a complete code-stamped ASME VIII-1 design.

The supplied material allowable stresses are a preliminary database and
must be verified against the applicable ASME Section II, Part D tables
before fabrication or code certification.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
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
# ASME MATERIAL ALLOWABLE-STRESS DATABASE
# ============================================================================
#
# Values are allowable stress in ksi.
#
# Temperature bands are in °F.
#
# IMPORTANT:
# These are the supplied preliminary values and are NOT claimed to be the
# current official ASME Section II Part D values.
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
    # NICKEL / SPECIAL ALLOYS
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

    # ------------------------------------------------------------------------
    # Carbon / low-alloy steels
    # ------------------------------------------------------------------------

    "sa515-55": "SA515-55",
    "sa515-70": "SA515-70",
    "sa516-55": "SA516-55",
    "sa516-70": "SA516-70",

    "sa256-a": "SA256-A",

    "sa285-b": "SA285-B",
    "sa285-c": "SA285-C",

    "sa202-a": "SA202-A",
    "sa202-b": "SA202-B",

    "sa387-d": "SA387-D",

    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "carbonsteel": "SA516-70",
    "cs": "SA516-70",

    "sa516": "SA516-70",
    "sa-516-70": "SA516-70",

    # ------------------------------------------------------------------------
    # Stainless steels
    # ------------------------------------------------------------------------

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
    "347": "SA240-347",

    # ------------------------------------------------------------------------
    # Nickel / special alloys
    # ------------------------------------------------------------------------

    "b162": "B162",
    "201": "201",
    "b127": "B127",
    "b168": "B168",
    "b443": "B443",

    "c-22 alloy": "C-22 alloy",
    "c22 alloy": "C-22 alloy",
    "c22": "C-22 alloy",

    "b575": "B575",
    "b333": "B333",
    "b463": "B463",
    "b409": "B409",
    "b424": "B424",
    "b688": "B688",

    "a240 904": "A240 904",
    "a240-904": "A240 904",
    "904": "A240 904",

    "g-30 alloy": "G-30 Alloy",
    "g30 alloy": "G-30 Alloy",
    "g30": "G-30 Alloy",

    "titanium grade 2": "Titanium Grade 2",
    "ti grade 2": "Titanium Grade 2",

    # Supplied spelling retained for compatibility.
    "zirconium 702": "Zinccronium 702",
    "zinccronium 702": "Zinccronium 702",
    "zirconium grade 702": "Zinccronium 702",
}


# ============================================================================
# SUPPORTED TEMPERATURE BANDS
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
# UNIT / VALUE HELPER
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from a ProcessPI unit object or plain number.

    When a target unit is supplied, the object's ``to()`` method is used.

    The function intentionally handles both ``value`` and ``original_value``
    because ProcessPI unit implementations have evolved over time.
    """

    if value is None:
        raise ValueError(
            f"{name} must be specified."
        )

    if unit and hasattr(value, "to"):
        try:
            converted = value.to(unit)

            # IMPORTANT:
            # Prefer the converted object's current value.
            #
            # original_value represents the value as originally supplied,
            # not necessarily the converted value.
            if hasattr(converted, "value"):
                value = converted.value
            elif hasattr(converted, "original_value"):
                value = converted.original_value
            else:
                value = converted

        except Exception:
            # Fall through to direct extraction below.
            pass

    if hasattr(value, "value"):
        value = value.value
    elif hasattr(value, "original_value"):
        value = value.original_value

    try:
        return float(value)

    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value."
        ) from exc


# ============================================================================
# TEMPERATURE CONVERSION
# ============================================================================

def _temperature_to_f(
    temperature: Temperature,
) -> float:
    """
    Convert a ProcessPI Temperature object to Fahrenheit.

    This function deliberately performs the conversion from the original
    value/unit when those attributes are available.

    This prevents pressure-vessel ASME stress-band selection from depending
    on an inconsistent Temperature.to("F") implementation in an older
    ProcessPI installation.

    Supported units:
        C
        F
        K

    Examples
    --------
    150 C -> 302 F
    302 F -> 302 F
    423.15 K -> 302 F
    """

    if not isinstance(temperature, Temperature):
        raise TypeError(
            "Design temperature must be a Temperature object."
        )

    # ------------------------------------------------------------------------
    # Best path: use original user input.
    # ------------------------------------------------------------------------

    original_value = getattr(
        temperature,
        "original_value",
        None,
    )

    original_unit = getattr(
        temperature,
        "original_unit",
        None,
    )

    if (
        original_value is not None
        and original_unit is not None
    ):

        value = float(original_value)

        unit = str(
            original_unit
        ).strip().upper()

        # Normalize common spellings.
        unit = {
            "°C": "C",
            "CELSIUS": "C",
            "DEG C": "C",

            "°F": "F",
            "FAHRENHEIT": "F",
            "DEG F": "F",

            "°K": "K",
            "KELVIN": "K",
        }.get(
            unit,
            unit,
        )

        if unit == "C":
            temperature_f = (
                value * 9.0 / 5.0
            ) + 32.0

        elif unit == "F":
            temperature_f = value

        elif unit == "K":
            temperature_f = (
                (value - 273.15)
                * 9.0 / 5.0
            ) + 32.0

        else:
            raise ValueError(
                f"Unsupported temperature unit '{original_unit}'. "
                "Expected C, F, or K."
            )

        return round(
            temperature_f,
            6,
        )

    # ------------------------------------------------------------------------
    # Fallback.
    # ------------------------------------------------------------------------

    try:
        converted = temperature.to("F")

        value = getattr(
            converted,
            "value",
            getattr(
                converted,
                "original_value",
                converted,
            ),
        )

        return round(
            float(value),
            6,
        )

    except Exception as exc:

        raise ValueError(
            "Unable to convert design temperature to Fahrenheit."
        ) from exc


# ============================================================================
# TEMPERATURE BAND SELECTION
# ============================================================================

def set_temperature_range(
    temperature: Temperature,
) -> Temperature:
    """
    Select the conservative ASME allowable-stress temperature band.

    The first available band greater than or equal to the design temperature
    is selected.

    Examples
    --------
    25 C  -> 100 F
    50 C  -> 200 F
    100 C -> 300 F
    150 C -> 400 F
    175 C -> 400 F
    225 C -> 500 F
    275 C -> 600 F
    325 C -> 700 F
    375 C -> 800 F
    425 C -> 800 F

    Above 800 F:
        ValueError

    Below -20 F:
        ValueError
    """

    fahrenheit = _temperature_to_f(
        temperature
    )

    if (
        fahrenheit
        < MIN_SUPPORTED_TEMPERATURE_F
        - TEMPERATURE_TOLERANCE_F
    ):
        raise ValueError(
            "Design temperature is below the available "
            "allowable-stress database. "
            f"Minimum supported temperature is "
            f"{MIN_SUPPORTED_TEMPERATURE_F:g}°F."
        )

    for band in ASME_TEMPERATURE_BANDS:

        if (
            fahrenheit
            <= band + TEMPERATURE_TOLERANCE_F
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


# ============================================================================
# MATERIAL NORMALIZATION
# ============================================================================

def normalize_material(
    material: Any,
) -> str:
    """
    Normalize a material name or alias to the canonical database key.
    """

    if material is None:
        raise ValueError(
            "Material must be specified."
        )

    key = str(
        material
    ).strip()

    if not key:
        raise ValueError(
            "Material must not be empty."
        )

    # Exact database key.
    if key in asme_material_stress_data:
        return key

    # Case-insensitive direct lookup.
    lowered = key.lower()

    for material_name in asme_material_stress_data:

        if (
            material_name.lower()
            == lowered
        ):
            return material_name

    # Alias.
    if lowered in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[
            lowered
        ]

    raise ValueError(
        f"Unsupported pressure-vessel material: "
        f"{material!r}. "
        f"Available materials: "
        f"{', '.join(asme_material_stress_data.keys())}"
    )


# Backward-compatible private helper.
def _normalize_material_key(
    material: Any,
) -> str:
    return normalize_material(material)


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return allowable stress for the supplied material and temperature.

    Material database:
        ksi

    Returned value:
        Pressure in psi

    Numerical material input:
        If ``material`` is numeric, it is interpreted as allowable stress
        in ksi and the temperature lookup is bypassed.

    Temperature:
        A ProcessPI Temperature object is expected.

    Temperature-band selection:
        Conservative next-higher ASME database band.

    Example
    -------
    150 C
        -> 302 F
        -> 400 F band
    """

    # ------------------------------------------------------------------------
    # Explicit numerical allowable stress.
    # ------------------------------------------------------------------------

    if isinstance(
        material,
        (int, float),
    ):

        stress_ksi = float(
            material
        )

        if stress_ksi <= 0:
            raise ValueError(
                "Allowable stress must be greater than zero."
            )

        return Pressure(
            stress_ksi * 1000.0,
            "psi",
        )

    # ------------------------------------------------------------------------
    # Normalize material.
    # ------------------------------------------------------------------------

    material_key = normalize_material(
        material
    )

    # ------------------------------------------------------------------------
    # Temperature band.
    # ------------------------------------------------------------------------

    temperature_band = set_temperature_range(
        temperature
    )

    temperature_f = int(
        round(
            _temperature_to_f(
                temperature_band
            )
        )
    )

    # ------------------------------------------------------------------------
    # Lookup table.
    # ------------------------------------------------------------------------

    stress_table = (
        asme_material_stress_data[
            material_key
        ]
    )

    if temperature_f not in stress_table:

        raise ValueError(
            "No allowable stress temperature band "
            f"is available for material "
            f"'{material_key}' at "
            f"{temperature_f}°F."
        )

    stress_ksi = float(
        stress_table[
            temperature_f
        ]
    )

    # ------------------------------------------------------------------------
    # Zero/negative values indicate unavailable allowable stress.
    # ------------------------------------------------------------------------

    if stress_ksi <= 0:

        raise ValueError(
            "No allowable stress is available for "
            f"material '{material_key}' at "
            f"{temperature_f}°F."
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
    Structured result container.

    ``to_dict()`` is retained so existing ProcessPI workflows that expect
    dictionaries continue to work.
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

class PressureVessel(
    CalculationBase
):
    """
    Preliminary ASME VIII-1 pressure vessel.

    Supported vessel types:
        horizontal
        vertical
        spherical

    Supported head types:
        2:1_ellipsoidal
        ellipsoidal
        2:1 ellipsoidal
        flat
    """

    # ========================================================================
    # INITIALIZATION
    # ========================================================================

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        # ------------------------------------------------------------
        # Defaults
        # ------------------------------------------------------------

        kwargs.setdefault(
            "vessel_type",
            "horizontal",
        )

        kwargs.setdefault(
            "head_type",
            "2:1_ellipsoidal",
        )

        kwargs.setdefault(
            "joint_efficiency",
            1.0,
        )

        kwargs.setdefault(
            "corrosion_allowance",
            Length(0, "mm"),
        )

        kwargs.setdefault(
            "material",
            "SA516-70",
        )

        # ------------------------------------------------------------
        # Base class performs input validation.
        # ------------------------------------------------------------

        super().__init__(
            **kwargs
        )

        # ------------------------------------------------------------
        # Attachment storage.
        # ------------------------------------------------------------

        self.nozzles: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self.manholes: Dict[
            str,
            Dict[str, Any],
        ] = {}

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def validate_inputs(
        self,
    ) -> None:

        inputs = self.inputs

        # --------------------------------------------------------------------
        # Required inputs.
        # --------------------------------------------------------------------

        if (
            inputs.get("design_pressure")
            is None
            and inputs.get("pressure")
            is None
        ):
            raise ValueError(
                "design_pressure must be specified."
            )

        if (
            inputs.get("design_temperature")
            is None
            and inputs.get("temperature")
            is None
        ):
            raise ValueError(
                "design_temperature must be specified."
            )

        if (
            inputs.get("diameter")
            is None
            and inputs.get("inside_diameter")
            is None
        ):
            raise ValueError(
                "diameter must be specified."
            )

        vessel_type = str(
            inputs.get(
                "vessel_type",
                "horizontal",
            )
        ).lower().strip()

        if vessel_type not in {
            "horizontal",
            "vertical",
            "spherical",
        }:
            raise ValueError(
                "vessel_type must be "
                "'horizontal', 'vertical', or 'spherical'."
            )

        # --------------------------------------------------------------------
        # Cylindrical vessels require length.
        # --------------------------------------------------------------------

        if vessel_type != "spherical":

            if (
                inputs.get("length")
                is None
                and inputs.get(
                    "tangent_to_tangent_length"
                )
                is None
            ):
                raise ValueError(
                    "length must be specified for "
                    "non-spherical vessels."
                )

        # --------------------------------------------------------------------
        # Material.
        # --------------------------------------------------------------------

        material = inputs.get(
            "material",
            "SA516-70",
        )

        material_key = normalize_material(
            material
        )

        # Store canonical material in inputs.
        inputs["material"] = material_key

        # --------------------------------------------------------------------
        # Temperature.
        # --------------------------------------------------------------------

        temperature = inputs.get(
            "design_temperature",
            inputs.get("temperature"),
        )

        if not isinstance(
            temperature,
            Temperature,
        ):
            raise TypeError(
                "design_temperature must be a Temperature object."
            )

        # Validate temperature and stress lookup now.
        get_allowable_stress(
            material_key,
            temperature,
        )

        # --------------------------------------------------------------------
        # Pressure.
        # --------------------------------------------------------------------

        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        p = _value(
            pressure,
            "design_pressure",
            "Pa",
        )

        if p <= 0:
            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Diameter.
        # --------------------------------------------------------------------

        diameter = _value(
            inputs.get(
                "diameter",
                inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        if diameter <= 0:
            raise ValueError(
                "diameter must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Length.
        # --------------------------------------------------------------------

        if vessel_type != "spherical":

            length = _value(
                inputs.get(
                    "length",
                    inputs.get(
                        "tangent_to_tangent_length"
                    ),
                ),
                "length",
                "m",
            )

            if length <= 0:
                raise ValueError(
                    "length must be greater than zero."
                )

        # --------------------------------------------------------------------
        # Joint efficiency.
        # --------------------------------------------------------------------

        joint_efficiency = float(
            inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        if not (
            0.0 < joint_efficiency <= 1.0
        ):
            raise ValueError(
                "joint_efficiency must be > 0 and <= 1."
            )

        # --------------------------------------------------------------------
        # Corrosion allowance.
        # --------------------------------------------------------------------

        corrosion_allowance = _value(
            inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        if corrosion_allowance < 0:
            raise ValueError(
                "corrosion_allowance cannot be negative."
            )

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def vessel_type(self) -> str:

        return str(
            self.inputs.get(
                "vessel_type",
                "horizontal",
            )
        ).lower().strip()

    @property
    def head_type(self) -> str:

        return str(
            self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).lower().strip()

    @property
    def material(self) -> str:

        return normalize_material(
            self.inputs.get(
                "material",
                "SA516-70",
            )
        )

    @property
    def design_temperature(
        self,
    ) -> Temperature:

        return self.inputs.get(
            "design_temperature",
            self.inputs.get(
                "temperature"
            ),
        )

    # ========================================================================
    # ALLOWABLE STRESS
    # ========================================================================

    def allowable_stress(
        self,
    ) -> Pressure:

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # ========================================================================
    # SHELL THICKNESS
    # ========================================================================

    def shell_thickness(
        self,
    ) -> Length:
        """
        Cylindrical shell internal-pressure sizing.

        ASME VIII-1 preliminary form:

            t = P R / (S E - 0.6 P)

        where:

            P = design pressure
            R = inside radius
            S = allowable stress
            E = joint efficiency

        Corrosion allowance is added after pressure thickness.
        """

        pressure_pa = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        diameter_m = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
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

        corrosion_allowance_m = _value(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        denominator = (
            allowable_stress_pa
            * joint_efficiency
            - 0.6
            * pressure_pa
        )

        if denominator <= 0:
            raise ValueError(
                "Shell thickness equation denominator is "
                "non-positive. Check pressure, allowable "
                "stress, and joint efficiency."
            )

        pressure_thickness = (
            pressure_pa
            * radius_m
            / denominator
        )

        total_thickness = (
            pressure_thickness
            + corrosion_allowance_m
        )

        return Length(
            total_thickness,
            "m",
        )

    # ========================================================================
    # HEAD THICKNESS
    # ========================================================================

    def head_thickness(
        self,
    ) -> Length:
        """
        Preliminary head sizing.

        2:1 ellipsoidal head:

            t = P D / (2 S E - 0.2 P)

        Flat head:

            A simplified preliminary plate relation is used.

        For flat heads, a more complete ASME UG-34 design requires detailed
        geometry, attachment and bolting considerations and is outside this
        preliminary module.
        """

        pressure_pa = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        diameter_m = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

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

        corrosion_allowance_m = _value(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        head_type = self.head_type

        # Normalize naming.
        normalized_head = (
            head_type
            .replace("-", "_")
            .replace(" ", "_")
        )

        # --------------------------------------------------------------------
        # 2:1 ellipsoidal head.
        # --------------------------------------------------------------------

        if normalized_head in {
            "2:1_ellipsoidal",
            "2:1_ellipsoid",
            "ellipsoidal",
            "2_1_ellipsoidal",
            "2_1_ellipsoid",
        }:

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2
                * pressure_pa
            )

            if denominator <= 0:
                raise ValueError(
                    "Head thickness equation denominator is "
                    "non-positive."
                )

            pressure_thickness = (
                pressure_pa
                * diameter_m
                / denominator
            )

        # --------------------------------------------------------------------
        # Flat head.
        # --------------------------------------------------------------------

        elif normalized_head in {
            "flat",
            "flat_head",
            "flat_end",
        }:

            # Preliminary flat-head approximation.
            #
            # This is intentionally conservative and is NOT a replacement
            # for a complete UG-34 calculation.
            pressure_thickness = (
                diameter_m
                * (
                    pressure_pa
                    / allowable_stress_pa
                ) ** 0.5
                / (
                    2.0
                    * max(
                        joint_efficiency,
                        1.0e-12,
                    )
                )
            )

        else:

            raise ValueError(
                f"Unsupported head_type: "
                f"{self.inputs.get('head_type')!r}. "
                "Supported values include "
                "'2:1_ellipsoidal' and 'flat'."
            )

        total_thickness = (
            pressure_thickness
            + corrosion_allowance_m
        )

        return Length(
            total_thickness,
            "m",
        )

    # ========================================================================
    # STANDARD THICKNESS
    # ========================================================================

    def select_standard_thickness(
        self,
        required_thickness: Length,
    ) -> Length:
        """
        Select the next standard nominal plate thickness.

        The list is intentionally simple and suitable for preliminary
        ProcessPI sizing.
        """

        required_mm = _value(
            required_thickness,
            "required thickness",
            "mm",
        )

        standard_thicknesses_mm = (
            3,
            4,
            5,
            6,
            8,
            10,
            12,
            14,
            16,
            18,
            20,
            22,
            25,
            28,
            30,
            32,
            36,
            40,
            45,
            50,
            55,
            60,
            65,
            70,
            75,
            80,
            90,
            100,
            110,
            120,
        )

        for thickness_mm in standard_thicknesses_mm:

            if thickness_mm >= required_mm:

                return Length(
                    thickness_mm,
                    "mm",
                )

        raise ValueError(
            "Required vessel thickness exceeds the "
            "available preliminary standard thickness range."
        )

    # ========================================================================
    # VOLUME
    # ========================================================================

    def volume(
        self,
    ) -> Volume:
        """
        Calculate approximate internal vessel volume.

        Cylindrical vessel:
            V = cylindrical volume + two hemispherical-equivalent end volumes

        For a 2:1 ellipsoidal head, each head is approximated as half of an
        ellipsoid, giving approximately:

            V_head_pair = pi D^3 / 12

        Spherical vessel:
            V = 4/3 pi r^3
        """

        diameter_m = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        radius_m = diameter_m / 2.0

        if self.vessel_type == "spherical":

            volume_m3 = (
                4.0
                / 3.0
                * pi
                * radius_m**3
            )

            return Volume(
                volume_m3,
                "m3",
            )

        length_m = _value(
            self.inputs.get(
                "length",
                self.inputs.get(
                    "tangent_to_tangent_length"
                ),
            ),
            "length",
            "m",
        )

        cylindrical_volume = (
            pi
            * radius_m**2
            * length_m
        )

        normalized_head = (
            self.head_type
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized_head in {
            "2:1_ellipsoidal",
            "2:1_ellipsoid",
            "ellipsoidal",
            "2_1_ellipsoidal",
            "2_1_ellipsoid",
        }:

            head_pair_volume = (
                pi
                * diameter_m**3
                / 12.0
            )

        elif normalized_head in {
            "flat",
            "flat_head",
            "flat_end",
        }:

            head_pair_volume = 0.0

        else:

            # Default to ellipsoidal approximation for unknown legacy names.
            head_pair_volume = (
                pi
                * diameter_m**3
                / 12.0
            )

        total_volume = (
            cylindrical_volume
            + head_pair_volume
        )

        return Volume(
            total_volume,
            "m3",
        )

    # ========================================================================
    # EXTERNAL AREA
    # ========================================================================

    def _external_area(
        self,
        diameter_m: float,
        length_m: float,
    ) -> float:
        """
        Approximate external surface area.

        Cylindrical section:
            pi D L

        End contribution:
            2 pi r²

        This is intentionally approximate.
        """

        if self.vessel_type == "spherical":

            radius_m = diameter_m / 2.0

            return (
                4.0
                * pi
                * radius_m**2
            )

        radius_m = diameter_m / 2.0

        cylindrical_area = (
            pi
            * diameter_m
            * length_m
        )

        end_area = (
            2.0
            * pi
            * radius_m**2
        )

        return (
            cylindrical_area
            + end_area
        )

    # ========================================================================
    # NOZZLES
    # ========================================================================

    def add_nozzle(
        self,
        name: str,
        diameter: Diameter,
        **kwargs: Any,
    ) -> None:
        """
        Add a nozzle to the vessel.

        Nozzle reinforcement is NOT calculated by this module.
        """

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

        self.nozzles[
            str(name)
        ] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **kwargs,
        }

    # ========================================================================
    # MANHOLES
    # ========================================================================

    def add_manhole(
        self,
        name: str,
        diameter: Diameter,
        **kwargs: Any,
    ) -> None:
        """
        Add a manhole to the vessel.

        Reinforcement is NOT calculated by this module.
        """

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

        self.manholes[
            str(name)
        ] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **kwargs,
        }

    # ========================================================================
    # DESIGN
    # ========================================================================

    def design(
        self,
    ) -> Dict[str, Any]:
        """
        Perform complete preliminary vessel design.
        """

        # --------------------------------------------------------------------
        # Geometry.
        # --------------------------------------------------------------------

        diameter_m = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        if self.vessel_type == "spherical":

            length_m = 0.0

        else:

            length_m = _value(
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
        # Pressure.
        # --------------------------------------------------------------------

        design_pressure = Pressure(
            _value(
                self.inputs.get(
                    "design_pressure",
                    self.inputs.get("pressure"),
                ),
                "design_pressure",
                "Pa",
            ),
            "Pa",
        )

        design_pressure_bar = _value(
            design_pressure,
            "design pressure",
            "bar",
        )

        design_pressure_psi = _value(
            design_pressure,
            "design pressure",
            "psi",
        )

        # --------------------------------------------------------------------
        # Temperature.
        # --------------------------------------------------------------------

        design_temperature = (
            self.design_temperature
        )

        design_temperature_f = (
            _temperature_to_f(
                design_temperature
            )
        )

        temperature_band = (
            set_temperature_range(
                design_temperature
            )
        )

        temperature_band_f = int(
            round(
                _temperature_to_f(
                    temperature_band
                )
            )
        )

        # --------------------------------------------------------------------
        # Allowable stress.
        # --------------------------------------------------------------------

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

        # --------------------------------------------------------------------
        # Thickness calculations.
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

        # --------------------------------------------------------------------
        # Volume.
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

        specified_volume_m3 = None
        volume_check = None
        volume_margin_m3 = None
        volume_margin_percent = None

        if specified_volume is not None:

            specified_volume_m3 = _value(
                specified_volume,
                "volume",
                "m3",
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
        # External area.
        # --------------------------------------------------------------------

        external_area_m2 = (
            self._external_area(
                diameter_m,
                length_m,
            )
        )

        # --------------------------------------------------------------------
        # Material density.
        # --------------------------------------------------------------------

        material_density = self.inputs.get(
            "material_density"
        )

        if material_density is None:

            material_density = (
                MATERIAL_DENSITIES.get(
                    self.material,
                    7850.0,
                )
            )

        material_density = float(
            material_density
        )

        # --------------------------------------------------------------------
        # Approximate weight.
        # --------------------------------------------------------------------

        selected_thickness_m = (
            selected_thickness_mm
            / 1000.0
        )

        estimated_weight_kg = (
            external_area_m2
            * selected_thickness_m
            * material_density
        )

        # --------------------------------------------------------------------
        # Hydrotest.
        # --------------------------------------------------------------------

        hydrotest_pressure = Pressure(
            1.3
            * _value(
                design_pressure,
                "design pressure",
                "Pa",
            ),
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
        # Warnings.
        # --------------------------------------------------------------------

        warnings = [

            (
                "Preliminary ASME Section VIII "
                "Division 1 internal-pressure sizing only."
            ),

            (
                "Allowable stresses are taken from the "
                "supplied temperature-specific preliminary "
                "material database."
            ),

            (
                "Verify all material allowable stresses "
                "against the applicable ASME Section II, "
                "Part D tables before code-stamped design "
                "or fabrication."
            ),

            (
                "External pressure/vacuum, complete nozzle "
                "reinforcement, supports, wind, seismic, "
                "fatigue, MDMT, PWHT, and flanges are not "
                "evaluated."
            ),
        ]

        if (
            self.nozzles
            or self.manholes
        ):

            warnings.append(
                "Nozzle and manhole reinforcement "
                "calculations are not included."
            )

        if (
            volume_check is False
        ):

            warnings.append(
                "Calculated internal vessel volume is "
                "less than the specified design volume."
            )

        # --------------------------------------------------------------------
        # Design basis.
        # --------------------------------------------------------------------

        design_basis = (
            "ASME VIII-1 preliminary: "
            "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
        )

        # --------------------------------------------------------------------
        # Results.
        # --------------------------------------------------------------------

        result = {

            # Identification
            "vessel_type":
                self.vessel_type,

            "head_type":
                self.inputs.get(
                    "head_type",
                    "2:1_ellipsoidal",
                ),

            "material":
                self.material,

            # Design pressure
            "design_pressure":
                design_pressure,

            "design_pressure_bar":
                design_pressure_bar,

            "design_pressure_psi":
                design_pressure_psi,

            # Design temperature
            "design_temperature":
                design_temperature,

            "design_temperature_F":
                Temperature(
                    design_temperature_f,
                    "F",
                ),

            "allowable_stress_temperature_band":
                temperature_band,

            "allowable_stress_temperature_band_F":
                temperature_band_f,

            # Stress
            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            # Geometry
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
                    _value(
                        self.inputs.get(
                            "corrosion_allowance",
                            Length(0, "mm"),
                        ),
                        "corrosion allowance",
                        "m",
                    ),
                    "m",
                ),

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
                selected_thickness,

            # Volume
            "specified_volume":
                specified_volume,

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
                    external_area_m2,
                    "m2",
                ),

            "material_density_kg_m3":
                material_density,

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

            # Warnings
            "warnings":
                warnings,

            # Design basis
            "design_basis":
                design_basis,
        }

        return result

    # ========================================================================
    # CALCULATIONBASE IMPLEMENTATION
    # ========================================================================

    def calculate(
        self,
    ) -> Dict[str, Any]:
        """
        Concrete implementation required by CalculationBase.

        This MUST be an explicit method rather than:

            calculate = design

        because CalculationBase defines calculate() as an abstract method.
        """

        return self.design()


# ============================================================================
# BACKWARD-COMPATIBLE CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(
    PressureVessel
):
    """
    Backward-compatible horizontal cylindrical vessel with flat ends.
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
    Backward-compatible horizontal cylindrical vessel with dished heads.
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        super().__init__(
            vessel_type="horizontal",
            head_type="2:1_ellipsoidal",
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
