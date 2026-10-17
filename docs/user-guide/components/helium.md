# **Class: `Helium`**

## **Description**

The `Helium` class represents the properties and constants for Helium (He).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 157).

## **Properties**

* **`name`** (string): Helium  
* **`formula`** (string): He  
* **`molecular_weight`** (float): 4.003 g/mol  

## **Class Reference**

**`class Helium()`**

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

The properties of the `Helium` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions helium is a gas, far above its critical temperature (5.2 K); it boils at 4.22 K (-268.9 °C) at 1 atm by its Table 2-8 row.)  
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
from processpi.components import Helium
from processpi.units import *

he = Helium(temperature=Temperature(25, "C"))
print(he.phase())
print(he.density().to("kg/m3"))
print(he.viscosity().to("Pa·s"))
print(he.specific_heat().to("J/kgK"))
print(he.thermal_conductivity().to("W/mK"))
print(he.vapor_pressure().to("Pa"))
print(he.enthalpy().to("J/kg"))
```

### Output

```text
gas
0.163619 kg/m3
1.8e-05 Pa·s (dynamic)
5192.605546 J/kgK
0.153964 W/mK
1.5036305013512178e+42 Pa
0.0 J/kg
```
