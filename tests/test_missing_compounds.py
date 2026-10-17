"""The 16 components that processpi.components listed without a file.

Helium, HydrogenChloride, HydrogenCyanide, HydrogenSulfide, Methane, Neon,
Nitrogen, NitrousOxide, NitricOxide, Oxygen, Ozone, Phenol, Propane,
PropionicAcid, Styrene and SulfurDioxide now exist. Every constant is from
Perry's Chemical Engineers' Handbook, 8th ed. (2008), Section 2, read from the
PDF (printed page numbers below):

    Table 2-8    vapour pressure, DIPPR Eq. 101          pp. 2-57 to 2-60
    Table 2-32   liquid density, DIPPR Eq. 105           pp. 2-100 to 2-103
    Table 2-141  critical constants                      pp. 2-140 to 2-142
    Table 2-150  heat of vaporization, DIPPR Eq. 106     pp. 2-152 to 2-155
    Table 2-153  liquid Cp, Eq. (1) or "use Eq. (2)"     pp. 2-167 to 2-170
    Table 2-155  ideal-gas Cp, polynomial (He, Ne, NO)   pp. 2-174, 2-175
    Table 2-156  ideal-gas Cp, DIPPR Eq. 107             pp. 2-179 to 2-181
    Table 2-313  liquid viscosity, DIPPR Eq. 101         pp. 2-429 to 2-432
    Table 2-314  vapour k, DIPPR Eq. 102                 pp. 2-435 to 2-438
    Table 2-315  liquid k, polynomial                    pp. 2-441 to 2-444

Each table prints the property at its own Tmin and Tmax, which checks the
equation form, the column of every constant (several rows leave columns
blank) and the unit conversion. Vapour pressure is held to 0.5 %, the rest to
1 %; the largest gaps are Perry's rounding of the printed values (helium's
heat of vaporization at 2.2 K is printed as 0.0097E7, two digits).

Nitric oxide's Table 2-155 row prints C5 = 0.0014526 under the heading
"C5 x 1E 10"; only C5 = 1.4526E-08 gives the 0.3586E5 the row prints at
1500 K, so that is the value used and tested here.
"""
import pytest

import processpi.components as components
from processpi.units import Pressure, Temperature

NEW = [
    "Helium", "HydrogenChloride", "HydrogenCyanide", "HydrogenSulfide", "Methane",
    "Neon", "Nitrogen", "NitrousOxide", "NitricOxide", "Oxygen", "Ozone", "Phenol",
    "Propane", "PropionicAcid", "Styrene", "SulfurDioxide",
]

# Table 2-8: Pvap in Pa at Tmin and Tmax
VAPOUR_PRESSURE = [
    ("Helium", 1.76, 1.46e+03, 5.2, 2.285e+05),  # p. 2-57
    ("HydrogenChloride", 158.97, 1.35e+04, 324.65, 8.356e+06),  # p. 2-58
    ("HydrogenCyanide", 259.83, 1.87e+04, 456.65, 5.353e+06),  # p. 2-58
    ("HydrogenSulfide", 187.68, 2.29e+04, 373.53, 8.999e+06),  # p. 2-58
    ("Methane", 90.69, 1.17e+04, 190.56, 4.590e+06),  # p. 2-58
    ("Neon", 24.56, 4.38e+04, 44.4, 2.665e+06),  # p. 2-59
    ("Nitrogen", 63.15, 1.25e+04, 126.2, 3.391e+06),  # p. 2-59
    ("NitrousOxide", 182.3, 8.69e+04, 309.57, 7.278e+06),  # p. 2-59
    ("NitricOxide", 109.5, 2.20e+04, 180.15, 6.516e+06),  # p. 2-59
    ("Oxygen", 54.36, 1.48e+02, 154.58, 5.021e+06),  # p. 2-59
    ("Ozone", 80.15, 7.35e-01, 261, 5.566e+06),  # p. 2-59
    ("Phenol", 314.06, 1.88e+02, 694.25, 6.059e+06),  # p. 2-59
    ("Propane", 85.47, 1.68e-04, 369.83, 4.214e+06),  # p. 2-59
    ("PropionicAcid", 252.45, 1.31e+01, 600.81, 4.608e+06),  # p. 2-59
    ("Styrene", 242.54, 1.06e+01, 636, 3.823e+06),  # p. 2-60
    ("SulfurDioxide", 197.67, 1.67e+03, 430.75, 7.860e+06),  # p. 2-60
]

