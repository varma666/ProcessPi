"""
ProcessPI Pressure Vessel Module
================================

Preliminary ASME Section VIII Division 1 internal-pressure vessel design.

Features
--------
- Cylindrical and spherical vessels
- Horizontal / vertical orientation
- Flat, 2:1 ellipsoidal, torispherical,
  hemispherical and conical heads
- Temperature-dependent allowable stresses
- ASME material aliases
- Conservative temperature-band selection
- Corrosion allowance
- Weld joint efficiency
- Nozzle and manhole registration
- Geometry-derived vessel volume
- Specified-vs-calculated volume consistency check
- Hydrotest pressure
- Preliminary vessel weight estimation

IMPORTANT
---------
This module is intended for preliminary engineering calculations.

The material allowable-stress values included here are the supplied
ProcessPI database values. They must be verified against the applicable
ASME Section II, Part D tables before code-stamped design or fabrication.

This module does NOT perform complete ASME VIII-1 design verification for:

- external pressure / vacuum
- nozzle reinforcement
- flange design
- support design
- saddle stresses
- wind
- seismic
- fatigue
- MDMT / impact testing
- PWHT
- local discontinuity stresses
- thermal stresses
- detailed head geometry
- openings and reinforcement
- detailed UG-99 hydrotest evaluation
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
# ASME MATERIAL ALLOWABLE STRESS DATABASE
# ============================================================================
#
# Values are in ksi.
#
# Temperature values are in °F.
#
# The supplied database contains allowable stress values at:
#
#     100, 200, 300, 400, 500, 600, 700 and 800°F
#
# For an actual design temperature between two table temperatures,
# ProcessPI conservatively selects the NEXT HIGHER temperature band.
#
# Example:
#
#     302°F -> 400°F
#     450°F -> 500°F
#     550°F -> 600°F
#
# Temperatures <= 100°F use the 100°F value.
#
# Temperatures > 800°F are rejected because this database does not
# contain values above 800°F.
#
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

    # Carbon / low alloy
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "sa-516-70": "SA516-70",
    "sa51670": "SA516-70",

    # Stainless
    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",
    "ss304": "SA240-304",

    "stainless_304l": "SA240-304L",
    "stainless 304l": "SA240-304L",
    "ss304l": "SA240-304L",

    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
    "ss316": "SA240-316",

    "stainless_316l": "SA240-316L",
    "stainless 316l": "SA240-316L",
    "ss316l": "SA240-316L",

    # Other aliases
    "c22": "C-22 alloy",
    "c-22": "C-22 alloy",

    "g30": "G-30 Alloy",
    "g-30": "G-30 Alloy",

    "titanium grade 2": "Titanium Grade 2",
    "ti grade 2": "Titanium Grade 2",

    "zirconium 702": "Zinccronium 702",
    "zirconium grade 702": "Zinccronium 702",
}


# ============================================================================
# CONSTANTS
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

SUPPORTED_VESSEL_TYPES = {
    "horizontal",
    "vertical",
    "spherical",
}

SUPPORTED_HEAD_TYPES = {
    "flat",
    "ellipsoidal",
    "torispherical",
    "hemispherical",
    "conical",
}


# ============================================================================
# GENERAL VALUE HELPER
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from a ProcessPI unit object or numeric value.

    If a unit is supplied and the object supports ``to()``, the value is
    converted first.
    """

    if value is None:
        raise ValueError(f"{name} cannot be None.")

    if hasattr(value, "to") and unit is not None:
        value = value.to(unit)

    if hasattr(value, "value"):
        value = value.value
    elif hasattr(value, "original_value"):
        value = value.original_value

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a compatible ProcessPI unit."
        ) from exc


# ============================================================================
# MATERIAL NORMALIZATION
# ============================================================================

def normalize_material(material: Any) -> str:
    """
    Convert material aliases and case variations into canonical material names.

    Examples
    --------
    ``carbon_steel`` -> ``SA516-70``

    ``stainless_316`` -> ``SA240-316``

    ``sa516-70`` -> ``SA516-70``
    """

    if material is None:
        raise ValueError("Material cannot be None.")

    material_string = str(material).strip()

    # Exact match
    if material_string in asme_material_stress_data:
        return material_string

    # Alias
    alias_key = material_string.lower()

    if alias_key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[alias_key]

    # Case-insensitive direct match
    for material_name in asme_material_stress_data:
        if material_name.lower() == alias_key:
            return material_name

    available = ", ".join(asme_material_stress_data.keys())

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: {available}"
    )


