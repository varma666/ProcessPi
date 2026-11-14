"""Liquid property constants against Perry's Chemical Engineers' Handbook, 8th ed.

A sweep of every component against the values Perry's tables print at each
row's Tmin and Tmax found 53 constant sets that do not reproduce them:

- Table 2-8 (vapour pressure): 22 rows with C4 cut to three digits (C4
  multiplies T**C5 with C5 up to 6, so the error shows near Tc) or with
  transposed digits in C2 (2-Hexanone -8258.6 for -8528.6, Diisopropyl
  ketone -6063.5 for -6036.5, Terephthalic acid -32283 for -32238).
- Table 2-150 (heat of vaporization): 11 lists of 2 or 4 constants, which
  raised "not enough values to unpack (expected 5)"; 2-Hexanol's C1 without
  its 1E7 factor; Terephthalic acid's list held its temperature, 298.15, as
  the exponent C2.
- Table 2-153 (liquid Cp): wrong digits (Benzyl mercaptan C1 1,000,320 for
  100,320; Propionitrile 181,190 for 118,190; Methylpropyl ether 140,110 for
  144,110; SiF4 C2 -7311.5 for -7331.5), Cyanogen's C2 sign, 2-Hexyne's C2
  missing, and four 7-entry lists with the table's two check values appended
  ("too many values to unpack").
- Table 2-313 (liquid viscosity): C4/C5 dropped or invented (Butane C5 = 10,
  Cyclohexanol, Hydrogen fluoride and Undecane C4, Chlorobenzene's 1.5E14 and
  -6), Acetonitrile's two-entry list (IndexError), and Deuterium's single
  value 1.348E-06 Pa s stored as C1 of exp(C1 + ...), which gave 1 Pa s.
- Table 2-315 (liquid conductivity): Bromine's C4 and C5 cut to three digits.

Each case below is a value the table prints (Cp and heat of vaporization in
J/kmol, as printed with their x 1E-05 / x 1E-07 factors applied).
"""

import pytest

from processpi.components import (
    Acetaldehyde, Acetonitrile, Acrolein, Anisole, BenzylMercaptan, Bromine,
    Bromomethane, Butane, ChloroBenzene, Chloroform, Cyanogen, Cyclobutane,
    Cyclohexanol, Decanal, Deuterium, DiethylAmine, DiisopropylKetone, Formaldehyde,
    HexanoicAcid, HexylMercaptan, Hydrazine, HydrogenFluoride, IsopropylAmine,
    MethylpropylEther, Nonanal, Ocresol, OctanoicAcid, Propionitrile, PropylAcetate,
    Propylene, SiliconTetrafluoride, TerephthalicAcid, Undecane, _12Dimethoxypropane,
    _12PropyleneGlycol, _135Trinitrobenzene, _1Hexyne, _1Nonanol, _1Nonene, _1Octyne,
    _2EthylHexanoicAcid, _2Hexanol, _2Hexanone, _2Hexyne, _2Methyl1Butene3Yne,
    _2MethyloctanoicAcid, _2Methylpropane, _2Nonanol
)
from processpi.components.base import Component
import processpi.components as components
from processpi.units import Pressure, Temperature


def _value(cls, prop, t_k):
    c = cls(temperature=Temperature(t_k, "K"), pressure=Pressure(500, "bar"), phase="liquid")
    if prop == "vapor_pressure":
        return c.vapor_pressure().to("Pa").value
    if prop == "Hvap":
        return c.enthalpy().to("J/kg").value * cls.molecular_weight
    if prop == "Cp":
        return c.specific_heat().to("J/kgK").value * cls.molecular_weight
    if prop == "viscosity":
        return c.viscosity().to("Pa·s").value
    return c.thermal_conductivity().to("W/mK").value


