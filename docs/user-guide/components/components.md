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

The ProcessPI component catalogue contains **345 chemical component classes**, six general fluid-category classes, and two legacy aliases. The names below are the exact Python import names exported by `processpi.components`.

Search by class name or jump to an alphabetical group. The search filters the list in place; clear the search field to restore the full catalogue.

<div class="component-directory">
<div class="component-directory__toolbar">
<label class="component-directory__search-label" for="component-directory-search">Find a component</label>
<input id="component-directory-search" class="component-directory__search" type="search" placeholder="Search by Python class name — e.g. AceticAcid, Water, _1Propanol" autocomplete="off" spellcheck="false">
<p id="component-directory-status" class="component-directory__status" role="status" aria-live="polite">Showing all exported component names.</p>
</div>
<nav class="component-directory__jump" aria-label="Jump to component group">
<a href="#components-0-9">0–9</a>
<a href="#components-a-c">A–C</a>
<a href="#components-d-h">D–H</a>
<a href="#components-i-m">I–M</a>
<a href="#components-n-r">N–R</a>
<a href="#components-s-z">S–Z</a>
<a href="#components-general">Fluid classes</a><a href="#components-aliases">Legacy aliases</a></nav>
<section class="component-directory__group" id="components-0-9" data-component-group><h3>0–9 <span>91 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="_112trichloroethane"><code>_112Trichloroethane</code></li>
<li data-component-item data-component="_1butene"><code>_1Butene</code></li>
<li data-component-item data-component="_1propanol"><code>_1Propanol</code></li>
<li data-component-item data-component="_2methylbutanoicacid"><code>_2MethylbutanoicAcid</code></li>
<li data-component-item data-component="_11dibromoethane"><code>_11Dibromoethane</code></li>
<li data-component-item data-component="_1butyne"><code>_1Butyne</code></li>
<li data-component-item data-component="_1undecanol"><code>_1Undecanol</code></li>
<li data-component-item data-component="_2methyloctanoicacid"><code>_2MethyloctanoicAcid</code></li>
<li data-component-item data-component="_11dichloroethane"><code>_11Dichloroethane</code></li>
<li data-component-item data-component="_1chloropropane"><code>_1Chloropropane</code></li>
<li data-component-item data-component="_2233tetramethylbutane"><code>_2233Tetramethylbutane</code></li>
<li data-component-item data-component="_2methylpentane"><code>_2Methylpentane</code></li>
<li data-component-item data-component="_11dichloropropane"><code>_11Dichloropropane</code></li>
<li data-component-item data-component="_1decanol"><code>_1Decanol</code></li>
<li data-component-item data-component="_224trimethylpentane"><code>_224Trimethylpentane</code></li>
<li data-component-item data-component="_2methylpropane"><code>_2Methylpropane</code></li>
<li data-component-item data-component="_11difluoroethane"><code>_11Difluoroethane</code></li>
<li data-component-item data-component="_1decene"><code>_1Decene</code></li>
<li data-component-item data-component="_233trimethylpentane"><code>_233Trimethylpentane</code></li>
<li data-component-item data-component="_2nonanol"><code>_2Nonanol</code></li>
<li data-component-item data-component="_11dimethoxyethane"><code>_11Dimethoxyethane</code></li>
<li data-component-item data-component="_1decyne"><code>_1Decyne</code></li>
<li data-component-item data-component="_23dimethylbutane"><code>_23Dimethylbutane</code></li>
<li data-component-item data-component="_2octanol"><code>_2Octanol</code></li>
<li data-component-item data-component="_11dimethylcyclohexane"><code>_11Dimethylcyclohexane</code></li>
<li data-component-item data-component="_1heptanol"><code>_1Heptanol</code></li>
<li data-component-item data-component="_23dimethylpentane"><code>_23Dimethylpentane</code></li>
<li data-component-item data-component="_2octanone"><code>_2Octanone</code></li>
<li data-component-item data-component="_1234tetrahydronaphthalene"><code>_1234Tetrahydronaphthalene</code></li>
<li data-component-item data-component="_1heptene"><code>_1Heptene</code></li>
<li data-component-item data-component="_246trinitrotoluene"><code>_246Trinitrotoluene</code></li>
<li data-component-item data-component="_2pentanol"><code>_2Pentanol</code></li>
<li data-component-item data-component="_123trimethylbenzene"><code>_123Trimethylbenzene</code></li>
<li data-component-item data-component="_1heptyne"><code>_1Heptyne</code></li>
<li data-component-item data-component="_2butanol"><code>_2Butanol</code></li>
<li data-component-item data-component="_2pentanone"><code>_2Pentanone</code></li>
<li data-component-item data-component="_124trimethylbenzene"><code>_124Trimethylbenzene</code></li>
<li data-component-item data-component="_1hexanol"><code>_1Hexanol</code></li>
<li data-component-item data-component="_2chloropropane"><code>_2Chloropropane</code></li>
<li data-component-item data-component="_2pentylmercaptan"><code>_2PentylMercaptan</code></li>
<li data-component-item data-component="_12butadiene"><code>_12Butadiene</code></li>
<li data-component-item data-component="_1hexene"><code>_1Hexene</code></li>
<li data-component-item data-component="_2ethylbutanoicacid"><code>_2EthylButanoicAcid</code></li>
<li data-component-item data-component="_2pentyne"><code>_2Pentyne</code></li>
<li data-component-item data-component="_12butanediol"><code>_12Butanediol</code></li>
<li data-component-item data-component="_1hexyne"><code>_1Hexyne</code></li>
<li data-component-item data-component="_2ethylhexanoicacid"><code>_2EthylHexanoicAcid</code></li>
<li data-component-item data-component="_2propanol"><code>_2Propanol</code></li>
<li data-component-item data-component="_12dibromoethane"><code>_12Dibromoethane</code></li>
<li data-component-item data-component="_1methylcyclohexanol"><code>_1Methylcyclohexanol</code></li>
<li data-component-item data-component="_2heptanol"><code>_2Heptanol</code></li>
<li data-component-item data-component="_2propylmercaptan"><code>_2PropylMercaptan</code></li>
<li data-component-item data-component="_12dichloroethane"><code>_12Dichloroethane</code></li>
<li data-component-item data-component="_1methylcyclopentene"><code>_1Methylcyclopentene</code></li>
<li data-component-item data-component="_2heptanone"><code>_2Heptanone</code></li>
<li data-component-item data-component="_3heptanone"><code>_3Heptanone</code></li>
<li data-component-item data-component="_12dichloropropane"><code>_12Dichloropropane</code></li>
<li data-component-item data-component="_1nonanol"><code>_1Nonanol</code></li>
<li data-component-item data-component="_2hexanol"><code>_2Hexanol</code></li>
<li data-component-item data-component="_3hexanone"><code>_3Hexanone</code></li>
<li data-component-item data-component="_12difluoroethane"><code>_12Difluoroethane</code></li>
<li data-component-item data-component="_1nonene"><code>_1Nonene</code></li>
<li data-component-item data-component="_2hexanone"><code>_2Hexanone</code></li>
<li data-component-item data-component="_3hexyne"><code>_3Hexyne</code></li>
<li data-component-item data-component="_12dimethoxypropane"><code>_12Dimethoxypropane</code></li>
<li data-component-item data-component="_1nonyne"><code>_1Nonyne</code></li>
<li data-component-item data-component="_2hexyne"><code>_2Hexyne</code></li>
<li data-component-item data-component="_3methyl12butadiene"><code>_3Methyl12Butadiene</code></li>
<li data-component-item data-component="_12propyleneglycol"><code>_12PropyleneGlycol</code></li>
<li data-component-item data-component="_1octanol"><code>_1Octanol</code></li>
<li data-component-item data-component="_2methyl1butene"><code>_2Methyl1Butene</code></li>
<li data-component-item data-component="_3methyl1butanol"><code>_3Methyl1Butanol</code></li>
<li data-component-item data-component="_135trinitrobenzene"><code>_135Trinitrobenzene</code></li>
<li data-component-item data-component="_1octene"><code>_1Octene</code></li>
<li data-component-item data-component="_2methyl1butene3yne"><code>_2Methyl1Butene3Yne</code></li>
<li data-component-item data-component="_3methyl1butyne"><code>_3Methyl1Butyne</code></li>
<li data-component-item data-component="_13butadiene"><code>_13Butadiene</code></li>
<li data-component-item data-component="_1octyne"><code>_1Octyne</code></li>
<li data-component-item data-component="_2methyl2butene"><code>_2Methyl2Butene</code></li>
<li data-component-item data-component="_3methylcyclopentene"><code>_3Methylcyclopentene</code></li>
<li data-component-item data-component="_13butanediol"><code>_13Butanediol</code></li>
<li data-component-item data-component="_1pentanol"><code>_1Pentanol</code></li>
<li data-component-item data-component="_2methyl2propanol"><code>_2Methyl2Propanol</code></li>
<li data-component-item data-component="_3octanone"><code>_3Octanone</code></li>
<li data-component-item data-component="_14dioxane"><code>_14Dioxane</code></li>
<li data-component-item data-component="_1pentene"><code>_1Pentene</code></li>
<li data-component-item data-component="_2methylpropene"><code>_2MethylPropene</code></li>
<li data-component-item data-component="_3pentanone"><code>_3Pentanone</code></li>
<li data-component-item data-component="_1butanol"><code>_1Butanol</code></li>
<li data-component-item data-component="_1pentyne"><code>_1Pentyne</code></li>
<li data-component-item data-component="_2methylbutane"><code>_2Methylbutane</code></li>
</ul></section>
<section class="component-directory__group" id="components-a-c" data-component-group><h3>A–C <span>60 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="acetaldehyde"><code>Acetaldehyde</code></li>
<li data-component-item data-component="benzamide"><code>Benzamide</code></li>
<li data-component-item data-component="butylacetate"><code>ButylAcetate</code></li>
<li data-component-item data-component="chloroform"><code>Chloroform</code></li>
<li data-component-item data-component="acetamide"><code>Acetamide</code></li>
<li data-component-item data-component="benzene"><code>Benzene</code></li>
<li data-component-item data-component="butylmercaptan"><code>ButylMercaptan</code></li>
<li data-component-item data-component="cis12dimethylcyclohexane"><code>Cis12Dimethylcyclohexane</code></li>
<li data-component-item data-component="aceticacid"><code>AceticAcid</code></li>
<li data-component-item data-component="benzenethiol"><code>Benzenethiol</code></li>
<li data-component-item data-component="butylbenzene"><code>Butylbenzene</code></li>
<li data-component-item data-component="cis2butene"><code>Cis2Butene</code></li>
<li data-component-item data-component="aceticanhydride"><code>AceticAnhydride</code></li>
<li data-component-item data-component="benzoicacid"><code>BenzoicAcid</code></li>
<li data-component-item data-component="butyraldehyde"><code>Butyraldehyde</code></li>
<li data-component-item data-component="cis2methylcyclohexanol"><code>Cis2Methylcyclohexanol</code></li>
<li data-component-item data-component="acetone"><code>Acetone</code></li>
<li data-component-item data-component="benzonitrile"><code>Benzonitrile</code></li>
<li data-component-item data-component="butyricacid"><code>ButyricAcid</code></li>
<li data-component-item data-component="cumene"><code>Cumene</code></li>
<li data-component-item data-component="acetonitrile"><code>Acetonitrile</code></li>
<li data-component-item data-component="benzophenone"><code>Benzophenone</code></li>
<li data-component-item data-component="butyronitrile"><code>Butyronitrile</code></li>
<li data-component-item data-component="cyanogen"><code>Cyanogen</code></li>
<li data-component-item data-component="acetylene"><code>Acetylene</code></li>
<li data-component-item data-component="benzylalcohol"><code>BenzylAlcohol</code></li>
<li data-component-item data-component="carbondisulfide"><code>CarbonDisulfide</code></li>
<li data-component-item data-component="cyclobutane"><code>Cyclobutane</code></li>
<li data-component-item data-component="acrolein"><code>Acrolein</code></li>
<li data-component-item data-component="benzylethylether"><code>BenzylEthylEther</code></li>
<li data-component-item data-component="carbonmonoxide"><code>CarbonMonoxide</code></li>
<li data-component-item data-component="cyclohexane"><code>Cyclohexane</code></li>
<li data-component-item data-component="acrylicacid"><code>AcrylicAcid</code></li>
<li data-component-item data-component="benzylmercaptan"><code>BenzylMercaptan</code></li>
<li data-component-item data-component="carbontetrachloride"><code>CarbonTetrachloride</code></li>
<li data-component-item data-component="cyclohexanol"><code>Cyclohexanol</code></li>
<li data-component-item data-component="acrylonitrile"><code>Acrylonitrile</code></li>
<li data-component-item data-component="biphenyl"><code>Biphenyl</code></li>
<li data-component-item data-component="carbontetrafluoride"><code>CarbonTetrafluoride</code></li>
<li data-component-item data-component="cyclohexanone"><code>Cyclohexanone</code></li>
<li data-component-item data-component="air"><code>Air</code></li>
<li data-component-item data-component="bromine"><code>Bromine</code></li>
<li data-component-item data-component="carbondioxide"><code>Carbondioxide</code></li>
<li data-component-item data-component="cyclohexene"><code>Cyclohexene</code></li>
<li data-component-item data-component="alphamethylstyrene"><code>AlphaMethylStyrene</code></li>
<li data-component-item data-component="bromobenzene"><code>Bromobenzene</code></li>
<li data-component-item data-component="chlorine"><code>Chlorine</code></li>
<li data-component-item data-component="cyclohexylmercaptan"><code>CyclohexylMercaptan</code></li>
<li data-component-item data-component="ammonia"><code>Ammonia</code></li>
<li data-component-item data-component="bromoethane"><code>Bromoethane</code></li>
<li data-component-item data-component="chlorobenzene"><code>ChloroBenzene</code></li>
<li data-component-item data-component="cyclopentane"><code>Cyclopentane</code></li>
<li data-component-item data-component="anisole"><code>Anisole</code></li>
<li data-component-item data-component="bromomethane"><code>Bromomethane</code></li>
<li data-component-item data-component="chloromethane"><code>ChloroMethane</code></li>
<li data-component-item data-component="cyclopentene"><code>Cyclopentene</code></li>
<li data-component-item data-component="argon"><code>Argon</code></li>
<li data-component-item data-component="butane"><code>Butane</code></li>
<li data-component-item data-component="chloroethane"><code>Chloroethane</code></li>
<li data-component-item data-component="cyclopropane"><code>Cyclopropane</code></li>
</ul></section>
<section class="component-directory__group" id="components-d-h" data-component-group><h3>D–H <span>77 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="decanal"><code>Decanal</code></li>
<li data-component-item data-component="dimethylphthalate"><code>DimethylPhthalate</code></li>
<li data-component-item data-component="ethylcyclopentane"><code>Ethylcyclopentane</code></li>
<li data-component-item data-component="heptadecane"><code>Heptadecane</code></li>
<li data-component-item data-component="decane"><code>Decane</code></li>
<li data-component-item data-component="dimethylsulfide"><code>DimethylSulfide</code></li>
<li data-component-item data-component="ethylene"><code>Ethylene</code></li>
<li data-component-item data-component="heptanal"><code>Heptanal</code></li>
<li data-component-item data-component="decanoicacid"><code>DecanoicAcid</code></li>
<li data-component-item data-component="dimethylsulfoxide"><code>DimethylSulfoxide</code></li>
<li data-component-item data-component="ethyleneglycol"><code>EthyleneGlycol</code></li>
<li data-component-item data-component="heptane"><code>Heptane</code></li>
<li data-component-item data-component="decylmercaptan"><code>DecylMercaptan</code></li>
<li data-component-item data-component="dimethylterephthalate"><code>DimethylTerephthalate</code></li>
<li data-component-item data-component="ethyleneoxide"><code>EthyleneOxide</code></li>
<li data-component-item data-component="heptanoicacid"><code>HeptanoicAcid</code></li>
<li data-component-item data-component="deuterium"><code>Deuterium</code></li>
<li data-component-item data-component="dimethylsilane"><code>Dimethylsilane</code></li>
<li data-component-item data-component="ethylenediamine"><code>Ethylenediamine</code></li>
<li data-component-item data-component="heptylmercaptan"><code>HeptylMercaptan</code></li>
<li data-component-item data-component="dibromomethane"><code>Dibromomethane</code></li>
<li data-component-item data-component="diphenylether"><code>DiphenylEther</code></li>
<li data-component-item data-component="ethyleneimine"><code>Ethyleneimine</code></li>
<li data-component-item data-component="hexadecane"><code>Hexadecane</code></li>
<li data-component-item data-component="dibutylether"><code>DibutylEther</code></li>
<li data-component-item data-component="dipropylamine"><code>DipropylAmine</code></li>
<li data-component-item data-component="ethylhexylether"><code>EthylhexylEther</code></li>
<li data-component-item data-component="hexanal"><code>Hexanal</code></li>
<li data-component-item data-component="dichloromethane"><code>Dichloromethane</code></li>
<li data-component-item data-component="dodecane"><code>Dodecane</code></li>
<li data-component-item data-component="ethylisopropylether"><code>EthylisopropylEther</code></li>
<li data-component-item data-component="hexane"><code>Hexane</code></li>
<li data-component-item data-component="diethanolamine"><code>DiethanolAmine</code></li>
<li data-component-item data-component="eicosane"><code>Eicosane</code></li>
<li data-component-item data-component="ethylisopropylketone"><code>EthylisopropylKetone</code></li>
<li data-component-item data-component="hexanoicacid"><code>HexanoicAcid</code></li>
<li data-component-item data-component="diethylamine"><code>DiethylAmine</code></li>
<li data-component-item data-component="ethane"><code>Ethane</code></li>
<li data-component-item data-component="ethylpropylether"><code>EthylpropylEther</code></li>
<li data-component-item data-component="hexylmercaptan"><code>HexylMercaptan</code></li>
<li data-component-item data-component="diethylether"><code>DiethylEther</code></li>
<li data-component-item data-component="ethanol"><code>Ethanol</code></li>
<li data-component-item data-component="ethyltrichlorosilane"><code>Ethyltrichlorosilane</code></li>
<li data-component-item data-component="hydrazine"><code>Hydrazine</code></li>
<li data-component-item data-component="diethylsulfide"><code>DiethylSulfide</code></li>
<li data-component-item data-component="ethylacetate"><code>EthylAcetate</code></li>
<li data-component-item data-component="fluorine"><code>Fluorine</code></li>
<li data-component-item data-component="hydrogen"><code>Hydrogen</code></li>
<li data-component-item data-component="difluoromethane"><code>Difluoromethane</code></li>
<li data-component-item data-component="ethylamine"><code>EthylAmine</code></li>
<li data-component-item data-component="fluorobenzene"><code>FluoroBenzene</code></li>
<li data-component-item data-component="hydrogenbromide"><code>HydrogenBromide</code></li>
<li data-component-item data-component="diisopropylamine"><code>DiisopropylAmine</code></li>
<li data-component-item data-component="ethylbenzoate"><code>EthylBenzoate</code></li>
<li data-component-item data-component="fluoroethane"><code>Fluoroethane</code></li>
<li data-component-item data-component="hydrogenchloride"><code>HydrogenChloride</code></li>
<li data-component-item data-component="diisopropylether"><code>DiisopropylEther</code></li>
<li data-component-item data-component="ethylbutyrate"><code>EthylButyrate</code></li>
<li data-component-item data-component="fluoromethane"><code>Fluoromethane</code></li>
<li data-component-item data-component="hydrogencyanide"><code>HydrogenCyanide</code></li>
<li data-component-item data-component="diisopropylketone"><code>DiisopropylKetone</code></li>
<li data-component-item data-component="ethylformate"><code>EthylFormate</code></li>
<li data-component-item data-component="formaldehyde"><code>Formaldehyde</code></li>
<li data-component-item data-component="hydrogenfluoride"><code>HydrogenFluoride</code></li>
<li data-component-item data-component="dimethylacetylene"><code>DimethylAcetylene</code></li>
<li data-component-item data-component="ethylmercaptan"><code>EthylMercaptan</code></li>
<li data-component-item data-component="formamide"><code>Formamide</code></li>
<li data-component-item data-component="hydrogensulfide"><code>HydrogenSulfide</code></li>
<li data-component-item data-component="dimethylamine"><code>DimethylAmine</code></li>
<li data-component-item data-component="ethylpropionate"><code>EthylPropionate</code></li>
<li data-component-item data-component="formicacid"><code>FormicAcid</code></li>
<li data-component-item data-component="dimethyldisulfide"><code>DimethylDisulfide</code></li>
<li data-component-item data-component="ethylbenzene"><code>Ethylbenzene</code></li>
<li data-component-item data-component="furan"><code>Furan</code></li>
<li data-component-item data-component="dimethylether"><code>DimethylEther</code></li>
<li data-component-item data-component="ethylcyclohexane"><code>Ethylcyclohexane</code></li>
<li data-component-item data-component="helium"><code>Helium</code></li>
</ul></section>
<section class="component-directory__group" id="components-i-m" data-component-group><h3>I–M <span>40 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="isobutyricacid"><code>IsobutyricAcid</code></li>
<li data-component-item data-component="methylacrylate"><code>MethylAcrylate</code></li>
<li data-component-item data-component="methyltertbutylether"><code>MethylTertButylEther</code></li>
<li data-component-item data-component="methylethylsulfide"><code>MethylethylSulfide</code></li>
<li data-component-item data-component="isopropylamine"><code>IsopropylAmine</code></li>
<li data-component-item data-component="methylamine"><code>MethylAmine</code></li>
<li data-component-item data-component="methylvinylether"><code>MethylVinylEther</code></li>
<li data-component-item data-component="methylisobutylether"><code>MethylisobutylEther</code></li>
<li data-component-item data-component="malonicacid"><code>MalonicAcid</code></li>
<li data-component-item data-component="methylbenzoate"><code>MethylBenzoate</code></li>
<li data-component-item data-component="methylbutylether"><code>MethylbutylEther</code></li>
<li data-component-item data-component="methylisobutylketone"><code>MethylisobutylKetone</code></li>
<li data-component-item data-component="mcresol"><code>Mcresol</code></li>
<li data-component-item data-component="methylbutyrate"><code>MethylButyrate</code></li>
<li data-component-item data-component="methylbutylsulfide"><code>MethylbutylSulfide</code></li>
<li data-component-item data-component="methylisopropylether"><code>MethylisopropylEther</code></li>
<li data-component-item data-component="mdichlorobenzene"><code>Mdichlorobenzene</code></li>
<li data-component-item data-component="methylformate"><code>MethylFormate</code></li>
<li data-component-item data-component="methylchlorosilane"><code>Methylchlorosilane</code></li>
<li data-component-item data-component="methylisopropylketone"><code>MethylisopropylKetone</code></li>
<li data-component-item data-component="methacrylicacid"><code>MethacrylicAcid</code></li>
<li data-component-item data-component="methylisocyanate"><code>MethylIsocyanate</code></li>
<li data-component-item data-component="methylcyclohexane"><code>Methylcyclohexane</code></li>
<li data-component-item data-component="methylisopropylsulfide"><code>MethylisopropylSulfide</code></li>
<li data-component-item data-component="methane"><code>Methane</code></li>
<li data-component-item data-component="methylmercaptan"><code>MethylMercaptan</code></li>
<li data-component-item data-component="methylcyclopentane"><code>Methylcyclopentane</code></li>
<li data-component-item data-component="methylpropylether"><code>MethylpropylEther</code></li>
<li data-component-item data-component="methanol"><code>Methanol</code></li>
<li data-component-item data-component="methylmethacrylate"><code>MethylMethacrylate</code></li>
<li data-component-item data-component="methyldichlorosilane"><code>Methyldichlorosilane</code></li>
<li data-component-item data-component="methylpropylsulfide"><code>MethylpropylSulfide</code></li>
<li data-component-item data-component="methylacetate"><code>MethylAcetate</code></li>
<li data-component-item data-component="methylpentylether"><code>MethylPentylEther</code></li>
<li data-component-item data-component="methylethylether"><code>MethylethylEther</code></li>
<li data-component-item data-component="methylsilane"><code>Methylsilane</code></li>
<li data-component-item data-component="methylacetylene"><code>MethylAcetylene</code></li>
<li data-component-item data-component="methylpropionate"><code>MethylPropionate</code></li>
<li data-component-item data-component="methylethylketone"><code>MethylethylKetone</code></li>
<li data-component-item data-component="mxylene"><code>Mxylene</code></li>
</ul></section>
<section class="component-directory__group" id="components-n-r" data-component-group><h3>N–R <span>52 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="naphthalene"><code>Naphthalene</code></li>
<li data-component-item data-component="nonanoicacid"><code>NonanoicAcid</code></li>
<li data-component-item data-component="ozone"><code>Ozone</code></li>
<li data-component-item data-component="propane"><code>Propane</code></li>
<li data-component-item data-component="neon"><code>Neon</code></li>
<li data-component-item data-component="nonylmercaptan"><code>NonylMercaptan</code></li>
<li data-component-item data-component="pcresol"><code>Pcresol</code></li>
<li data-component-item data-component="propenylcyclohexene"><code>Propenylcyclohexene</code></li>
<li data-component-item data-component="nitricoxide"><code>NitricOxide</code></li>
<li data-component-item data-component="ocresol"><code>Ocresol</code></li>
<li data-component-item data-component="pdichlorobenzene"><code>Pdichlorobenzene</code></li>
<li data-component-item data-component="propionaldehyde"><code>Propionaldehyde</code></li>
<li data-component-item data-component="nitroethane"><code>Nitroethane</code></li>
<li data-component-item data-component="octadecane"><code>Octadecane</code></li>
<li data-component-item data-component="pentadecane"><code>Pentadecane</code></li>
<li data-component-item data-component="propionicacid"><code>PropionicAcid</code></li>
<li data-component-item data-component="nitrogen"><code>Nitrogen</code></li>
<li data-component-item data-component="octanal"><code>Octanal</code></li>
<li data-component-item data-component="pentanal"><code>Pentanal</code></li>
<li data-component-item data-component="propionitrile"><code>Propionitrile</code></li>
<li data-component-item data-component="nitrogentrifluoride"><code>NitrogenTrifluoride</code></li>
<li data-component-item data-component="octane"><code>Octane</code></li>
<li data-component-item data-component="pentane"><code>Pentane</code></li>
<li data-component-item data-component="propylacetate"><code>PropylAcetate</code></li>
<li data-component-item data-component="nitromethane"><code>Nitromethane</code></li>
<li data-component-item data-component="octanoicacid"><code>OctanoicAcid</code></li>
<li data-component-item data-component="pentanoicacid"><code>PentanoicAcid</code></li>
<li data-component-item data-component="propylamine"><code>PropylAmine</code></li>
<li data-component-item data-component="nitrousoxide"><code>NitrousOxide</code></li>
<li data-component-item data-component="octylmercaptan"><code>OctylMercaptan</code></li>
<li data-component-item data-component="pentylmercaptan"><code>PentylMercaptan</code></li>
<li data-component-item data-component="propylformate"><code>PropylFormate</code></li>
<li data-component-item data-component="nmethylacetamide"><code>NmethylAcetamide</code></li>
<li data-component-item data-component="odichlorobenzene"><code>Odichlorobenzene</code></li>
<li data-component-item data-component="phenanthrene"><code>Phenanthrene</code></li>
<li data-component-item data-component="propylmercaptan"><code>PropylMercaptan</code></li>
<li data-component-item data-component="nndimethylformamide"><code>NndimethylFormamide</code></li>
<li data-component-item data-component="oterphenyl"><code>Oterphenyl</code></li>
<li data-component-item data-component="phenol"><code>Phenol</code></li>
<li data-component-item data-component="propylbenzene"><code>Propylbenzene</code></li>
<li data-component-item data-component="nonadecane"><code>Nonadecane</code></li>
<li data-component-item data-component="oxalicacid"><code>OxalicAcid</code></li>
<li data-component-item data-component="phenylisocyanate"><code>PhenylIsocyanate</code></li>
<li data-component-item data-component="propylene"><code>Propylene</code></li>
<li data-component-item data-component="nonanal"><code>Nonanal</code></li>
<li data-component-item data-component="oxygen"><code>Oxygen</code></li>
<li data-component-item data-component="phthalicanhydride"><code>PhthalicAnhydride</code></li>
<li data-component-item data-component="pxylene"><code>Pxylene</code></li>
<li data-component-item data-component="nonane"><code>Nonane</code></li>
<li data-component-item data-component="oxylene"><code>Oxylene</code></li>
<li data-component-item data-component="propadiene"><code>Propadiene</code></li>
<li data-component-item data-component="quinone"><code>Quinone</code></li>
</ul></section>
<section class="component-directory__group" id="components-s-z" data-component-group><h3>S–Z <span>25 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="sebutylmercaptan"><code>SeButylmercaptan</code></li>
<li data-component-item data-component="terephthalicacid"><code>TerephthalicAcid</code></li>
<li data-component-item data-component="trans2butene"><code>Trans2Butene</code></li>
<li data-component-item data-component="vinylacetylene"><code>VinylAcetylene</code></li>
<li data-component-item data-component="silicontetrafluoride"><code>SiliconTetrafluoride</code></li>
<li data-component-item data-component="tetradecane"><code>Tetradecane</code></li>
<li data-component-item data-component="trans2methylcyclohexanol"><code>Trans2Methylcyclohexanol</code></li>
<li data-component-item data-component="vinylchloride"><code>VinylChloride</code></li>
<li data-component-item data-component="styrene"><code>Styrene</code></li>
<li data-component-item data-component="tetrahydrofuran"><code>Tetrahydrofuran</code></li>
<li data-component-item data-component="tridecane"><code>Tridecane</code></li>
<li data-component-item data-component="vinyltrichlorosilane"><code>VinylTrichlorosilane</code></li>
<li data-component-item data-component="succinicacid"><code>SuccinicAcid</code></li>
<li data-component-item data-component="tetrahydrothiophene"><code>Tetrahydrothiophene</code></li>
<li data-component-item data-component="triethylamine"><code>TriethylAmine</code></li>
<li data-component-item data-component="water"><code>Water</code></li>
<li data-component-item data-component="sulfurdioxide"><code>SulfurDioxide</code></li>
<li data-component-item data-component="thiophene"><code>Thiophene</code></li>
<li data-component-item data-component="trimethylamine"><code>TrimethylAmine</code></li>
<li data-component-item data-component="sulfurhexafluoride"><code>SulfurHexafluoride</code></li>
<li data-component-item data-component="toluene"><code>Toluene</code></li>
<li data-component-item data-component="undecane"><code>Undecane</code></li>
<li data-component-item data-component="sulfurtrioxide"><code>SulfurTrioxide</code></li>
<li data-component-item data-component="trans12dimethylcyclohexane"><code>Trans12Dimethylcyclohexane</code></li>
<li data-component-item data-component="vinylacetate"><code>VinylAcetate</code></li>
</ul></section>
<section class="component-directory__group" id="components-general" data-component-group><h3>General fluid classes <span>6 classes</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="gas"><code>Gas</code></li>
<li data-component-item data-component="inorganicliquid"><code>InorganicLiquid</code></li>
<li data-component-item data-component="oil"><code>Oil</code></li>
<li data-component-item data-component="organicliquid"><code>OrganicLiquid</code></li>
<li data-component-item data-component="steam"><code>Steam</code></li>
<li data-component-item data-component="vapor"><code>Vapor</code></li>
</ul>
</section>
<section class="component-directory__group" id="components-aliases" data-component-group><h3>Legacy aliases <span>2 aliases</span></h3><ul class="component-directory__grid">
<li data-component-item data-component="ethlylacetate"><code>EthlylAcetate</code></li>
<li data-component-item data-component="ethlylene"><code>Ethlylene</code></li>
</ul>
<p class="component-directory__note">These names remain exported for backward compatibility. Prefer <code>EthylAcetate</code> and <code>Ethylene</code> in new code.</p>
</section>
</div>

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
| viscosity() | Viscosity | Returns supplied dynamic viscosity if present; otherwise evaluates the liquid correlation (DIPPR Eq. 101, Perry Table 2-313) or, in the gas phase, the vapour correlation (DIPPR Eq. 102, Perry Table 2-312); generic components without vapour data (`Gas`, `Vapor`) use Sutherland's law with air constants. |
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