# ============================================================================
# HEAD TYPE NORMALIZATION
# ============================================================================

def normalize_head_type(head_type: Any) -> str:
    """
    Normalize user-facing head names.

    Examples
    --------
    ``2:1_ellipsoidal`` -> ``ellipsoidal``

    ``2:1 ellipsoidal`` -> ``ellipsoidal``

    ``2:1-ellipsoidal`` -> ``ellipsoidal``
    """

    if head_type is None:
        return "ellipsoidal"

    key = str(head_type).strip().lower()

    aliases = {
        "flat": "flat",

        "ellipsoidal": "ellipsoidal",
        "2:1_ellipsoidal": "ellipsoidal",
        "2:1 ellipsoidal": "ellipsoidal",
        "2:1-ellipsoidal": "ellipsoidal",
        "2:1 elliptical": "ellipsoidal",
        "2:1_elliptical": "ellipsoidal",

        "torispherical": "torispherical",
        "torispheric": "torispherical",

        "hemispherical": "hemispherical",
        "hemispheric": "hemispherical",
        "half spherical": "hemispherical",

        "conical": "conical",
        "cone": "conical",
    }

    if key in aliases:
        return aliases[key]

    raise ValueError(
        f"Unsupported head_type: {head_type!r}. "
        f"Supported head types: {sorted(SUPPORTED_HEAD_TYPES)}"
    )


# ============================================================================
# TEMPERATURE RANGE
# ============================================================================

def set_temperature_range(
    temperature: Any,
) -> Temperature:
    """
    Select the conservative allowable-stress temperature band.

    The supplied database is tabulated at 100°F increments.

    Temperatures between table points use the next higher temperature band.

    Examples
    --------
    100°F -> 100°F
    101°F -> 200°F
    302°F -> 400°F
    450°F -> 500°F
    800°F -> 800°F
    """

    # ProcessPI Temperature -> Fahrenheit
    if hasattr(temperature, "to"):
        temperature_f = _value(
            temperature,
            "temperature",
            "F",
        )
    else:
        # Plain numeric temperatures are interpreted as Fahrenheit.
        temperature_f = float(temperature)

    if temperature_f <= 100:
        return Temperature(100, "F")

    for table_temperature in ASME_STRESS_TEMPERATURES_F:

        if temperature_f <= table_temperature:
            return Temperature(
                table_temperature,
                "F",
            )

    raise ValueError(
        "Design temperature exceeds the available allowable-stress "
        "database limit of 800°F."
    )


# ============================================================================
# ALLOWABLE STRESS
# ============================================================================

def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return allowable material stress.

    Parameters
    ----------
    material:
        Material name or ProcessPI material alias.

    temperature:
        ProcessPI Temperature object or numeric Fahrenheit value.

    Returns
    -------
    Pressure
        Allowable stress in psi.

    Notes
    -----
    The database values are in ksi.
    """

    # ------------------------------------------------------------------------
    # Direct numerical allowable stress
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
    # Retrieve stress
    # ------------------------------------------------------------------------

    stress_ksi = asme_material_stress_data[
        material_key
    ][temperature_f]

    # Zero means no usable allowable stress was supplied.
    if stress_ksi <= 0:

        raise ValueError(
            f"No positive allowable stress is available for "
            f"{material_key} at {temperature_f}°F."
        )

    return Pressure(
        stress_ksi * 1000,
        "psi",
    )


# ============================================================================
# STRESS INFORMATION
# ============================================================================

def get_stress_data(
    material: Any,
    temperature: Any,
) -> Dict[str, Any]:
    """
    Return complete audit information for the selected allowable stress.
    """

    material_key = normalize_material(material)

    # Actual temperature in F
    if hasattr(temperature, "to"):

        actual_temperature_f = _value(
            temperature,
            "design temperature",
            "F",
        )

    else:

        actual_temperature_f = float(
            temperature
        )

    selected_band = set_temperature_range(
        temperature
    )

    selected_temperature_f = int(
        round(
            _value(
                selected_band,
                "selected temperature band",
                "F",
            )
        )
    )

    allowable_stress_ksi = (
        asme_material_stress_data[
            material_key
        ][selected_temperature_f]
    )

    if allowable_stress_ksi <= 0:

        raise ValueError(
            f"No positive allowable stress is available for "
            f"{material_key} at {selected_temperature_f}°F."
        )

    return {
        "material": material_key,

        "temperature_actual": temperature,

        "temperature_actual_f": actual_temperature_f,

        "temperature_table_band": selected_band,

        "temperature_table_band_f": selected_temperature_f,

        "allowable_stress_ksi": allowable_stress_ksi,

        "allowable_stress_psi": (
            allowable_stress_ksi * 1000
        ),

        "selection_method": (
            "next_higher_temperature_band"
        ),
    }


# ============================================================================
# RESULTS CONTAINER
# ============================================================================

@dataclass
class PressureVesselResults:
    """
    Structured PressureVessel design results.
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

    def __repr__(self) -> str:
        return repr(self.data)