# Table 2-32: liquid density in kmol/m3 (mol/dm3) at Tmin and Tmax
LIQUID_DENSITY = [
    ("Helium", 2.20, 37.115, 5.20, 17.3120),  # p. 2-100
    ("HydrogenChloride", 158.97, 34.854, 324.65, 12.2460),  # p. 2-101
    ("HydrogenCyanide", 259.83, 27.202, 456.65, 7.2156),  # p. 2-101
    ("HydrogenSulfide", 187.68, 29.130, 373.53, 10.1110),  # p. 2-101
    ("Methane", 90.69, 28.180, 190.56, 10.0820),  # p. 2-101
    ("Neon", 24.56, 61.796, 44.40, 24.0360),  # p. 2-102
    ("Nitrogen", 63.15, 31.063, 126.20, 11.2170),  # p. 2-102
    ("NitrousOxide", 182.30, 27.928, 309.57, 10.2080),  # p. 2-102
    ("NitricOxide", 109.50, 44.487, 180.15, 17.2340),  # p. 2-102
    ("Oxygen", 54.35, 40.770, 154.58, 13.6050),  # p. 2-102
    ("Ozone", 80.15, 33.361, 261.00, 11.2410),  # p. 2-102
    ("Phenol", 314.06, 11.244, 694.25, 4.3667),  # p. 2-102
    ("Propane", 85.47, 16.583, 369.83, 5.0111),  # p. 2-102
    ("PropionicAcid", 252.45, 13.935, 600.81, 4.2901),  # p. 2-102
    ("Styrene", 242.54, 9.109, 636.00, 2.8417),  # p. 2-103
    ("SulfurDioxide", 197.67, 25.298, 430.75, 8.1495),  # p. 2-103
]

# Table 2-153: liquid Cp in J/(kmol K) at Tmin and Tmax
LIQUID_CP = [
    ("Helium", 2.20, 0.1087e5, 4.60, 0.2965e5),  # p. 2-167
    ("HydrogenChloride", 165.00, 0.6215e5, 185.00, 0.6395e5),  # p. 2-168
    ("HydrogenCyanide", 259.83, 0.7029e5, 298.85, 0.7105e5),  # p. 2-168
    ("HydrogenSulfide", 187.68, 0.6733e5, 370.00, 4.9183e5),  # p. 2-168
    ("Methane", 90.69, 0.5361e5, 190.00, 14.9780e5),  # p. 2-168
    ("Neon", 24.56, 0.3666e5, 40.00, 0.6980e5),  # p. 2-169
    ("Nitrogen", 63.15, 0.5593e5, 112.00, 0.7960e5),  # p. 2-169
    ("NitrousOxide", 182.30, 0.7747e5, 200.00, 0.7843e5),  # p. 2-169
    ("NitricOxide", 109.50, 0.6229e5, 150.00, 1.9909e5),  # p. 2-169
    ("Oxygen", 54.36, 0.5365e5, 142.00, 0.9066e5),  # p. 2-169
    ("Ozone", 90.00, 0.8535e5, 150.00, 1.0222e5),  # p. 2-169
    ("Phenol", 314.06, 2.0147e5, 425.00, 2.3670e5),  # p. 2-169
    ("Propane", 85.47, 0.8488e5, 360.00, 2.6079e5),  # p. 2-169
    ("PropionicAcid", 252.45, 1.4209e5, 414.32, 2.0756e5),  # p. 2-170
    ("Styrene", 242.54, 1.6749e5, 418.31, 2.2816e5),  # p. 2-170
    ("SulfurDioxide", 197.67, 0.8688e5, 350.00, 0.8775e5),  # p. 2-170
]

