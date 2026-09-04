"""
ProcessPI Pressure Vessel Module
================================

Preliminary pressure-vessel design based on ASME Section VIII Division 1
internal-pressure equations.

This module provides:

    - Temperature-specific allowable-stress lookup
    - Material aliases
    - Cylindrical shell sizing
    - Pressure-head sizing
    - Standard thickness selection
    - Vessel volume calculation
    - Volume adequacy checking
    - Nozzle registration
    - Manhole registration
    - Hydrotest pressure
    - Approximate vessel weight
    - Expanded design results

IMPORTANT
---------
This is a preliminary engineering calculation module.

The supplied allowable-stress database is a preliminary data set and must
be verified against the applicable ASME Section II, Part D tables before
code-stamped design, fabrication, or certification.

The module does NOT perform:

    - External-pressure / vacuum design
    - Complete nozzle reinforcement calculations
    - Flange design
    - Saddle/support design
    - Wind/seismic calculations
    - Fatigue analysis
    - MDMT determination
    - PWHT assessment
    - Detailed UG-28 external-pressure calculations
    - Full ASME fabrication/code compliance
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, pi, sqrt
from typing import Any, Dict, List, Mapping, Optional

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
# ASME PRELIMINARY ALLOWABLE STRESS DATABASE
# ============================================================================
#
# Values are in ksi.
#
# Temperature keys are Fahrenheit.
#
# These are the values supplied for the ProcessPI pressure-vessel module.
#
# DO NOT silently substitute another database.
# Verify against the applicable ASME Section II, Part D tables before
# engineering release.
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
# TEMPERATURE BANDS
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


def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from a ProcessPI unit object or plain number.

    Parameters
    ----------
    value:
        ProcessPI unit object or numeric value.

    name:
        Name used in error messages.

    unit:
        Desired unit for conversion.
    """

    if value is None:
        raise ValueError(f"{name} is required")

    if hasattr(value, "to") and unit:
        value = value.to(unit)

    # ProcessPI unit implementations may expose either ``value`` or
    # ``original_value`` after conversion.
    if hasattr(value, "original_value"):
        raw = value.original_value
    else:
        raw = getattr(value, "value", value)

    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value"
        ) from exc


def set_temperature_range(temperature: Any) -> Temperature:
    """
    Select the conservative ASME stress-temperature band.

    Examples
    --------
    95 F  -> 100 F
    150 F -> 200 F
    250 F -> 300 F
    302 F -> 400 F
    450 F -> 500 F

    The next higher tabulated temperature is selected so that a temperature
    between table points does not accidentally use a higher allowable stress.

    Temperatures above 800 F are rejected.
    """

    fahrenheit = _value(
        temperature,
        "temperature",
        "F",
    )

    if fahrenheit <= 100:
        return Temperature(100, "F")

    if fahrenheit <= 200:
        return Temperature(200, "F")

    if fahrenheit <= 300:
        return Temperature(300, "F")

    if fahrenheit <= 400:
        return Temperature(400, "F")

    if fahrenheit <= 500:
        return Temperature(500, "F")

    if fahrenheit <= 600:
        return Temperature(600, "F")

    if fahrenheit <= 700:
        return Temperature(700, "F")

    if fahrenheit <= 800:
        return Temperature(800, "F")

    raise ValueError(
        "Design temperature exceeds the available allowable-stress "
        "database. Maximum supported temperature is 800°F."
    )


# ============================================================================
# MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES: Dict[str, str] = {

    "sa515-55": "SA515-55",
    "sa515-70": "SA515-70",

    "sa516-55": "SA516-55",
    "sa516-70": "SA516-70",
    "sa-516-70": "SA516-70",

    "sa256-a": "SA256-A",

    "sa285-b": "SA285-B",
    "sa285-c": "SA285-C",

    "sa202-a": "SA202-A",
    "sa202-b": "SA202-B",

    "sa387-d": "SA387-D",

    "sa240-304": "SA240-304",
    "sa240-304l": "SA240-304L",
    "sa240-309s": "SA240-309S",
    "sa240-310": "SA240-310",
    "sa240-316": "SA240-316",
    "sa240-316l": "SA240-316L",
    "sa240-317l": "SA240-317L",
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

    # ------------------------------------------------------------------------
    # Existing ProcessPI generic names
    # ------------------------------------------------------------------------

    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "carbon-steel": "SA516-70",

    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",
    "stainless-304": "SA240-304",

    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
    "stainless-316": "SA240-316",
}