# ============================================================================
# PRESSURE VESSEL
# ============================================================================

class PressureVessel(CalculationBase):
    """
    Preliminary ASME VIII-1 pressure vessel.

    Parameters
    ----------
    volume:
        Optional specified vessel volume.

    diameter:
        Vessel internal diameter.

    length:
        Cylindrical tangent-to-tangent length.

    design_pressure:
        Internal design pressure.

    design_temperature:
        Design temperature.

    vessel_type:
        ``horizontal``, ``vertical`` or ``spherical``.

    head_type:
        ``flat``, ``2:1_ellipsoidal``, ``torispherical``,
        ``hemispherical`` or ``conical``.

    material:
        ASME material or ProcessPI material alias.

    corrosion_allowance:
        Corrosion allowance.

    joint_efficiency:
        Weld joint efficiency.
    """

    # Standard preliminary plate thicknesses
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
        75,
        80,
        100,
    )

    def __init__(self, **kwargs: Any):

        super().__init__(**kwargs)

        self.nozzles: Dict[str, Dict[str, Any]] = {}

        self.manholes: Dict[str, Dict[str, Any]] = {}

    # ========================================================================
    # INPUT PROPERTIES
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
    def material_input(self) -> str:

        return str(
            self.inputs.get(
                "material",
                "SA516-70",
            )
        )

    @property
    def material(self) -> str:

        return normalize_material(
            self.material_input
        )

    @property
    def head_type_input(self) -> str:

        return str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        )

    @property
    def head_type(self) -> str:

        return normalize_head_type(
            self.head_type_input
        )

    @property
    def design_temperature(self) -> Any:

        return self.inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def validate_inputs(self) -> None:

        inputs = self.inputs

        # --------------------------------------------------------------------
        # Vessel type
        # --------------------------------------------------------------------

        if self.vessel_type not in SUPPORTED_VESSEL_TYPES:

            raise ValueError(
                f"vessel_type must be one of "
                f"{sorted(SUPPORTED_VESSEL_TYPES)}"
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
                "design_pressure is required."
            )

        pressure_pa = _value(
            pressure,
            "design_pressure",
            "Pa",
        )

        if pressure_pa <= 0:

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
                "diameter is required."
            )

        diameter_m = _value(
            diameter,
            "diameter",
            "m",
        )

        if diameter_m <= 0:

            raise ValueError(
                "diameter must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Length
        # --------------------------------------------------------------------

        if self.vessel_type != "spherical":

            length = inputs.get(
                "length",
                inputs.get(
                    "tangent_to_tangent_length"
                ),
            )

            if length is None:

                raise ValueError(
                    "length is required for cylindrical vessels."
                )

            length_m = _value(
                length,
                "length",
                "m",
            )

            if length_m <= 0:

                raise ValueError(
                    "length must be greater than zero."
                )

        # --------------------------------------------------------------------
        # Joint efficiency
        # --------------------------------------------------------------------

        joint_efficiency = float(
            inputs.get(
                "joint_efficiency",
                1.0,
            )
        )

        if not 0 < joint_efficiency <= 1:

            raise ValueError(
                "joint_efficiency must be > 0 and <= 1."
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
                "corrosion_allowance cannot be negative."
            )

        # --------------------------------------------------------------------
        # Material
        # --------------------------------------------------------------------

        normalize_material(
            inputs.get(
                "material",
                "SA516-70",
            )
        )

        # --------------------------------------------------------------------
        # Head
        # --------------------------------------------------------------------

        normalize_head_type(
            inputs.get(
                "head_type",
                "ellipsoidal",
            )
        )

        # --------------------------------------------------------------------
        # Temperature / allowable stress
        # --------------------------------------------------------------------

        get_allowable_stress(
            inputs.get(
                "material",
                "SA516-70",
            ),
            inputs.get(
                "design_temperature",
                Temperature(20, "C"),
            ),
        )

        # --------------------------------------------------------------------
        # Volume
        # --------------------------------------------------------------------

        if "volume" in inputs and inputs["volume"] is not None:

            volume_m3 = _value(
                inputs["volume"],
                "volume",
                "m3",
            )

            if volume_m3 <= 0:

                raise ValueError(
                    "volume must be greater than zero."
                )

    # ========================================================================
    # ALLOWABLE STRESS
    # ========================================================================

    def allowable_stress(self) -> Pressure:

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

    # ========================================================================
    # STRESS DATA
    # ========================================================================

    def stress_data(self) -> Dict[str, Any]:

        return get_stress_data(
            self.material,
            self.design_temperature,
        )

    # ========================================================================
    # SHELL THICKNESS
    # ========================================================================

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical shell thickness.

        Based on the internal-pressure relation:

            t = P R / (S E - 0.6P)

        Corrosion allowance is added after calculating the pressure
        thickness.
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

        radius = diameter / 2

        allowable_stress = _value(
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

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

        denominator = (
            allowable_stress
            * joint_efficiency
            - 0.6 * pressure
        )

        if denominator <= 0:

            raise ValueError(
                "Invalid pressure/material combination: "
                "S*E - 0.6P must be greater than zero."
            )

        pressure_thickness = (
            pressure
            * radius
            / denominator
        )

        return Length(
            pressure_thickness
            + corrosion_allowance
        )

    # ========================================================================
    # HEAD THICKNESS
    # ========================================================================

    def head_thickness(self) -> Length:
        """
        Preliminary head thickness.

        The head factors used here are preliminary engineering factors and
        are not a substitute for detailed ASME head design.
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

        allowable_stress = _value(
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

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                0.0,
            ),
            "corrosion_allowance",
            "m",
        )

        head = self.head_type

        # Preliminary pressure-thickness factors
        factors = {
            "flat": 0.50,
            "ellipsoidal": 0.25,
            "torispherical": 0.885,
            "hemispherical": 0.125,
            "conical": 0.35,
        }

        factor = factors[head]

        denominator = (
            allowable_stress
            * joint_efficiency
            - 0.1 * pressure
        )

        if denominator <= 0:

            raise ValueError(
                "Invalid pressure/material combination for head."
            )

        pressure_thickness = (
            factor
            * pressure
            * diameter
            / denominator
        )

        return Length(
            pressure_thickness
            + corrosion_allowance
        )

    # ========================================================================
    # HEAD VOLUME
    # ========================================================================

    def _head_volume(
        self,
        radius: float,
    ) -> float:
        """
        Preliminary geometric head-volume contribution.

        This is a simplified geometry model used for preliminary volume
        estimation.
        """

        factors = {
            "flat": 0.0,

            # 2:1 ellipsoidal head approximation
            "ellipsoidal": 2.0 / 3.0,

            "torispherical": 0.5,

            "hemispherical": 4.0 / 3.0,

            "conical": 1.0 / 3.0,
        }

        return (
            factors[self.head_type]
            * pi
            * radius**3
        )

    # ========================================================================
    # VOLUME
    # ========================================================================

    def volume(
        self,
        liquid_level: Optional[Any] = None,
    ) -> Volume:
        """
        Calculate internal vessel volume from geometry.

        Important:
        The supplied ``volume`` input is treated as a specified/reference
        volume. It does NOT override explicitly supplied diameter and length.

        The calculated geometric volume is therefore the governing result
        for the geometry.
        """

        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        radius = diameter / 2

        # --------------------------------------------------------------------
        # Spherical vessel
        # --------------------------------------------------------------------

        if self.vessel_type == "spherical":

            full_volume = (
                4.0
                / 3.0
                * pi
                * radius**3
            )

        # --------------------------------------------------------------------
        # Cylindrical vessel
        # --------------------------------------------------------------------

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

            cylindrical_volume = (
                pi
                * radius**2
                * length
            )

            head_volume = self._head_volume(
                radius
            )

            full_volume = (
                cylindrical_volume
                + head_volume
            )

        # --------------------------------------------------------------------
        # Full volume requested
        # --------------------------------------------------------------------

        if liquid_level is None:

            return Volume(
                full_volume,
                "m3",
            )

        # --------------------------------------------------------------------
        # Liquid level
        # --------------------------------------------------------------------

        level = _value(
            liquid_level,
            "liquid_level",
            "m",
        )

        if not 0 <= level <= diameter:

            raise ValueError(
                "liquid_level must be between "
                "0 and vessel diameter."
            )

        # --------------------------------------------------------------------
        # Simplified cylindrical segment calculation
        # --------------------------------------------------------------------

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

        segment_fraction = (
            segment_volume
            /
            (
                pi * radius**2
            )
        )

        return Volume(
            full_volume
            * segment_fraction,
            "m3",
        )

    # ========================================================================
    # VOLUME CHECK
    # ========================================================================

    def volume_check(self) -> Dict[str, Any]:
        """
        Compare user-specified volume with geometry-derived volume.

        The geometry-derived volume is not replaced by the specified volume.
        """

        calculated_volume = self.volume()

        calculated_m3 = _value(
            calculated_volume,
            "calculated volume",
            "m3",
        )

        specified = self.inputs.get(
            "volume"
        )

        # No volume supplied
        if specified is None:

            return {
                "specified_volume": None,
                "calculated_volume": calculated_volume,
                "difference_m3": None,
                "difference_percent": None,
                "status": "calculated_from_geometry",
            }

        specified_m3 = _value(
            specified,
            "volume",
            "m3",
        )

        difference_m3 = (
            calculated_m3
            - specified_m3
        )

        difference_percent = (
            difference_m3
            / specified_m3
            * 100.0
        )

        tolerance_percent = float(
            self.inputs.get(
                "volume_tolerance_percent",
                1.0,
            )
        )

        if abs(difference_percent) <= tolerance_percent:

            status = "consistent"

        else:

            status = "geometry_volume_differs"

        return {
            "specified_volume": specified,
            "calculated_volume": calculated_volume,
            "difference_m3": difference_m3,
            "difference_percent": difference_percent,
            "tolerance_percent": tolerance_percent,
            "status": status,
        }

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

        for thickness_mm in self.STANDARD_THICKNESSES_MM:

            if thickness_mm >= required_mm:

                return Length(
                    thickness_mm,
                    "mm",
                )

        # If required thickness exceeds the standard list,
        # return the calculated requirement rather than silently
        # selecting an inadequate plate.
        return Length(
            required_mm,
            "mm",
        )

    # ========================================================================
    # NOZZLE
    # ========================================================================

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Register a nozzle.

        This method registers the nozzle only. It does not perform
        UG-37/UG-40 reinforcement calculations.
        """

        if not name:
            raise ValueError(
                "Nozzle name cannot be empty."
            )

        diameter_m = _value(
            diameter,
            "nozzle diameter",
            "m",
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

    # ========================================================================
    # MANHOLE
    # ========================================================================

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:
        """
        Register a manhole.

        This method registers the manhole only. It does not perform
        detailed opening reinforcement calculations.
        """

        if not name:
            raise ValueError(
                "Manhole name cannot be empty."
            )

        diameter_m = _value(
            diameter,
            "manhole diameter",
            "m",
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
    # DESIGN
    # ========================================================================

    def design(self) -> Dict[str, Any]:
        """
        Run the complete preliminary pressure-vessel design.

        Returns
        -------
        dict
            Design results.
        """

        # --------------------------------------------------------------------
        # Validate
        # --------------------------------------------------------------------

        self.validate_inputs()

        # --------------------------------------------------------------------
        # Thickness calculations
        # --------------------------------------------------------------------

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
        # Pressure
        # --------------------------------------------------------------------

        design_pressure = self.inputs.get(
            "design_pressure",
            self.inputs.get("pressure"),
        )

        design_pressure_pa = _value(
            design_pressure,
            "design_pressure",
            "Pa",
        )

        hydrotest_pressure = Pressure(
            1.3 * design_pressure_pa,
            "Pa",
        )

        # --------------------------------------------------------------------
        # Geometry
        # --------------------------------------------------------------------

        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get(
                    "inside_diameter"
                ),
            ),
            "diameter",
            "m",
        )

        radius = diameter / 2.0

        if self.vessel_type == "spherical":

            length = 0.0

            external_area = (
                4.0
                * pi
                * radius**2
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

            shell_area = (
                pi
                * diameter
                * length
            )

            head_area = (
                2.0
                * pi
                * radius**2
            )

            external_area = (
                shell_area
                + head_area
            )

        # --------------------------------------------------------------------
        # Weight estimate
        # --------------------------------------------------------------------

        density = float(
            self.inputs.get(
                "material_density",
                7850.0,
            )
        )

        selected_thickness_m = (
            selected_thickness_mm
            / 1000.0
        )

        estimated_weight_kg = (
            external_area
            * selected_thickness_m
            * density
        )

        # --------------------------------------------------------------------
        # Stress data
        # --------------------------------------------------------------------

        stress_data = self.stress_data()

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
        # Volume
        # --------------------------------------------------------------------

        volume_data = (
            self.volume_check()
        )

        calculated_volume = (
            volume_data[
                "calculated_volume"
            ]
        )

        # --------------------------------------------------------------------
        # Warnings
        # --------------------------------------------------------------------

        warnings: List[str] = []

        warnings.append(
            "Preliminary ASME Section VIII "
            "Division 1 internal-pressure "
            "sizing only."
        )

        warnings.append(
            "Allowable stresses are taken from "
            "the supplied ProcessPI material "
            "database."
        )

        warnings.append(
            "Verify all material allowable stresses "
            "against the applicable ASME Section II, "
            "Part D tables before code-stamped design "
            "or fabrication."
        )

        warnings.append(
            "External pressure/vacuum, complete nozzle "
            "reinforcement, supports, wind, seismic, "
            "fatigue, MDMT, PWHT, and flange design "
            "are not evaluated."
        )

        if self.nozzles:

            warnings.append(
                "Nozzle reinforcement calculations "
                "are not included."
            )

        if self.manholes:

            warnings.append(
                "Manhole/opening reinforcement calculations "
                "are not included."
            )

        if (
            volume_data["status"]
            == "geometry_volume_differs"
        ):

            warnings.append(
                "Specified vessel volume differs from "
                "the geometry-derived volume by "
                f"{abs(volume_data['difference_percent']):.2f}%."
            )

        # --------------------------------------------------------------------
        # Standard thickness warning
        # --------------------------------------------------------------------

        if (
            selected_thickness_mm
            > governing_required_mm
        ):

            warnings.append(
                "Selected thickness has been rounded up "
                "to the next available standard plate thickness."
            )

        # --------------------------------------------------------------------
        # Temperature-band warning
        # --------------------------------------------------------------------

        actual_temperature_f = (
            stress_data[
                "temperature_actual_f"
            ]
        )

        selected_temperature_f = (
            stress_data[
                "temperature_table_band_f"
            ]
        )

        if (
            abs(
                actual_temperature_f
                - selected_temperature_f
            )
            > 1e-9
        ):

            warnings.append(
                "Allowable stress was selected using "
                f"the next higher temperature band "
                f"({selected_temperature_f:.0f}°F) "
                f"for the actual design temperature "
                f"of {actual_temperature_f:.1f}°F."
            )

        # --------------------------------------------------------------------
        # Result
        # --------------------------------------------------------------------

        result = {

            # ---------------------------------------------------------------
            # Vessel identification
            # ---------------------------------------------------------------

            "vessel_type": self.vessel_type,

            "head_type": self.head_type,

            "head_type_input": self.head_type_input,

            "material": self.material,

            "material_input": self.material_input,

            # ---------------------------------------------------------------
            # Design conditions
            # ---------------------------------------------------------------

            "design_pressure": design_pressure,

            "design_temperature": self.design_temperature,

            # ---------------------------------------------------------------
            # Stress
            # ---------------------------------------------------------------

            "allowable_stress_temperature_band": (
                stress_data[
                    "temperature_table_band"
                ]
            ),

            "allowable_stress": (
                allowable_stress
            ),

            "allowable_stress_ksi": (
                allowable_stress_ksi
            ),

            "stress_data": stress_data,

            # ---------------------------------------------------------------
            # Thickness
            # ---------------------------------------------------------------

            "shell_required_thickness": (
                shell_required
            ),

            "head_required_thickness": (
                head_required
            ),

            "governing_required_thickness": (
                Length(
                    governing_required_mm,
                    "mm",
                )
            ),

            "selected_thickness": (
                selected_thickness
            ),

            "selected_thickness_mm": (
                selected_thickness_mm
            ),

            # ---------------------------------------------------------------
            # Geometry
            # ---------------------------------------------------------------

            "diameter": (
                self.inputs.get(
                    "diameter",
                    self.inputs.get(
                        "inside_diameter"
                    ),
                )
            ),

            "length": (
                self.inputs.get(
                    "length",
                    self.inputs.get(
                        "tangent_to_tangent_length"
                    ),
                )
                if self.vessel_type != "spherical"
                else None
            ),

            # ---------------------------------------------------------------
            # Volume
            # ---------------------------------------------------------------

            "specified_volume": (
                volume_data[
                    "specified_volume"
                ]
            ),

            "internal_volume": (
                calculated_volume
            ),

            "calculated_volume": (
                calculated_volume
            ),

            "volume_difference_m3": (
                volume_data[
                    "difference_m3"
                ]
            ),

            "volume_difference_percent": (
                volume_data[
                    "difference_percent"
                ]
            ),

            "volume_check": volume_data,

            # ---------------------------------------------------------------
            # Area / weight
            # ---------------------------------------------------------------

            "external_area": Area(
                external_area,
                "m2",
            ),

            "estimated_weight_kg": (
                estimated_weight_kg
            ),

            "material_density_kg_m3": (
                density
            ),

            # ---------------------------------------------------------------
            # Hydrotest
            # ---------------------------------------------------------------

            "hydrotest_pressure": (
                hydrotest_pressure
            ),

            # ---------------------------------------------------------------
            # Openings
            # ---------------------------------------------------------------

            "nozzles": (
                self.nozzles.copy()
            ),

            "manholes": (
                self.manholes.copy()
            ),

            # ---------------------------------------------------------------
            # Warnings
            # ---------------------------------------------------------------

            "warnings": warnings,

            # ---------------------------------------------------------------
            # Design basis
            # ---------------------------------------------------------------

            "design_basis": (
                "ASME VIII-1 preliminary: "
                "UG-27(c)(1), UG-32, UG-34, "
                "UG-99(b)"
            ),
        }

        return PressureVesselResults(
            result
        ).to_dict()

    # ========================================================================
    # CALCULATION ALIAS
    # ========================================================================

    calculate = design


# ============================================================================
# BACKWARD COMPATIBILITY CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(
    PressureVessel
):
    """
    Backward-compatible horizontal cylindrical
    vessel with flat heads.
    """

    def __init__(
        self,
        **kwargs: Any,
    ):

        super().__init__(
            vessel_type="horizontal",
            head_type="flat",
            **kwargs,
        )


class CylindricalHorizontalDishEnd(
    PressureVessel
):
    """
    Backward-compatible horizontal cylindrical
    vessel with ellipsoidal heads.
    """

    def __init__(
        self,
        **kwargs: Any,
    ):

        super().__init__(
            vessel_type="horizontal",
            head_type="ellipsoidal",
            **kwargs,
        )


# ============================================================================
# BACKWARD-COMPATIBLE ALIAS
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
    "normalize_head_type",

    "set_temperature_range",
    "get_allowable_stress",
    "get_stress_data",
]
