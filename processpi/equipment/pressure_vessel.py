"""
ProcessPI Pressure Vessel Module
================================

Preliminary ASME Section VIII Division 1 internal-pressure vessel design.

Features
--------
- Cylindrical / spherical pressure vessels
- Horizontal / vertical / spherical vessel types
- Flat, 2:1 ellipsoidal, torispherical,
  hemispherical and conical heads
- Temperature-dependent allowable stresses
- ASME material aliases
- Conservative temperature-band selection
- Corrosion allowance
- Weld joint efficiency
- Nozzle registration
- Manhole registration
- Geometry-derived vessel volume
- Specified-vs-calculated volume consistency check
- Hydrotest pressure
- Preliminary vessel weight estimation
- Expanded auditable design result dictionary

IMPORTANT
---------
This module is intended for preliminary engineering calculations.

The allowable-stress values included here are the supplied
ProcessPI preliminary material database values.

They MUST be verified against the applicable ASME Section II,
Part D tables before code-stamped design or fabrication.

This module does NOT constitute complete ASME VIII-1 design verification.

Not included:
- External pressure / vacuum
- Complete nozzle reinforcement
- Complete manhole reinforcement
- Flange design
- Support / saddle design
- Wind
- Seismic
- Fatigue
- MDMT / impact testing
- PWHT
- Local discontinuity stresses
- Thermal stresses
- Detailed opening reinforcement
- Detailed UG-99 hydrotest evaluation
- Complete head design verification
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
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
# Units:
#   Temperature -> °F
#   Stress      -> ksi
#
# The values below are the complete supplied ProcessPI database.
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

    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "carbonsteel": "SA516-70",
    "sa516-70": "SA516-70",
    "sa-516-70": "SA516-70",
    "sa51670": "SA516-70",

    "sa515-55": "SA515-55",
    "sa51555": "SA515-55",

    "sa515-70": "SA515-70",
    "sa51570": "SA515-70",

    "sa516-55": "SA516-55",
    "sa51655": "SA516-55",

    "sa285-b": "SA285-B",
    "sa285b": "SA285-B",

    "sa285-c": "SA285-C",
    "sa285c": "SA285-C",

    "sa202-a": "SA202-A",
    "sa202a": "SA202-A",

    "sa202-b": "SA202-B",
    "sa202b": "SA202-B",

    "sa387-d": "SA387-D",
    "sa387d": "SA387-D",

    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",
    "ss304": "SA240-304",

    "stainless_304l": "SA240-304L",
    "stainless 304l": "SA240-304L",
    "ss304l": "SA240-304L",

    "stainless_309s": "SA240-309S",
    "stainless 309s": "SA240-309S",
    "ss309s": "SA240-309S",

    "stainless_310": "SA240-310",
    "stainless 310": "SA240-310",
    "ss310": "SA240-310",

    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
    "ss316": "SA240-316",

    "stainless_316l": "SA240-316L",
    "stainless 316l": "SA240-316L",
    "ss316l": "SA240-316L",

    "stainless_317l": "SA240-317L",
    "stainless 317l": "SA240-317L",
    "ss317l": "SA240-317L",

    "stainless_347": "SA240-347",
    "stainless 347": "SA240-347",
    "ss347": "SA240-347",

    "c22": "C-22 alloy",
    "c-22": "C-22 alloy",
    "c22 alloy": "C-22 alloy",

    "g30": "G-30 Alloy",
    "g-30": "G-30 Alloy",
    "g30 alloy": "G-30 Alloy",

    "titanium grade 2": "Titanium Grade 2",
    "ti grade 2": "Titanium Grade 2",
    "titanium_2": "Titanium Grade 2",

    "zirconium 702": "Zinccronium 702",
    "zirconium grade 702": "Zinccronium 702",
    "zirconium_702": "Zinccronium 702",
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
# VALUE HELPERS
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Convert ProcessPI unit objects or numeric values into floats.

    If ``unit`` is supplied, ProcessPI's ``to()`` conversion is used.
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


def _length_m(value: Any, name: str) -> float:
    return _value(value, name, "m")


def _diameter_m(value: Any, name: str) -> float:
    return _value(value, name, "m")


def _pressure_pa(value: Any, name: str) -> float:
    return _value(value, name, "Pa")


def _volume_m3(value: Any, name: str) -> float:
    return _value(value, name, "m3")


# ============================================================================
# MATERIAL NORMALIZATION
# ============================================================================

def normalize_material(material: Any) -> str:
    """
    Convert material aliases into canonical material names.
    """

    if material is None:
        raise ValueError("Material cannot be None.")

    material_string = str(material).strip()

    if material_string in asme_material_stress_data:
        return material_string

    alias_key = material_string.lower()

    if alias_key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[alias_key]

    for material_name in asme_material_stress_data:
        if material_name.lower() == alias_key:
            return material_name

    available = ", ".join(asme_material_stress_data.keys())

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: {available}"
    )


# ============================================================================
# HEAD NORMALIZATION
# ============================================================================

def normalize_head_type(head_type: Any) -> str:
    """
    Normalize user-facing head names.
    """

    if head_type is None:
        return "ellipsoidal"

    key = str(head_type).strip().lower()

    aliases = {
        "flat": "flat",

        "ellipsoidal": "ellipsoidal",
        "ellipsoid": "ellipsoidal",
        "elliptical": "ellipsoidal",
        "2:1": "ellipsoidal",
        "2:1_ellipsoidal": "ellipsoidal",
        "2:1 ellipsoidal": "ellipsoidal",
        "2:1-ellipsoidal": "ellipsoidal",
        "2:1 elliptical": "ellipsoidal",
        "2:1_elliptical": "ellipsoidal",

        "torispherical": "torispherical",
        "torispheric": "torispherical",
        "torispheric head": "torispherical",

        "hemispherical": "hemispherical",
        "hemispheric": "hemispherical",
        "half spherical": "hemispherical",
        "hemisphere": "hemispherical",

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
# TEMPERATURE BAND SELECTION
# ============================================================================

def _temperature_f(
    temperature: Any,
) -> float:
    """
    Convert a temperature into °F.

    ProcessPI Temperature objects are converted through the units system.

    Plain numeric values are interpreted as °F.
    """

    if hasattr(temperature, "to"):
        return _value(
            temperature,
            "temperature",
            "F",
        )

    return float(temperature)


def set_temperature_range(
    temperature: Any,
) -> Temperature:
    """
    Select the next higher allowable-stress temperature band.

    Examples
    --------
    100°F -> 100°F
    101°F -> 200°F
    250°F -> 300°F
    302°F -> 400°F
    450°F -> 500°F
    550°F -> 600°F
    800°F -> 800°F

    This function NEVER performs an exact lookup using the actual
    design temperature.

    This is the key protection against errors such as:

        KeyError: 533
    """

    temperature_f = _temperature_f(temperature)

    if temperature_f < -20.0:
        raise ValueError(
            f"Design temperature {temperature_f:.2f}°F is below "
            f"the supported minimum temperature of -20°F."
        )

    for table_temperature in ASME_STRESS_TEMPERATURES_F:

        if temperature_f <= table_temperature:

            return Temperature(
                table_temperature,
                "F",
            )

    raise ValueError(
        f"Design temperature {temperature_f:.2f}°F exceeds "
        f"the available allowable-stress database limit of 800°F."
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

    The stress database is in ksi.

    The selected temperature is always a valid database temperature.
    """

    # ------------------------------------------------------------------------
    # Direct numerical stress support
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

    material_key = normalize_material(material)

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

    # IMPORTANT:
    # This lookup can only use a valid table temperature.
    stress_ksi = asme_material_stress_data[
        material_key
    ][temperature_f]

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
# COMPLETE STRESS DATA
# ============================================================================

