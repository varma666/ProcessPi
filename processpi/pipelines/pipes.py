# processpi/pipelines/pipes.py

import numbers
import os
import sys
import warnings
from typing import Optional, Dict, Any, Tuple
from .base import PipelineBase
from ..units import *
from .standards import (
    PIPE_SCHEDULES, get_roughness, normalize_schedule, find_nominal_size, get_outside_diameter
)

# The processpi package directory: warnings about inputs are reported at the
# first caller outside it (the user's line), see `_warn_at_caller`.
_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_UNIT_NAMES = {"m": "metres", "mm": "millimetres"}


def _warn_at_caller(message: str, category: type = UserWarning) -> None:
    """
    Warn at the first frame outside the processpi package.

    A warning about an input then points at the line that passed it, however
    deep in the package it is noticed, and Python's default filter shows it once
    for that line rather than once per pipe or per solver iteration. The
    messages are fixed texts for the same reason (the filter keys on the text).
    """
    frame = sys._getframe(1)
    level = 2
    while frame is not None and os.path.abspath(frame.f_code.co_filename).startswith(
        _PACKAGE_DIR + os.sep
    ):
        frame = frame.f_back
        level += 1
    warnings.warn(message, category, stacklevel=level)


def _is_bare_number(value: Any) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, bool)


def as_diameter(value: Any, bare_unit: str, what: str) -> Optional[Diameter]:
    """
    A diameter input as a Diameter.

    A Length is converted. A bare number keeps the unit the package has always
    read it in (`bare_unit`), with a UserWarning naming that unit.

    Raises:
        TypeError: For anything else (a string such as "100 mm" included).
    """
    if value is None or isinstance(value, Diameter):
        return value
    if isinstance(value, Length):
        return Diameter(value.value, "m")
    if _is_bare_number(value):
        _warn_at_caller(
            f"{what} was given as a bare number and is taken in "
            f"{_UNIT_NAMES.get(bare_unit, bare_unit)}. Pass a Diameter to state "
            f"the unit, e.g. Diameter(4, \"in\") or Diameter(102.26, \"mm\")."
        )
        return Diameter(float(value), bare_unit)
    raise TypeError(f"{what} must be a Diameter or a Length, not {value!r}")


def as_length(value: Any, bare_unit: str, what: str) -> Optional[Length]:
    """
    A length input as a Length; a bare number is read in `bare_unit` with a
    UserWarning naming that unit.

    Raises:
        TypeError: For anything that is neither a Length nor a number.
    """
    if value is None or isinstance(value, Length):
        return value
    if _is_bare_number(value):
        _warn_at_caller(
            f"{what} was given as a bare number and is taken in "
            f"{_UNIT_NAMES.get(bare_unit, bare_unit)}. Pass a Length to state "
            f"the unit, e.g. Length(100, \"m\")."
        )
        return Length(float(value), bare_unit)
    raise TypeError(f"{what} must be a Length, not {value!r}")


