"""The generic Vapor and Gas placeholders are gases unless a phase is given.

The docs example of `Vapor` (docs/user-guide/components/vapor.md: water
vapour, molecular_weight 18.015, 100 C, 1 atm) printed phase "liquid" and a
density of 138 kg/m3. `Component.phase()` compares the pressure with the
vapour pressure from `_vapor_pressure_constants`, and Vapor's (and Gas's)
placeholder constants [50, -5000, -6.8, 5e-6, 2] are not data for any
substance:

    ln Pvap = 50 - 5000/373.15 - 6.8 ln(373.15) + 5e-6 x 373.15^2
            = 50 - 13.399 - 40.270 + 0.696 = -2.973
    Pvap = 0.051 Pa  <  101325 Pa  ->  "liquid"

so `density()` took the liquid DIPPR 105 branch with Vapor's made-up
constants [a, b, Tc, n] = [1.0, 0.25, 400, 0.28]. Its `T_celsius` is the SI
value, 373.15 K, so 1 - 373.15/400 = 0.06713, 0.06713^0.28 = 0.46938, and
rho = 1.0 / 0.25^1.46938 x 18.015 = 7.666 x 18.015 = 138.1 kg/m3. Above
Tc = 400 K (for example 200 C) the same branch raised a TypeError on a
complex density. Gas hid the same wrong phase behind its own ideal-gas
`density()`, but its viscosity came from the liquid correlation
(9.25e-3 Pa s at 25 C).

Both classes now report "gas" unless a phase is given, so the base class
takes its ideal-gas branch, rho = P M / (R T), with R = 8.314462618 J/(mol K)
(processpi.constants) and M in kg/mol.
"""

import math

import pytest

from processpi.components import Benzene, Gas, Vapor, Water
from processpi.streams import MaterialStream
from processpi.units import MassFlowRate, Pressure, Temperature

R = 8.314462618  # J/(mol K), processpi.constants.R_UNIVERSAL


def _rho_ideal(p_pa, mw_g_mol, t_k, r=R):
    return p_pa * mw_g_mol / 1000.0 / (r * t_k)


def _sutherland(t_k, mu0=1.8e-5, t0=300.0, c=120.0):
    # Component.viscosity() gas branch, with its default constants.
    return mu0 * (t0 + c) / (t_k + c) * (t_k / t0) ** 1.5


def test_docs_water_vapour_at_100_c_is_an_ideal_gas():
    vapour = Vapor(temperature=Temperature(100, "C"), pressure=Pressure(1, "atm"))
    vapour.molecular_weight = 18.015

    # Before: "liquid" and 138.13 kg/m3.
    assert vapour.phase() == "gas"
    # 101325 x 0.018015 / (8.314462618 x 373.15) = 1825.37 / 3102.57
    # = 0.58834 kg/m3.
    rho = vapour.density().to("kg/m3").value
    assert rho == pytest.approx(0.58834, rel=1e-4)
    assert rho == pytest.approx(_rho_ideal(101325.0, 18.015, 373.15), rel=1e-9)


def test_vapor_class_defaults_are_an_ideal_gas():
    # 25 C, 1 atm, 28 g/mol: 101325 x 0.028 / (8.314462618 x 298.15)
    # = 2837.10 / 2478.98 = 1.14446 kg/m3 (before: liquid, 288.2 kg/m3).
    vapour = Vapor()
    assert vapour.phase() == "gas"
    assert vapour.density().to("kg/m3").value == pytest.approx(1.14446, rel=1e-4)


def test_vapor_density_follows_pressure_and_temperature():
    # 5 bar, 200 C, 28 g/mol: 500000 x 0.028 / (8.314462618 x 473.15)
    # = 14000 / 3933.97 = 3.55875 kg/m3. Before: TypeError (complex liquid
    # density above the placeholder Tc of 400 K).
    vapour = Vapor(temperature=Temperature(200, "C"), pressure=Pressure(5, "bar"))
    assert vapour.density().to("kg/m3").value == pytest.approx(3.55875, rel=1e-4)


def test_vapor_viscosity_takes_the_gas_branch():
    # Sutherland at 373.15 K: 1.8e-5 x 420 / 493.15 x (373.15/300)^1.5
    # = 1.8e-5 x 0.85167 x 1.38722 = 2.1266e-5 Pa s. Before, the liquid
    # correlation exp(-10.5 + 800/T + 0.55 ln T) gave 6.10e-3 Pa s.
    vapour = Vapor(temperature=Temperature(100, "C"))
    mu = vapour.viscosity().to("Pa·s").value
    assert mu == pytest.approx(2.1266e-5, rel=1e-4)
    assert mu == pytest.approx(_sutherland(373.15), rel=1e-9)


def test_gas_placeholder_reports_gas():
    gas = Gas(temperature=Temperature(25, "C"), pressure=Pressure(1, "atm"))
    # Before: "liquid" (the same placeholder vapour-pressure constants).
    assert gas.phase() == "gas"
    # Gas keeps its own density(), with R = 8.314 J/(mol K) from
    # components/constants.py: 2837.10 / (8.314 x 298.15) = 1.14454 kg/m3.
    assert gas.density().to("kg/m3").value == pytest.approx(
        _rho_ideal(101325.0, 28.0, 298.15, r=8.314), rel=1e-9
    )
    # Sutherland at 298.15 K: 1.8e-5 x 420/418.15 x (298.15/300)^1.5
    # = 1.7914e-5 Pa s (before, liquid correlation: 9.25e-3 Pa s).
    assert gas.viscosity().to("Pa·s").value == pytest.approx(1.7914e-5, rel=1e-4)


def test_a_given_phase_still_wins():
    # A condensed outlet stream of a generic vapour can still say "liquid".
    vapour = Vapor(temperature=Temperature(100, "C"), phase="liquid")
    assert vapour.phase() == "liquid"
    gas = Gas(phase="liquid")
    assert gas.phase() == "liquid"


def test_stream_of_vapor_carries_the_ideal_gas_density():
    stream = MaterialStream(
        "vapour",
        component=Vapor(),
        temperature=Temperature(100, "C"),
        pressure=Pressure(1, "atm"),
        mass_flow=MassFlowRate(1, "kg/s"),
    )
    # 101325 x 0.028 / (8.314462618 x 373.15) = 2837.10 / 3102.57 = 0.91444.
    assert stream.density.to("kg/m3").value == pytest.approx(0.91444, rel=1e-4)
    assert stream.component.phase() == "gas"


def test_real_components_keep_the_vapour_pressure_test():
    # Guards: only the placeholders get a default phase.
    assert Water(temperature=Temperature(25, "C")).phase() == "liquid"
    # Benzene boils at 80.1 C at 1 atm.
    assert Benzene(temperature=Temperature(25, "C")).phase() == "liquid"
    assert Benzene(temperature=Temperature(120, "C")).phase() == "gas"