def get_stress_data(
    material: Any,
    temperature: Any,
) -> Dict[str, Any]:
    """
    Return complete allowable-stress audit information.
    """

    material_key = normalize_material(material)

    actual_temperature_f = _temperature_f(
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
        "allowable_stress_psi": allowable_stress_ksi * 1000.0,
        "selection_method": "next_higher_temperature_band",
    }


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
        return self.data.get("warnings", [])

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __repr__(self) -> str:
        return repr(self.data)


# ============================================================================
# PRESSURE VESSEL
# ============================================================================

class PressureVessel(CalculationBase):
    """
    Preliminary ASME VIII-1 internal-pressure vessel design.

    Parameters
    ----------
    volume:
        Optional specified vessel volume.

    diameter:
        Internal vessel diameter.

    length:
        Cylindrical tangent-to-tangent length.

    design_pressure:
        Internal design pressure.

    design_temperature:
        Design temperature.

    vessel_type:
        horizontal, vertical or spherical.

    head_type:
        flat, 2:1_ellipsoidal, torispherical,
        hemispherical or conical.

    material:
        ASME material name or ProcessPI alias.

    corrosion_allowance:
        Corrosion allowance.

    joint_efficiency:
        Weld joint efficiency.
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

    @property
    def design_pressure(self) -> Any:

        return self.inputs.get(
            "design_pressure",
            self.inputs.get("pressure"),
        )

    @property
    def diameter(self) -> Any:

        return self.inputs.get(
            "diameter",
            self.inputs.get("inside_diameter"),
        )

    @property
    def length(self) -> Any:

        return self.inputs.get(
            "length",
            self.inputs.get(
                "tangent_to_tangent_length"
            ),
        )

    @property
    def corrosion_allowance(self) -> Any:

        return self.inputs.get(
            "corrosion_allowance",
            Length(0, "mm"),
        )

    @property
    def joint_efficiency(self) -> float:

        return float(
            self.inputs.get(
                "joint_efficiency",
                1.0,
            )
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

        if self.design_pressure is None:

            raise ValueError(
                "design_pressure is required."
            )

        pressure_pa = _pressure_pa(
            self.design_pressure,
            "design_pressure",
        )

        if pressure_pa <= 0:

            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Diameter
        # --------------------------------------------------------------------

        if self.diameter is None:

            raise ValueError(
                "diameter is required."
            )

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        if diameter_m <= 0:

            raise ValueError(
                "diameter must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Length
        # --------------------------------------------------------------------

        if self.vessel_type != "spherical":

            if self.length is None:

                raise ValueError(
                    "length is required for cylindrical vessels."
                )

            length_m = _length_m(
                self.length,
                "length",
            )

            if length_m <= 0:

                raise ValueError(
                    "length must be greater than zero."
                )

        # --------------------------------------------------------------------
        # Joint efficiency
        # --------------------------------------------------------------------

        if not 0 < self.joint_efficiency <= 1:

            raise ValueError(
                "joint_efficiency must be greater than zero "
                "and less than or equal to 1."
            )

        # --------------------------------------------------------------------
        # Corrosion allowance
        # --------------------------------------------------------------------

        corrosion_m = _length_m(
            self.corrosion_allowance,
            "corrosion_allowance",
        )

        if corrosion_m < 0:

            raise ValueError(
                "corrosion_allowance cannot be negative."
            )

        # --------------------------------------------------------------------
        # Material
        # --------------------------------------------------------------------

        normalize_material(
            self.material_input
        )

        # --------------------------------------------------------------------
        # Head
        # --------------------------------------------------------------------

        normalize_head_type(
            self.head_type_input
        )

        # --------------------------------------------------------------------
        # Stress
        # --------------------------------------------------------------------

        get_allowable_stress(
            self.material,
            self.design_temperature,
        )

        # --------------------------------------------------------------------
        # Specified volume
        # --------------------------------------------------------------------

        if "volume" in inputs:

            if inputs["volume"] is not None:

                volume_m3 = _volume_m3(
                    inputs["volume"],
                    "volume",
                )

                if volume_m3 <= 0:

                    raise ValueError(
                        "volume must be greater than zero."
                    )

    # ========================================================================
    # STRESS
    # ========================================================================

    def allowable_stress(self) -> Pressure:

        return get_allowable_stress(
            self.material,
            self.design_temperature,
        )

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

        ASME VIII-1 UG-27(c)(1):

            t = P R / (S E - 0.6 P)

        where:

            P = design pressure
            R = inside radius
            S = allowable stress
            E = joint efficiency
        """

        pressure_pa = _pressure_pa(
            self.design_pressure,
            "design_pressure",
        )

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        radius_m = diameter_m / 2.0

        allowable_pa = _value(
            self.allowable_stress(),
            "allowable stress",
            "Pa",
        )

        efficiency = self.joint_efficiency

        denominator = (
            allowable_pa * efficiency
            - 0.6 * pressure_pa
        )

        if denominator <= 0:

            raise ValueError(
                "Invalid shell-thickness calculation: "
                "S*E - 0.6P must be greater than zero."
            )

        thickness_m = (
            pressure_pa * radius_m
            / denominator
        )

        return Length(
            thickness_m,
            "m",
        )

    # ========================================================================
    # HEAD THICKNESS
    # ========================================================================

    def head_thickness(self) -> Length:
        """
        Preliminary head thickness.

        The implementation uses simplified preliminary relationships
        appropriate for early-stage sizing.

        Final code design must use the applicable ASME VIII-1
        head-specific equations and geometry parameters.
        """

        pressure_pa = _pressure_pa(
            self.design_pressure,
            "design_pressure",
        )

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        allowable_pa = _value(
            self.allowable_stress(),
            "allowable stress",
            "Pa",
        )

        efficiency = self.joint_efficiency

        head_type = self.head_type

        if head_type == "flat":

            # Simplified preliminary flat-head relation.
            #
            # This is deliberately conservative for preliminary sizing.
            coefficient = 0.30

            thickness_m = (
                diameter_m
                * sqrt(
                    pressure_pa
                    / (
                        allowable_pa
                        * efficiency
                    )
                )
                * coefficient
            )

        elif head_type == "ellipsoidal":

            # 2:1 ellipsoidal preliminary relation.
            #
            # Equivalent simplified ASME-style pressure relation:
            #
            # t ≈ P D / (2 S E - 0.2P)

            denominator = (
                2.0
                * allowable_pa
                * efficiency
                - 0.2 * pressure_pa
            )

            if denominator <= 0:

                raise ValueError(
                    "Invalid ellipsoidal-head calculation."
                )

            thickness_m = (
                pressure_pa
                * diameter_m
                / denominator
            )

        elif head_type == "hemispherical":

            denominator = (
                4.0
                * allowable_pa
                * efficiency
                - 0.4 * pressure_pa
            )

            if denominator <= 0:

                raise ValueError(
                    "Invalid hemispherical-head calculation."
                )

            thickness_m = (
                pressure_pa
                * diameter_m
                / denominator
            )

        elif head_type == "torispherical":

            # Preliminary approximation using a standard
            # ASME-style geometry factor.

            geometry_factor = 1.77

            denominator = (
                allowable_pa
                * efficiency
                - 0.1 * pressure_pa
            )

            if denominator <= 0:

                raise ValueError(
                    "Invalid torispherical-head calculation."
                )

            thickness_m = (
                geometry_factor
                * pressure_pa
                * diameter_m
                / (
                    4.0
                    * denominator
                )
            )

        elif head_type == "conical":

            # Preliminary conical-head approximation.

            denominator = (
                2.0
                * allowable_pa
                * efficiency
                - 0.2 * pressure_pa
            )

            if denominator <= 0:

                raise ValueError(
                    "Invalid conical-head calculation."
                )

            thickness_m = (
                pressure_pa
                * diameter_m
                / denominator
            )

        else:

            raise ValueError(
                f"Unsupported head type: {head_type}"
            )

        return Length(
            thickness_m,
            "m",
        )

    # ========================================================================
    # REQUIRED THICKNESS
    # ========================================================================

    def required_thickness(self) -> Dict[str, Length]:

        shell_t = self.shell_thickness()

        head_t = self.head_thickness()

        corrosion_m = _length_m(
            self.corrosion_allowance,
            "corrosion_allowance",
        )

        shell_required = Length(
            shell_t.value + corrosion_m,
            "m",
        )

        head_required = Length(
            head_t.value + corrosion_m,
            "m",
        )

        governing = max(
            shell_required.value,
            head_required.value,
        )

        return {
            "shell": shell_required,
            "head": head_required,
            "governing": Length(
                governing,
                "m",
            ),
        }

    # ========================================================================
    # STANDARD THICKNESS SELECTION
    # ========================================================================

    def selected_thickness(self) -> Length:

        required = self.required_thickness()

        required_mm = _length_m(
            required["governing"],
            "governing thickness",
        ) * 1000.0

        for standard_mm in self.STANDARD_THICKNESSES_MM:

            if standard_mm >= required_mm:

                return Length(
                    standard_mm,
                    "mm",
                )

        raise ValueError(
            f"Required thickness {required_mm:.2f} mm exceeds "
            f"the available standard thickness range."
        )

    # ========================================================================
    # HEAD DEPTH
    # ========================================================================

    def head_depth(self) -> float:
        """
        Approximate internal head depth in metres.
        """

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        if self.head_type == "flat":
            return 0.0

        if self.head_type == "ellipsoidal":
            return diameter_m / 4.0

        if self.head_type == "hemispherical":
            return diameter_m / 2.0

        if self.head_type == "torispherical":
            return diameter_m / 4.0

        if self.head_type == "conical":
            return diameter_m / 2.0

        return 0.0

    # ========================================================================
    # HEAD VOLUME
    # ========================================================================

    def head_volume(self) -> float:
        """
        Approximate volume of one head in m³.
        """

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        radius_m = diameter_m / 2.0

        if self.head_type == "flat":
            return 0.0

        if self.head_type == "hemispherical":

            return (
                2.0
                * pi
                * radius_m**3
                / 3.0
            )

        if self.head_type == "ellipsoidal":

            # One half of an ellipsoid with
            # semi-axis depth = D/4.

            depth_m = diameter_m / 4.0

            return (
                2.0
                * pi
                * radius_m**2
                * depth_m
                / 3.0
            )

        if self.head_type == "torispherical":

            # Preliminary approximation.

            depth_m = diameter_m / 4.0

            return (
                pi
                * radius_m**2
                * depth_m
                * 0.75
            )

        if self.head_type == "conical":

            depth_m = diameter_m / 2.0

            return (
                pi
                * radius_m**2
                * depth_m
                / 3.0
            )

        return 0.0

    # ========================================================================
    # INTERNAL VOLUME
    # ========================================================================

    def calculated_volume(self) -> Volume:
        """
        Calculate internal vessel volume from geometry.

        For horizontal / vertical cylindrical vessels:

            V = cylindrical volume + two heads

        For spherical vessels:

            V = sphere volume
        """

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        radius_m = diameter_m / 2.0

        if self.vessel_type == "spherical":

            volume_m3 = (
                4.0
                * pi
                * radius_m**3
                / 3.0
            )

            return Volume(
                volume_m3,
                "m3",
            )

        length_m = _length_m(
            self.length,
            "length",
        )

        cylindrical_volume = (
            pi
            * radius_m**2
            * length_m
        )

        total_volume = (
            cylindrical_volume
            + 2.0 * self.head_volume()
        )

        return Volume(
            total_volume,
            "m3",
        )

    # ========================================================================
    # SPECIFIED VOLUME
    # ========================================================================

    def specified_volume(self) -> Optional[Volume]:

        if (
            "volume" not in self.inputs
            or self.inputs["volume"] is None
        ):
            return None

        return self.inputs["volume"]

    # ========================================================================
    # VOLUME CHECK
    # ========================================================================

    def volume_check(self) -> Dict[str, Any]:
        """
        Compare specified vessel volume with geometry-derived volume.

        The check is informational and does not modify vessel dimensions.
        """

        calculated = self.calculated_volume()

        specified = self.specified_volume()

        calculated_m3 = _volume_m3(
            calculated,
            "calculated volume",
        )

        if specified is None:

            return {
                "specified_volume": None,
                "calculated_volume": calculated,
                "volume_difference_m3": None,
                "volume_difference_percent": None,
                "volume_check": "not_requested",
            }

        specified_m3 = _volume_m3(
            specified,
            "specified volume",
        )

        difference_m3 = (
            calculated_m3
            - specified_m3
        )

        if specified_m3 != 0:

            difference_percent = (
                difference_m3
                / specified_m3
                * 100.0
            )

        else:

            difference_percent = 0.0

        # Preliminary engineering tolerance.
        tolerance_percent = 5.0

        if abs(difference_percent) <= tolerance_percent:

            status = "PASS"

        else:

            status = "WARNING"

        return {
            "specified_volume": specified,
            "calculated_volume": calculated,
            "volume_difference_m3": difference_m3,
            "volume_difference_percent": difference_percent,
            "volume_tolerance_percent": tolerance_percent,
            "volume_check": status,
        }

    # ========================================================================
    # EXTERNAL AREA
    # ========================================================================

    def external_area(self) -> Area:
        """
        Approximate external surface area.
        """

        diameter_m = _diameter_m(
            self.diameter,
            "diameter",
        )

        radius_m = diameter_m / 2.0

        if self.vessel_type == "spherical":

            area_m2 = (
                4.0
                * pi
                * radius_m**2
            )

            return Area(
                area_m2,
                "m2",
            )

        length_m = _length_m(
            self.length,
            "length",
        )

        shell_area = (
            pi
            * diameter_m
            * length_m
        )

        if self.head_type == "hemispherical":

            head_area = (
                2.0
                * 2.0
                * pi
                * radius_m**2
            )

        elif self.head_type == "ellipsoidal":

            # Preliminary approximation.

            head_area = (
                2.0
                * pi
                * radius_m**2
                * 1.15
            )

        elif self.head_type == "torispherical":

            head_area = (
                2.0
                * pi
                * radius_m**2
                * 1.20
            )

        elif self.head_type == "conical":

            slant = sqrt(
                radius_m**2
                + self.head_depth()**2
            )

            head_area = (
                2.0
                * pi
                * radius_m
                * slant
            )

        else:

            head_area = 0.0

        return Area(
            shell_area + head_area,
            "m2",
        )

    # ========================================================================
    # ESTIMATED WEIGHT
    # ========================================================================

    def estimated_weight(self) -> float:
        """
        Preliminary steel weight estimation.

        Density:
            7850 kg/m³

        The selected nominal thickness is applied to the
        approximate external area.
        """

        area_m2 = _value(
            self.external_area(),
            "external area",
            "m2",
        )

        thickness_m = _length_m(
            self.selected_thickness(),
            "selected thickness",
        )

        density_kg_m3 = 7850.0

        return (
            area_m2
            * thickness_m
            * density_kg_m3
        )

    # ========================================================================
    # HYDROTEST
    # ========================================================================

    def hydrotest_pressure(self) -> Pressure:
        """
        Preliminary hydrotest pressure.

        Uses:

            P_test = 1.3 × MAWP/design pressure

        This is a preliminary value only.

        Final hydrostatic test pressure must be established using
        the applicable ASME VIII-1 UG-99 requirements and material
        stress ratio limitations.
        """

        design_pressure_pa = _pressure_pa(
            self.design_pressure,
            "design_pressure",
        )

        return Pressure(
            design_pressure_pa * 1.30,
            "Pa",
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
        Register a nozzle.

        Nozzle reinforcement calculation is intentionally not performed.
        """

        if not name:
            raise ValueError(
                "Nozzle name cannot be empty."
            )

        diameter_m = _diameter_m(
            diameter,
            f"nozzle {name} diameter",
        )

        if diameter_m <= 0:
            raise ValueError(
                f"Nozzle {name} diameter must be greater than zero."
            )

        if name in self.nozzles:
            raise ValueError(
                f"Nozzle '{name}' already exists."
            )

        self.nozzles[name] = {
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
        Register a manhole.

        Manhole reinforcement calculation is intentionally not performed.
        """

        if not name:
            raise ValueError(
                "Manhole name cannot be empty."
            )

        diameter_m = _diameter_m(
            diameter,
            f"manhole {name} diameter",
        )

        if diameter_m <= 0:
            raise ValueError(
                f"Manhole {name} diameter must be greater than zero."
            )

        if name in self.manholes:
            raise ValueError(
                f"Manhole '{name}' already exists."
            )

        self.manholes[name] = {
            "diameter": Diameter(
                diameter_m,
                "m",
            ),
            **kwargs,
        }

    # ========================================================================
    # DESIGN
    # ========================================================================

    def design(self) -> Dict[str, Any]:
        """
        Execute the complete preliminary pressure-vessel design.

        Returns
        -------
        dict
            Expanded auditable result dictionary.
        """

        # Revalidate explicitly before calculation.
        self.validate_inputs()

        # --------------------------------------------------------------------
        # Basic information
        # --------------------------------------------------------------------

        stress = self.stress_data()

        required = self.required_thickness()

        selected = self.selected_thickness()

        volume_data = self.volume_check()

        calculated_volume = self.calculated_volume()

        # --------------------------------------------------------------------
        # Thickness values
        # --------------------------------------------------------------------

        shell_required_m = _length_m(
            required["shell"],
            "shell required thickness",
        )

        head_required_m = _length_m(
            required["head"],
            "head required thickness",
        )

        governing_required_m = _length_m(
            required["governing"],
            "governing required thickness",
        )

        selected_mm = _length_m(
            selected,
            "selected thickness",
        ) * 1000.0

        # --------------------------------------------------------------------
        # Geometry
        # --------------------------------------------------------------------

        specified_volume = self.specified_volume()

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
            "supports, wind, seismic, fatigue, MDMT, PWHT and flanges "
            "are not evaluated.",

            "Nozzle and manhole reinforcement calculations are not included.",

            "Head equations are preliminary sizing relationships and "
            "must be verified against the applicable ASME VIII-1 "
            "head-specific requirements.",

            "Hydrotest pressure is preliminary and must be verified "
            "against ASME VIII-1 UG-99 and applicable stress-ratio limits.",
        ]

        if volume_data["volume_check"] == "WARNING":

            warnings.append(
                "Specified vessel volume and geometry-derived volume "
                "differ by more than the preliminary 5% tolerance."
            )

        # --------------------------------------------------------------------
        # Final result
        # --------------------------------------------------------------------

        result: Dict[str, Any] = {

            # ================================================================
            # DESIGN BASIS
            # ================================================================

            "design_basis": (
                "ASME VIII-1 preliminary: "
                "UG-27(c)(1), UG-32, UG-34, UG-99(b)"
            ),

            # ================================================================
            # INPUTS
            # ================================================================

            "vessel_type": self.vessel_type,

            "head_type": self.head_type,

            "head_type_input": self.head_type_input,

            "material": self.material,

            "material_input": self.material_input,

            "design_pressure": self.design_pressure,

            "design_temperature": self.design_temperature,

            "joint_efficiency": self.joint_efficiency,

            "corrosion_allowance": self.corrosion_allowance,

            # ================================================================
            # STRESS DATA
            # ================================================================

            "design_temperature_f": stress[
                "temperature_actual_f"
            ],

            "allowable_stress_temperature_band": stress[
                "temperature_table_band"
            ],

            "allowable_stress_temperature_band_f": stress[
                "temperature_table_band_f"
            ],

            "allowable_stress": Pressure(
                stress["allowable_stress_psi"],
                "psi",
            ),

            "allowable_stress_ksi": stress[
                "allowable_stress_ksi"
            ],

            "stress_selection_method": stress[
                "selection_method"
            ],

            # ================================================================
            # THICKNESS
            # ================================================================

            "shell_required_thickness": required[
                "shell"
            ],

            "head_required_thickness": required[
                "head"
            ],

            "governing_required_thickness": required[
                "governing"
            ],

            "shell_required_thickness_mm": (
                shell_required_m * 1000.0
            ),

            "head_required_thickness_mm": (
                head_required_m * 1000.0
            ),

            "governing_required_thickness_mm": (
                governing_required_m * 1000.0
            ),

            "selected_thickness": selected,

            "selected_thickness_mm": selected_mm,

            # ================================================================
            # VOLUME
            # ================================================================

            "specified_volume": specified_volume,

            "calculated_volume": calculated_volume,

            "internal_volume": calculated_volume,

            "volume_difference_m3": volume_data[
                "volume_difference_m3"
            ],

            "volume_difference_percent": volume_data[
                "volume_difference_percent"
            ],

            "volume_tolerance_percent": volume_data[
                "volume_tolerance_percent"
            ],

            "volume_check": volume_data[
                "volume_check"
            ],

            # ================================================================
            # GEOMETRY
            # ================================================================

            "head_depth": Length(
                self.head_depth(),
                "m",
            ),

            "external_area": self.external_area(),

            # ================================================================
            # WEIGHT
            # ================================================================

            "estimated_weight_kg": self.estimated_weight(),

            # ================================================================
            # HYDROTEST
            # ================================================================

            "hydrotest_pressure": self.hydrotest_pressure(),

            # ================================================================
            # OPENINGS
            # ================================================================

            "nozzles": self.nozzles.copy(),

            "manholes": self.manholes.copy(),

            # ================================================================
            # WARNINGS
            # ================================================================

            "warnings": warnings,
        }

        return result


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================

__all__ = [
    "PressureVessel",
    "PressureVesselResults",
    "asme_material_stress_data",
    "MATERIAL_ALIASES",
    "ASME_STRESS_TEMPERATURES_F",
    "normalize_material",
    "normalize_head_type",
    "set_temperature_range",
    "get_allowable_stress",
    "get_stress_data",
]