def resolve_diameters(
    nominal_diameter: Optional[Diameter],
    internal_diameter: Optional[Diameter],
    schedule: str,
    owner: str,
) -> Tuple[Optional[Diameter], Optional[Diameter]]:
    """
    The (nominal, internal) diameter pair of a pipe.

    - A standard nominal size (NPS or DN, see `find_nominal_size`) is returned
      as the table's NPS, and gives the internal diameter of its `schedule`
      (ASME B36.10M / B36.19M) unless an internal diameter is given.
    - A given internal diameter is the bore used in the calculations (a lined
      or corroded pipe, a wall the table does not list). With a standard
      nominal size it must be smaller than that size's outside diameter.
    - A nominal size that is not a standard size cannot be looked up, so, as
      before, it is used as the internal diameter, with a UserWarning.

    Raises:
        ValueError: If the schedule is not tabulated for the nominal size, or
            the internal diameter does not fit inside the nominal size.
    """
    if nominal_diameter is None:
        return None, internal_diameter

    size = find_nominal_size(nominal_diameter)
    if size is None:
        if internal_diameter is None:
            _warn_at_caller(
                f"{owner} nominal_diameter is not a standard pipe size (an NPS or "
                f"DN of ASME B36.10M), so it cannot be looked up and is used as "
                f"the internal diameter, as before. Pass internal_diameter for a "
                f"non-standard bore."
            )
            internal_diameter = nominal_diameter
        return nominal_diameter, internal_diameter

    if internal_diameter is None:
        # A schedule the table does not have for this size used to give no
        # internal diameter, and the engine then used the nominal size as
        # the bore ("40" or "Sch40" for a 4 in pipe: 101.6 mm, not 102.26).
        available = PIPE_SCHEDULES[size]
        if schedule not in available:
            raise ValueError(
                f"Schedule {schedule!r} is not tabulated for "
                f"{size}; available: {', '.join(available)}"
            )
        return size, available[schedule][2]

    outside = get_outside_diameter(size)
    if internal_diameter.to_base() >= outside.to_base():
        raise ValueError(
            f"{owner}: internal_diameter {internal_diameter} does not fit in "
            f"nominal size {size} (outside diameter {outside}). Give the bore as "
            f"internal_diameter and the pipe size as nominal_diameter."
        )
    return size, internal_diameter


