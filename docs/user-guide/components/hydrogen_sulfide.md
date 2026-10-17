# **Class: `HydrogenSulfide`**

## **Description**

The `HydrogenSulfide` class represents the properties and constants for Hydrogen Sulfide (H₂S).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 188).

## **Properties**

* **`name`** (string): Hydrogen Sulfide  
* **`formula`** (string): H₂S  
* **`molecular_weight`** (float): 34.081 g/mol  

## **Class Reference**

**`class HydrogenSulfide()`**

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

The properties of the `HydrogenSulfide` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions hydrogen sulfide is a gas; it boils at 212.9 K (-60.2 °C) at 1 atm by its Table 2-8 row.)  
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
from processpi.components import HydrogenSulfide
from processpi.units import *

h2s = HydrogenSulfide(temperature=Temperature(25, "C"))
print(h2s.phase())
print(h2s.density().to("kg/m3"))
print(h2s.viscosity().to("Pa·s"))
print(h2s.specific_heat().to("J/kgK"))
print(h2s.thermal_conductivity().to("W/mK"))
print(h2s.vapor_pressure().to("Pa"))
print(h2s.enthalpy().to("J/kg"))
```

### Output

```text
gas
1.393028 kg/m3
1.8e-05 Pa·s (dynamic)
1003.170956 J/kgK
0.014464 W/mK
2016871.032858 Pa
414334.434543 J/kg
```
