# **Class: `NitrousOxide`**

## **Description**

The `NitrousOxide` class represents the properties and constants for Nitrous Oxide (N₂O).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 252).

## **Properties**

* **`name`** (string): Nitrous Oxide  
* **`formula`** (string): N₂O  
* **`molecular_weight`** (float): 44.013 g/mol  

## **Class Reference**

**`class NitrousOxide()`**

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

The properties of the `NitrousOxide` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions nitrous oxide is a gas; it boils at 184.7 K (-88.4 °C) at 1 atm by its Table 2-8 row.)  
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
from processpi.components import NitrousOxide
from processpi.units import *

n2o = NitrousOxide(temperature=Temperature(25, "C"))
print(n2o.phase())
print(n2o.density().to("kg/m3"))
print(n2o.viscosity().to("Pa·s"))
print(n2o.specific_heat().to("J/kgK"))
print(n2o.thermal_conductivity().to("W/mK"))
print(n2o.vapor_pressure().to("Pa"))
print(n2o.enthalpy().to("J/kg"))
```

### Output

```text
gas
1.798989 kg/m3
1.8e-05 Pa·s (dynamic)
878.540809 J/kgK
0.017433 W/mK
5729121.826386 Pa
148552.544509 J/kg
```
