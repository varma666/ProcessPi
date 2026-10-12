"""Regression tests for the docs examples that crashed in the component and
calculation pages (air, carbon_monoxide, steam, ethylacetate, cyclohexene,
flow_regime).

Reference values:
- Perry's Chemical Engineers' Handbook, 8th ed. (2008), Section 2: Table 2-153
  (liquid Cp, p. 2-165), Table 2-156 (ideal-gas Cp, DIPPR Eq. 107, p. 2-176),
  Table 2-314 (vapour k, DIPPR Eq. 102, p. 2-433), Table 2-315 (liquid k,
  p. 2-439). Each table lists the property at its own Tmin and Tmax, which
  checks the equation form and the constants.
- NIST Chemistry WebBook, SRD 69, fluid properties, isobar at 0.101325 MPa:
  carbon monoxide Cp and k, water Cp at 423.15 K.
- The Engineering ToolBox, "Specific Heat Capacity of Air" (1.006 kJ/kgK at
  300 K, 1 bar) and "Air Properties - Thermal Conductivity" (26.24 mW/mK at
  25 C).
"""
import warnings

import pytest

from processpi.units import Dimensionless, Pressure, Temperature
from processpi.components import Air, CarbonMonoxide, Cyclohexene
from processpi.calculations import CalculationEngine
from processpi.calculations.fluids.flow_type import TypeOfFlow


# ----------------------------------------------------------------------
# Air: gas-phase Cp and k
# ----------------------------------------------------------------------
def test_air_docs_example_runs():
    # Used to raise "Unphysical Cp detected: 162856.9 J/kgK", then
    # "Thermal conductivity cannot be negative." (liquid-air constants at 35 C).
    air = Air(temperature=Temperature(35, "C"))
    assert air.phase() == "gas"
    assert air.specific_heat().value == pytest.approx(1001.5, rel=1e-3)
    assert air.thermal_conductivity().value == pytest.approx(0.02669, rel=1e-3)


def test_air_cp_at_300_k_matches_reference():
    cp = Air(temperature=Temperature(300, "K")).specific_heat().value
    assert cp == pytest.approx(1006.0, rel=0.01)  # Engineering ToolBox, 1 bar


@pytest.mark.parametrize("T, cp_kmol", [(50, 0.2896e5), (1500, 0.3496e5)])
def test_air_ideal_gas_cp_matches_perry_table_2_156(T, cp_kmol):
    air = Air(temperature=Temperature(T, "K"), pressure=Pressure(100, "Pa"))
    assert air.phase() == "gas"
    assert air.specific_heat().value * Air.molecular_weight == pytest.approx(cp_kmol, rel=5e-4)


def test_air_k_at_25_c_matches_reference():
    k = Air(temperature=Temperature(25, "C")).thermal_conductivity().value
    assert k == pytest.approx(0.02624, rel=0.02)  # Engineering ToolBox


@pytest.mark.parametrize("T, k", [(70, 0.00603), (2000, 0.11675)])
def test_air_vapor_k_matches_perry_table_2_314(T, k):
    air = Air(temperature=Temperature(T, "K"), pressure=Pressure(100, "Pa"))
    assert air.thermal_conductivity().value == pytest.approx(k, rel=1e-3)


def test_liquid_air_keeps_the_liquid_correlations():
    # 90 K and 5 bar is liquid; Table 2-153 and Table 2-315 still apply.
    air = Air(temperature=Temperature(90, "K"), pressure=Pressure(5, "bar"))
    assert air.phase() == "liquid"
    T = 90.0
    cp_kmol = -214460 + 9185.1 * T - 106.12 * T**2 + 0.41616 * T**3
    assert air.specific_heat().value == pytest.approx(cp_kmol / 28.96, rel=1e-6)
    assert air.thermal_conductivity().value == pytest.approx(0.28472 - 0.0017393 * T, rel=1e-4)


# ----------------------------------------------------------------------
# Carbon monoxide: gas-phase k (and Cp)
# ----------------------------------------------------------------------
def test_carbon_monoxide_docs_example_runs():
    # Used to raise "Thermal conductivity cannot be negative." and print
    # Cp = 354050 J/kgK.
    co = CarbonMonoxide(temperature=Temperature(25, "C"))
    assert co.phase() == "gas"
    assert co.thermal_conductivity().value == pytest.approx(0.02496, rel=1e-3)
    assert co.specific_heat().value == pytest.approx(1040.3, rel=1e-3)


# NIST WebBook, carbon monoxide, 0.101325 MPa.
NIST_CO = [
    # T (K), Cp (J/kgK), k (W/mK)
    (200, 1043.9, 0.017450),
    (250, 1042.2, 0.021365),
    (300, 1042.2, 0.025028),
    (350, 1044.1, 0.028485),
    (400, 1048.4, 0.031770),
    (450, 1055.1, 0.034900),
    (500, 1064.2, 0.037874),
]


