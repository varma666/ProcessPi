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
print(water.viscosity().to("Pa·s"))
~~~

Pass ProcessPI unit objects to the constructor and convert returned quantities with .to("unit"). Pressure is absolute pressure in the base implementation.

## Component catalogue

The current package exports 353 names in total: 345 chemical component classes, six general fluid-category classes (Gas, InorganicLiquid, Oil, OrganicLiquid, Steam, and Vapor), and two legacy compatibility aliases (EthlylAcetate and Ethlylene). The list below follows the package's exported names in processpi/components/__init__.py. Class names are used as import names.

The catalogue below is generated from the public exports in `processpi.components.__all__`. Expand only the range you need; names are the exact Python import names. There are 91 numeric/positional-name classes and 254 alphabetic chemical component classes.

<details>
<summary>0–9 — 91 classes</summary>

| Class name | Class name | Class name | Class name |
|---|---|---|---|
| `_112Trichloroethane` | `_1Butene` | `_1Propanol` | `_2MethylbutanoicAcid` |
| `_11Dibromoethane` | `_1Butyne` | `_1Undecanol` | `_2MethyloctanoicAcid` |
| `_11Dichloroethane` | `_1Chloropropane` | `_2233Tetramethylbutane` | `_2Methylpentane` |
| `_11Dichloropropane` | `_1Decanol` | `_224Trimethylpentane` | `_2Methylpropane` |
| `_11Difluoroethane` | `_1Decene` | `_233Trimethylpentane` | `_2Nonanol` |
| `_11Dimethoxyethane` | `_1Decyne` | `_23Dimethylbutane` | `_2Octanol` |
| `_11Dimethylcyclohexane` | `_1Heptanol` | `_23Dimethylpentane` | `_2Octanone` |
| `_1234Tetrahydronaphthalene` | `_1Heptene` | `_246Trinitrotoluene` | `_2Pentanol` |
| `_123Trimethylbenzene` | `_1Heptyne` | `_2Butanol` | `_2Pentanone` |
| `_124Trimethylbenzene` | `_1Hexanol` | `_2Chloropropane` | `_2PentylMercaptan` |
| `_12Butadiene` | `_1Hexene` | `_2EthylButanoicAcid` | `_2Pentyne` |
| `_12Butanediol` | `_1Hexyne` | `_2EthylHexanoicAcid` | `_2Propanol` |
| `_12Dibromoethane` | `_1Methylcyclohexanol` | `_2Heptanol` | `_2PropylMercaptan` |
| `_12Dichloroethane` | `_1Methylcyclopentene` | `_2Heptanone` | `_3Heptanone` |
| `_12Dichloropropane` | `_1Nonanol` | `_2Hexanol` | `_3Hexanone` |
| `_12Difluoroethane` | `_1Nonene` | `_2Hexanone` | `_3Hexyne` |
| `_12Dimethoxypropane` | `_1Nonyne` | `_2Hexyne` | `_3Methyl12Butadiene` |
| `_12PropyleneGlycol` | `_1Octanol` | `_2Methyl1Butene` | `_3Methyl1Butanol` |
| `_135Trinitrobenzene` | `_1Octene` | `_2Methyl1Butene3Yne` | `_3Methyl1Butyne` |
| `_13Butadiene` | `_1Octyne` | `_2Methyl2Butene` | `_3Methylcyclopentene` |
| `_13Butanediol` | `_1Pentanol` | `_2Methyl2Propanol` | `_3Octanone` |
| `_14Dioxane` | `_1Pentene` | `_2MethylPropene` | `_3Pentanone` |
| `_1Butanol` | `_1Pentyne` | `_2Methylbutane` |  |

</details>

<details>
<summary>A–C — 60 classes</summary>

| Class name | Class name | Class name | Class name |
|---|---|---|---|
| `Acetaldehyde` | `Benzamide` | `ButylAcetate` | `Chloroform` |
| `Acetamide` | `Benzene` | `ButylMercaptan` | `Cis12Dimethylcyclohexane` |
| `AceticAcid` | `Benzenethiol` | `Butylbenzene` | `Cis2Butene` |
| `AceticAnhydride` | `BenzoicAcid` | `Butyraldehyde` | `Cis2Methylcyclohexanol` |
| `Acetone` | `Benzonitrile` | `ButyricAcid` | `Cumene` |
| `Acetonitrile` | `Benzophenone` | `Butyronitrile` | `Cyanogen` |
| `Acetylene` | `BenzylAlcohol` | `CarbonDisulfide` | `Cyclobutane` |
| `Acrolein` | `BenzylEthylEther` | `CarbonMonoxide` | `Cyclohexane` |
| `AcrylicAcid` | `BenzylMercaptan` | `CarbonTetrachloride` | `Cyclohexanol` |
| `Acrylonitrile` | `Biphenyl` | `CarbonTetrafluoride` | `Cyclohexanone` |
| `Air` | `Bromine` | `Carbondioxide` | `Cyclohexene` |
| `AlphaMethylStyrene` | `Bromobenzene` | `Chlorine` | `CyclohexylMercaptan` |
| `Ammonia` | `Bromoethane` | `ChloroBenzene` | `Cyclopentane` |
| `Anisole` | `Bromomethane` | `ChloroMethane` | `Cyclopentene` |
| `Argon` | `Butane` | `Chloroethane` | `Cyclopropane` |

