# ProcessPI Components Reference

The ProcessPI components module provides substance-property models for process calculations. Component classes are exported from processpi.components and inherit a common API from the Component base class.

## Quick start

~~~python
from processpi.components import Water, AceticAcid, Benzene
from processpi.units import Temperature, Pressure

water = Water(
    temperature=Temperature(25, "C"),
    pressure=Pressure(101325, "Pa"),
)
print(water.name)
print(water.density().to("kg/m3"))
print(water.viscosity().to("Pa*s"))
~~~

Pass ProcessPI unit objects to the constructor and convert returned quantities with .to("unit"). Pressure is absolute pressure in the base implementation.

## Component catalogue

The package exports **353 component classes** (excluding the shared `Component` base class): **254 chemical substances**, **6 general fluid categories**, and **2 legacy compatibility aliases**.

To make the catalogue easier to browse, names are grouped alphabetically. Expand only the section you need. The class names are the exact Python import names exported by `processpi.components`.

~~~python
from processpi.components import AceticAcid, Benzene, Water
~~~

<details>
<summary><strong>0–9 · Numbered compounds (91)</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `_112Trichloroethane` | `_11Dibromoethane` | `_11Dichloroethane` | `_11Dichloropropane` |
| `_11Difluoroethane` | `_11Dimethoxyethane` | `_11Dimethylcyclohexane` | `_123Trimethylbenzene` |
| `_1234Tetrahydronaphthalene` | `_124Trimethylbenzene` | `_12Butadiene` | `_12Butanediol` |
| `_12Dibromoethane` | `_12Dichloroethane` | `_12Dichloropropane` | `_12Difluoroethane` |
| `_12Dimethoxypropane` | `_12PropyleneGlycol` | `_135Trinitrobenzene` | `_13Butadiene` |
| `_13Butanediol` | `_14Dioxane` | `_1Butanol` | `_1Butene` |
| `_1Butyne` | `_1Chloropropane` | `_1Decanol` | `_1Decene` |
| `_1Decyne` | `_1Heptanol` | `_1Heptene` | `_1Heptyne` |
| `_1Hexanol` | `_1Hexene` | `_1Hexyne` | `_1Methylcyclohexanol` |
| `_1Methylcyclopentene` | `_1Nonanol` | `_1Nonene` | `_1Nonyne` |
| `_1Octanol` | `_1Octene` | `_1Octyne` | `_1Pentanol` |
| `_1Pentene` | `_1Pentyne` | `_1Propanol` | `_1Undecanol` |
| `_2233Tetramethylbutane` | `_224Trimethylpentane` | `_233Trimethylpentane` | `_23Dimethylbutane` |
| `_23Dimethylpentane` | `_246Trinitrotoluene` | `_2Butanol` | `_2Chloropropane` |
| `_2EthylButanoicAcid` | `_2EthylHexanoicAcid` | `_2Heptanol` | `_2Heptanone` |
| `_2Hexanol` | `_2Hexanone` | `_2Hexyne` | `_2Methyl1Butene` |
| `_2Methyl1Butene3Yne` | `_2Methyl2Butene` | `_2Methyl2Propanol` | `_2Methylbutane` |
| `_2MethylbutanoicAcid` | `_2MethyloctanoicAcid` | `_2Methylpentane` | `_2Methylpropane` |
| `_2MethylPropene` | `_2Nonanol` | `_2Octanol` | `_2Octanone` |
| `_2Pentanol` | `_2Pentanone` | `_2PentylMercaptan` | `_2Pentyne` |
| `_2Propanol` | `_2PropylMercaptan` | `_3Heptanone` | `_3Hexanone` |
| `_3Hexyne` | `_3Methyl12Butadiene` | `_3Methyl1Butanol` | `_3Methyl1Butyne` |
| `_3Methylcyclopentene` | `_3Octanone` | `_3Pentanone` | — |

</details>

