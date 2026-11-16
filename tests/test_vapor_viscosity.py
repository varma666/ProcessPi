"""Gas-phase viscosity comes from each component's own data.

Before, `Component.viscosity()` had one gas branch for every component:
Sutherland's law with air's constants (1.8e-5 Pa s at 300 K, C = 120 K),
because no component set its own. Benzene, hydrogen, methane and nitrogen
all returned 2.2383e-5 Pa s at 400 K; benzene is about 1.0e-5 and hydrogen
about 1.09e-5.

Each component now carries `_vapor_viscosity_constants` from Perry's
Chemical Engineers' Handbook, 8th ed., Table 2-312 (pp. 2-421 to 2-426),
DIPPR Eq. 102:

    mu = C1 * T^C2 / (1 + C3/T + C4/T^2),  mu in Pa s, T in K.

The table prints the viscosity at Tmin and Tmax of each row; the checks
below use those printed values.
"""

import pytest

import processpi.components as components
from processpi.components import (
    Air, Argon, Benzene, Deuterium, Gas, Hydrogen, Methane, Nitrogen, Toluene, Vapor, Water,
)
from processpi.components.base import Component
from processpi.units import Pressure, Temperature


def _gas_mu(cls, t_k):
    c = cls(temperature=Temperature(t_k, "K"), pressure=Pressure(1, "atm"), phase="gas")
    return c.viscosity().to("Pa·s").value


# (class, Tmin K, printed mu at Tmin, Tmax K, printed mu at Tmax), Table 2-312.
# Benzene: C3 only; Hydrogen: negative C3 and a C4; Water: C1 and C2 only;
# Deuterium: C3 below 1 (it sits in the C3 column, not C4).
PERRY_ROWS = [
    (Air, 80.00, 5.508e-06, 2000, 6.227e-05),         # no. 11, p. 2-421
    (Benzene, 278.68, 7.077e-06, 1000, 2.486e-05),    # no. 16, p. 2-421
    (Deuterium, 60.00, 4.137e-06, 480, 1.744e-05),    # no. 80, p. 2-422
    (Hydrogen, 13.95, 6.517e-07, 3000, 4.330e-05),    # no. 183, p. 2-424
    (Methane, 90.69, 3.468e-06, 1000, 2.800e-05),     # no. 193, p. 2-424
    (Water, 273.16, 8.882e-06, 1073.15, 4.082e-05),   # no. 342, p. 2-426
]


@pytest.mark.parametrize("cls, tmin, mu_tmin, tmax, mu_tmax", PERRY_ROWS,
                         ids=[r[0].__name__ for r in PERRY_ROWS])
def test_gas_viscosity_reproduces_perry_at_tmin_and_tmax(cls, tmin, mu_tmin, tmax, mu_tmax):
    # The printed values have four significant figures.
    assert _gas_mu(cls, tmin) == pytest.approx(mu_tmin, rel=5e-4)
    assert _gas_mu(cls, tmax) == pytest.approx(mu_tmax, rel=5e-4)


def test_argon_matches_perry_at_tmin():
    # No. 14: the table prints 1.001E-11 Pa s at Tmax = 3273.1 K, a misprint
    # (the same constants give 6.742E-06 at Tmin, as printed, and 2.87e-5 at
    # 400 K, in line with other sources). Only Tmin is checked.
    assert _gas_mu(Argon, 83.78) == pytest.approx(6.742e-06, rel=5e-4)


def test_gas_viscosity_differs_between_components():
    # Before: all four were 2.2383e-5 Pa s at 400 K.
    values = {cls.__name__: _gas_mu(cls, 400.0) for cls in (Benzene, Toluene, Hydrogen, Methane, Nitrogen)}
    assert len({round(v, 9) for v in values.values()}) == len(values)
    # Benzene at 400 K: 3.134E-08 x 400^0.9676 / (1 + 7.9/400) = 1.0124e-5 Pa s.
    assert values["Benzene"] == pytest.approx(1.0124e-5, rel=1e-3)
    assert values["Benzene"] < values["Methane"] < values["Nitrogen"]


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


def test_every_component_with_perry_data_has_vapour_viscosity_constants():
    missing = [
        cls.__name__ for cls in _component_classes()
        if cls.__name__ not in _NO_PERRY_ROW
        and len(getattr(cls, "_vapor_viscosity_constants", None) or []) != 4
    ]
    assert missing == []


def test_every_vapour_viscosity_is_a_gas_viscosity_at_500_k():
    # Gas viscosities at 500 K lie between about 5e-6 (heavy organics) and
    # 4e-5 Pa s (helium, neon); a misplaced constant gives orders of magnitude off.
    out = {}
    for cls in _component_classes():
        if getattr(cls, "_vapor_viscosity_constants", None):
            mu = _gas_mu(cls, 500.0)
            if not 3e-6 < mu < 5e-5:
                out[cls.__name__] = mu
    assert out == {}


@pytest.mark.parametrize("cls", [Gas, Vapor])
def test_generic_gas_and_vapor_keep_sutherland_with_air_constants(cls):
    # 1.8e-5 x (300 + 120) / (400 + 120) x (400/300)^1.5 = 2.2383e-5 Pa s.
    c = cls(temperature=Temperature(400, "K"), pressure=Pressure(1, "atm"))
    assert c.viscosity().to("Pa·s").value == pytest.approx(2.2383e-5, rel=1e-4)


def test_liquid_viscosity_is_unchanged():
    # The liquid branch still uses `_viscosity_constants` (Table 2-313):
    # benzene at 25 C is about 6e-4 Pa s.
    liquid = Benzene(temperature=Temperature(25, "C"), pressure=Pressure(1, "atm"))
    assert liquid.phase() == "liquid"
    assert liquid.viscosity().to("Pa·s").value == pytest.approx(6.0e-4, rel=0.05)
