"""Regression tests for component data follow-ups: the liquid Cp Eq. (2) of
Ammonia, Ethane, 1,2-Butanediol and 1,3-Butanediol (with gas-phase Cp and k
for ammonia and ethane), the Ethylene class name, the 1-Propanol constants,
the new Cyclohexane component, and the heat-of-vaporization C1 of four
"A" components.

Reference values:
- Perry's Chemical Engineers' Handbook, 8th ed. (2008), Section 2: Table 2-153
  (liquid Cp, "use Eq. (2)" rows, pp. 2-165 and 2-167), Table 2-156 (ideal-gas
  Cp, DIPPR Eq. 107, pp. 2-176 and 2-178) and Table 2-314 (vapour k, DIPPR
  Eq. 102, pp. 2-433 and 2-435). Each table lists the property at its own Tmin
  and Tmax, which checks the equation form and the constants.
  1-Propanol: Tables 2-8 (p. 2-59), 2-150 (p. 2-154) and 2-153 (p. 2-169).
  Acetaldehyde, acetamide, acetic anhydride, acrylonitrile: Table 2-150
  (p. 2-150) and Table 2-8 (p. 2-55).
- NIST Chemistry WebBook, SRD 69, fluid properties (fetched 2026-10-12):
  saturated liquid Cp of ammonia and ethane, and Cp and k on the 0.101325 MPa
  isobar.
  1-Propanol (CAS 71-23-8) phase-change and condensed-phase pages.
  Cyclohexane (CAS 110-82-7): fluid properties and gas-phase Cp.
  Acetaldehyde and acrylonitrile phase-change pages.
- Cyclohexane constants: Perry's 8th ed., compound no. 65, Tables 2-8, 2-32,
  2-141, 2-150, 2-153, 2-156, 2-313, 2-314 and 2-315.
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


# ----------------------------------------------------------------------
# Cyclohexane: new component, Perry's 8th ed. constants
# ----------------------------------------------------------------------
def _cyclohexane(T, phase=None):
    from processpi.components import Cyclohexane

    return Cyclohexane(temperature=Temperature(T, "K"), pressure=Pressure(101325, "Pa"), phase=phase)


# (property, T in K, phase, value printed at Tmin or Tmax, scale to the
# printed unit). Densities in mol/dm3 and Cp and Hv in J/kmol(K), as printed.
CYCLOHEXANE_PERRY = [
    ("density", 279.69, "liquid", 9.380, "per_kmol"),        # Table 2-32, p. 2-99
    ("density", 553.80, "liquid", 3.2509, "per_kmol"),
    ("specific_heat", 279.69, "liquid", 1.4836e5, "kmol"),  # Table 2-153, p. 2-166
    ("specific_heat", 400.00, "liquid", 2.0323e5, "kmol"),
    ("viscosity", 279.69, "liquid", 1.260e-3, None),        # Table 2-313, p. 2-428
    ("viscosity", 443.04, "liquid", 2.070e-4, None),
    ("thermal_conductivity", 279.69, "liquid", 0.1281, None),  # Table 2-315, p. 2-440
    ("thermal_conductivity", 353.87, "liquid", 0.1095, None),
    ("vapor_pressure", 279.69, "liquid", 5.36e3, None),     # Table 2-8, p. 2-56
    ("vapor_pressure", 553.80, "liquid", 4.094e6, None),
    ("enthalpy", 279.69, "liquid", 3.3920e7, "kmol"),       # Table 2-150, p. 2-151
    ("specific_heat", 100, "gas", 0.4366e5, "kmol"),        # Table 2-156, p. 2-177
    ("specific_heat", 1500, "gas", 3.6516e5, "kmol"),
    ("thermal_conductivity", 325, "gas", 0.01380, None),    # Table 2-314, p. 2-434
    ("thermal_conductivity", 1000, "gas", 0.14198, None),
]


@pytest.mark.parametrize("prop, T, phase, expected, scale", CYCLOHEXANE_PERRY)
def test_cyclohexane_matches_perry_tables(prop, T, phase, expected, scale):
    c6h12 = _cyclohexane(T, phase)
    value = getattr(c6h12, prop)().value
    if scale == "kmol":
        value *= c6h12.molecular_weight
    elif scale == "per_kmol":
        value /= c6h12.molecular_weight
    # The tables print 4 or 5 significant figures, computed from unrounded
    # constants; the largest gap is the viscosity at Tmin, 0.28 %.
    assert value == pytest.approx(expected, rel=3e-3)


def test_cyclohexane_constants_match_perry_table_2_141():
    from processpi.components import Cyclohexane

    assert Cyclohexane.formula == "C6H12"
    assert Cyclohexane.molecular_weight == 84.159
    assert Cyclohexane._critical_temperature.to("K").value == 553.8
    assert Cyclohexane._critical_pressure.value == pytest.approx(4.08e6)  # Pa
    assert Cyclohexane._critical_acentric_factor == 0.2081


# NIST WebBook fluid properties (fetched 2026-10-12), isobar at 0.101325 MPa.
@pytest.mark.parametrize("T, rho, cp, mu, k", [
    (300, 772.218, 1867.60, 8.63709e-4, 0.117611),
    (350, 723.390, 2108.52, 4.30496e-4, 0.105872),
])
def test_cyclohexane_liquid_matches_nist(T, rho, cp, mu, k):
    c6h12 = _cyclohexane(T)
    assert c6h12.phase() == "liquid"
    assert c6h12.density().value == pytest.approx(rho, rel=0.005)
    assert c6h12.specific_heat().value == pytest.approx(cp, rel=0.02)
    assert c6h12.viscosity().value == pytest.approx(mu, rel=0.01)
    # Perry's DIPPR k is 4.3-4.6 % above the NIST correlation here.
    assert c6h12.thermal_conductivity().value == pytest.approx(k, rel=0.05)


@pytest.mark.parametrize("T, P", [
    (296.611, 0.0121406e6),
    (325.330, 0.0393083e6),
    (353.865, 0.101325e6),  # normal boiling point
])
def test_cyclohexane_vapor_pressure_matches_nist(T, P):
    assert _cyclohexane(T, "liquid").vapor_pressure().value == pytest.approx(P, rel=0.005)


@pytest.mark.parametrize("T, hv", [(296.611, 393.481e3), (353.865, 356.362e3)])
def test_cyclohexane_heat_of_vaporization_matches_nist(T, hv):
    # NIST saturated vapour minus saturated liquid enthalpy, J/kg.
    assert _cyclohexane(T, "liquid").enthalpy().value == pytest.approx(hv, rel=0.005)


@pytest.mark.parametrize("T, cp_mol", [(400, 148.64), (500, 188.68), (1000, 314.42)])
def test_cyclohexane_ideal_gas_cp_matches_nist(T, cp_mol):
    # NIST gas-phase Cp, J/(mol K) (Dorofeeva, 1986).
    c6h12 = _cyclohexane(T)
    assert c6h12.phase() == "gas"
    assert c6h12.specific_heat().value * c6h12.molecular_weight / 1000 == pytest.approx(cp_mol, rel=0.01)


@pytest.mark.parametrize("T, k", [(400, 0.0218486), (500, 0.0352067), (600, 0.0503773)])
def test_cyclohexane_vapor_k_matches_nist(T, k):
    c6h12 = _cyclohexane(T)
    assert c6h12.phase() == "gas"
    assert c6h12.thermal_conductivity().value == pytest.approx(k, rel=0.015)


def test_cyclohexane_docs_example_runs():
    from processpi.components import Cyclohexane

    c6h12 = Cyclohexane(temperature=Temperature(25, "C"))
    assert c6h12.phase() == "liquid"
    # NIST WebBook, 298.15 K and 0.101325 MPa: 773.966 kg/m3.
    assert c6h12.density().value == pytest.approx(773.966, rel=0.005)
    assert c6h12.enthalpy().value > 0


# ----------------------------------------------------------------------
# Ammonia and ethane gas: vapour k, Perry's Table 2-314
# ----------------------------------------------------------------------
@pytest.mark.parametrize("cls, T, k", [
    (Ammonia, 200, 0.01446),   # p. 2-433
    (Ammonia, 900, 0.11523),
    (Ethane, 184.55, 0.00886),  # p. 2-435
    (Ethane, 1000, 0.15807),
])
def test_vapor_k_matches_perry_table_2_314(cls, T, k):
    gas = cls(temperature=Temperature(T, "K"), phase="gas")
    assert gas.thermal_conductivity().value == pytest.approx(k, rel=1e-3)


@pytest.mark.parametrize("cls, T, k_nist, rel", [
    (Ammonia, 300, 0.0253719, 0.01),
    (Ammonia, 400, 0.0374695, 0.01),
    (Ethane, 300, 0.0209725, 0.04),  # Perry's fit is 3.7 % above NIST here
    (Ethane, 400, 0.0358207, 0.01),
])
def test_gas_k_at_one_atm_matches_nist(cls, T, k_nist, rel):
    # Used to return the liquid polynomial: 0.475 W/mK for ammonia at 300 K.
    gas = cls(temperature=Temperature(T, "K"), pressure=Pressure(101325, "Pa"))
    assert gas.phase() == "gas"
    assert gas.thermal_conductivity().value == pytest.approx(k_nist, rel=rel)


# ----------------------------------------------------------------------
# Heat of vaporization C1 given as the table's "C1 x 1E-07" number
# ----------------------------------------------------------------------
@pytest.mark.parametrize("name, T, hv_kmol", [
    ("Acetaldehyde", 150.15, 3.2828e7),   # Table 2-150, p. 2-150, Hv at Tmin
    ("Acetamide", 353.15, 6.2386e7),
    ("AceticAnhydride", 200.15, 5.4139e7),
    ("Acrylonitrile", 189.63, 3.6866e7),
])
def test_heat_of_vaporization_matches_perry_table_2_150(name, T, hv_kmol):
    # C1 was 3.8366 for 3.8366E7 J/kmol, so Hv came out near 0.05 J/kg.
    import processpi.components as components

    c = getattr(components, name)(temperature=Temperature(T, "K"))
    assert c.enthalpy().value * c.molecular_weight == pytest.approx(hv_kmol, rel=5e-4)


@pytest.mark.parametrize("name, T, hv_mol", [
    ("Acetaldehyde", 293.3, 25.76),   # NIST WebBook, Majer and Svoboda, 1985
    ("Acrylonitrile", 308.0, 32.9),   # NIST WebBook, Gubkov, Fermor, et al., 1964
])
def test_heat_of_vaporization_matches_nist(name, T, hv_mol):
    import processpi.components as components

    c = getattr(components, name)(temperature=Temperature(T, "K"))
    assert c.enthalpy().value * c.molecular_weight / 1e6 == pytest.approx(hv_mol, rel=0.01)


@pytest.mark.parametrize("T, P", [(150.15, 3.23e-1), (466.0, 5.565e6)])
def test_acetaldehyde_vapor_pressure_matches_perry_table_2_8(T, P):
    # C2 was 0.0 for -8,036.7 (Table 2-8, p. 2-55).
    from processpi.components import Acetaldehyde

    vp = Acetaldehyde(temperature=Temperature(T, "K")).vapor_pressure().value
    # C4 is stored rounded (0.0437 for 4.3678E-02): 1 % at Tmax.
    assert vp == pytest.approx(P, rel=0.015)


def test_acetaldehyde_boils_near_20_c():
    # NIST WebBook Tboil 294.0 +/- 0.8 K: liquid at 10 C, gas at 25 C and 1 atm.
    from processpi.components import Acetaldehyde

    assert Acetaldehyde(temperature=Temperature(10, "C")).phase() == "liquid"
    assert Acetaldehyde(temperature=Temperature(25, "C")).phase() == "gas"
