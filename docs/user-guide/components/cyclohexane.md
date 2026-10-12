# **Class: `Cyclohexane`**

## **Description**

The `Cyclohexane` class represents the properties and constants for Cyclohexane (C₆H₁₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 65). The liquid correlations start at the melting point, 279.69 K (6.5 °C).

## **Properties**

* **`name`** (string): Cyclohexane  
* **`formula`** (string): C₆H₁₂  
* **`molecular_weight`** (float): 84.159 g/mol  

## **Class Reference**

**`class Cyclohexane()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(25,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  
* `density`: `Density`, default = `None`  
* `specific_heat`: `SpecificHeat`, default = `None`  
* `viscosity`: `Viscosity`, default = `None`  
* `thermal_conductivity`: `ThermalConductivity`, default = `None`  
* `vapor_pressure`: `Pressure`, default = `None`  
* `enthalpy`: `HeatOfVaporization`, default = `None`  

## **Methods**

The properties of the `Cyclohexane` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (At standard conditions, cyclohexane is a liquid; it boils at 80.7 °C at 1 atm.)  
* **`density()`**:  
  * **Liquid Phase**: DIPPR Eq. 105 (Perry's Table 2-32)  
  * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-153)  
  * **Gas Phase**: Ideal-gas heat capacity (Cp), DIPPR Eq. 107 (Perry's Table 2-156)  
* **`viscosity()`**:  
  * **Liquid Phase**: DIPPR Eq. 101 (Perry's Table 2-313)  
  * **Gas Phase**: Uses Sutherland’s Law  
* **`thermal_conductivity()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-315)  
  * **Gas Phase**: Vapor thermal conductivity (k), DIPPR Eq. 102 (Perry's Table 2-314)  
* **`vapor_pressure()`**: DIPPR Eq. 101 (Perry's Table 2-8)  
* **`enthalpy()`**: Enthalpy of vaporization (ΔHvap), DIPPR Eq. 106 (Perry's Table 2-150)  

## **Examples**

```py
from processpi.components import Cyclohexane
from processpi.units import *

c6h12 = Cyclohexane(temperature=Temperature(25, "C"))
print(c6h12.density().to("kg/m3"))
print(c6h12.viscosity().to("Pa·s"))
print(c6h12.specific_heat().to("J/kgK"))
print(c6h12.thermal_conductivity().to("W/mK"))
print(c6h12.vapor_pressure().to("Pa"))
print(c6h12.enthalpy().to("J/kg"))
```
