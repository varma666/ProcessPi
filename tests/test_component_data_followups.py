"""Regression tests for component data follow-ups: the liquid Cp Eq. (2) of
Ammonia, Ethane, 1,2-Butanediol and 1,3-Butanediol, the Ethylene class name,
and the 1-Propanol constants.

Reference values:
- Perry's Chemical Engineers' Handbook, 8th ed. (2008), Section 2: Table 2-153
  (liquid Cp, "use Eq. (2)" rows, pp. 2-165 and 2-167) and Table 2-156
  (ideal-gas Cp, DIPPR Eq. 107, pp. 2-176 and 2-178). Each table lists the
  property at its own Tmin and Tmax, which checks the equation form and the
  constants.
  1-Propanol: Tables 2-8 (p. 2-59), 2-150 (p. 2-154) and 2-153 (p. 2-169).
- NIST Chemistry WebBook, SRD 69, fluid properties (fetched 2026-10-12):
  saturated liquid Cp of ammonia and ethane, and Cp on the 0.101325 MPa isobar.
  1-Propanol (CAS 71-23-8) phase-change and condensed-phase pages.
"""
import warnings

import pytest

from processpi.units import Pressure, Temperature
from processpi.components import Ammonia, Ethane, _12Butanediol, _13Butanediol


def _cp_kmol(component):
    """Cp in J/(kmol K), the unit Perry's tables print."""
    return component.specific_heat().value * component.molecular_weight


# ----------------------------------------------------------------------
# Liquid Cp, Perry's Table 2-153, Eq. (2)
# ----------------------------------------------------------------------
# (class, T in K, Cp in J/(kmol K) printed at Tmin and Tmax)
EQ2_TABLE_2_153 = [
    (Ammonia, 203.15, 0.7575e5),
    (Ammonia, 401.15, 4.1847e5),
    (Ethane, 92.00, 0.6855e5),
    (Ethane, 290.00, 1.2444e5),
    (_12Butanediol, 220.00, 1.5590e5),
    (_12Butanediol, 670.00, 5.2045e5),
    (_13Butanediol, 196.15, 0.6251e5),
    (_13Butanediol, 670.00, 5.2437e5),
]


@pytest.mark.parametrize("cls, T, cp_kmol", EQ2_TABLE_2_153)
def test_liquid_cp_eq2_matches_perry_table_2_153(cls, T, cp_kmol):
    # The old code had C1/t for C1^2/t, C1^2 for C4^2 in the last term and
    # returned J/(kmol K) as J/(kg K): 111900 "J/kgK" for ammonia at 203.15 K.
    liquid = cls(temperature=Temperature(T, "K"), phase="liquid")
    assert _cp_kmol(liquid) == pytest.approx(cp_kmol, rel=5e-4)


@pytest.mark.parametrize("cls, T, cp_nist", [
    (Ammonia, 239.711, 4464.86),  # saturated liquid at 0.1007 MPa
    (Ethane, 148.034, 2328.14),   # saturated liquid at 0.0081 MPa
])
def test_liquid_cp_eq2_matches_nist(cls, T, cp_nist):
    liquid = cls(temperature=Temperature(T, "K"), phase="liquid")
    assert liquid.specific_heat().value == pytest.approx(cp_nist, rel=0.01)


def test_liquid_cp_is_per_kg():
    # 1,2-Butanediol at 25 C: Eq. (2) gives 231030 J/(kmol K), 2563.5 J/kgK.
    bd = _12Butanediol(temperature=Temperature(25, "C"))
    assert bd.phase() == "liquid"
    assert bd.specific_heat().value == pytest.approx(2563.5, rel=1e-3)


def test_specific_heat_works_as_property_and_method():
    nh3 = Ammonia(temperature=Temperature(239.711, "K"), phase="liquid")
    assert nh3.specific_heat.value.value == nh3.specific_heat().value


# ----------------------------------------------------------------------
# Gas phase: ideal-gas Cp, Perry's Table 2-156
# ----------------------------------------------------------------------
@pytest.mark.parametrize("cls, T, cp_kmol", [
    (Ammonia, 100, 0.3343e5),
    (Ammonia, 1500, 0.6647e5),
    (Ethane, 200, 0.4256e5),
    (Ethane, 1500, 1.4562e5),
])
def test_ideal_gas_cp_matches_perry_table_2_156(cls, T, cp_kmol):
    gas = cls(temperature=Temperature(T, "K"), phase="gas")
    assert _cp_kmol(gas) == pytest.approx(cp_kmol, rel=5e-4)


