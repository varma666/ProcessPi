"""
ProcessPI - Pressure Vessel Equipment Module
============================================

Preliminary pressure-vessel sizing based on ASME Section VIII Division 1.

Implemented
-----------
- Complete preliminary material allowable-stress database
- Material aliases
- Temperature-band selection
- Temperature conversion to Fahrenheit
- Zero allowable-stress protection
- Shell internal-pressure sizing
- 2:1 ellipsoidal head sizing
- Hemispherical head sizing
- Flat-head preliminary sizing
- Corrosion allowance
- Joint efficiency
- Vessel volume calculation
- Volume check against specified volume
- Nozzles
- Manholes
- Hydrotest pressure
- Material density
- Estimated vessel weight
- Expanded design result dictionary
- CalculationBase compatibility
- Backward-compatible PressureVessels alias

Important
---------
This module is intended for preliminary engineering calculations.

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

All final engineering designs must be independently verified against
the applicable code edition and project design basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt, acos
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
# Temperature keys:
#     Fahrenheit
#
# Stress values:
#     ksi
#
# These are the values originally supplied for ProcessPI.
#
# IMPORTANT:
# This is a preliminary application database.
# Verify all values against the applicable ASME Section II, Part D tables
# before code-stamped design or fabrication.
# ============================================================================

asme_material_stress_data: Dict[str, Dict[int, float]] = {

    # ------------------------------------------------------------------------
    # CARBON / LOW ALLOY STEELS
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
    # NICKEL / NICKEL ALLOYS
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
    "sa240-304": "SA240-304",
    "sa240 304": "SA240-304",

    "sa240-304l": "SA240-304L",
    "sa240 304l": "SA240-304L",

    "sa240-309s": "SA240-309S",
    "sa240 309s": "SA240-309S",

    "sa240-310": "SA240-310",
    "sa240 310": "SA240-310",

    "sa240-316": "SA240-316",
    "sa240 316": "SA240-316",

    "sa240-316l": "SA240-316L",
    "sa240 316l": "SA240-316L",

    "sa240-317l": "SA240-317L",
    "sa240 317l": "SA240-317L",

    "sa240-347": "SA240-347",
    "sa240 347": "SA240-347",

    # Nickel alloys
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

    # Special alloys
    "a240 904": "A240 904",
    "a240-904": "A240 904",

    "g-30 alloy": "G-30 Alloy",
    "g30 alloy": "G-30 Alloy",

    "titanium grade 2": "Titanium Grade 2",

    "zirconium 702": "Zinccronium 702",
    "zinccronium 702": "Zinccronium 702",

    # Existing ProcessPI generic names
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "carbonsteel": "SA516-70",

    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",

    "stainless_304l": "SA240-304L",
    "stainless 304l": "SA240-304L",

    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",

    "stainless_316l": "SA240-316L",
    "stainless 316l": "SA240-316L",
}


# ============================================================================
# TEMPERATURE DATABASE
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


# ============================================================================
# UNIT / VALUE HELPER
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from either a ProcessPI unit object or a number.

    Parameters
    ----------
    value:
        ProcessPI unit object or numeric value.

    name:
        Name used in error messages.

    unit:
        Target unit for conversion.

    Notes
    -----
    ProcessPI unit implementations may expose the converted value through
    either ``value`` or ``original_value``. Both are handled.
    """

    if value is None:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value"
        )

    converted = value

    if hasattr(converted, "to") and unit:
        converted = converted.to(unit)

    # Prefer original_value only when it represents the converted quantity.
    # Most ProcessPI units expose the useful converted magnitude through
    # value after calling .to().
    if hasattr(converted, "value"):
        numeric = converted.value
    elif hasattr(converted, "original_value"):
        numeric = converted.original_value
    else:
        numeric = converted

    try:
        return float(numeric)

    except (TypeError, ValueError) as exc:

        # Fallback for implementations where original_value is required.
        if hasattr(converted, "original_value"):

            try:
                return float(converted.original_value)

            except (TypeError, ValueError):
                pass

        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value"
        ) from exc


# ============================================================================
# TEMPERATURE BAND SELECTION
# ============================================================================