<details>
<summary><strong>A · 15 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Acetaldehyde` | `Acetamide` | `AceticAcid` | `AceticAnhydride` |
| `Acetone` | `Acetonitrile` | `Acetylene` | `Acrolein` |
| `AcrylicAcid` | `Acrylonitrile` | `Air` | `AlphaMethylStyrene` |
| `Ammonia` | `Anisole` | `Argon` | — |

</details>

<details>
<summary><strong>B · 21 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Benzamide` | `Benzene` | `Benzenethiol` | `BenzoicAcid` |
| `Benzonitrile` | `Benzophenone` | `BenzylAlcohol` | `BenzylEthylEther` |
| `BenzylMercaptan` | `Biphenyl` | `Bromine` | `Bromobenzene` |
| `Bromoethane` | `Bromomethane` | `Butane` | `ButylAcetate` |
| `Butylbenzene` | `ButylMercaptan` | `Butyraldehyde` | `ButyricAcid` |
| `Butyronitrile` | — | — | — |

</details>

<details>
<summary><strong>C · 24 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Carbondioxide` | `CarbonDisulfide` | `CarbonMonoxide` | `CarbonTetrachloride` |
| `CarbonTetrafluoride` | `Chlorine` | `ChloroBenzene` | `Chloroethane` |
| `Chloroform` | `ChloroMethane` | `Cis12Dimethylcyclohexane` | `Cis2Butene` |
| `Cis2Methylcyclohexanol` | `Cumene` | `Cyanogen` | `Cyclobutane` |
| `Cyclohexane` | `Cyclohexanol` | `Cyclohexanone` | `Cyclohexene` |
| `CyclohexylMercaptan` | `Cyclopentane` | `Cyclopentene` | `Cyclopropane` |

</details>

<details>
<summary><strong>D · 28 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Decanal` | `Decane` | `DecanoicAcid` | `DecylMercaptan` |
| `Deuterium` | `Dibromomethane` | `DibutylEther` | `Dichloromethane` |
| `DiethanolAmine` | `DiethylAmine` | `DiethylEther` | `DiethylSulfide` |
| `Difluoromethane` | `DiisopropylAmine` | `DiisopropylEther` | `DiisopropylKetone` |
| `DimethylAcetylene` | `DimethylAmine` | `DimethylDisulfide` | `DimethylEther` |
| `DimethylPhthalate` | `Dimethylsilane` | `DimethylSulfide` | `DimethylSulfoxide` |
| `DimethylTerephthalate` | `DiphenylEther` | `DipropylAmine` | `Dodecane` |

</details>

<details>
<summary><strong>E · 25 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Eicosane` | `Ethane` | `Ethanol` | `EthylAcetate` |
| `EthylAmine` | `Ethylbenzene` | `EthylBenzoate` | `EthylButyrate` |
| `Ethylcyclohexane` | `Ethylcyclopentane` | `Ethylene` | `Ethylenediamine` |
| `EthyleneGlycol` | `Ethyleneimine` | `EthyleneOxide` | `EthylFormate` |
| `EthylhexylEther` | `EthylisopropylEther` | `EthylisopropylKetone` | `EthylMercaptan` |
| `EthylPropionate` | `EthylpropylEther` | `Ethyltrichlorosilane` | — |

**General categories and compatibility aliases**

| Component | Component | Component | Component |
|---|---|---|---|
| `EthlylAcetate` | `Ethlylene` | — | — |

</details>

<details>
<summary><strong>F · 8 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Fluorine` | `FluoroBenzene` | `Fluoroethane` | `Fluoromethane` |
| `Formaldehyde` | `Formamide` | `FormicAcid` | `Furan` |

</details>

<details>
<summary><strong>G · 1 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|

**General categories and compatibility aliases**

| Component | Component | Component | Component |
|---|---|---|---|
| `Gas` | — | — | — |

</details>