# Table 2-156 (Table 2-155 for He, Ne, NO): ideal-gas Cp in J/(kmol K)
IDEAL_GAS_CP = [
    ("Helium", 100, 0.2079e5, 1500, 0.2079e5),  # p. 2-174
    ("HydrogenChloride", 50, 0.2914e5, 1500, 0.3406e5),  # p. 2-179
    ("HydrogenCyanide", 100, 0.3014e5, 1500, 0.5522e5),  # p. 2-179
    ("HydrogenSulfide", 100, 0.3329e5, 1500, 0.5143e5),  # p. 2-179
    ("Methane", 50, 0.3330e5, 1500, 0.8890e5),  # p. 2-179
    ("Neon", 100, 0.2079e5, 1500, 0.2079e5),  # p. 2-175
    ("Nitrogen", 50, 0.2911e5, 1500, 0.3484e5),  # p. 2-180
    ("NitrousOxide", 100, 0.2948e5, 1500, 0.5828e5),  # p. 2-180
    ("NitricOxide", 100, 0.3217e5, 1500, 0.3586e5),  # p. 2-175
    ("Oxygen", 50, 0.2910e5, 1500, 0.3653e5),  # p. 2-180
    ("Ozone", 100, 0.3349e5, 1500, 0.5928e5),  # p. 2-180
    ("Phenol", 100, 0.4401e5, 1500, 2.6045e5),  # p. 2-180
    ("Propane", 200, 0.5632e5, 1500, 2.0556e5),  # p. 2-180
    ("PropionicAcid", 298.15, 0.8938e5, 1500, 2.1248e5),  # p. 2-180
    ("Styrene", 100, 0.8931e5, 1500, 3.2416e5),  # p. 2-181
    ("SulfurDioxide", 100, 0.3354e5, 1500, 0.5695e5),  # p. 2-181
]

# Table 2-313: liquid viscosity in Pa s at Tmin and Tmax
LIQUID_VISCOSITY = [
    ("Helium", 2.20, 3.628e-06, 5.10, 2.532e-06),  # p. 2-429
    ("HydrogenChloride", 158.97, 1.000e-03, 318.15, 5.780e-05),  # p. 2-430
    ("HydrogenCyanide", 259.83, 2.754e-04, 298.85, 1.821e-04),  # p. 2-430
    ("HydrogenSulfide", 187.68, 5.726e-04, 350.00, 8.089e-05),  # p. 2-430
    ("Methane", 90.69, 2.063e-04, 188.00, 2.263e-05),  # p. 2-430
    ("Neon", 25.09, 1.602e-04, 44.13, 2.706e-05),  # p. 2-431
    ("Nitrogen", 63.15, 2.633e-04, 124.00, 3.331e-05),  # p. 2-431
    ("NitrousOxide", 210.00, 2.065e-04, 283.09, 7.730e-05),  # p. 2-431
    ("NitricOxide", 109.50, 3.858e-04, 180.05, 3.791e-05),  # p. 2-431
    ("Oxygen", 54.36, 7.170e-04, 150.00, 6.990e-05),  # p. 2-431
    ("Ozone", 77.55, 3.790e-03, 208.80, 1.300e-04),  # p. 2-431
    ("Phenol", 291.45, 1.270e-02, 555.40, 1.940e-04),  # p. 2-431
    ("Propane", 85.47, 9.458e-03, 360.00, 4.275e-05),  # p. 2-431
    ("PropionicAcid", 252.45, 2.275e-03, 414.32, 3.430e-04),  # p. 2-431
    ("Styrene", 242.54, 1.919e-03, 418.31, 2.268e-04),  # p. 2-432
    ("SulfurDioxide", 225.00, 6.900e-04, 400.00, 6.557e-05),  # p. 2-432
]

