# **Class: `Propane`**

## **Description**

The `Propane` class represents the properties and constants for Propane (C₃H₈).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 295).

## **Properties**

* **`name`** (string): Propane  
* **`formula`** (string): C₃H₈  
* **`molecular_weight`** (float): 44.096 g/mol  

## **Class Reference**

**`class Propane()`**

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

The properties of the `Propane` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions propane is a gas; it boils at 231.1 K (-42.1 °C) at 1 atm by its Table 2-8 row.)  
* **`density()`**:  
  * **Liquid Phase**: DIPPR Eq. 105 (Perry's Table 2-32)  
  * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**:  
  * **Liquid Phase**: Perry's Table 2-153, Eq. (2), a function of reduced temperature  
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
from processpi.components import Propane
from processpi.units import *

c3h8 = Propane(temperature=Temperature(25, "C"))
print(c3h8.phase())
print(c3h8.density().to("kg/m3"))
print(c3h8.viscosity().to("Pa·s"))
print(c3h8.specific_heat().to("J/kgK"))
print(c3h8.thermal_conductivity().to("W/mK"))
print(c3h8.vapor_pressure().to("Pa"))
print(c3h8.enthalpy().to("J/kg"))
```

### Output

```text
gas
1.802382 kg/m3
1.8e-05 Pa·s (dynamic)
1666.044316 J/kgK
0.017924 W/mK
953257.139017 Pa
335754.091747 J/kg
```
