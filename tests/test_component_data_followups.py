"""Regression tests for component data follow-ups: the liquid Cp Eq. (2) of
Ammonia, Ethane, 1,2-Butanediol and 1,3-Butanediol.

Reference values:
- Perry's Chemical Engineers' Handbook, 8th ed. (2008), Section 2: Table 2-153
  (liquid Cp, "use Eq. (2)" rows, pp. 2-165 and 2-167) and Table 2-156
  (ideal-gas Cp, DIPPR Eq. 107, pp. 2-176 and 2-178). Each table lists the
  property at its own Tmin and Tmax, which checks the equation form and the
  constants.
- NIST Chemistry WebBook, SRD 69, fluid properties (fetched 2026-10-12):
  saturated liquid Cp of ammonia and ethane, and Cp on the 0.101325 MPa isobar.
"""
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
