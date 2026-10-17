# **Class: `Methane`**

## **Description**

The `Methane` class represents the properties and constants for Methane (CH₄).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 193).

## **Properties**

* **`name`** (string): Methane  
* **`formula`** (string): CH₄  
* **`molecular_weight`** (float): 16.042 g/mol  

## **Class Reference**

**`class Methane()`**

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

The properties of the `Methane` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions methane is a gas, above its critical temperature (190.564 K); it boils at 111.7 K (-161.5 °C) at 1 atm by its Table 2-8 row.)  
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
* **`vapor_pressure()`**: DIPPR Eq. 101 (Perry's Table 2-8). Above the critical temperature, as at 25 °C here, the value is the correlation extrapolated past its range: `phase()` uses it, but it is not a physical vapor pressure.  
* **`enthalpy()`**: Enthalpy of vaporization (ΔHvap), DIPPR Eq. 106 (Perry's Table 2-150). It is 0 above the critical temperature.  

## **Examples**

```py
from processpi.components import Methane
from processpi.units import *

ch4 = Methane(temperature=Temperature(25, "C"))
print(ch4.phase())
print(ch4.density().to("kg/m3"))
print(ch4.viscosity().to("Pa·s"))
print(ch4.specific_heat().to("J/kgK"))
print(ch4.thermal_conductivity().to("W/mK"))
print(ch4.vapor_pressure().to("Pa"))
print(ch4.enthalpy().to("J/kg"))
```

### Output

```text
gas
0.655701 kg/m3
1.8e-05 Pa·s (dynamic)
2224.085851 J/kgK
0.034185 W/mK
61834055.697315 Pa
0.0 J/kg
```
