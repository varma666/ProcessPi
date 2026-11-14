"""Gas-phase heat capacity comes from each component's own ideal-gas data.

`Component.specific_heat()` uses the ideal-gas Cp in the gas phase when a
component gives the constants, but only 21 components did. The rest
evaluated their liquid correlation (Perry's Table 2-153, valid only between
the liquid Tmin and Tmax) at gas temperatures. At 400 K and 1 atm:

    Benzene    2072 J/(kg K)   (ideal gas 1451)
    Water      4262            (1902)
    Methanol   3463            (1610)
    Argon      ValueError "Unphysical Cp detected: 27673.7 J/kgK"

and three components (Hydrogen, Heptane, 1,1-Difluoroethane) had a
`specific_heat()` copied from Benzene that reads `_specific_heat_constants_1`
and `_2`, which they do not define, so their Cp raised AttributeError in
every phase (Hydrogen's was also a plain property, so `specific_heat()`
could not be called at all).

Every component with a row in Perry's Chemical Engineers' Handbook, 8th ed.,
Table 2-156 (pp. 2-176 to 2-181) now carries its DIPPR Eq. 107 constants:

    Cp = C1 + C2*[(C3/T)/sinh(C3/T)]^2 + C4*[(C5/T)/cosh(C5/T)]^2

and the four compounds that table has no row for (argon, helium-4, neon,
nitric oxide) the Table 2-155 polynomial. The tables print Cp at Tmin and
Tmax of each row (x 1E-05); the checks below use them.
"""

import pytest

import processpi.components as components
from processpi.components import (
    _11Difluoroethane, _12Butanediol, Argon, Benzene, BenzylAlcohol, Heptane, Hydrogen,
    HydrogenFluoride, Water,
)
from processpi.components.base import Component
from processpi.units import Pressure, SpecificHeat, Temperature


def _cp(cls, t_k, phase="gas", pressure=Pressure(1, "atm")):
    c = cls(temperature=Temperature(t_k, "K"), pressure=pressure, phase=phase)
    return c.specific_heat().to("J/kgK").value


def _cp_molar(cls, t_k, phase="gas", pressure=Pressure(1, "atm")):
    return _cp(cls, t_k, phase, pressure) * cls.molecular_weight


# (class, Tmin K, printed Cp at Tmin, Tmax K, printed Cp at Tmax), J/(kmol K).
PERRY_ROWS = [
    (Benzene, 200, 0.5358e5, 1500, 2.4157e5),              # no. 16, p. 2-176
    # No. 21: the table prints the formula C9H8O; benzyl alcohol is C7H8O.
    (BenzylAlcohol, 298.15, 1.1198e5, 1500, 3.2880e5),     # no. 21, p. 2-176
    (_12Butanediol, 298.15, 1.2667e5, 1500.1, 3.0289e5),   # no. 32, p. 2-176
    (_11Difluoroethane, 200, 0.5373e5, 1500, 1.5424e5),    # no. 97, p. 2-177
    (Heptane, 200, 1.2828e5, 1500, 4.4283e5),              # no. 160, p. 2-178
    (Hydrogen, 250, 0.2843e5, 1500, 0.3225e5),             # no. 183, p. 2-179
    # No. 187 prints C4 and C5 in E notation (1.95E-03 x 1E5, 1.33E+03).
    (HydrogenFluoride, 50, 0.2913e5, 1500, 0.3224e5),      # no. 187, p. 2-179
    (Water, 100, 0.3336e5, 2273.15, 0.5276e5),             # no. 342, p. 2-181
]


@pytest.mark.parametrize("cls, tmin, cp_tmin, tmax, cp_tmax", PERRY_ROWS,
                         ids=[r[0].__name__ for r in PERRY_ROWS])
def test_gas_cp_reproduces_perry_at_tmin_and_tmax(cls, tmin, cp_tmin, tmax, cp_tmax):
    # The printed values have four or five significant figures.
    assert _cp_molar(cls, tmin) == pytest.approx(cp_tmin, rel=5e-4)
    assert _cp_molar(cls, tmax) == pytest.approx(cp_tmax, rel=5e-4)


def test_argon_is_a_monatomic_ideal_gas():
    # Table 2-155, no. 14: Cp = 20786 J/(kmol K) = (5/2) R at every T.
    # Before: ValueError "Unphysical Cp detected" from the liquid polynomial.
    for t in (100, 400, 1500):
        assert _cp(Argon, t) == pytest.approx(20786 / 39.948, rel=1e-4)