# Table 2-315: liquid thermal conductivity in W/(m K) at Tmin and Tmax
LIQUID_K = [
    ("Helium", 2.20, 0.0149, 4.80, 0.0204),  # p. 2-441
    ("HydrogenChloride", 273.15, 0.2303, 323.15, 0.1252),  # p. 2-442
    ("HydrogenCyanide", 259.83, 0.2525, 298.85, 0.2251),  # p. 2-442
    ("HydrogenSulfide", 193.15, 0.2555, 292.42, 0.1380),  # p. 2-442
    ("Methane", 90.69, 0.2245, 180.00, 0.0915),  # p. 2-442
    ("Neon", 25.00, 0.1167, 44.00, 0.0457),  # p. 2-443
    ("Nitrogen", 63.15, 0.1595, 124.00, 0.0575),  # p. 2-443
    ("NitrousOxide", 277.59, 0.1011, 277.59, 0.1011),  # p. 2-443
    ("NitricOxide", 110.00, 0.1869, 176.40, 0.0759),  # p. 2-443
    ("Oxygen", 60.00, 0.1913, 150.00, 0.0671),  # p. 2-443
    ("Ozone", 77.35, 0.2180, 161.85, 0.2306),  # p. 2-443
    ("Phenol", 314.06, 0.1569, 454.99, 0.1428),  # p. 2-443
    ("Propane", 85.47, 0.2128, 350.00, 0.0689),  # p. 2-443
    ("PropionicAcid", 252.45, 0.1540, 543.15, 0.1063),  # p. 2-444
    ("Styrene", 242.54, 0.1488, 418.31, 0.1101),  # p. 2-444
    ("SulfurDioxide", 197.67, 0.2586, 400.00, 0.1320),  # p. 2-444
]

# Table 2-314: vapour thermal conductivity in W/(m K) at Tmin and Tmax
VAPOUR_K = [
    ("Helium", 30.00, 0.03124, 2000, 0.58820),  # p. 2-435
    ("HydrogenChloride", 190.00, 0.00880, 700, 0.03213),  # p. 2-436
    ("HydrogenCyanide", 273.15, 0.00985, 673.15, 0.04185),  # p. 2-436
    ("HydrogenSulfide", 212.80, 0.00724, 600, 0.03258),  # p. 2-436
    ("Methane", 111.63, 0.01263, 600, 0.08425),  # p. 2-436
    ("Neon", 30.00, 0.00846, 3273.1, 0.24616),  # p. 2-437
    ("Nitrogen", 63.15, 0.00602, 2000, 0.11638),  # p. 2-437
    ("NitrousOxide", 182.30, 0.00891, 1000, 0.07133),  # p. 2-437
    ("NitricOxide", 121.38, 0.01094, 750, 0.05567),  # p. 2-437
    ("Oxygen", 80.00, 0.00691, 2000, 0.12655),  # p. 2-437
    ("Ozone", 161.85, 0.00931, 1000, 0.06990),  # p. 2-437
    ("Phenol", 454.99, 0.02183, 1000, 0.06936),  # p. 2-437
    ("Propane", 231.11, 0.01114, 1000, 0.14599),  # p. 2-437
    ("PropionicAcid", 414.32, 0.02124, 1000, 0.07487),  # p. 2-437
    ("Styrene", 418.31, 0.01837, 1000, 0.07276),  # p. 2-438
    ("SulfurDioxide", 250.00, 0.00745, 900, 0.03969),  # p. 2-438
]

# Table 2-150: heat of vaporization in J/kmol at Tmin
HEAT_OF_VAPORIZATION = [
    ("Helium", 2.20, 0.0097e7),  # p. 2-152
    ("HydrogenChloride", 158.97, 1.7498e7),  # p. 2-153
    ("HydrogenCyanide", 259.83, 2.8176e7),  # p. 2-153
    ("HydrogenSulfide", 187.68, 1.9782e7),  # p. 2-153
    ("Methane", 90.69, 0.8724e7),  # p. 2-153
    ("Neon", 24.56, 0.1803e7),  # p. 2-154
    ("Nitrogen", 63.15, 0.6024e7),  # p. 2-154
    ("NitrousOxide", 182.30, 1.6502e7),  # p. 2-154
    ("NitricOxide", 109.50, 1.4578e7),  # p. 2-154
    ("Oxygen", 54.36, 0.7742e7),  # p. 2-154
    ("Ozone", 80.15, 1.6625e7),  # p. 2-154
    ("Phenol", 314.06, 5.6577e7),  # p. 2-154
    ("Propane", 85.47, 2.4787e7),  # p. 2-154
    ("PropionicAcid", 252.45, 3.0922e7),  # p. 2-154
    ("Styrene", 242.54, 4.7128e7),  # p. 2-155
    ("SulfurDioxide", 197.67, 2.8753e7),  # p. 2-155
]


