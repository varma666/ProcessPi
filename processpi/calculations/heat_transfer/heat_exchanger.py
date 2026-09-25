"""Deprecated names for the heat exchanger calculations in ``hx_kern``.

These six classes used to be a second copy of calculations that ``hx_kern``
also implements, under other names and keywords. Only the ``hx_kern`` set is
used by the exchangers, so it is now the single implementation. Each class
here keeps its old keywords, its old error messages, its ``inputs`` and its
return type, maps the keywords onto the ``hx_kern`` class and warns with a
``DeprecationWarning``. The formulas were identical, so the numbers are too.

========================  ==================  ==================================
old name                  use instead         keywords renamed
========================  ==================  ==================================
SensibleHeatDuty          SensibleDuty        mass_flow_rate -> m_dot,
                                              specific_heat -> cp
LatentHeatDuty            LatentDuty          mass_flow_rate -> m_dot
KernNusselt               DittusBoelter       none (0.023 Re^0.8 Pr^n is the
                                              Dittus-Boelter form, not Kern's
                                              shell-side ``KernShellNu``)
ConvectiveCoefficient     ConvectiveH         thermal_conductivity -> k,
                                              characteristic_diameter ->
                                              diameter
DarcyPressureDrop         DarcyDrop           friction_factor -> f
ReynoldsFromProperties    Reynolds            none
========================  ==================  ==================================
"""

from __future__ import annotations

import warnings
from typing import Dict, Tuple, Type

from ..base import CalculationBase
from .hx_kern import (
    ConvectiveH,
    DarcyDrop,
    DittusBoelter,
    LatentDuty,
    Reynolds,
    SensibleDuty,
)


class _DeprecatedHXCalculation(CalculationBase):
    """Old keyword interface over one ``hx_kern`` calculation.

    ``_keyword_map`` lists the required old keywords, in the order the old
    class checked them, with the ``hx_kern`` keyword each one becomes.
    ``_optional`` lists keywords passed through unchanged when given.
    """

    _canonical: Type[CalculationBase]
    _keyword_map: Tuple[Tuple[str, str], ...]
    _optional: Tuple[str, ...] = ()

    def __init__(self, **kwargs):
        warnings.warn(
            f"{type(self).__name__} is deprecated; use "
            f"processpi.calculations.heat_transfer.{self._canonical.__name__} "
            f"({self._rename_note()}).",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**kwargs)

    @classmethod
    def _rename_note(cls) -> str:
        renamed = [f"{old} -> {new}" for old, new in cls._keyword_map if old != new]
        return "keywords " + ", ".join(renamed) if renamed else "same keywords"

    def validate_inputs(self):
        for old, _new in self._keyword_map:
            if old not in self.inputs:
                raise ValueError(f"Missing required input: {old}")

    def _canonical_inputs(self) -> Dict[str, object]:
        mapped = {}
        for old, new in self._keyword_map:
            # Same check and message as the old class, under the old name.
            self._get_value(self.inputs[old], old)
            mapped[new] = self.inputs[old]
        for key in self._optional:
            if key in self.inputs:
                mapped[key] = self.inputs[key]
        return mapped

    def calculate(self):
        return self._canonical(**self._canonical_inputs()).calculate()


class SensibleHeatDuty(_DeprecatedHXCalculation):
    """Q = m * Cp * (Tin - Tout). Deprecated: use ``SensibleDuty``."""

    _canonical = SensibleDuty
    _keyword_map = (
        ("mass_flow_rate", "m_dot"),
        ("specific_heat", "cp"),
        ("t_in", "t_in"),
        ("t_out", "t_out"),
    )


class LatentHeatDuty(_DeprecatedHXCalculation):
    """Q = m * lambda. Deprecated: use ``LatentDuty``."""

    _canonical = LatentDuty
    _keyword_map = (
        ("mass_flow_rate", "m_dot"),
        ("latent_heat", "latent_heat"),
    )


class KernNusselt(_DeprecatedHXCalculation):
    """Nu = 0.023 * Re^0.8 * Pr^n. Deprecated: use ``DittusBoelter``.

    Despite the name this is the Dittus-Boelter tube-side correlation, the
    same formula and default n = 0.4 as ``DittusBoelter``. Kern's shell-side
    correlation is ``KernShellNu``.
    """

    _canonical = DittusBoelter
    _keyword_map = (
        ("reynolds", "reynolds"),
        ("prandtl", "prandtl"),
    )
    _optional = ("n",)


class ConvectiveCoefficient(_DeprecatedHXCalculation):
    """h = Nu * k / D. Deprecated: use ``ConvectiveH``."""

    _canonical = ConvectiveH
    _keyword_map = (
        ("nusselt", "nusselt"),
        ("thermal_conductivity", "k"),
        ("characteristic_diameter", "diameter"),
    )


class DarcyPressureDrop(_DeprecatedHXCalculation):
    """dP = f * (L / D) * (rho * v^2 / 2), f the Darcy factor. Deprecated: use ``DarcyDrop``.

    The old body grouped ``rho * v * v / 2`` before multiplying and
    ``DarcyDrop`` multiplies left to right, so a result can differ from the
    old one in the last bit or two of the float (at most 4e-16 relative over
    2700 random cases); the formula is the same.
    """

    _canonical = DarcyDrop
    _keyword_map = (
        ("friction_factor", "f"),
        ("length", "length"),
        ("diameter", "diameter"),
        ("density", "density"),
        ("velocity", "velocity"),
    )


class ReynoldsFromProperties(_DeprecatedHXCalculation):
    """Re = rho * v * D / mu. Deprecated: use ``Reynolds``."""

    _canonical = Reynolds
    _keyword_map = (
        ("density", "density"),
        ("velocity", "velocity"),
        ("diameter", "diameter"),
        ("viscosity", "viscosity"),
    )
