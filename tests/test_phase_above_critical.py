"""phase() above the critical temperature is "gas" and does not raise.

phase() compared the pressure with the vapour pressure at any temperature.
Above Tc the DIPPR 101 correlation is outside its range, and for rows with a
large C4*T^C5 term exp() overflowed:

    _2Pentanol(temperature=Temperature(1000, "K")).phase()
    OverflowError: math range error

At 1000 K that was 2-pentanol, 2-nonanol and silicon tetrafluoride; at
1500 K also hydrogen, acetylene, propylene, dimethylamine, sulfur trioxide and
others. Above Tc there is no liquid, so phase() now returns "gas" there
without evaluating the correlation. Below Tc nothing changes.
"""

import pytest

import processpi.components as components
from processpi.units import Pressure, Temperature

ALL = [name for name in components.__all__ if name != "Component"]


def _with_tc():
    return [n for n in ALL if getattr(getattr(components, n), "_critical_temperature", None) is not None]


@pytest.mark.parametrize("t_k", [1000.0, 1500.0])
def test_phase_never_raises_and_is_gas_above_every_tc(t_k):
    for name in ALL:
        comp = getattr(components, name)(temperature=Temperature(t_k, "K"))
        phase = comp.phase()
        tc = getattr(type(comp), "_critical_temperature", None)
        if tc is not None and t_k >= tc.to("K").value:
            assert phase == "gas", name


def test_the_overflowing_rows_are_gases():
    for name in ("_2Pentanol", "_2Nonanol", "SiliconTetrafluoride", "Hydrogen", "Acetylene"):
        assert getattr(components, name)(temperature=Temperature(1500, "K")).phase() == "gas"


def test_below_tc_the_vapour_pressure_test_still_decides():
    # Water at 25 C and 1 atm is a liquid, n-butane a gas; at 50 bar butane
    # (Tc 425.1 K) is a liquid at 25 C.
    assert components.Water(temperature=Temperature(25, "C")).phase() == "liquid"
    assert components.Butane(temperature=Temperature(25, "C")).phase() == "gas"
    assert components.Butane(temperature=Temperature(25, "C"), pressure=Pressure(50, "bar")).phase() == "liquid"


def test_a_given_phase_still_wins():
    assert components.Hydrogen(temperature=Temperature(1500, "K"), phase="liquid").phase() == "liquid"