<details>
<summary><strong>H · 18 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Helium` | `Heptadecane` | `Heptanal` | `Heptane` |
| `HeptanoicAcid` | `HeptylMercaptan` | `Hexadecane` | `Hexanal` |
| `Hexane` | `HexanoicAcid` | `HexylMercaptan` | `Hydrazine` |
| `Hydrogen` | `HydrogenBromide` | `HydrogenChloride` | `HydrogenCyanide` |
| `HydrogenFluoride` | `HydrogenSulfide` | — | — |

</details>

<details>
<summary><strong>I · 3 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `IsobutyricAcid` | `IsopropylAmine` | — | — |

**General categories and compatibility aliases**

| Component | Component | Component | Component |
|---|---|---|---|
| `InorganicLiquid` | — | — | — |

</details>

<details>
<summary><strong>M · 38 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `MalonicAcid` | `Mcresol` | `Mdichlorobenzene` | `MethacrylicAcid` |
| `Methane` | `Methanol` | `MethylAcetate` | `MethylAcetylene` |
| `MethylAcrylate` | `MethylAmine` | `MethylBenzoate` | `MethylbutylEther` |
| `MethylbutylSulfide` | `MethylButyrate` | `Methylchlorosilane` | `Methylcyclohexane` |
| `Methylcyclopentane` | `Methyldichlorosilane` | `MethylethylEther` | `MethylethylKetone` |
| `MethylethylSulfide` | `MethylFormate` | `MethylisobutylEther` | `MethylisobutylKetone` |
| `MethylIsocyanate` | `MethylisopropylEther` | `MethylisopropylKetone` | `MethylisopropylSulfide` |
| `MethylMercaptan` | `MethylMethacrylate` | `MethylPentylEther` | `MethylPropionate` |
| `MethylpropylEther` | `MethylpropylSulfide` | `Methylsilane` | `MethylTertButylEther` |
| `MethylVinylEther` | `Mxylene` | — | — |

</details>

<details>
<summary><strong>N · 15 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Naphthalene` | `Neon` | `NitricOxide` | `Nitroethane` |
| `Nitrogen` | `NitrogenTrifluoride` | `Nitromethane` | `NitrousOxide` |
| `NmethylAcetamide` | `NndimethylFormamide` | `Nonadecane` | `Nonanal` |
| `Nonane` | `NonanoicAcid` | `NonylMercaptan` | — |

</details>

<details>
<summary><strong>O · 14 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Ocresol` | `Octadecane` | `Octanal` | `Octane` |
| `OctanoicAcid` | `OctylMercaptan` | `Odichlorobenzene` | `Oterphenyl` |
| `OxalicAcid` | `Oxygen` | `Oxylene` | `Ozone` |

**General categories and compatibility aliases**

| Component | Component | Component | Component |
|---|---|---|---|
| `Oil` | `OrganicLiquid` | — | — |

</details>

<details>
<summary><strong>P · 24 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Pcresol` | `Pdichlorobenzene` | `Pentadecane` | `Pentanal` |
| `Pentane` | `PentanoicAcid` | `PentylMercaptan` | `Phenanthrene` |
| `Phenol` | `PhenylIsocyanate` | `PhthalicAnhydride` | `Propadiene` |
| `Propane` | `Propenylcyclohexene` | `Propionaldehyde` | `PropionicAcid` |
| `Propionitrile` | `PropylAcetate` | `PropylAmine` | `Propylbenzene` |
| `Propylene` | `PropylFormate` | `PropylMercaptan` | `Pxylene` |

</details>

