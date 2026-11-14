"""Gas-phase thermal conductivity comes from each component's own data.

`Component.thermal_conductivity()` already uses DIPPR Eq. 102 in the gas
phase when a component gives `_vapor_thermal_conductivity_constants`, but
only 21 components did. The rest evaluated their liquid polynomial
(Perry's Table 2-315, valid only between the liquid Tmin and Tmax) at gas
temperatures. At 400 K and 1 atm:

    Hydrogen  2369.5 W/(m K)   (real about 0.23)
    Water        0.685         (real 0.027)
    Benzene      0.112         (real 0.020)
    Argon, Acetylene, Carbon dioxide, Ethylene, Fluorine, ...:
                 ValueError "Thermal conductivity cannot be negative."

All components with a row in Perry's Chemical Engineers' Handbook, 8th ed.,
Table 2-314 (pp. 2-433 to 2-438) now carry its constants:

    k = C1 * T^C2 / (1 + C3/T + C4/T^2),  k in W/(m K), T in K.

The table prints k at Tmin and Tmax of each row; the checks below use them.
"""

import pytest

import processpi.components as components
from processpi.components import (
    Argon, Benzene, ChloroMethane, Deuterium, Hydrogen, VinylAcetylene, Water,
)
from processpi.components.base import Component
from processpi.units import Pressure, Temperature


def _gas_k(cls, t_k):
    c = cls(temperature=Temperature(t_k, "K"), pressure=Pressure(1, "atm"), phase="gas")
    return c.thermal_conductivity().to("W/mK").value


# (class, Tmin K, printed k at Tmin, Tmax K, printed k at Tmax), Table 2-314.
PERRY_ROWS = [
    (Argon, 90.0, 0.00585, 3273.1, 0.09525),            # no. 14, p. 2-433
    (Benzene, 339.15, 0.01407, 1000, 0.09542),          # no. 16, p. 2-433
    # No. 56: C1 = -22136 and C3 = -4.8749E+10 (read from the printed page).
    (ChloroMethane, 213.15, 0.00590, 750, 0.05448),     # no. 56, p. 2-433
    (Deuterium, 233.15, 0.11474, 1500, 0.44547),        # no. 80, p. 2-434
    (Hydrogen, 22.0, 0.01718, 1600, 0.64299),           # no. 183, p. 2-436
    # No. 339: C4 is printed "9,0617"; only 90617 reproduces both printed k.
    (VinylAcetylene, 278.25, 0.01123, 1000, 0.08222),   # no. 339, p. 2-438
    (Water, 273.16, 0.01574, 1073.15, 0.10652),         # no. 342, p. 2-438
]


@pytest.mark.parametrize("cls, tmin, k_tmin, tmax, k_tmax", PERRY_ROWS,
                         ids=[r[0].__name__ for r in PERRY_ROWS])
def test_gas_conductivity_reproduces_perry_at_tmin_and_tmax(cls, tmin, k_tmin, tmax, k_tmax):
    # The printed values have four or five significant figures.
    assert _gas_k(cls, tmin) == pytest.approx(k_tmin, rel=1e-3)
    assert _gas_k(cls, tmax) == pytest.approx(k_tmax, rel=1e-3)


def test_hydrogen_at_400_k():
    # Before: 2369.5 W/(m K) from the liquid polynomial.
    # 0.002653 x 400^0.7452 / (1 + 12/400) = 0.22385 W/(m K).
    assert _gas_k(Hydrogen, 400.0) == pytest.approx(0.22385, rel=1e-4)


def test_water_vapour_and_benzene_vapour_at_400_k():
    # Before: 0.685 and 0.112 W/(m K) (liquid values).
    # Water: 6.2041E-06 x 400^1.3973 = 0.02682.
    assert _gas_k(Water, 400.0) == pytest.approx(0.02682, rel=1e-3)
    # Benzene: 1.652E-05 x 400^1.3117 / (1 + 491/400) = 0.01920.
    assert _gas_k(Benzene, 400.0) == pytest.approx(0.01920, rel=1e-3)


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


def test_every_component_with_perry_data_has_vapour_conductivity_constants():
    missing = [
        cls.__name__ for cls in _component_classes()
        if cls.__name__ not in _NO_PERRY_ROW
        and len(getattr(cls, "_vapor_thermal_conductivity_constants", None) or []) != 4
    ]
    assert missing == []


def test_every_vapour_conductivity_is_a_gas_conductivity_at_400_k():
    # Gas conductivities at 400 K lie between about 0.005 (heavy organics,
    # halocarbons) and 0.25 W/(m K) (hydrogen, helium); liquid values or a
    # misplaced constant fall outside, and a negative value raises.
    out = {}
    for cls in _component_classes():
        if getattr(cls, "_vapor_thermal_conductivity_constants", None):
            try:
                k = _gas_k(cls, 400.0)
            except ValueError as exc:
                out[cls.__name__] = str(exc)
                continue
            if not 0.003 < k < 0.3:
                out[cls.__name__] = k
    assert out == {}


def test_liquid_conductivity_is_unchanged():
    # The liquid branch still uses `_thermal_conductivity_constants`
    # (Table 2-315): benzene at 25 C, 0.23444 - 0.00030572 x 298.15 = 0.14329.
    liquid = Benzene(temperature=Temperature(25, "C"), pressure=Pressure(1, "atm"))
    assert liquid.phase() == "liquid"
    assert liquid.thermal_conductivity().to("W/mK").value == pytest.approx(0.14329, rel=1e-4)