# (component, property, T in K, value printed by Perry's table)
PERRY_POINTS = [
    (_12PropyleneGlycol, "vapor_pressure", 213.15, 9.29e-05),  # Table 2-8, no. 309
    (_12PropyleneGlycol, "vapor_pressure", 626, 6.041e+06),  # Table 2-8, no. 309
    (_135Trinitrobenzene, "vapor_pressure", 398.4, 8.5),  # Table 2-8, no. 334
    (_135Trinitrobenzene, "vapor_pressure", 846, 3.41e+06),  # Table 2-8, no. 334
    (_1Hexyne, "vapor_pressure", 141.25, 0.000392),  # Table 2-8, no. 180
    (_1Hexyne, "vapor_pressure", 516.2, 3.635e+06),  # Table 2-8, no. 180
    (_2Hexanone, "vapor_pressure", 217.35, 1.45),  # Table 2-8, no. 175
    (_2Hexanone, "vapor_pressure", 587.61, 3.286e+06),  # Table 2-8, no. 175
    (_2Methyl1Butene3Yne, "vapor_pressure", 160.15, 2.92),  # Table 2-8, no. 207
    (_2Methyl1Butene3Yne, "vapor_pressure", 492, 4.469e+06),  # Table 2-8, no. 207
    (_2Methylpropane, "vapor_pressure", 113.54, 0.0121),  # Table 2-8, no. 236
    (_2Methylpropane, "vapor_pressure", 407.8, 3.63e+06),  # Table 2-8, no. 236
    (Acetaldehyde, "vapor_pressure", 150.15, 0.323),  # Table 2-8, no. 1
    (Acetaldehyde, "vapor_pressure", 466, 5.565e+06),  # Table 2-8, no. 1
    (Acrolein, "vapor_pressure", 185.45, 10.3),  # Table 2-8, no. 8
    (Acrolein, "vapor_pressure", 506, 5.02e+06),  # Table 2-8, no. 8
    (Anisole, "vapor_pressure", 235.65, 2.45),  # Table 2-8, no. 13
    (Anisole, "vapor_pressure", 645.6, 4.273e+06),  # Table 2-8, no. 13
    (Bromine, "vapor_pressure", 265.85, 5850),  # Table 2-8, no. 25
    (Bromine, "vapor_pressure", 584.15, 1.028e+07),  # Table 2-8, no. 25
    (Bromomethane, "vapor_pressure", 179.47, 195),  # Table 2-8, no. 28
    (Bromomethane, "vapor_pressure", 467, 7.997e+06),  # Table 2-8, no. 28
    (Chloroform, "vapor_pressure", 207.15, 52.5),  # Table 2-8, no. 55
    (Chloroform, "vapor_pressure", 536.4, 5.554e+06),  # Table 2-8, no. 55
    (Cyclobutane, "vapor_pressure", 182.48, 180),  # Table 2-8, no. 64
    (Cyclobutane, "vapor_pressure", 459.93, 4.991e+06),  # Table 2-8, no. 64
    (Cyclohexanol, "vapor_pressure", 296.6, 76.5),  # Table 2-8, no. 66
    (Cyclohexanol, "vapor_pressure", 650.1, 4.265e+06),  # Table 2-8, no. 66
    (Decanal, "vapor_pressure", 267.15, 0.486),  # Table 2-8, no. 73
    (Decanal, "vapor_pressure", 674.2, 2.599e+06),  # Table 2-8, no. 73
    (DiisopropylKetone, "vapor_pressure", 204.81, 0.821),  # Table 2-8, no. 102
    (DiisopropylKetone, "vapor_pressure", 576, 3.017e+06),  # Table 2-8, no. 102
    (Formaldehyde, "vapor_pressure", 181.15, 887),  # Table 2-8, no. 153
    (Formaldehyde, "vapor_pressure", 408, 6.594e+06),  # Table 2-8, no. 153
    (IsopropylAmine, "vapor_pressure", 177.95, 7.73),  # Table 2-8, no. 190
    (IsopropylAmine, "vapor_pressure", 471.85, 4.54e+06),  # Table 2-8, no. 190
    (Nonanal, "vapor_pressure", 255.15, 0.342),  # Table 2-8, no. 255
    (Nonanal, "vapor_pressure", 658, 2.743e+06),  # Table 2-8, no. 255
    (Ocresol, "vapor_pressure", 304.19, 65.3),  # Table 2-8, no. 60
    (Ocresol, "vapor_pressure", 697.55, 5.058e+06),  # Table 2-8, no. 60
    (PropylAcetate, "vapor_pressure", 178.15, 0.0171),  # Table 2-8, no. 302
    (PropylAcetate, "vapor_pressure", 549.73, 3.366e+06),  # Table 2-8, no. 302
    (TerephthalicAcid, "vapor_pressure", 700.15, 4570),  # Table 2-8, no. 317
    (TerephthalicAcid, "vapor_pressure", 1113, 3.943e+06),  # Table 2-8, no. 317
    (_1Nonanol, "Hvap", 268.15, 8.2411e+07),  # Table 2-150, no. 258
    (_1Nonene, "Hvap", 191.91, 4.9218e+07),  # Table 2-150, no. 260
    (_2EthylHexanoicAcid, "Hvap", 235.00, 8.2832e+07),  # Table 2-150, no. 141
    (_2Hexanol, "Hvap", 223.00, 6.5014e+07),  # Table 2-150, no. 174
    (_2MethyloctanoicAcid, "Hvap", 240.00, 8.1106e+07),  # Table 2-150, no. 233
    (_2Nonanol, "Hvap", 238.15, 8.037e+07),  # Table 2-150, no. 259
    (Acetonitrile, "Hvap", 229.32, 3.5996e+07),  # Table 2-150, no. 6
    (DiethylAmine, "Hvap", 223.35, 3.5761e+07),  # Table 2-150, no. 94
    (HexanoicAcid, "Hvap", 269.25, 6.4783e+07),  # Table 2-150, no. 172
    (Hydrazine, "Hvap", 274.69, 4.5238e+07),  # Table 2-150, no. 182
    (OctanoicAcid, "Hvap", 289.65, 8.4658e+07),  # Table 2-150, no. 266
    (Propylene, "Hvap", 87.89, 2.3177e+07),  # Table 2-150, no. 305
    (TerephthalicAcid, "Hvap", 298.15, 8.824e+07),  # Table 2-150, no. 317
    (_12Dimethoxypropane, "Cp", 226.10, 2.0145e+05),  # Table 2-153, no. 104
    (_12Dimethoxypropane, "Cp", 366.15, 2.4734e+05),  # Table 2-153, no. 104
    (_1Octyne, "Cp", 200.00, 1.9225e+05),  # Table 2-153, no. 273
    (_1Octyne, "Cp", 399.35, 2.8619e+05),  # Table 2-153, no. 273
    (_2Hexyne, "Cp", 300.00, 1.711e+05),  # Table 2-153, no. 181
    (_2Hexyne, "Cp", 357.67, 1.8576e+05),  # Table 2-153, no. 181
    (Acetonitrile, "Cp", 229.32, 87480),  # Table 2-153, no. 6
    (Acetonitrile, "Cp", 354.75, 97130),  # Table 2-153, no. 6
    (BenzylMercaptan, "Cp", 243.95, 1.8494e+05),  # Table 2-153, no. 23
    (BenzylMercaptan, "Cp", 472.03, 2.6406e+05),  # Table 2-153, no. 23
    (Cyanogen, "Cp", 200.08, 97000),  # Table 2-153, no. 63
    (Cyanogen, "Cp", 300.08, 1.1463e+05),  # Table 2-153, no. 63
    (HexylMercaptan, "Cp", 192.62, 2.1495e+05),  # Table 2-153, no. 179
    (HexylMercaptan, "Cp", 430.00, 2.7639e+05),  # Table 2-153, no. 179
    (MethylpropylEther, "Cp", 133.97, 1.4086e+05),  # Table 2-153, no. 240
    (MethylpropylEther, "Cp", 312.20, 1.6888e+05),  # Table 2-153, no. 240
    (Propionitrile, "Cp", 180.26, 1.1005e+05),  # Table 2-153, no. 301
    (Propionitrile, "Cp", 370.50, 1.3112e+05),  # Table 2-153, no. 301
    (SiliconTetrafluoride, "Cp", 186.35, 1.3e+05),  # Table 2-153, no. 311
    (SiliconTetrafluoride, "Cp", 253.15, 2.0403e+05),  # Table 2-153, no. 311
    (Acetonitrile, "viscosity", 229.32, 0.000822),  # Table 2-313, no. 6
    (Acetonitrile, "viscosity", 436.40, 0.000135),  # Table 2-313, no. 6
    (Butane, "viscosity", 134.86, 0.002243),  # Table 2-313, no. 31
    (Butane, "viscosity", 420.00, 3.566e-05),  # Table 2-313, no. 31
    (ChloroBenzene, "viscosity", 250.00, 0.001422),  # Table 2-313, no. 53
    (ChloroBenzene, "viscosity", 540.00, 0.0001291),  # Table 2-313, no. 53
    (Cyclohexanol, "viscosity", 296.60, 0.0633),  # Table 2-313, no. 66
    (Cyclohexanol, "viscosity", 520.08, 0.000165),  # Table 2-313, no. 66
    (Deuterium, "viscosity", 20.35, 1.348e-06),  # Table 2-313, no. 80
    (HydrogenFluoride, "viscosity", 189.79, 0.00155),  # Table 2-313, no. 187
    (HydrogenFluoride, "viscosity", 368.92, 0.000119),  # Table 2-313, no. 187
    (Undecane, "viscosity", 247.57, 0.00324),  # Table 2-313, no. 336
    (Undecane, "viscosity", 511.20, 0.000157),  # Table 2-313, no. 336
    (Bromine, "conductivity", 266.00, 0.1299),  # Table 2-315, no. 25
    (Bromine, "conductivity", 584.00, 0.0316),  # Table 2-315, no. 25
]


