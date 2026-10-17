# **Class: `Neon`**

## **Description**

The `Neon` class represents the properties and constants for Neon (Ne).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 247).

## **Properties**

* **`name`** (string): Neon  
* **`formula`** (string): Ne  
* **`molecular_weight`** (float): 20.180 g/mol  

## **Class Reference**

**`class Neon()`**

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

The properties of the `Neon` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions neon is a gas, far above its critical temperature (44.4 K); it boils at 27.07 K (-246.1 °C) at 1 atm by its Table 2-8 row.)  
* **`density()`**:  
  * **Liquid Phase**: DIPPR Eq. 105 (Perry's Table 2-32)  
  * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-153)  
  * **Gas Phase**: Ideal-gas heat capacity (Cp), polynomial in temperature (Perry's Table 2-155; there is no Table 2-156 row)  
* **`viscosity()`**:  
  * **Liquid Phase**: DIPPR Eq. 101 (Perry's Table 2-313)  
  * **Gas Phase**: Uses Sutherland’s Law with the base class's air constants (no gas viscosity data for this component yet)  
* **`thermal_conductivity()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-315)  
  * **Gas Phase**: Vapor thermal conductivity (k), DIPPR Eq. 102 (Perry's Table 2-314)  
* **`vapor_pressure()`**: DIPPR Eq. 101 (Perry's Table 2-8). Above the critical temperature, as at 25 °C here, the value is the correlation extrapolated past its range: `phase()` uses it, but it is not a physical vapor pressure.  
* **`enthalpy()`**: Enthalpy of vaporization (ΔHvap), DIPPR Eq. 106 (Perry's Table 2-150). It is 0 above the critical temperature.  

## **Examples**

```py
from processpi.components import Neon
from processpi.units import *

ne = Neon(temperature=Temperature(25, "C"))
print(ne.phase())
print(ne.density().to("kg/m3"))
print(ne.viscosity().to("Pa·s"))
print(ne.specific_heat().to("J/kgK"))
print(ne.thermal_conductivity().to("W/mK"))
print(ne.vapor_pressure().to("Pa"))
print(ne.enthalpy().to("J/kg"))
```

### Output

```text
gas
0.824838 kg/m3
1.8e-05 Pa·s (dynamic)
1030.029732 J/kgK
0.048792 W/mK
2.626309295662375e+26 Pa
0.0 J/kg
```