def test_benzene_and_water_vapour_at_400_k():
    # Before: 2072 and 4262 J/(kg K) from the liquid correlations.
    # Benzene: 1.1360E5 J/(kmol K) / 78.114 = 1454.3 J/(kg K).
    assert _cp(Benzene, 400.0) == pytest.approx(1454.3, rel=1e-3)
    # Water: 0.34247E5 / 18.015 = 1901.0 J/(kg K).
    assert _cp(Water, 400.0) == pytest.approx(1901.0, rel=1e-3)


# Liquid Cp, Table 2-153, "use Eq. (2)" (pp. 2-166 to 2-168): (class, T, Cp).
LIQUID_EQ2 = [
    (Hydrogen, 13.95, 0.1262e5), (Hydrogen, 32.00, 1.3122e5),
    (Heptane, 182.57, 1.9989e5), (Heptane, 520.00, 4.0657e5),
    # C2 was 0.0 in the file; the table prints 105,580.
    (_11Difluoroethane, 154.56, 0.9915e5), (_11Difluoroethane, 359.98, 1.6874e5),
]


@pytest.mark.parametrize("cls, t_k, cp_ref", LIQUID_EQ2,
                         ids=[f"{r[0].__name__}-{r[1]}K" for r in LIQUID_EQ2])
def test_liquid_cp_of_the_former_benzene_copies_uses_eq_2(cls, t_k, cp_ref):
    # Before: AttributeError ('_specific_heat_constants_1').
    assert _cp_molar(cls, t_k, phase="liquid", pressure=Pressure(50, "bar")) == pytest.approx(cp_ref, rel=5e-4)


def test_hydrogen_specific_heat_is_a_method():
    # It was a plain property, so hydrogen.specific_heat() could not be called.
    h2 = Hydrogen(temperature=Temperature(400, "K"), pressure=Pressure(1, "atm"))
    assert callable(h2.specific_heat)
    assert h2.specific_heat().to("J/kgK").value == pytest.approx(14487, rel=1e-3)


def test_a_given_cp_still_wins():
    # Benzene's own specific_heat() ignored a given Cp before.
    cp = Benzene(temperature=Temperature(400, "K"), pressure=Pressure(1, "atm"),
                 specific_heat=SpecificHeat(1234.0, "J/kgK")).specific_heat()
    assert cp.to("J/kgK").value == pytest.approx(1234.0)


# Classes with no Perry row: the base class, the generic placeholders,
# Steam (CoolProp gives its properties) and Mixture (mixes its components).
_NO_PERRY_ROW = {"Component", "Gas", "Vapor", "Oil", "OrganicLiquid", "InorganicLiquid", "Steam", "Mixture"}


def _component_classes():
    seen = set()
    for name in getattr(components, "__all__", dir(components)):
        cls = getattr(components, name, None)
        if isinstance(cls, type) and issubclass(cls, Component) and cls not in seen:
            seen.add(cls)
            yield cls


def test_every_component_with_perry_data_has_ideal_gas_cp():
    missing = [
        cls.__name__ for cls in _component_classes()
        if cls.__name__ not in _NO_PERRY_ROW
        and len(getattr(cls, "_ideal_gas_heat_capacity_constants", None) or []) != 5
        and len(getattr(cls, "_ideal_gas_heat_capacity_polynomial", None) or []) != 5
    ]
    assert missing == []


def test_every_ideal_gas_cp_is_used_and_plausible_at_400_k():
    # Ideal-gas Cp at 400 K runs from about 230 J/(kg K) (bromine) to
    # 14,500 (hydrogen). A component whose own specific_heat() skips the gas
    # branch, or a misplaced constant, falls outside or raises.
    out = {}
    for cls in _component_classes():
        if cls.__name__ in _NO_PERRY_ROW:
            continue
        gas = cls(temperature=Temperature(400, "K"), pressure=Pressure(1, "atm"), phase="gas")
        try:
            cp = gas.specific_heat().to("J/kgK").value
            ideal = gas._ideal_gas_specific_heat().to("J/kgK").value
        except Exception as exc:  # noqa: BLE001 - report every failure
            out[cls.__name__] = f"{type(exc).__name__}: {exc}"
            continue
        if cp != pytest.approx(ideal, rel=1e-12):
            out[cls.__name__] = f"specific_heat() {cp} is not the ideal-gas Cp {ideal}"
        elif not 200 < cp < 16000:
            out[cls.__name__] = cp
    assert out == {}