def normalize_material(material: Any) -> str:
    """
    Normalize material input to an ASME stress-database key.
    """

    if material is None:
        material = "carbon_steel"

    key = str(material).strip()

    # Exact lookup
    if key in asme_material_stress_data:
        return key

    # Alias lookup
    alias_key = key.lower()

    if alias_key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[alias_key]

    # Case-insensitive direct lookup
    for material_name in asme_material_stress_data:

        if material_name.lower() == alias_key:
            return material_name

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
    Return allowable stress as a ProcessPI Pressure object in psi.

    The database values are in ksi.

    A numerical ``material`` is interpreted as an explicit allowable stress
    in ksi.

    Temperature selection is conservative and uses the next higher
    temperature band.
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
    # Material normalization
    # ------------------------------------------------------------------------

    material_key = normalize_material(material)

    # ------------------------------------------------------------------------
    # Temperature band
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
    # IMPORTANT:
    #
    # Never directly index the table using the actual converted temperature.
    #
    # For example:
    #
    # 150 C -> 302 F
    #
    # must NOT result in:
    #
    #     data["SA516-70"][302]
    #
    # Instead:
    #
    #     302 F -> 400 F band
    #
    # ------------------------------------------------------------------------

    temp_dict = asme_material_stress_data[material_key]

    if temperature_f not in temp_dict:
        raise ValueError(
            f"No allowable-stress data is available for material "
            f"{material_key!r} at temperature band "
            f"{temperature_f}°F."
        )

    stress_ksi = float(
        temp_dict[temperature_f]
    )

    if stress_ksi <= 0:
        raise ValueError(
            f"No allowable stress is available for material "
            f"{material_key!r} at {temperature_f}°F."
        )

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
    Structured result object for pressure-vessel calculations.
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

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.data.get(
            key,
            default,
        )

    def __repr__(self) -> str:
        return repr(self.data)


# ============================================================================
# PRESSURE VESSEL
# ============================================================================