</details>

<details>
<summary>D–H — 77 classes</summary>

| Class name | Class name | Class name | Class name |
|---|---|---|---|
| `Decanal` | `DimethylPhthalate` | `Ethylcyclopentane` | `Heptadecane` |
| `Decane` | `DimethylSulfide` | `Ethylene` | `Heptanal` |
| `DecanoicAcid` | `DimethylSulfoxide` | `EthyleneGlycol` | `Heptane` |
| `DecylMercaptan` | `DimethylTerephthalate` | `EthyleneOxide` | `HeptanoicAcid` |
| `Deuterium` | `Dimethylsilane` | `Ethylenediamine` | `HeptylMercaptan` |
| `Dibromomethane` | `DiphenylEther` | `Ethyleneimine` | `Hexadecane` |
| `DibutylEther` | `DipropylAmine` | `EthylhexylEther` | `Hexanal` |
| `Dichloromethane` | `Dodecane` | `EthylisopropylEther` | `Hexane` |
| `DiethanolAmine` | `Eicosane` | `EthylisopropylKetone` | `HexanoicAcid` |
| `DiethylAmine` | `Ethane` | `EthylpropylEther` | `HexylMercaptan` |
| `DiethylEther` | `Ethanol` | `Ethyltrichlorosilane` | `Hydrazine` |
| `DiethylSulfide` | `EthylAcetate` | `Fluorine` | `Hydrogen` |
| `Difluoromethane` | `EthylAmine` | `FluoroBenzene` | `HydrogenBromide` |
| `DiisopropylAmine` | `EthylBenzoate` | `Fluoroethane` | `HydrogenChloride` |
| `DiisopropylEther` | `EthylButyrate` | `Fluoromethane` | `HydrogenCyanide` |
| `DiisopropylKetone` | `EthylFormate` | `Formaldehyde` | `HydrogenFluoride` |
| `DimethylAcetylene` | `EthylMercaptan` | `Formamide` | `HydrogenSulfide` |
| `DimethylAmine` | `EthylPropionate` | `FormicAcid` |  |
| `DimethylDisulfide` | `Ethylbenzene` | `Furan` |  |
| `DimethylEther` | `Ethylcyclohexane` | `Helium` |  |

</details>

<details>
<summary>I–M — 40 classes</summary>

| Class name | Class name | Class name | Class name |
|---|---|---|---|
| `IsobutyricAcid` | `MethylAcrylate` | `MethylTertButylEther` | `MethylethylSulfide` |
| `IsopropylAmine` | `MethylAmine` | `MethylVinylEther` | `MethylisobutylEther` |
| `MalonicAcid` | `MethylBenzoate` | `MethylbutylEther` | `MethylisobutylKetone` |
| `Mcresol` | `MethylButyrate` | `MethylbutylSulfide` | `MethylisopropylEther` |
| `Mdichlorobenzene` | `MethylFormate` | `Methylchlorosilane` | `MethylisopropylKetone` |
| `MethacrylicAcid` | `MethylIsocyanate` | `Methylcyclohexane` | `MethylisopropylSulfide` |
| `Methane` | `MethylMercaptan` | `Methylcyclopentane` | `MethylpropylEther` |
| `Methanol` | `MethylMethacrylate` | `Methyldichlorosilane` | `MethylpropylSulfide` |
| `MethylAcetate` | `MethylPentylEther` | `MethylethylEther` | `Methylsilane` |
| `MethylAcetylene` | `MethylPropionate` | `MethylethylKetone` | `Mxylene` |

</details>

<details>
<summary>N–R — 52 classes</summary>

