# **Class: `Styrene`**

## **Description**

The `Styrene` class represents the properties and constants for Styrene (C₆H₅CH=CH₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 312).

## **Properties**

* **`name`** (string): Styrene  
* **`formula`** (string): C₈H₈  
* **`molecular_weight`** (float): 104.149 g/mol  

## **Class Reference**

**`class Styrene()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(25,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  
* `density`: `Density`, default = `None`  
* `specific_heat`: `SpecificHeat`, default = `None`  
* `viscosity`: `Viscosity`, default = `None`  
* `thermal_conductivity`: `ThermalConductivity`, default = `None`  
* `vapor_pressure`: `Pressure`, default = `None`  
* `enthalpy`: `HeatOfVaporization`, default = `None`  
* `phase`: `str`, default = `None` (`"liquid"` or `"gas"` overrides the vapor-pressure test)  

## **Methods**

The properties of the `Styrene` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions styrene is a liquid; it boils at 418.6 K (145.5 °C) at 1 atm by its Table 2-8 row.)  
* **`density()`**:  
  * **Liquid Phase**: DIPPR Eq. 105 (Perry's Table 2-32)  
  * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-153)  
  * **Gas Phase**: Ideal-gas heat capacity (Cp), DIPPR Eq. 107 (Perry's Table 2-156)  
* **`viscosity()`**:  
  * **Liquid Phase**: DIPPR Eq. 101 (Perry's Table 2-313)  
  * **Gas Phase**: Uses Sutherland’s Law with the base class's air constants (no gas viscosity data for this component yet)  
* **`thermal_conductivity()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-315)  
  * **Gas Phase**: Vapor thermal conductivity (k), DIPPR Eq. 102 (Perry's Table 2-314)  
* **`vapor_pressure()`**: DIPPR Eq. 101 (Perry's Table 2-8).  
* **`enthalpy()`**: Enthalpy of vaporization (ΔHvap), DIPPR Eq. 106 (Perry's Table 2-150).  

## **Examples**

```py
from processpi.components import Styrene
from processpi.units import *

styrene = Styrene(temperature=Temperature(25, "C"))
print(styrene.phase())
print(styrene.density().to("kg/m3"))
print(styrene.viscosity().to("Pa·s"))
print(styrene.specific_heat().to("J/kgK"))
print(styrene.thermal_conductivity().to("W/mK"))
print(styrene.vapor_pressure().to("Pa"))
print(styrene.enthalpy().to("J/kg"))
```

### Output

```text
liquid
900.424281 kg/m3
0.000701 Pa·s (dynamic)
1747.795166 J/kgK
0.136527 W/mK
816.543835 Pa
425394.558055 J/kg
```
