"""Vapour-pressure constants and formulas that did not match Perry Table 2-8.

Perry's Chemical Engineers' Handbook, 8th ed., Table 2-8 (vapour pressure of
inorganic and organic liquids, ln P = C1 + C2/T + C3 ln T + C4 T^C5, P in Pa):

    Acetonitrile      C2 0.0      for -5,385.6   (p. 2-55)
    Benzamide         C2 -11.932  for -11,932    (p. 2-55, thousands comma)
    Ethylene glycol   C2 -104,111 for -10,411    (p. 2-57)
    Methyl propionate C2 -4,634.1 for -6,439.7   (p. 2-58)
    Tetrahydrofuran   C2 -4,762.7 for -5,305.4   (p. 2-60)

The first four made the liquid a gas at 25 C (acetonitrile's vapour pressure
was 8.5E11 Pa there), and ethylene glycol had no vapour pressure at all
(3E-57 of Pc at Tc). The table's own Pvap at Tmin and Tmax now comes back.

Formulas from the same table: CarbonTetrachloride "CO" for CCl4,
BenzoicAcid "C7H6O" for C7H6O2, Propenylcyclohexene "C3H14" for C9H14,
Acetonitrile "C2?H3?N" and 1-Heptyne "C7?H12?". ChloroBenzene, ChloroMethane,
Chloroform and Cyanogen carried zero-width spaces.

2-Nonanol fails the Psat(Tc) = Pc check too, but its constants are Perry's as
printed (p. 2-59): the printed row itself gives 1.0E7 Pa at Tc = 649.5 K, against
the 2.551E6 Pa it lists there. It is left as it is.
"""

import re

import pytest

import processpi.components as components
from processpi.units import Temperature

# name: (Tmin K, Pvap at Tmin Pa, Tmax K, Pvap at Tmax Pa), Perry Table 2-8
PERRY_ROWS = {
    "Acetonitrile": (229.32, 1.87e2, 545.5, 4.852e6),
    "Benzamide": (403.0, 3.55e2, 824.0, 5.047e6),
    "EthyleneGlycol": (260.15, 2.19e-1, 720.0, 8.257e6),
    "MethylPropionate": (185.65, 6.34e-1, 530.6, 4.028e6),
    "Tetrahydrofuran": (164.65, 1.96e-1, 540.15, 5.203e6),
}

PLACEHOLDERS = {"Air", "Gas", "Vapor", "Oil", "OrganicLiquid", "InorganicLiquid"}
# Steam and Water have their own vapour-pressure methods; 2-Nonanol is Perry's
# own inconsistent row (see above).
NOT_CHECKED_AT_TC = PLACEHOLDERS | {"Steam", "Water", "_2Nonanol"}

ATOMIC_MASS = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007, "S": 32.06, "Cl": 35.45,
               "Br": 79.904, "F": 18.998, "Si": 28.085, "Ar": 39.948, "D": 2.014,
               "He": 4.0026, "Ne": 20.180}


def _pvap(name, t_k):
    return getattr(components, name)(temperature=Temperature(t_k, "K")).vapor_pressure().to("Pa").value


@pytest.mark.parametrize("name", sorted(PERRY_ROWS))
def test_the_tables_own_vapour_pressure_comes_back_at_tmin_and_tmax(name):
    t_min, p_min, t_max, p_max = PERRY_ROWS[name]
    assert _pvap(name, t_min) == pytest.approx(p_min, rel=5e-3)
    assert _pvap(name, t_max) == pytest.approx(p_max, rel=5e-3)


@pytest.mark.parametrize("name", sorted(PERRY_ROWS))
def test_the_fixed_components_are_liquids_at_25_c(name):
    assert getattr(components, name)(temperature=Temperature(25, "C")).phase() == "liquid"


def _components():
    return [name for name in components.__all__ if name != "Component"]


def test_every_vapour_pressure_reaches_the_critical_pressure_at_tc():
    off = []
    for name in _components():
        if name in NOT_CHECKED_AT_TC:
            continue
        cls = getattr(components, name)
        tc = cls._critical_temperature.to("K").value
        ratio = _pvap(name, tc) / cls._critical_pressure.to("Pa").value
        if not 0.5 < ratio < 2.0:
            off.append((name, ratio))
    assert off == []


def test_every_formula_is_plain_and_gives_the_molecular_weight():
    wrong = []
    for name in _components():
        if name in PLACEHOLDERS:
            continue
        cls = getattr(components, name)
        formula = cls.formula
        atoms = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
        if "".join(a + n for a, n in atoms) != formula:
            wrong.append((name, formula))
            continue
        mass = sum(ATOMIC_MASS[a] * (int(n) if n else 1) for a, n in atoms)
        if abs(mass - cls.molecular_weight) > 0.01 * cls.molecular_weight:
            wrong.append((name, formula, round(mass, 2), cls.molecular_weight))
    assert wrong == []