def set_temperature_range(
    temperature: Any,
) -> Temperature:
    """
    Return the conservative ASME allowable-stress temperature band.

    The stress database is tabulated at:

        100°F
        200°F
        300°F
        400°F
        500°F
        600°F
        700°F
        800°F

    Temperature selection is conservative:

        <= 100°F  -> 100°F
        <= 200°F  -> 200°F
        <= 300°F  -> 300°F
        <= 400°F  -> 400°F
        <= 500°F  -> 500°F
        <= 600°F  -> 600°F
        <= 700°F  -> 700°F
        <= 800°F  -> 800°F

    Therefore:

        302°F -> 400°F
        533°F -> 600°F
        617°F -> 700°F
        797°F -> 800°F

    Temperatures above 800°F are rejected.
    """

    # ------------------------------------------------------------------------
    # Convert FIRST to Fahrenheit.
    #
    # This is the critical fix for the previous 533°F KeyError.
    # ------------------------------------------------------------------------

    fahrenheit = _value(
        temperature,
        "temperature",
        "F",
    )

    # ------------------------------------------------------------------------
    # Reject temperatures above available database.
    # ------------------------------------------------------------------------

    if fahrenheit > 800.0:

        raise ValueError(
            "Design temperature exceeds the available "
            "allowable-stress database. "
            "Maximum supported temperature is 800°F."
        )

    # ------------------------------------------------------------------------
    # Conservative band selection.
    # ------------------------------------------------------------------------

    for band in ASME_STRESS_TEMPERATURES_F:

        if fahrenheit <= band:

            return Temperature(
                band,
                "F",
            )

    # Defensive fallback.
    raise ValueError(
        "Unable to determine allowable-stress temperature band."
    )


# ============================================================================
# MATERIAL NORMALIZATION
# ============================================================================

def normalize_material(
    material: Any,
) -> str:
    """
    Normalize a material identifier to the stress-database key.
    """

    if material is None:
        material = "SA516-70"

    key = str(material).strip()

    # Direct exact lookup
    if key in asme_material_stress_data:
        return key

    # Case-insensitive direct lookup
    lowered = key.lower()

    for material_name in asme_material_stress_data:

        if material_name.lower() == lowered:

            return material_name

    # Alias lookup
    if lowered in MATERIAL_ALIASES:

        return MATERIAL_ALIASES[lowered]

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: "
        f"{', '.join(asme_material_stress_data.keys())}"
    )


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return allowable stress for a material at a specified temperature.

    Parameters
    ----------
    material:
        Material name or alias.

        A numerical value is also accepted and interpreted as
        an allowable stress in ksi.

    temperature:
        ProcessPI Temperature object or numeric temperature.

        Numeric temperatures are interpreted as Fahrenheit.

    Returns
    -------
    Pressure
        Allowable stress represented as psi.

    Notes
    -----
    The database is stored in ksi.

    The temperature is ALWAYS converted to Fahrenheit and mapped to the
    next higher available temperature band.
    """

    # ------------------------------------------------------------------------
    # Numerical allowable stress
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
    # Normalize material
    # ------------------------------------------------------------------------

    material_key = normalize_material(material)

    stress_table = asme_material_stress_data[
        material_key
    ]

    # ------------------------------------------------------------------------
    # IMPORTANT:
    #
    # Always call set_temperature_range().
    #
    # Never directly use the actual temperature as a dictionary key.
    #
    # For example:
    #
    #     533°F -> 600°F
    #
    # not:
    #
    #     stress_table[533]
    #
    # ------------------------------------------------------------------------

    temperature_band = set_temperature_range(
        temperature
    )

    temperature_f = int(
        round(
            _value(
                temperature_band,
                "temperature band",
                "F",
            )
        )
    )

    # ------------------------------------------------------------------------
    # Defensive check.
    # ------------------------------------------------------------------------

    if temperature_f not in stress_table:

        raise ValueError(
            f"No allowable stress temperature band is available "
            f"for material '{material_key}' at "
            f"{temperature_f}°F."
        )

    stress_ksi = float(
        stress_table[temperature_f]
    )

    # ------------------------------------------------------------------------
    # Zero stress protection.
    #
    # Zero values in the supplied database mean that no allowable stress
    # is available at that temperature.
    # ------------------------------------------------------------------------

    if stress_ksi <= 0:

        raise ValueError(
            f"No allowable stress is available for material "
            f"'{material_key}' at {temperature_f}°F."
        )

    # ------------------------------------------------------------------------
    # ksi -> psi
    # ------------------------------------------------------------------------

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
    Structured pressure-vessel design result.
    """

    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()

    @property
    def warnings(self) -> List[str]:
        return self.data["warnings"]

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __repr__(self) -> str:
        return repr(self.data)