@pytest.mark.parametrize("cls, T, cp_nist, rel", [
    (Ammonia, 300, 2163.38, 0.04),   # real gas at 1 atm, 3.4 % above ideal
    (Ammonia, 400, 2286.84, 0.01),
    (Ethane, 300, 1764.37, 0.01),
    (Ethane, 400, 2181.26, 0.01),
])
def test_gas_cp_at_one_atm_matches_nist(cls, T, cp_nist, rel):
    gas = cls(temperature=Temperature(T, "K"), pressure=Pressure(101325, "Pa"))
    assert gas.phase() == "gas"
    assert gas.specific_heat().value == pytest.approx(cp_nist, rel=rel)


# ----------------------------------------------------------------------
# Ethylene: correct class name, old name still works
# ----------------------------------------------------------------------
def test_ethylene_imports_under_its_name():
    from processpi.components import Ethylene

    c2h4 = Ethylene(temperature=Temperature(25, "C"))
    assert c2h4.name == "Ethylene"
    assert c2h4.formula == "C2H4"
    assert c2h4.density().value > 0


def test_misspelt_ethylene_warns_and_still_works():
    from processpi.components import Ethlylene, Ethylene

    with pytest.warns(DeprecationWarning, match="Ethylene"):
        old = Ethlylene(temperature=Temperature(25, "C"))
    assert isinstance(old, Ethylene)
    new = Ethylene(temperature=Temperature(25, "C"))
    assert old.density().value == new.density().value


def test_new_ethylene_name_does_not_warn():
    from processpi.components import Ethylene

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        Ethylene()


# ----------------------------------------------------------------------
# 1-Propanol: enthalpy, Cp and vapour-pressure constants
# ----------------------------------------------------------------------
def _propanol(T):
    from processpi.components import _1Propanol

    return _1Propanol(temperature=Temperature(T, "K"))


def test_propanol_enthalpy_runs_and_matches_perry_table_2_150():
    # Used to raise "not enough values to unpack (expected 5, got 4)".
    # Table 2-150, p. 2-154: Hv = 5.8356E7 J/kmol at Tmin = 146.95 K.
    c3 = _propanol(146.95)
    assert c3.enthalpy().value * c3.molecular_weight == pytest.approx(5.8356e7, rel=5e-4)


def test_propanol_enthalpy_matches_nist():
    # NIST WebBook: 41.44 kJ/mol at 370.3 K (Majer and Svoboda, 1985).
    c3 = _propanol(370.3)
    assert c3.enthalpy().value * c3.molecular_weight / 1e6 == pytest.approx(41.44, rel=0.01)


@pytest.mark.parametrize("T, cp_kmol", [(146.95, 1.0797e5), (400.00, 2.1980e5)])
def test_propanol_cp_matches_perry_table_2_153(T, cp_kmol):
    # Used to raise "too many values to unpack (expected 5)".
    c3 = _propanol(T)
    assert _cp_kmol(c3) == pytest.approx(cp_kmol, rel=5e-4)


def test_propanol_cp_matches_nist():
    # NIST WebBook: 143.96 J/(mol K) at 298.15 K (Tanaka, Toyama, et al., 1986).
    assert _cp_kmol(_propanol(298.15)) / 1000 == pytest.approx(143.96, rel=0.01)


@pytest.mark.parametrize("T, P", [(536.8, 5.170e6), (370.3, 101325)])
def test_propanol_vapor_pressure(T, P):
    # Table 2-8, p. 2-59, P at Tmax; and 1 atm at the normal boiling point,
    # 370.3 +/- 0.5 K (NIST WebBook). With C2 = 0.0 it gave 3.5E15 Pa at 25 C.
    assert _propanol(T).vapor_pressure().value == pytest.approx(P, rel=0.01)


def test_propanol_is_liquid_at_25_c():
    c3 = _propanol(298.15)
    assert c3.phase() == "liquid"
    assert c3.formula == "C3H8O"
    assert c3.density().value == pytest.approx(799.5, rel=1e-3)