<details>
<summary><strong>Q · 1 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Quinone` | — | — | — |

</details>

<details>
<summary><strong>S · 8 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `SeButylmercaptan` | `SiliconTetrafluoride` | `Styrene` | `SuccinicAcid` |
| `SulfurDioxide` | `SulfurHexafluoride` | `SulfurTrioxide` | — |

**General categories and compatibility aliases**

| Component | Component | Component | Component |
|---|---|---|---|
| `Steam` | — | — | — |

</details>

<details>
<summary><strong>T · 12 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `TerephthalicAcid` | `Tetradecane` | `Tetrahydrofuran` | `Tetrahydrothiophene` |
| `Thiophene` | `Toluene` | `Trans12Dimethylcyclohexane` | `Trans2Butene` |
| `Trans2Methylcyclohexanol` | `Tridecane` | `TriethylAmine` | `TrimethylAmine` |

</details>

<details>
<summary><strong>U · 1 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Undecane` | — | — | — |

</details>

<details>
<summary><strong>V · 5 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `VinylAcetate` | `VinylAcetylene` | `VinylChloride` | `VinylTrichlorosilane` |

**General categories and compatibility aliases**

| Component | Component | Component | Component |
|---|---|---|---|
| `Vapor` | — | — | — |

</details>

<details>
<summary><strong>W · 1 components</strong></summary>

| Component | Component | Component | Component |
|---|---|---|---|
| `Water` | — | — | — |

</details>

### General fluid categories

These classes represent broad fluid types rather than individual chemical species: `Gas`, `InorganicLiquid`, `Oil`, `OrganicLiquid`, `Steam`, and `Vapor`.

### Legacy import aliases

`EthlylAcetate` and `Ethlylene` remain exported for backward compatibility. Prefer `EthylAcetate` and `Ethylene` in new code.

## Constructor parameters

All substance classes inherit the Component constructor. The defaults and accepted inputs are:

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| temperature | Temperature | Temperature(25, "C") | Temperature at which properties are evaluated |
| pressure | Pressure | Pressure(101325, "Pa") | Absolute system pressure used in phase and gas-property calculations |
| density | Density or None | None | Optional supplied density; bypasses the density correlation |
| specific_heat | SpecificHeat or None | None | Optional supplied heat capacity |
| viscosity | Viscosity or None | None | Optional supplied dynamic viscosity |
| thermal_conductivity | ThermalConductivity or None | None | Optional supplied thermal conductivity |
| vapor_pressure | Pressure or None | None | Optional supplied vapour pressure |
| enthalpy | HeatOfVaporization or None | None | Optional supplied heat of vaporisation |
| phase | str or None | None | Optional phase override: liquid, gas, vapor, or steam |

Use unit objects, not bare numeric values. A phase override is useful for a pressurised liquid above its normal boiling point. Without an override, phase is inferred from component defaults, critical temperature, and the pressure-versus-vapour-pressure comparison.

## Public metadata properties

| Attribute | Meaning |
|---|---|
| name | Human-readable component name |
| formula | Chemical formula |
| molecular_weight | Molecular weight in g/mol |

Component classes may also define internal critical-property and correlation data. These are implementation details and should not normally be changed by application code:

| Internal attribute | Meaning |
|---|---|
| _critical_temperature | Critical temperature |
| _critical_pressure | Critical pressure |
| _critical_volume | Critical molar volume |
| _critical_zc | Critical compressibility factor |
| _critical_acentric_factor | Acentric factor |
| _density_constants | Liquid-density correlation constants |
| _specific_heat_constants | Heat-capacity correlation constants |
| _ideal_gas_heat_capacity_constants | Optional ideal-gas Cp correlation constants |
| _viscosity_constants | Liquid-viscosity correlation constants |
| _thermal_conductivity_constants | Liquid thermal-conductivity correlation constants |
| _vapor_thermal_conductivity_constants | Optional gas/vapour conductivity constants |
| _vapor_pressure_constants | Vapour-pressure correlation constants |
| _enthalpy_constants | Heat-of-vaporisation correlation constants |

The exact constants and valid ranges are component-specific. Do not reuse one substance's constants for another substance.

## Inherited methods and calculated properties