| Class name | Class name | Class name | Class name |
|---|---|---|---|
| `Naphthalene` | `NonanoicAcid` | `Ozone` | `Propane` |
| `Neon` | `NonylMercaptan` | `Pcresol` | `Propenylcyclohexene` |
| `NitricOxide` | `Ocresol` | `Pdichlorobenzene` | `Propionaldehyde` |
| `Nitroethane` | `Octadecane` | `Pentadecane` | `PropionicAcid` |
| `Nitrogen` | `Octanal` | `Pentanal` | `Propionitrile` |
| `NitrogenTrifluoride` | `Octane` | `Pentane` | `PropylAcetate` |
| `Nitromethane` | `OctanoicAcid` | `PentanoicAcid` | `PropylAmine` |
| `NitrousOxide` | `OctylMercaptan` | `PentylMercaptan` | `PropylFormate` |
| `NmethylAcetamide` | `Odichlorobenzene` | `Phenanthrene` | `PropylMercaptan` |
| `NndimethylFormamide` | `Oterphenyl` | `Phenol` | `Propylbenzene` |
| `Nonadecane` | `OxalicAcid` | `PhenylIsocyanate` | `Propylene` |
| `Nonanal` | `Oxygen` | `PhthalicAnhydride` | `Pxylene` |
| `Nonane` | `Oxylene` | `Propadiene` | `Quinone` |

</details>

<details>
<summary>S–Z — 25 classes</summary>

| Class name | Class name | Class name | Class name |
|---|---|---|---|
| `SeButylmercaptan` | `TerephthalicAcid` | `Trans2Butene` | `VinylAcetylene` |
| `SiliconTetrafluoride` | `Tetradecane` | `Trans2Methylcyclohexanol` | `VinylChloride` |
| `Styrene` | `Tetrahydrofuran` | `Tridecane` | `VinylTrichlorosilane` |
| `SuccinicAcid` | `Tetrahydrothiophene` | `TriethylAmine` | `Water` |
| `SulfurDioxide` | `Thiophene` | `TrimethylAmine` |  |
| `SulfurHexafluoride` | `Toluene` | `Undecane` |  |
| `SulfurTrioxide` | `Trans12Dimethylcyclohexane` | `VinylAcetate` |  |

</details>

**General fluid-category classes:** `Gas`, `InorganicLiquid`, `Oil`, `OrganicLiquid`, `Steam`, and `Vapor`.

**Legacy aliases:** `EthlylAcetate` and `Ethlylene` remain exported for compatibility. Prefer `EthylAcetate` and `Ethylene` in new code.

## Constructor parameters

Most chemical component classes inherit the Component constructor. The defaults and accepted inputs for those classes are listed below. Some exported classes override the constructor; in particular, Steam accepts temperature, pressure, and phase only, so the other arguments in this table do not apply to Steam.

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

Every chemical component class exposes three identity fields. These values describe the substance and are defined by the component class; they are not calculated from the operating temperature or pressure.

| Attribute | Type / unit | Meaning | Example (`Water`) |
|---|---|---|---|
| `name` | `str` | Human-readable substance name | `"Water"` |
| `formula` | `str` | Chemical formula using the class's stored notation | `"H2O"` |
| `molecular_weight` | `float`, g/mol | Molecular weight used in molar-to-mass conversions and gas-density calculations | `18.015` |

Read them directly from an instance or class:

~~~python
from processpi.components import Water

water = Water()
print(water.name)              # Water
print(water.formula)           # H2O
print(water.molecular_weight)  # 18.015 g/mol
~~~

### Operating-condition attributes

These are instance attributes, not chemical identity metadata:

| Attribute | Type | Meaning |
|---|---|---|
| `temperature` | `Temperature` | Current temperature used when evaluating properties; defaults to 25 °C in the base constructor |
| `pressure` | `Pressure` | Current absolute pressure; defaults to 101325 Pa in the base constructor |
| `hx_type` | `str` | Heat-exchanger fluid category used by the HX standards lookup; inferred by the base class unless the component defines an override |

The evaluated phase is obtained through `phase()`; the heat-exchanger classification is available through `httype()` and the detailed service mapping through `hx_data()`. These are methods, not identity fields.

### Internal correlation data

Attributes beginning with an underscore (for example, `_critical_temperature`, `_density_constants`, and `_vapor_pressure_constants`) are implementation data used by property correlations. Their presence varies by component. They are not part of the stable public metadata API and should not be modified by application code.

## Inherited methods and calculated properties

Call calculated-property members with parentheses to obtain their evaluated result; for example, water.density() returns a Density object. Do not assume that accessing water.density without parentheses returns a quantity: the uncalled attribute may be a callable wrapper or a bound method, depending on the component and member.

| Member | Return type | Explanation |
|---|---|---|
| phase() | str | Calling phase() returns gas or liquid. Use the call form to obtain the evaluated phase string. An explicit phase override takes priority; otherwise the base class considers the default phase, critical temperature, and vapour pressure. |
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
print(acid.viscosity().to("Pa·s"))
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
