# **Class: `Phenol`**

## **Description**

The `Phenol` class represents the properties and constants for Phenol (C₆H₅OH).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 291).

## **Properties**

* **`name`** (string): Phenol  
* **`formula`** (string): C₆H₆O  
* **`molecular_weight`** (float): 94.111 g/mol  

## **Class Reference**

**`class Phenol()`**

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

The properties of the `Phenol` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (Perry's liquid correlations start at 314.06 K (40.9 °C), where phenol melts. Below that the model extrapolates the liquid, so at 25 °C it reports a liquid although phenol is a solid there. It boils at 455.1 K (181.9 °C) at 1 atm by its Table 2-8 row.)  
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
from processpi.components import Phenol
from processpi.units import *

phenol = Phenol(temperature=Temperature(25, "C"))
print(phenol.phase())
print(phenol.density().to("kg/m3"))
print(phenol.viscosity().to("Pa·s"))
print(phenol.specific_heat().to("J/kgK"))
print(phenol.thermal_conductivity().to("W/mK"))
print(phenol.vapor_pressure().to("Pa"))
print(phenol.enthalpy().to("J/kg"))
```

### Output

```text
liquid
1071.758327 kg/m3
0.009044 Pa·s (dynamic)
2087.061252 J/kgK
0.158495 W/mK
56.873508 Pa
611729.704524 J/kg
```