The base class uses PropertyMethod descriptors. Calling water.density() evaluates the property and returns a Density object. Accessing water.density without parentheses returns a callable wrapper; its .value attribute contains the evaluated result. The same access pattern applies to phase, specific_heat, viscosity, thermal_conductivity, vapor_pressure, and enthalpy.

| Member | Return type | Explanation |
|---|---|---|
| phase() | str | Calling phase() returns gas or liquid. Accessing phase without parentheses returns the descriptor wrapper; phase.value contains the evaluated string. An explicit phase override takes priority; otherwise the base class considers the default phase, critical temperature, and vapour pressure. |
| density() | Density | Returns supplied density if present; otherwise calculates gas density using the ideal-gas equation or liquid density using the component's DIPPR-style correlation. |
| specific_heat() | SpecificHeat | Returns supplied Cp if present; otherwise uses an available ideal-gas Cp correlation for gas phase or the component temperature polynomial. |
| viscosity() | Viscosity | Returns supplied dynamic viscosity if present; otherwise evaluates the liquid correlation or gas-phase Sutherland approximation. |
| thermal_conductivity() | ThermalConductivity | Returns supplied conductivity if present; otherwise evaluates a gas correlation when supplied by the component or the component temperature polynomial. |
| vapor_pressure() | Pressure | Returns supplied vapour pressure if present; otherwise evaluates the component-specific vapour-pressure correlation. |
| enthalpy() | HeatOfVaporization | Returns supplied heat of vaporisation if present; otherwise calculates latent heat from reduced temperature and critical temperature. The base implementation returns zero at or above critical temperature. |
| latent_heat | HeatOfVaporization | Alias of enthalpy; supports the same property/call access. |
| httype() | str | Returns the fluid category used by the heat-exchanger overall heat-transfer coefficient standards lookup. |
| hx_data() | dict | Returns heat-exchanger metadata: family, phase, velocity key, U-value key, fouling key, and corrosion key. |

### Calculation behaviour and limitations

- Gas density uses the ideal-gas equation with molecular weight, absolute pressure, and absolute temperature.
- Liquid density and liquid transport/thermodynamic properties use component-specific correlations and constants.
- Gas-phase Cp and thermal conductivity use separate gas correlations only when those constants are provided by the component.
- User-supplied property values take precedence over calculated values.
- Correlations have component-specific validity ranges. Extrapolated results should be independently checked before being used for equipment design.
- The phase method returns only gas or liquid, even where a fluid may conventionally be described as vapour or steam.

## Example: Acetic Acid

~~~python
from processpi.components import AceticAcid
from processpi.units import Temperature, Pressure

acid = AceticAcid(
    temperature=Temperature(35, "C"),
    pressure=Pressure(101325, "Pa"),
)

print(acid.name)
print(acid.formula)
print(acid.molecular_weight)
print(acid.phase())
print(acid.density().to("kg/m3"))
print(acid.viscosity().to("Pa*s"))
print(acid.specific_heat().to("J/kgK"))
print(acid.thermal_conductivity().to("W/mK"))
print(acid.vapor_pressure().to("Pa"))
print(acid.enthalpy().to("J/kg"))
print(acid.httype())
print(acid.hx_data())
~~~

## Example: known phase and supplied property

~~~python
from processpi.components import Water
from processpi.units import Temperature, Pressure, Density

hot_water = Water(
    temperature=Temperature(150, "C"),
    pressure=Pressure(5, "bar"),
    density=Density(917, "kg/m3"),
    phase="liquid",
)

print(hot_water.phase())       # liquid: explicit override
print(hot_water.density())     # supplied Density object
~~~

## Source of truth

- [Component base class](https://github.com/varma666/ProcessPi/blob/master/processpi/components/base.py)
- [Public component exports](https://github.com/varma666/ProcessPi/blob/master/processpi/components/__init__.py)
- [Component source directory](https://github.com/varma666/ProcessPi/tree/master/processpi/components)

For each release, regenerate or reconcile the catalogue against processpi.components.__all__ so the documentation remains aligned with the package.