@pytest.mark.parametrize("T, cp, k", NIST_CO)
def test_carbon_monoxide_gas_k_positive_and_matches_nist(T, cp, k):
    co = CarbonMonoxide(temperature=Temperature(T, "K"))
    value = co.thermal_conductivity().value
    assert value > 0
    assert value == pytest.approx(k, rel=0.02)


@pytest.mark.parametrize("T, cp, k", NIST_CO)
def test_carbon_monoxide_gas_cp_matches_nist(T, cp, k):
    co = CarbonMonoxide(temperature=Temperature(T, "K"))
    assert co.specific_heat().value == pytest.approx(cp, rel=0.01)


@pytest.mark.parametrize("T, k", [(70, 0.00576), (1500, 0.08724)])
def test_carbon_monoxide_vapor_k_matches_perry_table_2_314(T, k):
    co = CarbonMonoxide(temperature=Temperature(T, "K"), pressure=Pressure(100, "Pa"))
    assert co.thermal_conductivity().value == pytest.approx(k, rel=1e-3)


@pytest.mark.parametrize("T, cp_kmol", [(60, 0.2911e5), (1500, 0.3521e5)])
def test_carbon_monoxide_ideal_gas_cp_matches_perry_table_2_156(T, cp_kmol):
    co = CarbonMonoxide(temperature=Temperature(T, "K"), pressure=Pressure(100, "Pa"))
    assert co.specific_heat().value * CarbonMonoxide.molecular_weight == pytest.approx(cp_kmol, rel=5e-4)


@pytest.mark.parametrize("T, P_bar, cp_kmol", [(68.15, 1, 0.5912e5), (132.0, 40, 6.4799e5)])
def test_liquid_carbon_monoxide_cp_matches_perry_table_2_153(T, P_bar, cp_kmol):
    # Eq. (2) of Table 2-153 with C4 = 1959.6 (it was split into 1 and 959.60).
    co = CarbonMonoxide(temperature=Temperature(T, "K"), pressure=Pressure(P_bar, "bar"))
    assert co.phase() == "liquid"
    assert co.specific_heat().value * CarbonMonoxide.molecular_weight == pytest.approx(cp_kmol, rel=5e-4)


def test_liquid_carbon_monoxide_keeps_the_liquid_k():
    co = CarbonMonoxide(temperature=Temperature(68.15, "K"))
    assert co.phase() == "liquid"
    assert co.thermal_conductivity().value == pytest.approx(0.1639, rel=1e-3)


# ----------------------------------------------------------------------
# Steam: CoolProp output key
# ----------------------------------------------------------------------
def test_steam_docs_example_runs():
    pytest.importorskip("CoolProp")
    from processpi.components import Steam

    steam = Steam(temperature=Temperature(150, "C"))
    # Used to raise "Output string is invalid [CP]"; NIST WebBook gives
    # 1.9856 kJ/kgK for water vapour at 423.15 K and 0.101325 MPa.
    assert steam.specific_heat().value == pytest.approx(1985.6, rel=1e-3)
    # Used to raise "'str' object is not callable".
    assert steam.phase() == "gas"
    assert Steam(temperature=Temperature(50, "C"), phase="liquid").phase() == "liquid"


# ----------------------------------------------------------------------
# EthylAcetate: correct class name, old name still works
# ----------------------------------------------------------------------
def test_ethyl_acetate_imports_under_its_name():
    from processpi.components import EthylAcetate

    ea = EthylAcetate(temperature=Temperature(25, "C"))
    assert ea.name == "Ethyl Acetate"
    assert ea.formula == "C4H8O2"
    assert ea.density().value > 0


def test_misspelt_ethyl_acetate_warns_and_still_works():
    from processpi.components import EthlylAcetate, EthylAcetate

    with pytest.warns(DeprecationWarning, match="EthylAcetate"):
        old = EthlylAcetate(temperature=Temperature(25, "C"))
    assert isinstance(old, EthylAcetate)
    new = EthylAcetate(temperature=Temperature(25, "C"))
    assert old.density().value == new.density().value


def test_new_ethyl_acetate_name_does_not_warn():
    from processpi.components import EthylAcetate

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        EthylAcetate()


# ----------------------------------------------------------------------
# Cyclohexene page: the class it documents exists
# ----------------------------------------------------------------------
def test_cyclohexene_docs_example_runs():
    c6h10 = Cyclohexene(temperature=Temperature(25, "C"))
    assert c6h10.formula == "C6H10"
    assert c6h10.density().value > 0


# ----------------------------------------------------------------------
# TypeOfFlow through the CalculationEngine
# ----------------------------------------------------------------------
@pytest.mark.parametrize("name", ["type_of_flow", "flow_type", "flow_regime"])
@pytest.mark.parametrize("re, expected", [(1500, "Laminar"), (3500, "Transitional"), (10000, "Turbulent")])
def test_type_of_flow_via_engine(name, re, expected):
    result = CalculationEngine().calculate(name, reynolds_number=Dimensionless(re))
    assert result.value == expected
    assert result.value == TypeOfFlow(reynolds_number=Dimensionless(re)).calculate().value
