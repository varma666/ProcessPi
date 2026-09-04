"""
ProcessPI - Pressure Vessel Equipment Module
============================================

Preliminary pressure-vessel sizing based on ASME Section VIII Division 1.

Implemented:
    - Material allowable-stress database
    - Material aliases
    - Temperature-band selection
    - Shell internal-pressure sizing
    - 2:1 ellipsoidal head sizing
    - Corrosion allowance
    - Joint efficiency
    - Vessel volume check
    - Nozzles
    - Manholes
    - Hydrotest pressure
    - Material density
    - Estimated vessel weight
    - Expanded design result dictionary

Important:
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

from typing import Any, Dict, Optional

from processpi.calculations.base import CalculationBase
from processpi.units import (
    Pressure,
    Temperature,
    Length,
    Diameter,
    Volume,
)


# ============================================================================
# ASME PRELIMINARY MATERIAL ALLOWABLE-STRESS DATABASE
# ============================================================================
#
# Temperature keys are in °F.
#
# Stress values are in ksi.
#
# These are the values originally supplied for ProcessPI.
#
# IMPORTANT:
# This is a preliminary application database. Verify against the applicable
# ASME Section II, Part D table before code-stamped design/fabrication.
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
# MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES: Dict[str, str] = {

    # Carbon steels
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "cs": "SA516-70",
    "sa516": "SA516-70",
    "sa516-70": "SA516-70",
    "sa516-55": "SA516-55",
    "sa515-55": "SA515-55",
    "sa515-70": "SA515-70",
    "sa285-b": "SA285-B",
    "sa285-c": "SA285-C",

    # Chrome-moly
    "sa387-d": "SA387-D",

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

    # Nickel / specialty alloys
    "b162": "B162",
    "b127": "B127",
    "b168": "B168",
    "b443": "B443",
    "c22": "C-22 alloy",
    "c-22": "C-22 alloy",
    "c-22 alloy": "C-22 alloy",
    "b575": "B575",
    "b333": "B333",
    "b463": "B463",
    "b409": "B409",
    "b424": "B424",
    "b688": "B688",
    "a240 904": "A240 904",
    "904": "A240 904",
    "904l": "A240 904",
    "g-30": "G-30 Alloy",
    "g-30 alloy": "G-30 Alloy",

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
# SUPPORTED TEMPERATURE BANDS
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

MIN_SUPPORTED_TEMPERATURE_F = -20.0
MAX_SUPPORTED_TEMPERATURE_F = 800.0

# Floating-point tolerance used at boundaries.
TEMPERATURE_TOLERANCE_F = 1.0e-6


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _normalize_material_key(material: Any) -> str:
    """
    Resolve a user material name/alias to the canonical database key.
    """

    if material is None:
        raise ValueError("Material must be specified.")

    material_text = str(material).strip()

    if not material_text:
        raise ValueError("Material must not be empty.")

    # Exact database key first.
    if material_text in asme_material_stress_data:
        return material_text

    # Case-insensitive exact database match.
    lowered = material_text.lower()

    for key in asme_material_stress_data:
        if key.lower() == lowered:
            return key

    # Alias lookup.
    if lowered in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[lowered]

    raise ValueError(
        f"Unsupported material '{material}'. "
        f"Available materials include: "
        f"{', '.join(asme_material_stress_data.keys())}"
    )


def _temperature_to_f(temperature: Temperature) -> float:
    """
    Convert Temperature to Fahrenheit and remove floating-point noise.

    The rounding is important for exact boundaries such as:

        800 C -> 1472 F
        800 F -> 800 F

    and prevents values such as 800.0000000000001 F from being treated
    as being above the 800 F database limit.
    """

    if not isinstance(temperature, Temperature):
        raise TypeError(
            "Design temperature must be a Temperature object."
        )

    temperature_f = float(temperature.to("F").value)

    # Normalize conversion noise.
    temperature_f = round(temperature_f, 6)

    return temperature_f


def set_temperature_range(temperature: Temperature) -> Temperature:
    """
    Select the ASME allowable-stress temperature band.

    The selected band is the first database temperature that is greater
    than or equal to the design temperature.

    Examples:
        302 F -> 400 F
        347 F -> 400 F
        797 F -> 800 F
        800 F -> 800 F

    Temperatures above 800 F are rejected.

    Temperatures below -20 F are rejected.
    """

    temperature_f = _temperature_to_f(temperature)

    if temperature_f < MIN_SUPPORTED_TEMPERATURE_F - TEMPERATURE_TOLERANCE_F:
        raise ValueError(
            "Design temperature is below the available "
            "allowable-stress database range. "
            f"Minimum supported temperature is "
            f"{MIN_SUPPORTED_TEMPERATURE_F:g}°F."
        )

    # IMPORTANT:
    # Use <= band + tolerance so that 800.0000000000001 does not
    # incorrectly fail the 800 F boundary.
    for band in ASME_TEMPERATURE_BANDS:

        if temperature_f <= band + TEMPERATURE_TOLERANCE_F:
            return Temperature(band, "F")

    raise ValueError(
        "Design temperature exceeds the available "
        "allowable-stress database. "
        f"Maximum supported temperature is "
        f"{MAX_SUPPORTED_TEMPERATURE_F:g}°F."
    )


def _get_temperature_band_f(temperature: Temperature) -> int:
    """
    Internal helper returning the selected temperature band as an integer.
    """

    band = set_temperature_range(temperature)

    band_f = round(float(band.to("F").value))

    return int(band_f)


def get_allowable_stress(
    material: Any,
    temperature: Temperature,
) -> Pressure:
    """
    Return allowable stress for material at the selected ASME temperature band.

    Stress database values are stored in ksi.

    Returned Pressure object is in psi.
    """

    material_key = _normalize_material_key(material)

    temperature_f = _temperature_to_f(temperature)

    temperature_band = _get_temperature_band_f(temperature)

    # Explicit upper-bound check.
    if temperature_f > (
        MAX_SUPPORTED_TEMPERATURE_F + TEMPERATURE_TOLERANCE_F
    ):
        raise ValueError(
            "Design temperature exceeds the available "
            "allowable-stress database. "
            f"Maximum supported temperature is "
            f"{MAX_SUPPORTED_TEMPERATURE_F:g}°F."
        )

    stress_table = asme_material_stress_data[material_key]

    if temperature_band not in stress_table:
        raise ValueError(
            f"No allowable stress temperature band is available "
            f"for material '{material_key}' at {temperature_band}°F."
        )

    stress_ksi = float(stress_table[temperature_band])

    # Do not allow a zero/negative allowable stress to enter the
    # pressure-vessel thickness equations.
    if stress_ksi <= 0.0:
        raise ValueError(
            f"No allowable stress is available for material "
            f"'{material_key}' at {temperature_band}°F."
        )

    return Pressure(stress_ksi * 1000.0, "psi")


def get_material_density(material: Any) -> float:
    """
    Return approximate material density in kg/m3.
    """

    material_key = _normalize_material_key(material)

    return MATERIAL_DENSITIES.get(
        material_key,
        7850.0,
    )


def _value_in(unit_object: Any, unit: str) -> float:
    """
    Return a unit object's numeric value after conversion.
    """

    converted = unit_object.to(unit)

    return float(converted.value)


def _pressure_pa(pressure: Pressure) -> float:
    return _value_in(pressure, "Pa")


def _pressure_bar(pressure: Pressure) -> float:
    return _value_in(pressure, "bar")


def _pressure_psi(pressure: Pressure) -> float:
    return _value_in(pressure, "psi")


def _length_m(length: Length) -> float:
    return _value_in(length, "m")


def _diameter_m(diameter: Diameter) -> float:
    return _value_in(diameter, "m")


def _temperature_c(temperature: Temperature) -> float:
    return _value_in(temperature, "C")


def _temperature_f(temperature: Temperature) -> float:
    return _value_in(temperature, "F")


# ============================================================================
# GEOMETRY FUNCTIONS
# ============================================================================

def _cylindrical_volume(
    diameter_m: float,
    length_m: float,
) -> float:
    """
    Cylindrical volume, m3.
    """

    import math

    return (
        math.pi
        * diameter_m ** 2
        / 4.0
        * length_m
    )


def _ellipsoidal_head_volume(
    diameter_m: float,
) -> float:
    """
    Volume of ONE 2:1 ellipsoidal head.

    A 2:1 ellipsoidal head has:
        major diameter = D
        minor/depth axis = D/2

    Full ellipsoid volume:
        pi/6 * D * D * (D/2)

    A vessel head represents half of the ellipsoid:

        pi * D^3 / 24

    Two heads:

        pi * D^3 / 12
    """

    import math

    return math.pi * diameter_m ** 3 / 24.0


def _head_depth_2_to_1(
    diameter_m: float,
) -> float:
    """
    Internal depth of a 2:1 ellipsoidal head.
    """

    return diameter_m / 4.0


def _ellipsoidal_head_area(
    diameter_m: float,
) -> float:
    """
    Approximate wetted/external surface area of ONE 2:1 ellipsoidal head.

    Uses numerical approximation of the half-ellipsoid surface.

    This is intended for preliminary area/weight estimation only.
    """

    import math

    a = diameter_m / 2.0
    b = diameter_m / 2.0
    c = diameter_m / 4.0

    # Parametric surface area of half an oblate/prolate ellipsoid
    # evaluated numerically over the upper half.
    #
    # x = a sin(theta) cos(phi)
    # y = b sin(theta) sin(phi)
    # z = c cos(theta)
    #
    # theta = 0 -> pole
    # theta = pi/2 -> equator

    n = 200
    total = 0.0

    dtheta = (math.pi / 2.0) / n

    for i in range(n):

        theta = (i + 0.5) * dtheta

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        # Surface element after integrating over phi for a=b:
        #
        # |r_theta x r_phi|
        # = a * sin(theta) *
        #   sqrt(c^2 * sin^2(theta) + a^2 * cos^2(theta))
        #
        element = (
            2.0
            * math.pi
            * a
            * sin_theta
            * math.sqrt(
                c ** 2 * sin_theta ** 2
                + a ** 2 * cos_theta ** 2
            )
        )

        total += element * dtheta

    return total


def _vessel_external_area(
    diameter_m: float,
    length_m: float,
    head_type: str,
) -> float:
    """
    Preliminary external surface area, m2.
    """

    import math

    cylindrical_area = (
        math.pi
        * diameter_m
        * length_m
    )

    normalized_head = str(head_type).strip().lower()

    if normalized_head in (
        "2:1_ellipsoidal",
        "2:1 ellipsoidal",
        "ellipsoidal",
        "elliptical",
    ):
        head_area = 2.0 * _ellipsoidal_head_area(diameter_m)

    elif normalized_head in (
        "hemispherical",
        "hemisphere",
    ):
        radius = diameter_m / 2.0

        # Two hemispheres = one complete sphere.
        head_area = 4.0 * math.pi * radius ** 2

    elif normalized_head in (
        "flat",
        "flat_head",
    ):
        head_area = (
            2.0
            * math.pi
            * diameter_m ** 2
            / 4.0
        )

    else:
        raise ValueError(
            f"Unsupported head type '{head_type}'."
        )

    return cylindrical_area + head_area


# ============================================================================
# PRESSURE-VESSEL CLASS
# ============================================================================

class PressureVessel(CalculationBase):
    """
    Preliminary ASME VIII-1 pressure vessel sizing model.
    """

    def __init__(self, **kwargs: Any):

        super().__init__(**kwargs)

        self.nozzles: Dict[str, Dict[str, Any]] = {}
        self.manholes: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------------
    # INPUT VALIDATION
    # ------------------------------------------------------------------------

    def validate_inputs(self) -> None:

        inputs = self.inputs

        required = [
            "volume",
            "diameter",
            "length",
            "design_pressure",
            "design_temperature",
            "vessel_type",
            "head_type",
            "material",
            "corrosion_allowance",
            "joint_efficiency",
        ]

        missing = [
            name
            for name in required
            if name not in inputs
        ]

        if missing:
            raise ValueError(
                "Missing required PressureVessel inputs: "
                + ", ".join(missing)
            )

        # Volume
        volume = inputs["volume"]

        if not isinstance(volume, Volume):
            raise TypeError(
                "volume must be a Volume object."
            )

        if _value_in(volume, "m3") <= 0.0:
            raise ValueError(
                "volume must be greater than zero."
            )

        # Diameter
        diameter = inputs["diameter"]

        if not isinstance(diameter, Diameter):
            raise TypeError(
                "diameter must be a Diameter object."
            )

        diameter_m = _diameter_m(diameter)

        if diameter_m <= 0.0:
            raise ValueError(
                "diameter must be greater than zero."
            )

        # Length
        length = inputs["length"]

        if not isinstance(length, Length):
            raise TypeError(
                "length must be a Length object."
            )

        length_m = _length_m(length)

        if length_m <= 0.0:
            raise ValueError(
                "length must be greater than zero."
            )

        # Design pressure
        pressure = inputs["design_pressure"]

        if not isinstance(pressure, Pressure):
            raise TypeError(
                "design_pressure must be a Pressure object."
            )

        pressure_pa = _pressure_pa(pressure)

        if pressure_pa <= 0.0:
            raise ValueError(
                "design_pressure must be greater than zero."
            )

        # Design temperature
        temperature = inputs["design_temperature"]

        if not isinstance(temperature, Temperature):
            raise TypeError(
                "design_temperature must be a Temperature object."
            )

        # Trigger temperature validation during object construction.
        set_temperature_range(temperature)

        # Material
        material = inputs["material"]

        _normalize_material_key(material)

        # Corrosion allowance
        corrosion_allowance = inputs["corrosion_allowance"]

        if not isinstance(corrosion_allowance, Length):
            raise TypeError(
                "corrosion_allowance must be a Length object."
            )

        ca_m = _length_m(corrosion_allowance)

        if ca_m < 0.0:
            raise ValueError(
                "corrosion_allowance cannot be negative."
            )

        # Joint efficiency
        joint_efficiency = float(
            inputs["joint_efficiency"]
        )

        if not 0.0 < joint_efficiency <= 1.0:
            raise ValueError(
                "joint_efficiency must be > 0 and <= 1."
            )

        # Vessel type
        vessel_type = str(
            inputs["vessel_type"]
        ).strip().lower()

        if vessel_type not in (
            "horizontal",
            "vertical",
        ):
            raise ValueError(
                "vessel_type must be 'horizontal' or 'vertical'."
            )

        # Head type
        head_type = str(
            inputs["head_type"]
        ).strip().lower()

        allowed_heads = {
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
            "hemispherical",
            "hemisphere",
            "flat",
            "flat_head",
        }

        if head_type not in allowed_heads:
            raise ValueError(
                f"Unsupported head_type '{inputs['head_type']}'. "
                "Supported types: "
                "2:1_ellipsoidal, hemispherical, flat."
            )

        # Validate allowable stress now.
        get_allowable_stress(
            material,
            temperature,
        )

    # ------------------------------------------------------------------------
    # NOZZLES
    # ------------------------------------------------------------------------

    def add_nozzle(
        self,
        name: str,
        diameter: Diameter,
        **kwargs: Any,
    ) -> None:
        """
        Add a nozzle to the vessel.

        Note:
            This stores the nozzle geometry for reporting.

            Nozzle reinforcement calculation is currently NOT performed.
        """

        if not name:
            raise ValueError(
                "Nozzle name must not be empty."
            )

        if not isinstance(diameter, Diameter):
            raise TypeError(
                "Nozzle diameter must be a Diameter object."
            )

        if _diameter_m(diameter) <= 0.0:
            raise ValueError(
                "Nozzle diameter must be greater than zero."
            )

        self.nozzles[str(name)] = {
            "diameter": diameter,
            **kwargs,
        }

    # ------------------------------------------------------------------------
    # MANHOLES
    # ------------------------------------------------------------------------

    def add_manhole(
        self,
        name: str,
        diameter: Diameter,
        **kwargs: Any,
    ) -> None:
        """
        Add a manhole to the vessel.

        Note:
            This stores the manhole geometry for reporting.

            Manhole reinforcement calculation is currently NOT performed.
        """

        if not name:
            raise ValueError(
                "Manhole name must not be empty."
            )

        if not isinstance(diameter, Diameter):
            raise TypeError(
                "Manhole diameter must be a Diameter object."
            )

        if _diameter_m(diameter) <= 0.0:
            raise ValueError(
                "Manhole diameter must be greater than zero."
            )

        self.manholes[str(name)] = {
            "diameter": diameter,
            **kwargs,
        }

    # ------------------------------------------------------------------------
    # SHELL THICKNESS
    # ------------------------------------------------------------------------

    def _calculate_shell_thickness(
        self,
        pressure_pa: float,
        diameter_m: float,
        allowable_stress_pa: float,
        joint_efficiency: float,
        corrosion_allowance_m: float,
    ) -> float:
        """
        Cylindrical shell internal-pressure thickness.

        ASME VIII-1 UG-27(c)(1) preliminary form:

            t = PR / (SE - 0.6P)

        where:

            P  = internal design pressure
            R  = inside radius
            S  = allowable stress
            E  = joint efficiency

        Corrosion allowance is then added.
        """

        radius_m = diameter_m / 2.0

        denominator = (
            allowable_stress_pa
            * joint_efficiency
            - 0.6 * pressure_pa
        )

        if denominator <= 0.0:
            raise ValueError(
                "Shell thickness equation has a non-positive "
                "denominator. Check pressure, allowable stress, "
                "and joint efficiency."
            )

        pressure_thickness = (
            pressure_pa
            * radius_m
            / denominator
        )

        return (
            pressure_thickness
            + corrosion_allowance_m
        )

    # ------------------------------------------------------------------------
    # HEAD THICKNESS
    # ------------------------------------------------------------------------

    def _calculate_head_thickness(
        self,
        pressure_pa: float,
        diameter_m: float,
        allowable_stress_pa: float,
        joint_efficiency: float,
        corrosion_allowance_m: float,
        head_type: str,
    ) -> float:
        """
        Preliminary pressure thickness for vessel heads.

        2:1 ellipsoidal:
            t = PD / (2SE - 0.2P)

        Hemispherical:
            t = PR / (2SE - 0.2P)

        Flat heads:
            A simplified preliminary expression is used here only for
            screening purposes.

        Final head design must be verified against the applicable
        ASME Section VIII formulas and construction details.
        """

        normalized = str(
            head_type
        ).strip().lower()

        radius_m = diameter_m / 2.0

        if normalized in (
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
        ):

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure_pa
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Ellipsoidal-head thickness equation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                pressure_pa
                * diameter_m
                / denominator
            )

        elif normalized in (
            "hemispherical",
            "hemisphere",
        ):

            denominator = (
                2.0
                * allowable_stress_pa
                * joint_efficiency
                - 0.2 * pressure_pa
            )

            if denominator <= 0.0:
                raise ValueError(
                    "Hemispherical-head thickness equation has a "
                    "non-positive denominator."
                )

            pressure_thickness = (
                pressure_pa
                * radius_m
                / denominator
            )

        elif normalized in (
            "flat",
            "flat_head",
        ):

            # Preliminary screening expression only.
            #
            # Flat head design is strongly dependent on geometry,
            # attachment, bending, edge conditions, and construction.
            #
            # This value must NOT be treated as a final code design.

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
                * diameter_m
                * (
                    pressure_pa
                    / denominator
                ) ** 0.5
            )

        else:
            raise ValueError(
                f"Unsupported head type '{head_type}'."
            )

        return (
            pressure_thickness
            + corrosion_allowance_m
        )

    # ------------------------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------------------------

    def _calculate_internal_volume(
        self,
        diameter_m: float,
        length_m: float,
        head_type: str,
    ) -> float:
        """
        Calculate preliminary internal vessel volume.

        For 2:1 ellipsoidal heads:

            V_head,total = pi D^3 / 12

        The supplied length is treated as the cylindrical straight length.
        """

        normalized = str(
            head_type
        ).strip().lower()

        cylinder_volume = _cylindrical_volume(
            diameter_m,
            length_m,
        )

        if normalized in (
            "2:1_ellipsoidal",
            "2:1 ellipsoidal",
            "ellipsoidal",
            "elliptical",
        ):

            head_volume = (
                2.0
                * _ellipsoidal_head_volume(
                    diameter_m
                )
            )

        elif normalized in (
            "hemispherical",
            "hemisphere",
        ):

            import math

            radius = diameter_m / 2.0

            # Two hemispheres = one sphere.
            head_volume = (
                4.0
                / 3.0
                * math.pi
                * radius ** 3
            )

        elif normalized in (
            "flat",
            "flat_head",
        ):

            head_volume = 0.0

        else:
            raise ValueError(
                f"Unsupported head type '{head_type}'."
            )

        return cylinder_volume + head_volume

    # ------------------------------------------------------------------------
    # DESIGN
    # ------------------------------------------------------------------------

    def design(self) -> Dict[str, Any]:
        """
        Perform preliminary pressure-vessel design.
        """

        inputs = self.inputs

        # Revalidate before calculation.
        self.validate_inputs()

        # --------------------------------------------------------------------
        # INPUTS
        # --------------------------------------------------------------------

        specified_volume = _value_in(
            inputs["volume"],
            "m3",
        )

        diameter_m = _diameter_m(
            inputs["diameter"]
        )

        length_m = _length_m(
            inputs["length"]
        )

        design_pressure = inputs[
            "design_pressure"
        ]

        pressure_pa = _pressure_pa(
            design_pressure
        )

        pressure_bar = _pressure_bar(
            design_pressure
        )

        pressure_psi = _pressure_psi(
            design_pressure
        )

        design_temperature = inputs[
            "design_temperature"
        ]

        temperature_c = _temperature_c(
            design_temperature
        )

        temperature_f = _temperature_to_f(
            design_temperature
        )

        temperature_band = _get_temperature_band_f(
            design_temperature
        )

        material_input = inputs[
            "material"
        ]

        material = _normalize_material_key(
            material_input
        )

        joint_efficiency = float(
            inputs["joint_efficiency"]
        )

        corrosion_allowance = inputs[
            "corrosion_allowance"
        ]

        corrosion_allowance_m = _length_m(
            corrosion_allowance
        )

        vessel_type = str(
            inputs["vessel_type"]
        ).strip().lower()

        head_type_input = str(
            inputs["head_type"]
        ).strip()

        # --------------------------------------------------------------------
        # ALLOWABLE STRESS
        # --------------------------------------------------------------------

        allowable_stress = get_allowable_stress(
            material,
            design_temperature,
        )

        allowable_stress_psi = _pressure_psi(
            allowable_stress
        )

        allowable_stress_pa = _pressure_pa(
            allowable_stress
        )

        allowable_stress_ksi = (
            allowable_stress_psi / 1000.0
        )

        # --------------------------------------------------------------------
        # SHELL THICKNESS
        # --------------------------------------------------------------------

        shell_required_thickness_m = (
            self._calculate_shell_thickness(
                pressure_pa=pressure_pa,
                diameter_m=diameter_m,
                allowable_stress_pa=allowable_stress_pa,
                joint_efficiency=joint_efficiency,
                corrosion_allowance_m=corrosion_allowance_m,
            )
        )

        # --------------------------------------------------------------------
        # HEAD THICKNESS
        # --------------------------------------------------------------------

        head_required_thickness_m = (
            self._calculate_head_thickness(
                pressure_pa=pressure_pa,
                diameter_m=diameter_m,
                allowable_stress_pa=allowable_stress_pa,
                joint_efficiency=joint_efficiency,
                corrosion_allowance_m=corrosion_allowance_m,
                head_type=head_type_input,
            )
        )

        governing_required_thickness_m = max(
            shell_required_thickness_m,
            head_required_thickness_m,
        )

        governing_required_thickness_mm = (
            governing_required_thickness_m
            * 1000.0
        )

        # --------------------------------------------------------------------
        # SELECTED NOMINAL THICKNESS
        # --------------------------------------------------------------------
        #
        # Preliminary selection:
        # round up to the next whole mm.
        #

        import math

        selected_thickness_mm = max(
            1,
            int(
                math.ceil(
                    governing_required_thickness_mm
                )
            ),
        )

        # --------------------------------------------------------------------
        # VOLUME
        # --------------------------------------------------------------------

        internal_volume = (
            self._calculate_internal_volume(
                diameter_m=diameter_m,
                length_m=length_m,
                head_type=head_type_input,
            )
        )

        volume_margin = (
            internal_volume
            - specified_volume
        )

        volume_margin_percent = (
            volume_margin
            / specified_volume
            * 100.0
        )

        volume_check = (
            internal_volume
            >= specified_volume
        )

        # --------------------------------------------------------------------
        # EXTERNAL AREA
        # --------------------------------------------------------------------

        external_area = _vessel_external_area(
            diameter_m=diameter_m,
            length_m=length_m,
            head_type=head_type_input,
        )

        # --------------------------------------------------------------------
        # MATERIAL WEIGHT
        # --------------------------------------------------------------------

        material_density = get_material_density(
            material
        )

        # Preliminary shell/head weight.
        #
        # We use selected nominal thickness for the complete pressure
        # boundary surface.
        #

        selected_thickness_m = (
            selected_thickness_mm / 1000.0
        )

        estimated_weight_kg = (
            external_area
            * selected_thickness_m
            * material_density
        )

        # --------------------------------------------------------------------
        # HYDROTEST
        # --------------------------------------------------------------------
        #
        # Preliminary value used by ProcessPI:
        #
        #     P_hydro = 1.3 * design pressure
        #
        # Actual code hydrotest requirements depend on the applicable
        # code edition, material stress ratios, temperature, and other
        # conditions.
        #

        hydrotest_pressure = Pressure(
            pressure_pa * 1.3,
            "Pa",
        )

        hydrotest_pressure_bar = (
            _pressure_bar(
                hydrotest_pressure
            )
        )

        # --------------------------------------------------------------------
        # NOZZLE RESULT
        # --------------------------------------------------------------------

        nozzles_result: Dict[str, Dict[str, Any]] = {}

        for name, data in self.nozzles.items():

            nozzles_result[name] = dict(
                data
            )

        # --------------------------------------------------------------------
        # MANHOLE RESULT
        # --------------------------------------------------------------------

        manholes_result: Dict[str, Dict[str, Any]] = {}

        for name, data in self.manholes.items():

            manholes_result[name] = dict(
                data
            )

        # --------------------------------------------------------------------
        # WARNINGS
        # --------------------------------------------------------------------

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

            "Nozzle and manhole reinforcement calculations "
            "are not included.",

            "Estimated weight is a preliminary pressure-boundary "
            "weight and does not include saddles, skirts, "
            "supports, platforms, ladders, insulation, "
            "internals, flanges, nozzles, manways, or other "
            "attachments.",

            "Hydrotest pressure is a preliminary 1.3 × design "
            "pressure value and must be verified against the "
            "applicable ASME requirements for the final design.",
        ]

        if not volume_check:

            warnings.append(
                "Calculated internal vessel volume is less than "
                "the specified required volume."
            )

        # --------------------------------------------------------------------
        # RESULT
        # --------------------------------------------------------------------

        result: Dict[str, Any] = {

            # ---------------------------------------------------------------
            # General vessel information
            # ---------------------------------------------------------------

            "vessel_type": vessel_type,

            "head_type": head_type_input,

            "material": material,

            # ---------------------------------------------------------------
            # Design pressure
            # ---------------------------------------------------------------

            "design_pressure": design_pressure,

            "design_pressure_bar": pressure_bar,

            "design_pressure_psi": pressure_psi,

            # ---------------------------------------------------------------
            # Design temperature
            # ---------------------------------------------------------------

            "design_temperature": design_temperature,

            "design_temperature_F": Temperature(
                temperature_f,
                "F",
            ),

            "allowable_stress_temperature_band": Temperature(
                temperature_band,
                "F",
            ),

            # ---------------------------------------------------------------
            # Allowable stress
            # ---------------------------------------------------------------

            "allowable_stress": allowable_stress,

            "allowable_stress_ksi": allowable_stress_ksi,

            # ---------------------------------------------------------------
            # Geometry
            # ---------------------------------------------------------------

            "diameter": inputs["diameter"],

            "length": inputs["length"],

            "joint_efficiency": joint_efficiency,

            "corrosion_allowance": corrosion_allowance,

            # ---------------------------------------------------------------
            # Thickness calculations
            # ---------------------------------------------------------------

            "shell_required_thickness": Length(
                shell_required_thickness_m,
                "m",
            ),

            "head_required_thickness": Length(
                head_required_thickness_m,
                "m",
            ),

            "governing_required_thickness": Length(
                governing_required_thickness_m,
                "m",
            ),

            "selected_thickness": Length(
                selected_thickness_mm,
                "mm",
            ),

            # ---------------------------------------------------------------
            # Volume
            # ---------------------------------------------------------------

            "specified_volume": Volume(
                specified_volume,
                "m3",
            ),

            "internal_volume": Volume(
                internal_volume,
                "m3",
            ),

            "volume_check": volume_check,

            "volume_margin": Volume(
                volume_margin,
                "m3",
            ),

            "volume_margin_percent": volume_margin_percent,

            # ---------------------------------------------------------------
            # Area / weight
            # ---------------------------------------------------------------

            "external_area": external_area,

            "material_density_kg_m3": material_density,

            "estimated_weight_kg": estimated_weight_kg,

            # ---------------------------------------------------------------
            # Hydrotest
            # ---------------------------------------------------------------

            "hydrotest_pressure": hydrotest_pressure,

            "hydrotest_pressure_bar": hydrotest_pressure_bar,

            # ---------------------------------------------------------------
            # Attachments
            # ---------------------------------------------------------------

            "nozzles": nozzles_result,

            "manholes": manholes_result,

            # ---------------------------------------------------------------
            # Warnings
            # ---------------------------------------------------------------

            "warnings": warnings,

            # ---------------------------------------------------------------
            # Design basis
            # ---------------------------------------------------------------

            "design_basis": (
                "ASME VIII-1 preliminary: "
                "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
            ),
        }

        return result


# ============================================================================
# COMPATIBILITY CLASS
# ============================================================================

class PressureVessels(PressureVessel):
    """
    Backward-compatible alias for PressureVessel.

    Some ProcessPI package versions import both:

        PressureVessel
        PressureVessels

    Keeping this class prevents an ImportError when older package
    __init__.py files expect the plural name.
    """

    pass


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "PressureVessel",
    "PressureVessels",
    "asme_material_stress_data",
    "MATERIAL_ALIASES",
    "MATERIAL_DENSITIES",
    "ASME_TEMPERATURE_BANDS",
    "set_temperature_range",
    "get_allowable_stress",
    "get_material_density",
]