# ============================================================================
# PRESSURE VESSEL
# ============================================================================

class PressureVessel(CalculationBase):
    """
    Preliminary ASME VIII-1 pressure vessel.

    Supported vessel types
    ----------------------
    - horizontal
    - vertical
    - spherical

    Supported head types
    --------------------
    - 2:1_ellipsoidal
    - 2:1 ellipsoidal
    - ellipsoidal
    - elliptical
    - hemispherical
    - hemisphere
    - flat
    - flat_head
    """

    # ------------------------------------------------------------------------
    # Standard nominal thicknesses.
    # ------------------------------------------------------------------------

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
        60,
        70,
        80,
        90,
        100,
    )

    _TYPES = {
        "horizontal",
        "vertical",
        "spherical",
    }

    _HEADS = {
        "flat",
        "ellipsoidal",
        "hemispherical",
    }

    # ------------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------------

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:

        # CalculationBase stores inputs and invokes validate_inputs().
        super().__init__(**kwargs)

        # These must exist after validation because the validation stage is
        # executed by CalculationBase before this line.
        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================

    def validate_inputs(self) -> None:
        """
        Validate pressure-vessel inputs.
        """

        inputs = self.inputs

        # ---------------------------------------------------------------------
        # Vessel type
        # ---------------------------------------------------------------------

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

        # ---------------------------------------------------------------------
        # Pressure
        # ---------------------------------------------------------------------

        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        if pressure is None:

            raise ValueError(
                "design_pressure is required"
            )

        pressure_pa = _value(
            pressure,
            "design_pressure",
            "Pa",
        )

        if pressure_pa <= 0:

            raise ValueError(
                "design_pressure must be greater than zero"
            )

        # ---------------------------------------------------------------------
        # Diameter
        # ---------------------------------------------------------------------

        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None:

            raise ValueError(
                "diameter is required"
            )

        diameter_m = _value(
            diameter,
            "diameter",
            "m",
        )

        if diameter_m <= 0:

            raise ValueError(
                "diameter must be greater than zero"
            )

        # ---------------------------------------------------------------------
        # Length
        # ---------------------------------------------------------------------

        if vessel_type != "spherical":

            length = inputs.get(
                "length",
                inputs.get(
                    "tangent_to_tangent_length"
                ),
            )

            if length is None:

                raise ValueError(
                    "length is required for cylindrical vessels"
                )

            length_m = _value(
                length,
                "length",
                "m",
            )

            if length_m <= 0:

                raise ValueError(
                    "length must be greater than zero "
                    "for cylindrical vessels"
                )

        # ---------------------------------------------------------------------
        # Joint efficiency
        # ---------------------------------------------------------------------

        joint_efficiency = float(
            inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        if not 0.0 < joint_efficiency <= 1.0:

            raise ValueError(
                "joint_efficiency must be greater than zero "
                "and no more than one"
            )

        # ---------------------------------------------------------------------
        # Corrosion allowance
        # ---------------------------------------------------------------------

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
                "corrosion_allowance must be non-negative"
            )

        # ---------------------------------------------------------------------
        # Head type
        # ---------------------------------------------------------------------

        head_type = str(
            inputs.get(
                "head_type",
                "2:1_ellipsoidal",
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
        }

        if head_type not in allowed_head_types:

            raise ValueError(
                f"Unsupported head_type '{inputs.get('head_type')}'. "
                "Supported types: "
                "2:1_ellipsoidal, hemispherical, flat."
            )

        # ---------------------------------------------------------------------
        # Material + temperature.
        #
        # This validation is intentionally performed here so errors are
        # detected during PressureVessel construction rather than much later.
        # ---------------------------------------------------------------------

        material = inputs.get(
            "material",
            "SA516-70",
        )

        design_temperature = inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

        get_allowable_stress(
            material,
            design_temperature,
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

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

    # =========================================================================
    # ALLOWABLE STRESS
    # =========================================================================

    def allowable_stress(self) -> Pressure:
        """
        Return allowable stress at design temperature.
        """

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # =========================================================================
    # NOZZLES
    # =========================================================================

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Add a nozzle.

        Nozzle reinforcement is NOT calculated.
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
                "nozzle diameter must be greater than zero"
            )

        self.nozzles[str(name)] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # =========================================================================
    # MANHOLES
    # =========================================================================

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Add a manhole.

        Manhole reinforcement is NOT calculated.
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
                "manhole diameter must be greater than zero"
            )

        self.manholes[str(name)] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **details,
        }

    # =========================================================================
    # SHELL THICKNESS
    # =========================================================================

    def shell_thickness(self) -> Length:
        """
        Preliminary ASME VIII-1 UG-27(c)(1) cylindrical-shell thickness.

        Formula:

            t = PR / (SE - 0.6P)

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
            - 0.6 * pressure_pa
        )

        if denominator <= 0:

            raise ValueError(
                "Shell thickness equation has a non-positive "
                "denominator. Check pressure, allowable stress, "
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

    # =========================================================================
    # HEAD THICKNESS
    # =========================================================================

    def head_thickness(self) -> Length:
        """
        Preliminary pressure-vessel head thickness.

        2:1 ellipsoidal head:

            t = 0.25 P D / (S E - 0.1 P)

        Hemispherical head:

            t = 0.125 P D / (S E - 0.1 P)

        Flat head:

            t = 0.50 D sqrt(P / SE)

        These expressions are for preliminary engineering screening only.
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

        head_type = str(
            self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

        normalized = (
            head_type
            .replace("2:1_", "")
            .replace("2:1 ", "")
        )

        # ---------------------------------------------------------------------
        # 2:1 ellipsoidal
        # ---------------------------------------------------------------------

        if normalized in (
            "ellipsoidal",
            "elliptical",
        ):

            denominator = (
                allowable_stress_pa
                * joint_efficiency
                - 0.1 * pressure_pa
            )

            if denominator <= 0:

                raise ValueError(
                    "Ellipsoidal-head thickness equation has "
                    "a non-positive denominator."
                )

            pressure_thickness_m = (
                0.25
                * pressure_pa
                * diameter_m
                / denominator
            )

        # ---------------------------------------------------------------------
        # Hemispherical
        # ---------------------------------------------------------------------

        elif normalized in (
            "hemispherical",
            "hemisphere",
        ):

            denominator = (
                allowable_stress_pa
                * joint_efficiency
                - 0.1 * pressure_pa
            )

            if denominator <= 0:

                raise ValueError(
                    "Hemispherical-head thickness equation has "
                    "a non-positive denominator."
                )

            pressure_thickness_m = (
                0.125
                * pressure_pa
                * diameter_m
                / denominator
            )

        # ---------------------------------------------------------------------
        # Flat head
        # ---------------------------------------------------------------------

        elif normalized in (
            "flat",
            "flat_head",
        ):

            denominator = (
                allowable_stress_pa
                * joint_efficiency
            )

            if denominator <= 0:

                raise ValueError(
                    "Flat-head thickness calculation has "
                    "a non-positive denominator."
                )

            pressure_thickness_m = (
                0.50
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

    # =========================================================================
    # HEAD VOLUME
    # =========================================================================

    def _head_volume(
        self,
        radius_m: float,
    ) -> float:
        """
        Return total volume contribution of both heads.
        """

        head_type = str(
            self.inputs.get(
                "head_type",
                "2:1_ellipsoidal",
            )
        ).strip().lower()

        normalized = (
            head_type
            .replace("2:1_", "")
            .replace("2:1 ", "")
        )

        # ---------------------------------------------------------------------
        # 2:1 ellipsoidal
        #
        # Each head = 2/3 * pi * r^3
        # Both heads = 4/3 * pi * r^3
        # ---------------------------------------------------------------------

        if normalized in (
            "ellipsoidal",
            "elliptical",
        ):

            return (
                4.0
                / 3.0
                * pi
                * radius_m ** 3
            )

        # ---------------------------------------------------------------------
        # Hemispherical
        #
        # Two hemispheres = one complete sphere.
        # ---------------------------------------------------------------------

        if normalized in (
            "hemispherical",
            "hemisphere",
        ):

            return (
                4.0
                / 3.0
                * pi
                * radius_m ** 3
            )

        # ---------------------------------------------------------------------
        # Flat
        # ---------------------------------------------------------------------

        if normalized in (
            "flat",
            "flat_head",
        ):

            return 0.0

        raise ValueError(
            f"Unsupported head type '{head_type}'."
        )

    # =========================================================================
    # VOLUME
    # =========================================================================

    def volume(
        self,
        liquid_level: Optional[Any] = None,
    ) -> Volume:
        """
        Calculate preliminary internal vessel volume.

        For cylindrical vessels:

            V = cylinder + heads

        For spherical vessels:

            V = 4/3 pi r^3

        ``liquid_level`` provides a preliminary cylindrical-segment
        calculation for liquid inventory.
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

        # ---------------------------------------------------------------------
        # Spherical vessel
        # ---------------------------------------------------------------------

        if self.vessel_type == "spherical":

            full_volume_m3 = (
                4.0
                / 3.0
                * pi
                * radius_m ** 3
            )

        # ---------------------------------------------------------------------
        # Cylindrical vessel
        # ---------------------------------------------------------------------

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

            cylinder_volume_m3 = (
                pi
                * radius_m ** 2
                * length_m
            )

            head_volume_m3 = self._head_volume(
                radius_m
            )

            full_volume_m3 = (
                cylinder_volume_m3
                + head_volume_m3
            )

        # ---------------------------------------------------------------------
        # Full vessel volume
        # ---------------------------------------------------------------------

        if liquid_level is None:

            return Volume(
                full_volume_m3,
                "m3",
            )

        # ---------------------------------------------------------------------
        # Liquid level.
        #
        # This is a preliminary cylindrical-segment calculation.
        # ---------------------------------------------------------------------

        level_m = _value(
            liquid_level,
            "liquid_level",
            "m",
        )

        if not 0.0 <= level_m <= diameter_m:

            raise ValueError(
                "liquid_level must be between zero "
                "and vessel diameter"
            )

        if self.vessel_type == "spherical":

            h = level_m

            liquid_volume_m3 = (
                pi
                * h ** 2
                * (
                    radius_m
                    - h / 3.0
                )
            )

            return Volume(
                liquid_volume_m3,
                "m3",
            )

        # Cylindrical cross-section segment fraction.
        fraction = (
            radius_m ** 2
            * acos(
                (radius_m - level_m)
                / radius_m
            )
            - (
                radius_m - level_m
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
        ) / (
            pi
            * radius_m ** 2
        )

        return Volume(
            full_volume_m3 * fraction,
            "m3",
        )

    # =========================================================================
    # STANDARD THICKNESS
    # =========================================================================

    def select_standard_thickness(
        self,
        required: Any,
    ) -> Length:
        """
        Select the next available nominal thickness.
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

        # If required thickness exceeds the table, return the required value
        # rather than silently under-sizing.
        return Length(
            required_mm,
            "mm",
        )

    # =========================================================================
    # EXTERNAL AREA
    # =========================================================================

    def _external_area(
        self,
        diameter_m: float,
        length_m: float,
    ) -> float:
        """
        Preliminary external surface area.

        For cylindrical vessels:

            A = pi D L + 2 pi r²

        For spherical vessels:

            A = 4 pi r²
        """

        radius_m = diameter_m / 2.0

        if self.vessel_type == "spherical":

            return (
                4.0
                * pi
                * radius_m ** 2
            )

        return (
            pi
            * diameter_m
            * length_m
            + 2.0
            * pi
            * radius_m ** 2
        )

    # =========================================================================
    # DESIGN
    # =========================================================================

    def design(self) -> Dict[str, Any]:
        """
        Perform complete preliminary pressure-vessel design.

        Returns
        -------
        Dict[str, Any]
            Expanded pressure-vessel result dictionary.
        """

        # ---------------------------------------------------------------------
        # Geometry
        # ---------------------------------------------------------------------

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

        # ---------------------------------------------------------------------
        # Material
        # ---------------------------------------------------------------------

        material = self.material

        # ---------------------------------------------------------------------
        # Design temperature
        # ---------------------------------------------------------------------

        design_temperature = (
            self.design_temperature
        )

        # ---------------------------------------------------------------------
        # Temperature band
        # ---------------------------------------------------------------------

        temperature_band = (
            set_temperature_range(
                design_temperature
            )
        )

        temperature_f = _value(
            design_temperature,
            "design temperature",
            "F",
        )

        # ---------------------------------------------------------------------
        # Allowable stress
        # ---------------------------------------------------------------------

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

        # ---------------------------------------------------------------------
        # Required shell thickness
        # ---------------------------------------------------------------------

        if self.vessel_type == "spherical":

            shell_required = (
                self.head_thickness()
            )

        else:

            shell_required = (
                self.shell_thickness()
            )

        # ---------------------------------------------------------------------
        # Required head thickness
        # ---------------------------------------------------------------------

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

        # ---------------------------------------------------------------------
        # Selected nominal thickness
        # ---------------------------------------------------------------------

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

        # ---------------------------------------------------------------------
        # Design pressure
        # ---------------------------------------------------------------------

        design_pressure_obj = Pressure(
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
            design_pressure_obj,
            "design pressure",
            "bar",
        )

        design_pressure_psi = _value(
            design_pressure_obj,
            "design pressure",
            "psi",
        )

        # ---------------------------------------------------------------------
        # Corrosion allowance
        # ---------------------------------------------------------------------

        corrosion_allowance = Length(
            _value(
                self.inputs.get(
                    "corrosion_allowance",
                    Length(0, "mm"),
                ),
                "corrosion_allowance",
                "m",
            ),
            "m",
        )

        # ---------------------------------------------------------------------
        # Volume
        # ---------------------------------------------------------------------

        internal_volume = self.volume()

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
        specified_volume_m3 = None

        if specified_volume is not None:

            specified_volume_m3 = _value(
                specified_volume,
                "volume",
                "m3",
            )

            if specified_volume_m3 <= 0:

                raise ValueError(
                    "volume must be greater than zero"
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

        # ---------------------------------------------------------------------
        # External area
        # ---------------------------------------------------------------------

        external_area_m2 = (
            self._external_area(
                diameter_m,
                length_m,
            )
        )

        # ---------------------------------------------------------------------
        # Material density
        # ---------------------------------------------------------------------

        density = float(
            self.inputs.get(
                "material_density",
                7850.0,
            )
        )

        if density <= 0:

            raise ValueError(
                "material_density must be greater than zero"
            )

        # ---------------------------------------------------------------------
        # Estimated weight
        # ---------------------------------------------------------------------

        selected_thickness_m = (
            selected_thickness_mm
            / 1000.0
        )

        estimated_weight_kg = (
            external_area_m2
            * selected_thickness_m
            * density
        )

        # ---------------------------------------------------------------------
        # Hydrotest
        # ---------------------------------------------------------------------

        hydrotest_pressure = Pressure(
            design_pressure_obj.to("Pa").value
            * 1.3,
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

        # ---------------------------------------------------------------------
        # Warnings
        # ---------------------------------------------------------------------

        warnings: List[str] = [

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
                "Calculated internal vessel volume is "
                "less than the specified design volume."
            )

        # ---------------------------------------------------------------------
        # Design basis
        # ---------------------------------------------------------------------

        design_basis = (
            "ASME VIII-1 preliminary: "
            "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
        )

        # ---------------------------------------------------------------------
        # Expanded result dictionary
        # ---------------------------------------------------------------------

        result: Dict[str, Any] = {

            # Identification
            "vessel_type":
                self.vessel_type,

            "head_type":
                self.inputs.get(
                    "head_type",
                    "2:1_ellipsoidal",
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
                Temperature(
                    temperature_f,
                    "F",
                ),

            "allowable_stress_temperature_band":
                temperature_band,

            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            # Dimensions
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
                    if self.vessel_type != "spherical"
                    else Length(
                        0,
                        "m",
                    )
                ),

            "joint_efficiency":
                float(
                    self.inputs.get(
                        "joint_efficiency",
                        1.0,
                    )
                ),

            "corrosion_allowance":
                corrosion_allowance,

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

    # =========================================================================
    # CALCULATIONBASE COMPATIBILITY
    # =========================================================================

    def calculate(self) -> Dict[str, Any]:
        """
        Required concrete implementation of CalculationBase.calculate().

        ``design()`` is retained as the primary pressure-vessel API.

        ``calculate()`` provides the standard ProcessPI calculation interface.
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
    with ellipsoidal heads.
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
            "2:1_ellipsoidal",
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
    "normalize_material",
    "get_allowable_stress",
    "set_temperature_range",
]
