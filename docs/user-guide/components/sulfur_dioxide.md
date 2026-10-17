# **Class: `SulfurDioxide`**

## **Description**

The `SulfurDioxide` class represents the properties and constants for Sulfur Dioxide (SO₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 314).

## **Properties**

* **`name`** (string): Sulfur Dioxide  
* **`formula`** (string): SO₂  
* **`molecular_weight`** (float): 64.064 g/mol  

## **Class Reference**

**`class SulfurDioxide()`**

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

The properties of the `SulfurDioxide` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions sulfur dioxide is a gas; it boils at 263.2 K (-10.0 °C) at 1 atm by its Table 2-8 row.)  
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
* **`enthalpy()`**: Enthalpy of vaporization (ΔHvap), DIPPR Eq. 106 (Perry's Table 2-150). It is 0 above the critical temperature.  

## **Examples**

```py
from processpi.components import SulfurDioxide
from processpi.units import *

so2 = SulfurDioxide(temperature=Temperature(25, "C"))
print(so2.phase())
print(so2.density().to("kg/m3"))
print(so2.viscosity().to("Pa·s"))
print(so2.specific_heat().to("J/kgK"))
print(so2.thermal_conductivity().to("W/mK"))
print(so2.vapor_pressure().to("Pa"))
print(so2.enthalpy().to("J/kg"))
```

### Output

```text
gas
2.618555 kg/m3
1.8e-05 Pa·s (dynamic)
622.783751 J/kgK
0.00954 W/mK
400148.615522 Pa
358169.620229 J/kg
```