class Pipe(PipelineBase):
    """
    Represents a straight section of a process pipeline.

    Encapsulates geometry (diameter, length), material properties (roughness),
    and state (inlet/outlet pressure). Useful for flow and pressure drop
    calculations, and compatible with optimization workflows.
    """

    def __init__(
        self,
        name: str,
        nominal_diameter: Optional[Diameter] = None,
        schedule: str = "STD",
        material: str = "CS",
        length: Optional[Length] = None,
        inlet_pressure: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
        internal_diameter: Optional[Diameter] = None,
        flow_rate: Optional[VolumetricFlowRate] = None,  # <-- NEW
        **kwargs: Any
    ):
        """
        Initialize a Pipe instance.

        Args:
            name (str): Unique name of the pipe.
            nominal_diameter (Optional[Diameter]): Nominal pipe size, a label:
                the NPS (Diameter(4, "in")) or the DN in millimetres
                (Diameter(100, "mm")). The internal diameter is looked up for
                `schedule` in the ASME B36.10M / B36.19M table. If neither
                diameter is given, this pipe is a candidate for optimization.
            schedule (str, optional): Pipe schedule. Defaults to "STD".
            material (str, optional): Pipe material. Defaults to "CS".
            length (Optional[Length], optional): Pipe length (default 1 meter).
            inlet_pressure (Optional[Pressure], optional): Inlet pressure.
            outlet_pressure (Optional[Pressure], optional): Outlet pressure.
            internal_diameter (Optional[Diameter], optional): The bore used in
                the calculations. Given with a nominal size, it replaces the
                tabulated bore (a lined pipe, a non-standard wall) and must fit
                inside that size's outside diameter.

            A bare number for a diameter or the length is read in metres, as
            before, with a UserWarning. `Pipe` has no `diameter` input: a
            `diameter` keyword is ignored (kept in `params`) with a UserWarning.
            flow_rate (Optional[VolumetricFlowRate], optional): Initial flow rate
                for solver. Defaults to 0.001 m³/s.
            **kwargs: Additional custom parameters to store in the base class.
        """
        super().__init__(name=name, **kwargs)
        if "diameter" in kwargs:
            # It never set a diameter: the pipe was sized as if none was given.
            _warn_at_caller(
                "Pipe has no `diameter` input; it is ignored, as before (the "
                "value stays in `params`). Pass nominal_diameter (with schedule) "
                "for a standard pipe size, or internal_diameter for the bore."
            )

        # Optimization flag
        self.is_optimization_target: bool = (
            nominal_diameter is None and internal_diameter is None
        )

        # Core attributes
        self.schedule: str = normalize_schedule(schedule)
        self.material: str = material
        self.length: Length = as_length(length, "m", "Pipe length") or Length(1.0, "m")

        # Physical properties from standards
        self.roughness: Variable = get_roughness(self.material)

        # Nominal size and bore are separate inputs; the calculations use the bore.
        self.nominal_diameter: Optional[Diameter]
        self.internal_diameter: Optional[Diameter]
        self.nominal_diameter, self.internal_diameter = resolve_diameters(
            as_diameter(nominal_diameter, "m", "Pipe nominal_diameter"),
            as_diameter(internal_diameter, "m", "Pipe internal_diameter"),
            self.schedule,
            "Pipe",
        )

        # Optional pressures
        self.inlet_pressure: Optional[Pressure] = inlet_pressure
        self.outlet_pressure: Optional[Pressure] = outlet_pressure

        # Nodes (set externally in network)
        self.start_node: Optional[Any] = None
        self.end_node: Optional[Any] = None

        # -----------------------------
        # NEW: flow_rate for solver initialization
        # -----------------------------
        self.flow_rate: VolumetricFlowRate = flow_rate or VolumetricFlowRate(0.001, "m3/s")

    # -------------------------------------------------------------------------
    # Derived calculations
    # -------------------------------------------------------------------------
    def cross_sectional_area(self) -> Optional[Variable]:
        """Calculate internal cross-sectional area (m²)."""
        if self.internal_diameter is None:
            return None
        d_m = self.internal_diameter.to("m").value
        area_m2 = (3.14159 / 4) * (d_m**2)
        return Variable(area_m2, "m²")

    def surface_area(self) -> Optional[Variable]:
        """
        Calculate external surface area (m²), on the outside diameter of the
        nominal size (the nominal size itself when it is not a standard size;
        it used to be the nominal size always: 4 in for a 114.3 mm pipe).
        """
        if self.nominal_diameter is None:
            return None
        outside = get_outside_diameter(self.nominal_diameter) or self.nominal_diameter
        d_m = outside.to("m").value
        area_m2 = 3.14159 * d_m * self.length.to("m").value
        return Variable(area_m2, "m²")

    def pressure_difference(self) -> Optional[Pressure]:
        """Calculate ΔP (inlet - outlet)."""
        if self.inlet_pressure and self.outlet_pressure:
            return self.inlet_pressure - self.outlet_pressure
        return None

    # -------------------------------------------------------------------------
    # Export and representation
    # -------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Export all key pipe data as a dictionary. Each quantity is
        {"value": ..., "units": ...} in the unit it was given in, or None.
        (The unit classes have no `to_dict`, so this used to raise.)
        """
        def _q(x: Any) -> Optional[Dict[str, Any]]:
            if x is None:
                return None
            return {
                "value": getattr(x, "original_value", x.value),
                "units": getattr(x, "original_unit", x.units),
            }

        return {
            "name": self.name,
            "nominal_diameter": _q(self.nominal_diameter),
            "is_optimization_target": self.is_optimization_target,
            "schedule": self.schedule,
            "material": self.material,
            "length": _q(self.length),
            "roughness": _q(self.roughness),
            "internal_diameter": _q(self.internal_diameter),
            "cross_sectional_area": _q(self.cross_sectional_area()),
            "flow_rate": _q(self.flow_rate),  # <-- NEW
            "inlet_pressure": _q(self.inlet_pressure),
            "outlet_pressure": _q(self.outlet_pressure),
            "pressure_difference": _q(self.pressure_difference()),
        }

    def __repr__(self) -> str:
        if self.nominal_diameter is not None:
            dia_repr = (
                f"nominal_diameter={self.nominal_diameter}, "
                f"internal_diameter={self.internal_diameter}"
            )
        elif self.internal_diameter is not None:
            dia_repr = f"internal_diameter={self.internal_diameter}"
        else:
            dia_repr = "OPTIMIZE"
        return (
            f"Pipe(name='{self.name}', {dia_repr}, "
            f"schedule='{self.schedule}', length={self.length}, "
            f"flow_rate={self.flow_rate})"  # <-- UPDATED
        )

    # -------------------------------------------------------------------------
    # Compatibility hook for PipelineEngine
    # -------------------------------------------------------------------------
    def calculate(self):
        """Return pipe data (for engine compatibility)."""
        return self.to_dict()
