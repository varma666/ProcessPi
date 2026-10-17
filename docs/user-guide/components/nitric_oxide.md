# **Class: `NitricOxide`**

## **Description**

The `NitricOxide` class represents the properties and constants for Nitric Oxide (NO).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 253).

## **Properties**

* **`name`** (string): Nitric Oxide  
* **`formula`** (string): NO  
* **`molecular_weight`** (float): 30.006 g/mol  

## **Class Reference**

**`class NitricOxide()`**

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

The properties of the `NitricOxide` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions nitric oxide is a gas, above its critical temperature (180.15 K); it boils at 121.4 K (-151.8 °C) at 1 atm by its Table 2-8 row.) Nitric oxide's Table 2-8 row has a C4·T⁶ term that grows fast: above about 644 K the vapor-pressure test in `phase()` overflows, so pass `phase="gas"` for hotter streams.  
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
from processpi.components import NitricOxide
from processpi.units import *

no = NitricOxide(temperature=Temperature(25, "C"))
print(no.phase())
print(no.density().to("kg/m3"))
print(no.viscosity().to("Pa·s"))
print(no.specific_heat().to("J/kgK"))
print(no.thermal_conductivity().to("W/mK"))
print(no.vapor_pressure().to("Pa"))
print(no.enthalpy().to("J/kg"))
```

### Output

```text
gas
1.226467 kg/m3
1.8e-05 Pa·s (dynamic)
996.951749 J/kgK
0.025622 W/mK
22385347585.213867 Pa
0.0 J/kg
```
