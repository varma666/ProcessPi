# **Class: `HydrogenChloride`**

## **Description**

The `HydrogenChloride` class represents the properties and constants for Hydrogen Chloride (HCl).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 185).

## **Properties**

* **`name`** (string): Hydrogen Chloride  
* **`formula`** (string): HCl  
* **`molecular_weight`** (float): 36.461 g/mol  

## **Class Reference**

**`class HydrogenChloride()`**

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

The properties of the `HydrogenChloride` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions hydrogen chloride is a gas; it boils at 188.1 K (-85.1 °C) at 1 atm by its Table 2-8 row.)  
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
from processpi.components import HydrogenChloride
from processpi.units import *

hcl = HydrogenChloride(temperature=Temperature(25, "C"))
print(hcl.phase())
print(hcl.density().to("kg/m3"))
print(hcl.viscosity().to("Pa·s"))
print(hcl.specific_heat().to("J/kgK"))
print(hcl.thermal_conductivity().to("W/mK"))
print(hcl.vapor_pressure().to("Pa"))
print(hcl.enthalpy().to("J/kg"))
```

### Output

```text
gas
1.490309 kg/m3
1.8e-05 Pa·s (dynamic)
799.309279 J/kgK
0.01443 W/mK
4722161.037697 Pa
254253.275539 J/kg
```