def _at(name, t_k, **kw):
    return getattr(components, name)(temperature=Temperature(t_k, "K"), **kw)


def _per_kmol(component, value):
    """A per-kg value from processpi, per kmol as Perry prints it."""
    return value * component.molecular_weight


def test_every_new_component_is_exported():
    for name in NEW:
        assert name in components.__all__
        assert getattr(components, name)().name


@pytest.mark.parametrize("name, t_min, p_min, t_max, p_max", VAPOUR_PRESSURE)
def test_vapour_pressure_matches_table_2_8(name, t_min, p_min, t_max, p_max):
    assert _at(name, t_min).vapor_pressure().value == pytest.approx(p_min, rel=5e-3)
    assert _at(name, t_max).vapor_pressure().value == pytest.approx(p_max, rel=5e-3)


@pytest.mark.parametrize("name", NEW)
def test_vapour_pressure_reaches_the_critical_pressure_at_tc(name):
    cls = getattr(components, name)
    tc = cls._critical_temperature.to("K").value
    ratio = _at(name, tc).vapor_pressure().value / cls._critical_pressure.to("Pa").value
    assert 0.5 < ratio < 2.0


@pytest.mark.parametrize("name, t_min, rho_min, t_max, rho_max", LIQUID_DENSITY)
def test_liquid_density_matches_table_2_32(name, t_min, rho_min, t_max, rho_max):
    for t, rho in ((t_min, rho_min), (t_max, rho_max)):
        liquid = _at(name, t, phase="liquid")
        assert liquid.density().value == pytest.approx(rho * liquid.molecular_weight, rel=1e-2)


@pytest.mark.parametrize("name, t_min, cp_min, t_max, cp_max", LIQUID_CP)
def test_liquid_cp_matches_table_2_153(name, t_min, cp_min, t_max, cp_max):
    for t, cp in ((t_min, cp_min), (t_max, cp_max)):
        liquid = _at(name, t, phase="liquid")
        assert _per_kmol(liquid, liquid.specific_heat().value) == pytest.approx(cp, rel=1e-2)


@pytest.mark.parametrize("name, t_min, cp_min, t_max, cp_max", IDEAL_GAS_CP)
def test_ideal_gas_cp_matches_tables_2_155_and_2_156(name, t_min, cp_min, t_max, cp_max):
    for t, cp in ((t_min, cp_min), (t_max, cp_max)):
        gas = _at(name, t, phase="gas")
        assert _per_kmol(gas, gas.specific_heat().value) == pytest.approx(cp, rel=1e-2)


@pytest.mark.parametrize("name, t_min, hv_min", HEAT_OF_VAPORIZATION)
def test_heat_of_vaporization_matches_table_2_150(name, t_min, hv_min):
    liquid = _at(name, t_min)
    assert _per_kmol(liquid, liquid.enthalpy().value) == pytest.approx(hv_min, rel=1e-2)


@pytest.mark.parametrize("name, t_min, mu_min, t_max, mu_max", LIQUID_VISCOSITY)
def test_liquid_viscosity_matches_table_2_313(name, t_min, mu_min, t_max, mu_max):
    assert _at(name, t_min, phase="liquid").viscosity().value == pytest.approx(mu_min, rel=1e-2)
    assert _at(name, t_max, phase="liquid").viscosity().value == pytest.approx(mu_max, rel=1e-2)


@pytest.mark.parametrize("name, t_min, k_min, t_max, k_max", LIQUID_K)
def test_liquid_thermal_conductivity_matches_table_2_315(name, t_min, k_min, t_max, k_max):
    assert _at(name, t_min, phase="liquid").thermal_conductivity().value == pytest.approx(k_min, rel=1e-2)
    assert _at(name, t_max, phase="liquid").thermal_conductivity().value == pytest.approx(k_max, rel=1e-2)