class PressureVessel(CalculationBase):
    """
    Preliminary ASME VIII-1 pressure-vessel design class.

    Plain numeric inputs are interpreted as:

        pressure  -> Pa
        diameter  -> m
        length    -> m
        volume    -> m³
        temperature -> °C

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
        60,
        65,
        70,
        75,
        80,
        90,
        100,
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

        super().__init__(
            **kwargs
        )

        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def validate_inputs(self) -> None:

        inputs = self.inputs

        # --------------------------------------------------------------------
        # Vessel type
        # --------------------------------------------------------------------

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
                f"vessel_type must be one of "
                f"{sorted(self._TYPES)}"
            )

        # --------------------------------------------------------------------
        # Pressure
        # --------------------------------------------------------------------

        pressure = inputs.get(
            "design_pressure",
            inputs.get(
                "pressure"
            ),
        )

        if pressure is None:

            raise ValueError(
                "design_pressure is required."
            )

        if _value(
            pressure,
            "design_pressure",
            "Pa",
        ) <= 0:

            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # --------------------------------------------------------------------
        # Diameter
        # --------------------------------------------------------------------

        diameter = inputs.get(
            "diameter",
            inputs.get(
                "inside_diameter"
            ),
        )

        if diameter is None:

            raise ValueError(
                "diameter is required."
            )

        if _value(
            diameter,
            "diameter",
            "m",
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
                    "length is required for cylindrical vessels."
                )

            if _value(
                length,
                "length",
                "m",
            ) <= 0:

                raise ValueError(
                    "length must be greater than zero."
                )

        # --------------------------------------------------------------------
        # Temperature
        # --------------------------------------------------------------------

        temperature = inputs.get(
            "design_temperature",
            Temperature(20, "C"),
        )

        # Validate that the temperature can be converted and is within
        # the available stress database.
        set_temperature_range(
            temperature
        )

        # --------------------------------------------------------------------
        # Material
        # --------------------------------------------------------------------

        normalize_material(
            inputs.get(
                "material",
                "carbon_steel",
            )
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
                "joint_efficiency must be greater than zero "
                "and no more than one."
            )

        # --------------------------------------------------------------------
        # Corrosion allowance
        # --------------------------------------------------------------------

        corrosion_allowance = inputs.get(
            "corrosion_allowance",
            Length(0, "mm"),
        )

        if _value(
            corrosion_allowance,
            "corrosion_allowance",
            "m",
        ) < 0:

            raise ValueError(
                "corrosion_allowance must be non-negative."
            )

        # --------------------------------------------------------------------
        # Head type
        # --------------------------------------------------------------------

        head_type = str(
            inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).lower()

        normalized_head = (
            head_type
            .replace(
                "2:1_",
                "",
            )
            .replace(
                "2:1 ",
                "",
            )
        )

        if normalized_head not in self._HEADS:

            raise ValueError(
                f"head_type must be one of "
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
    def material(self) -> str:

        return normalize_material(
            self.inputs.get(
                "material",
                "carbon_steel",
            )
        )

    @property
    def design_temperature(self) -> Temperature:

        return self.inputs.get(
            "design_temperature",
            Temperature(20, "C"),
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
    # NOZZLES
    # ========================================================================

    def add_nozzle(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:

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
    # MANHOLES
    # ========================================================================

    def add_manhole(
        self,
        name: str,
        diameter: Any,
        **details: Any,
    ) -> None:

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
    # SHELL THICKNESS
    # ========================================================================

    def shell_thickness(self) -> Length:
        """
        Preliminary cylindrical shell thickness.

        ASME VIII-1 UG-27(c)(1):

            t = P R / (S E - 0.6 P)

        Corrosion allowance is added after pressure sizing.
        """

        pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get(
                    "pressure"
                ),
            ),
            "design_pressure",
            "Pa",
        )

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

        denominator = (
            allowable_stress
            * joint_efficiency
            - 0.6
            * pressure
        )

        if denominator <= 0:

            raise ValueError(
                "Invalid pressure/stress combination: "
                "S*E - 0.6P must be greater than zero."
            )

        pressure_thickness = (
            pressure
            * radius
            / denominator
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        total_thickness = (
            pressure_thickness
            + corrosion_allowance
        )

        return Length(
            total_thickness,
            "m",
        )

    # ========================================================================
    # HEAD THICKNESS
    # ========================================================================

    def head_thickness(self) -> Length:
        """
        Preliminary pressure-head thickness.

        The implementation uses head-type factors for preliminary sizing.

        This is NOT a replacement for detailed ASME UG-32/UG-34 design
        calculations for a fabricated pressure head.
        """

        pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get(
                    "pressure"
                ),
            ),
            "design_pressure",
            "Pa",
        )

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

        head_type = str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).lower()

        head_type = (
            head_type
            .replace(
                "2:1_",
                "",
            )
            .replace(
                "2:1 ",
                "",
            )
        )

        if head_type not in self._HEADS:

            raise ValueError(
                f"head_type must be one of "
                f"{sorted(self._HEADS)}"
            )

        # --------------------------------------------------------------------
        # Preliminary geometry factors
        # --------------------------------------------------------------------

        factors = {

            # Flat head
            "flat": 0.50,

            # 2:1 ellipsoidal head
            "ellipsoidal": 0.25,

            # Preliminary torispherical factor
            "torispherical": 0.885,

            # Hemispherical
            "hemispherical": 0.125,

            # Preliminary conical
            "conical": 0.50,
        }

        factor = factors[head_type]

        denominator = (
            allowable_stress
            * joint_efficiency
        )

        if denominator <= 0:

            raise ValueError(
                "Invalid allowable stress/joint efficiency."
            )

        pressure_thickness = (
            factor
            * pressure
            * diameter
            / denominator
        )

        corrosion_allowance = _value(
            self.inputs.get(
                "corrosion_allowance",
                Length(0, "mm"),
            ),
            "corrosion_allowance",
            "m",
        )

        total_thickness = (
            pressure_thickness
            + corrosion_allowance
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

        # If requirement exceeds the predefined table, retain the calculated
        # requirement instead of silently selecting an undersized thickness.
        return Length(
            required_mm,
            "mm",
        )

    # ========================================================================
    # HEAD VOLUME
    # ========================================================================

    def _head_volume(
        self,
        radius: float,
    ) -> float:
        """
        Approximate volume of one vessel head.

        Values are preliminary geometric approximations.
        """

        head = str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).lower()

        head = (
            head
            .replace(
                "2:1_",
                "",
            )
            .replace(
                "2:1 ",
                "",
            )
        )

        factors = {

            "flat": 0.0,

            # One 2:1 ellipsoidal head
            "ellipsoidal": 2.0 / 3.0,

            "torispherical": 0.5,

            "hemispherical": 4.0 / 3.0,

            "conical": 1.0 / 3.0,
        }

        factor = factors.get(
            head,
            2.0 / 3.0,
        )

        return (
            factor
            * pi
            * radius ** 3
        )

    # ========================================================================
    # VOLUME
    # ========================================================================

    def volume(
        self,
        liquid_level: Any = None,
    ) -> Volume:
        """
        Calculate approximate internal vessel volume.

        For cylindrical vessels:

            cylindrical volume
            +
            two head volumes

        For spherical vessels:

            sphere volume

        ``liquid_level`` is supported for cylindrical horizontal vessels.
        """

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

        # --------------------------------------------------------------------
        # Spherical vessel
        # --------------------------------------------------------------------

        if self.vessel_type == "spherical":

            full_volume = (
                4.0
                / 3.0
                * pi
                * radius ** 3
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

            h = level

            segment_volume = (
                pi
                * h ** 2
                * (radius - h / 3.0)
            )

            return Volume(
                segment_volume,
                "m3",
            )

        # --------------------------------------------------------------------
        # Cylindrical vessel
        # --------------------------------------------------------------------

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
            * radius ** 2
            * length
        )

        head_volume = (
            2.0
            * self._head_volume(radius)
        )

        full_volume = (
            cylindrical_volume
            + head_volume
        )

        # --------------------------------------------------------------------
        # Full vessel
        # --------------------------------------------------------------------

        if liquid_level is None:

            return Volume(
                full_volume,
                "m3",
            )

        # --------------------------------------------------------------------
        # Horizontal liquid-level approximation
        # --------------------------------------------------------------------

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

        # Circular segment area
        segment_area = (
            radius ** 2
            * acos(
                (radius - level) / radius
            )
            -
            (radius - level)
            * sqrt(
                max(
                    0.0,
                    2.0 * radius * level
                    - level ** 2,
                )
            )
        )

        liquid_fraction = (
            segment_area
            / (
                pi
                * radius ** 2
            )
        )

        liquid_volume = (
            full_volume
            * liquid_fraction
        )

        return Volume(
            liquid_volume,
            "m3",
        )

    # ========================================================================
    # EXTERNAL AREA
    # ========================================================================

    def _external_area(
        self,
        diameter: float,
        length: float,
    ) -> float:

        radius = diameter / 2.0

        if self.vessel_type == "spherical":

            return (
                4.0
                * pi
                * radius ** 2
            )

        shell_area = (
            pi
            * diameter
            * length
        )

        head_area = (
            2.0
            * pi
            * radius ** 2
        )

        return (
            shell_area
            + head_area
        )

    # ========================================================================
    # DESIGN
    # ========================================================================

    def design(self) -> Dict[str, Any]:
        """
        Perform preliminary pressure-vessel design.

        Returns
        -------
        dict
            Expanded ProcessPI pressure-vessel result dictionary.
        """

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
        # Material / temperature
        # --------------------------------------------------------------------

        material = self.material

        design_temperature = (
            self.design_temperature
        )

        temperature_band = (
            set_temperature_range(
                design_temperature
            )
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

        # --------------------------------------------------------------------
        # Required shell/head thickness
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
        # Design pressure
        # --------------------------------------------------------------------

        design_pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get(
                    "pressure"
                ),
            ),
            "design_pressure",
            "Pa",
        )

        design_pressure_bar = (
            _value(
                Pressure(
                    design_pressure,
                    "Pa",
                ),
                "design pressure",
                "bar",
            )
        )

        design_pressure_psi = (
            _value(
                Pressure(
                    design_pressure,
                    "Pa",
                ),
                "design pressure",
                "psi",
            )
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

        # --------------------------------------------------------------------
        # Volume
        # --------------------------------------------------------------------

        internal_volume = self.volume()

        internal_volume_m3 = _value(
            internal_volume,
            "internal volume",
            "m3",
        )

        specified_volume = self.inputs.get(
            "volume"
        )

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
        # External area
        # --------------------------------------------------------------------

        external_area = self._external_area(
            diameter,
            length,
        )

        # --------------------------------------------------------------------
        # Weight
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
        # Warnings
        # --------------------------------------------------------------------

        warnings = [

            "Preliminary ASME Section VIII "
            "Division 1 internal-pressure sizing only.",

            "Allowable stresses are taken from the "
            "supplied temperature-specific preliminary "
            "material database.",

            "Verify all material allowable stresses "
            "against the applicable ASME Section II, "
            "Part D tables before code-stamped design "
            "or fabrication.",

            "External pressure/vacuum, complete nozzle "
            "reinforcement, supports, wind, seismic, "
            "fatigue, MDMT, PWHT, and flanges are not "
            "evaluated.",
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

        if selected_thickness_mm > 50:

            warnings.append(
                "Required thickness exceeds the predefined "
                "standard-thickness selection table."
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

            # ---------------------------------------------------------------
            # Basic identification
            # ---------------------------------------------------------------

            "vessel_type": self.vessel_type,

            "head_type": self.inputs.get(
                "head_type",
                "ellipsoidal",
            ),

            "material": material,

            # ---------------------------------------------------------------
            # Design conditions
            # ---------------------------------------------------------------

            "design_pressure": Pressure(
                design_pressure,
                "Pa",
            ),

            "design_pressure_bar": design_pressure_bar,

            "design_pressure_psi": design_pressure_psi,

            "design_temperature": design_temperature,

            "design_temperature_F": Temperature(
                _value(
                    design_temperature,
                    "design temperature",
                    "F",
                ),
                "F",
            ),

            "allowable_stress_temperature_band":
                temperature_band,

            "allowable_stress":
                allowable_stress,

            "allowable_stress_ksi":
                allowable_stress_ksi,

            # ---------------------------------------------------------------
            # Dimensions
            # ---------------------------------------------------------------

            "diameter": Diameter(
                diameter,
                "m",
            ),

            "length": Length(
                length,
                "m",
            ) if self.vessel_type != "spherical"
            else Length(0, "m"),

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

            # ---------------------------------------------------------------
            # Thickness calculations
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
                Volume(
                    volume_margin_m3,
                    "m3",
                )
                if volume_margin_m3 is not None
                else None,

            "volume_margin_percent":
                volume_margin_percent,

            # ---------------------------------------------------------------
            # Area / weight
            # ---------------------------------------------------------------

            "external_area":
                Area(
                    external_area,
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

            # ---------------------------------------------------------------
            # Attachments
            # ---------------------------------------------------------------

            "nozzles":
                self.nozzles.copy(),

            "manholes":
                self.manholes.copy(),

            # ---------------------------------------------------------------
            # Status / warnings
            # ---------------------------------------------------------------

            "warnings":
                warnings,

            "design_basis":
                design_basis,
        }

        return PressureVesselResults(
            result
        ).to_dict()

    # CalculationBase compatibility
    calculate = design


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
    with ellipsoidal/dished ends.
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
# IMPORTANT BACKWARD-COMPATIBILITY ALIAS
# ============================================================================
#
# processpi.equipment.__init__ imports BOTH:
#
#     PressureVessel
#     PressureVessels
#
# Therefore this alias MUST remain present.
#
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