@pytest.mark.parametrize(
    "cls, prop, t_k, expected", PERRY_POINTS,
    ids=[f"{c.__name__}-{p}-{t}K" for c, p, t, _ in PERRY_POINTS],
)
def test_liquid_property_reproduces_perry(cls, prop, t_k, expected):
    # The printed values have three to five significant figures.
    assert _value(cls, prop, t_k) == pytest.approx(expected, rel=5e-3)


_GENERIC = {"Component", "Gas", "Vapor", "Oil", "OrganicLiquid", "InorganicLiquid", "Steam", "Mixture"}


def _component_classes():
    seen = set()
    for name in getattr(components, "__all__", dir(components)):
        cls = getattr(components, name, None)
        if isinstance(cls, type) and issubclass(cls, Component) and cls not in seen and name not in _GENERIC:
            seen.add(cls)
            yield cls


def _overrides(cls, method):
    return any(method in vars(k) for k in cls.__mro__ if k is not Component and issubclass(k, Component))


def test_constant_lists_have_the_length_component_reads():
    # Component unpacks four density constants and five Cp and heat of
    # vaporization constants, and indexes five vapour-pressure and viscosity
    # constants; a shorter or longer list raised on every call.
    wrong = []
    for cls in _component_classes():
        checks = [("_density_constants", lambda n: n == 4, "density"),
                  ("_enthalpy_constants", lambda n: n == 5, "enthalpy"),
                  ("_specific_heat_constants", lambda n: n == 5, "specific_heat"),
                  ("_vapor_pressure_constants", lambda n: n >= 5, "vapor_pressure"),
                  ("_viscosity_constants", lambda n: n >= 5, "viscosity")]
        for attr, ok, method in checks:
            if _overrides(cls, method):
                continue
            values = getattr(cls, attr, None)
            if values is None or not ok(len(values)):
                wrong.append((cls.__name__, attr, None if values is None else len(values)))
    assert wrong == []
