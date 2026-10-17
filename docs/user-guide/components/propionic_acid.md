# **Class: `PropionicAcid`**

## **Description**

The `PropionicAcid` class represents the properties and constants for Propionic Acid (CH₃CH₂COOH).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 300).

## **Properties**

* **`name`** (string): Propionic Acid  
* **`formula`** (string): C₃H₆O₂  
* **`molecular_weight`** (float): 74.079 g/mol  

## **Class Reference**

**`class PropionicAcid()`**

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

The properties of the `PropionicAcid` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions propionic acid is a liquid; it boils at 414.3 K (141.1 °C) at 1 atm by its Table 2-8 row.)  
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
from processpi.components import PropionicAcid
from processpi.units import *

acid = PropionicAcid(temperature=Temperature(25, "C"))
print(acid.phase())
print(acid.density().to("kg/m3"))
print(acid.viscosity().to("Pa·s"))
print(acid.specific_heat().to("J/kgK"))
print(acid.thermal_conductivity().to("W/mK"))
print(acid.vapor_pressure().to("Pa"))
print(acid.enthalpy().to("J/kg"))
```

### Output

```text
liquid
988.211121 kg/m3
0.001026 Pa·s (dynamic)
2048.59033 J/kgK
0.146503 W/mK
495.503991 Pa
418053.938944 J/kg
```
