"""
Preliminary ASME VIII-1 internal-pressure pressure-vessel design.

This module is intentionally an equipment module (rather than a calculation in
``equipment.base``), in the same way that the heat-exchanger implementations
live below :mod:`processpi.equipment`.

It provides preliminary sizing only; the warnings returned by
:meth:`PressureVessel.design` are part of that scope.

Allowable material stresses are based on the supplied temperature-specific
material stress table.

IMPORTANT:
    The material allowable-stress values supplied in this module are treated
    as ksi and converted to psi when returned by ``get_allowable_stress()``.

    This is a preliminary engineering database and must be verified against
    the applicable ASME Section II, Part D material tables before code-stamped
    design or fabrication.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, pi, sqrt
from typing import Any, Dict, List, Optional

from processpi.calculations.base import CalculationBase
from processpi.units import Area, Diameter, Length, Pressure, Temperature, Volume


# ============================================================================
# ASME MATERIAL ALLOWABLE STRESS DATA
# ============================================================================
#
# Values are supplied in ksi.
#
# Temperature keys are in degrees Fahrenheit.
#
# The table contains the allowable stress at the specified ASME temperature
# bands:
#
#     100 F
#     200 F
#     300 F
#     400 F
#     500 F
#     600 F
#     700 F
#     800 F
#
# Temperature handling is intentionally conservative:
# a design temperature between two tabulated temperatures uses the NEXT HIGHER
# temperature band.
#
# Example:
#     450 F -> 500 F allowable stress
#
# Temperatures below 100 F use the 100 F value.
# Temperatures above 800 F are rejected because the supplied database does not
# contain allowable stresses above 800 F.
#
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
# LEGACY / USER-FRIENDLY MATERIAL ALIASES
# ============================================================================

MATERIAL_ALIASES = {
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

    # Existing ProcessPI generic names
    "carbon_steel": "SA516-70",
    "carbon steel": "SA516-70",
    "sa-516-70": "SA516-70",
    "stainless_304": "SA240-304",
    "stainless 304": "SA240-304",
    "stainless_316": "SA240-316",
    "stainless 316": "SA240-316",
}


# ============================================================================
# TEMPERATURE FUNCTIONS
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


def set_temperature_range(temperature: Any) -> Temperature:
    """
    Return the ASME material-stress temperature band.

    The supplied stress database is tabulated at 100°F increments.

    Selection is conservative:

        <= 100°F  -> 100°F
        <= 200°F  -> 200°F
        <= 300°F  -> 300°F
        ...
        <= 800°F  -> 800°F

    Temperatures above 800°F are rejected because no allowable-stress data
    has been supplied for higher temperatures.
    """

    fahrenheit = _value(temperature, "temperature", "F")

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
        "Design temperature exceeds the available allowable-stress database "
        "(maximum supported temperature = 800°F)."
    )


def normalize_material(material: Any) -> str:
    """
    Normalize a material name to the key used in the ASME stress database.
    """

    key = str(material).strip()

    if key in asme_material_stress_data:
        return key

    alias_key = key.lower()

    if alias_key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[alias_key]

    # Case-insensitive direct lookup
    for material_name in asme_material_stress_data:
        if material_name.lower() == alias_key:
            return material_name

    raise ValueError(
        f"Unsupported pressure-vessel material: {material!r}. "
        f"Available materials: {', '.join(asme_material_stress_data.keys())}"
    )


def get_allowable_stress(
    material: Any,
    temperature: Any = Temperature(20, "C"),
) -> Pressure:
    """
    Return the allowable stress for a material at the specified temperature.

    Parameters
    ----------
    material:
        ASME material identifier, for example ``SA516-70`` or ``SA240-316L``.

        A numerical value may also be supplied. In that case it is interpreted
        as an allowable stress in ksi.

    temperature:
        ProcessPI Temperature or numeric temperature.

        Numeric temperature values are interpreted as Fahrenheit when no
        ProcessPI Temperature object is supplied.

    Returns
    -------
    Pressure
        Allowable stress in psi.

    Notes
    -----
    The material database is in ksi.

    For a temperature between two tabulated values, the next higher
    temperature band is selected conservatively.

    Example:

        450°F -> 500°F stress

    """

    # ------------------------------------------------------------------------
    # Explicit numerical allowable stress
    # ------------------------------------------------------------------------

    if isinstance(material, (int, float)):
        stress_ksi = float(material)

        if stress_ksi <= 0:
            raise ValueError("Allowable stress must be greater than zero.")

        return Pressure(stress_ksi * 1000, "psi")

    # ------------------------------------------------------------------------
    # Normalize material
    # ------------------------------------------------------------------------

    material_key = normalize_material(material)

    # ------------------------------------------------------------------------
    # Convert design temperature to the ASME table band
    # ------------------------------------------------------------------------

    temperature_band = set_temperature_range(temperature)

    temperature_f = int(round(_value(temperature_band, "temperature", "F")))

    stress_ksi = asme_material_stress_data[material_key][temperature_f]

    # ------------------------------------------------------------------------
    # Zero values indicate that the supplied table has no allowable stress
    # available at that temperature.
    # ------------------------------------------------------------------------

    if stress_ksi <= 0:
        raise ValueError(
            f"No allowable stress is available for material "
            f"{material_key!r} at {temperature_f}°F."
        )

    # ------------------------------------------------------------------------
    # Convert ksi -> psi
    # ------------------------------------------------------------------------

    return Pressure(stress_ksi * 1000, "psi")


# ============================================================================
# UNIT / VALUE HELPER
# ============================================================================

def _value(
    value: Any,
    name: str,
    unit: Optional[str] = None,
) -> float:
    """
    Extract a numeric value from either a plain number or ProcessPI unit.

    ProcessPI unit objects expose ``value`` / ``original_value`` depending on
    the unit implementation, so both are handled.
    """

    if hasattr(value, "to") and unit:
        value = value.to(unit)

    value = getattr(
        value,
        "original_value",
        getattr(value, "value", value),
    )

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric or a ProcessPI unit value"
        ) from exc


# ============================================================================
# RESULTS
# ============================================================================

@dataclass
class PressureVesselResults:
    """
    Structured results returned by the pressure-vessel design workflow.
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
    Preliminary ASME VIII-1 vessel with cylindrical or spherical geometry.

    Dimensions are SI when plain numbers are supplied:

        length      -> m
        diameter    -> m
        pressure    -> Pa
        density     -> kg/m³

    ProcessPI:

        Pressure
        Temperature
        Length
        Diameter
        Volume

    objects are accepted directly.
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

    def __init__(self, **kwargs: Any):
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
        ).lower()

        if vessel_type not in self._TYPES:
            raise ValueError(
                f"vessel_type must be one of {sorted(self._TYPES)}"
            )

        pressure = inputs.get(
            "design_pressure",
            inputs.get("pressure"),
        )

        if pressure is None or _value(
            pressure,
            "design_pressure",
            "Pa",
        ) <= 0:
            raise ValueError(
                "design_pressure must be greater than zero"
            )

        diameter = inputs.get(
            "diameter",
            inputs.get("inside_diameter"),
        )

        if diameter is None or _value(
            diameter,
            "diameter",
            "m",
        ) <= 0:
            raise ValueError(
                "diameter must be greater than zero"
            )

        if vessel_type != "spherical":

            length = inputs.get(
                "length",
                inputs.get("tangent_to_tangent_length"),
            )

            if length is None or _value(
                length,
                "length",
                "m",
            ) <= 0:
                raise ValueError(
                    "length must be greater than zero for cylindrical vessels"
                )

        joint_efficiency = float(
            inputs.get("joint_efficiency", 1.0)
        )

        if not 0 < joint_efficiency <= 1:
            raise ValueError(
                "joint_efficiency must be greater than zero and no more than one"
            )

        corrosion_allowance = _value(
            inputs.get("corrosion_allowance", 0.0),
            "corrosion_allowance",
            "m",
        )

        if corrosion_allowance < 0:
            raise ValueError(
                "corrosion_allowance must be non-negative"
            )

        # Validate material and temperature database
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

    # ------------------------------------------------------------------------
    # VESSEL TYPE
    # ------------------------------------------------------------------------

    @property
    def vessel_type(self) -> str:
        return str(
            self.inputs.get(
                "vessel_type",
                self.inputs.get("orientation", "horizontal"),
            )
        ).lower()

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
            Temperature(20, "C"),
        )

    # ------------------------------------------------------------------------
    # ALLOWABLE STRESS
    # ------------------------------------------------------------------------

    def allowable_stress(self) -> Pressure:
        """
        Return allowable stress at the design temperature.
        """

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

        diameter_m = _value(
            diameter,
            "nozzle diameter",
            "m",
        )

        if diameter_m <= 0:
            raise ValueError(
                "nozzle diameter must be greater than zero"
            )

        self.nozzles[name] = {
            "diameter": Diameter(diameter_m),
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

        diameter_m = _value(
            diameter,
            "manhole diameter",
            "m",
        )

        if diameter_m <= 0:
            raise ValueError(
                "manhole diameter must be greater than zero"
            )

        self.manholes[name] = {
            "diameter": Diameter(diameter_m),
            **details,
        }

    # ------------------------------------------------------------------------
    # SHELL THICKNESS
    # ------------------------------------------------------------------------

    def shell_thickness(self) -> Length:
        """
        UG-27(c)(1) cylindrical-shell thickness.

        Includes corrosion allowance.
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

        allowable_stress = (
            self.allowable_stress().to("Pa")
        )

        s = _value(
            allowable_stress,
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

        t_pressure = (
            pressure * radius
            /
            (
                s * joint_efficiency
                - 0.6 * pressure
            )
        )

        return Length(
            t_pressure + corrosion_allowance
        )

    # ------------------------------------------------------------------------
    # HEAD THICKNESS
    # ------------------------------------------------------------------------

    def head_thickness(self) -> Length:
        """
        Preliminary UG-34 / UG-32 head thickness.

        Includes corrosion allowance.
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

        allowable_stress = (
            self.allowable_stress().to("Pa")
        )

        s = _value(
            allowable_stress,
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
        ).lower()

        head = (
            head
            .replace("2:1_", "")
            .replace("2:1 ", "")
        )

        if head not in self._HEADS:
            raise ValueError(
                f"head_type must be one of {sorted(self._HEADS)}"
            )

        factors = {
            "flat": 0.50,
            "ellipsoidal": 0.25,
            "torispherical": 0.885,
            "hemispherical": 0.125,
            "conical": 0.35,
        }

        t_pressure = (
            factors[head]
            * pressure
            * diameter
            /
            (
                s * joint_efficiency
                - 0.1 * pressure
            )
        )

        return Length(
            t_pressure + corrosion_allowance
        )

    # ------------------------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------------------------

    def volume(
        self,
        liquid_level: Optional[Any] = None,
    ) -> Volume:

        diameter = _value(
            self.inputs.get(
                "diameter",
                self.inputs.get("inside_diameter"),
            ),
            "diameter",
            "m",
        )

        radius = diameter / 2

        if self.vessel_type == "spherical":

            full_volume = (
                4
                * pi
                * radius**3
                / 3
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
            return Volume(full_volume)

        level = _value(
            liquid_level,
            "liquid_level",
            "m",
        )

        if not 0 <= level <= diameter:
            raise ValueError(
                "liquid_level must be between zero and vessel diameter"
            )

        fraction = (
            (
                radius**2
                * acos(
                    (radius - level)
                    / radius
                )
                -
                (radius - level)
                * sqrt(
                    max(
                        0,
                        2 * radius * level
                        - level**2,
                    )
                )
            )
            /
            (pi * radius**2)
        )

        return Volume(
            full_volume * fraction
        )

    # ------------------------------------------------------------------------
    # HEAD VOLUME
    # ------------------------------------------------------------------------

    def _head_volume(
        self,
        radius: float,
    ) -> float:

        head = str(
            self.inputs.get(
                "head_type",
                "ellipsoidal",
            )
        ).lower()

        factors = {
            "flat": 0.0,
            "ellipsoidal": 2 / 3,
            "torispherical": 0.5,
            "hemispherical": 4 / 3,
            "conical": 1 / 3,
        }

        return (
            factors.get(
                head,
                2 / 3,
            )
            * pi
            * radius**3
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
        """
        Execute the preliminary pressure-vessel design calculation.
        """

        # Validate inputs first
        self.validate_inputs()

        # --------------------------------------------------------------------
        # Required shell / head thickness
        # --------------------------------------------------------------------

        if self.vessel_type != "spherical":
            shell_required = self.shell_thickness()
        else:
            shell_required = self.head_thickness()

        head_required = self.head_thickness()

        # Convert both to mm before comparison
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

        # --------------------------------------------------------------------
        # Design pressure
        # --------------------------------------------------------------------

        design_pressure = _value(
            self.inputs.get(
                "design_pressure",
                self.inputs.get("pressure"),
            ),
            "design_pressure",
            "Pa",
        )

        hydrotest = Pressure(
            1.3 * design_pressure
        )

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

            external_area = (
                4
                * pi
                * (diameter / 2) ** 2
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

            external_area = (
                pi * diameter * length
                +
                2
                * pi
                * (diameter / 2) ** 2
            )

        # --------------------------------------------------------------------
        # Approximate material weight
        # --------------------------------------------------------------------

        density = float(
            self.inputs.get(
                "material_density",
                7850.0,
            )
        )

        selected_thickness_m = (
            _value(
                selected,
                "selected thickness",
                "m",
            )
        )

        weight = (
            external_area
            * selected_thickness_m
            * density
        )

        # --------------------------------------------------------------------
        # Temperature / allowable stress information
        # --------------------------------------------------------------------

        temperature_band = set_temperature_range(
            self.design_temperature
        )

        allowable_stress = self.allowable_stress()

        allowable_stress_psi = _value(
            allowable_stress,
            "allowable stress",
            "psi",
        )

        allowable_stress_ksi = (
            allowable_stress_psi / 1000
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
        ]

        if self.nozzles or self.manholes:

            warnings.append(
                "Nozzle and manhole reinforcement calculations "
                "are not included."
            )

        # --------------------------------------------------------------------
        # Results
        # --------------------------------------------------------------------

        return PressureVesselResults({

            "vessel_type": self.vessel_type,

            "head_type": self.inputs.get(
                "head_type",
                "ellipsoidal",
            ),

            "material": self.material,

            "design_temperature": self.design_temperature,

            "allowable_stress_temperature_band": temperature_band,

            "allowable_stress": allowable_stress,

            "allowable_stress_ksi": allowable_stress_ksi,

            "shell_required_thickness": shell_required,

            "head_required_thickness": head_required,

            "governing_required_thickness": Length(
                governing_required_mm,
                "mm",
            ),

            "selected_thickness": selected,

            "internal_volume": self.volume(),

            "external_area": Area(
                external_area
            ),

            "estimated_weight_kg": weight,

            "hydrotest_pressure": hydrotest,

            "nozzles": self.nozzles.copy(),

            "manholes": self.manholes.copy(),

            "warnings": warnings,

            "design_basis": (
                "ASME VIII-1 preliminary: "
                "UG-27(c)(1), UG-34, UG-32, UG-99(b)"
            ),

        }).to_dict()

    calculate = design


# ============================================================================
# BACKWARD-COMPATIBLE CLASSES
# ============================================================================

class CylindricalHorizontalFlatEnd(PressureVessel):
    """
    Backward-compatible horizontal cylindrical vessel with flat heads.
    """

    def __init__(self, **kwargs: Any):

        super().__init__(
            vessel_type="horizontal",
            head_type="flat",
            **kwargs,
        )


class CylindricalHorizontalDishEnd(PressureVessel):
    """
    Backward-compatible horizontal cylindrical vessel with dished heads.
    """

    def __init__(self, **kwargs: Any):

        super().__init__(
            vessel_type="horizontal",
            head_type="ellipsoidal",
            **kwargs,
        )


# Backward-compatible alias
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
