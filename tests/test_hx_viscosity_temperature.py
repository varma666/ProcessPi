"""Bulk and wall viscosities are taken at the right temperatures.

The exchanger evaluates every property at each side's mean temperature,
(inlet + outlet) / 2, and records it as ``t_props_k``; ``t_k`` stays the inlet
temperature. 4c54b3b added two steps that read ``t_k``:

- ``_side_props`` replaced the bulk viscosity with the component's value at
  ``t_k``, the inlet. On the docs benzene cooler the benzene viscosity went
  from 3.964E-4 Pa s (60 C, the mean) to 2.896E-4 (90 C, the inlet) and the
  water's from 1.031E-3 to 1.150E-3 (15 C), while density, cp and k stayed at
  the mean and the results still reported the mean temperature for all four.
- The wall temperature for the Sieder-Tate mu_w was the h-weighted average of
  the two inlet temperatures.

Perry's Chemical Engineers' Handbook, 8th ed., p. 5-9 (after Eq. 5-50): the
properties are evaluated at the bulk mean temperature, except mu_s, which is
at the temperature of the tube wall. Both steps now use ``t_props_k``. The
wall-viscosity correction itself (mu_w from the component at the wall
temperature) is unchanged.
"""

import contextlib
import io

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.streams import MaterialStream
from processpi.units import HeatTransferCoefficient, MassFlowRate, Pressure, Temperature


def _benzene_cooler():
    hx = HeatExchangerEngine().fit(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
        assumed_U=HeatTransferCoefficient(575, "W/m2K"),
        shell_dp=Pressure(1, "bar"),
        tube_dp=Pressure(1, "bar"),
        mode="design",
    )
    with contextlib.redirect_stdout(io.StringIO()):
        return hx.run().data


def _value(x):
    return getattr(x, "value", x)


def _mu(component, t_k):
    return component(temperature=Temperature(t_k, "K"), phase="liquid").viscosity().to("Pa·s").value


def test_the_bulk_viscosity_is_at_the_temperature_the_other_properties_are_at():
    basis = _benzene_cooler()["property_basis"]
    # Benzene 90 -> 30 C: mean 60 C.
    assert basis["hot"]["temperature_K"] == pytest.approx(333.15)
    assert basis["hot"]["viscosity_Pa_s"] == pytest.approx(_mu(Benzene, 333.15), rel=1e-9)
    assert basis["hot"]["viscosity_Pa_s"] == pytest.approx(3.9644e-4, rel=1e-4)
    assert basis["cold"]["viscosity_Pa_s"] == pytest.approx(
        _mu(Water, basis["cold"]["temperature_K"]), rel=1e-9
    )


def test_the_wall_temperature_lies_between_the_two_mean_temperatures():
    results = _benzene_cooler()
    basis = results["property_basis"]
    correction = results["viscosity_correction"]
    # Water is in the tubes and benzene in the shell here.
    h_t, h_s = _value(results["h_tube"]), _value(results["h_shell"])
    t_tube, t_shell = basis["cold"]["temperature_K"], basis["hot"]["temperature_K"]
    t_wall = (h_t * t_tube + h_s * t_shell) / (h_t + h_s)
    assert correction["shell"]["mu_wall"] == pytest.approx(_mu(Benzene, t_wall), rel=1e-9)
    assert correction["tube"]["mu_wall"] == pytest.approx(_mu(Water, t_wall), rel=1e-9)
    # A cooled liquid is more viscous at the wall (phi < 1), a heated one less.
    assert correction["shell"]["phi"] < 1.0 < correction["tube"]["phi"]