@pytest.mark.parametrize("name, t_min, k_min, t_max, k_max", VAPOUR_K)
def test_vapour_thermal_conductivity_matches_table_2_314(name, t_min, k_min, t_max, k_max):
    assert _at(name, t_min, phase="gas").thermal_conductivity().value == pytest.approx(k_min, rel=1e-2)
    assert _at(name, t_max, phase="gas").thermal_conductivity().value == pytest.approx(k_max, rel=1e-2)


GASES_AT_25_C = {
    "Helium", "Neon", "Nitrogen", "Oxygen", "Methane", "Propane", "NitricOxide",
    "NitrousOxide", "Ozone", "HydrogenChloride", "HydrogenSulfide", "SulfurDioxide",
}


@pytest.mark.parametrize("name", NEW)
def test_phase_at_25_c_and_1_atm(name):
    # Phenol melts at 314.06 K, where Perry's liquid tables start, so at 25 C
    # the model extrapolates the liquid. Hydrogen cyanide boils at 25.66 C by
    # its Table 2-8 row (98.8 kPa at 25 C), so it is a liquid at 25 C.
    comp = getattr(components, name)(temperature=Temperature(25, "C"), pressure=Pressure(1, "atm"))
    assert comp.phase() == ("gas" if name in GASES_AT_25_C else "liquid")


def test_hydrogen_cyanide_is_a_gas_just_above_its_boiling_point():
    hcn = components.HydrogenCyanide(temperature=Temperature(30, "C"), pressure=Pressure(1, "atm"))
    assert hcn.phase() == "gas"


@pytest.mark.parametrize("t_c", [25, 150])
@pytest.mark.parametrize("name", NEW)
def test_every_property_method_runs(name, t_c):
    comp = getattr(components, name)(temperature=Temperature(t_c, "C"), pressure=Pressure(1, "atm"))
    assert comp.density().value > 0
    assert comp.specific_heat().value > 0
    assert comp.viscosity().value > 0
    assert comp.thermal_conductivity().value > 0
    assert comp.vapor_pressure().value > 0
    assert comp.enthalpy().value >= 0  # 0 above Tc
    assert comp.hx_data()["velocity_key"] in {
        "helium_4", "hydrogen_chloride", "hydrogen_cyanide", "hydrogen_sulfide", "methane",
        "neon", "nitrogen", "nitrous_oxide", "nitric_oxide", "oxygen", "ozone", "phenol",
        "propane", "propionic_acid", "styrene", "sulfur_dioxide",
    }


def test_helium_and_neon_ideal_gas_cp_is_five_halves_r():
    # Table 2-155: C1 = 20,786 J/(kmol K), C2 to C5 = 0.
    for name, mw in (("Helium", 4.003), ("Neon", 20.180)):
        gas = getattr(components, name)(temperature=Temperature(25, "C"))
        assert gas.specific_heat().value == pytest.approx(20786 / mw, rel=1e-9)


def test_eq2_liquid_cp_is_per_kg():
    # Hydrogen sulfide, methane and propane are "use Eq. (2)" rows of Table
    # 2-153. Eq. (2) gives J/(kmol K); processpi returns J/(kg K).
    for name, t, cp_kmol in (("HydrogenSulfide", 187.68, 0.6733e5), ("Methane", 90.69, 0.5361e5),
                             ("Propane", 85.47, 0.8488e5)):
        liquid = _at(name, t, phase="liquid")
        assert liquid.specific_heat().value == pytest.approx(cp_kmol / liquid.molecular_weight, rel=1e-2)


def test_nitric_oxide_ideal_gas_cp_uses_the_c5_its_row_reproduces():
    # phase="gas": without it the vapour-pressure test overflows above about
    # 644 K, where the row's C4*T^6 term passes exp()'s range.
    gas = components.NitricOxide(temperature=Temperature(1500, "K"), phase="gas")
    assert _per_kmol(gas, gas.specific_heat().value) == pytest.approx(0.3586e5, rel=1e-3)
