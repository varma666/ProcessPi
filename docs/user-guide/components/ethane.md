# **Class: `Ethane`**

## **Description**

The `Ethane` class represents the properties and constants for Ethane (C₂H₆).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Ethane  
* **`formula`** (string): C₂H₆  
* **`molecular_weight`** (float): 30.07 g/mol  

## **Class Reference**

**`class Ethane()`**

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

The properties of the `Ethane` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system temperature and vapor pressure. (At standard conditions, ethane is a gas.)  
* **`density()`**:  
  * **Gas Phase**: Uses the Ideal Gas Law  
  * **Liquid Phase**: Uses DIPPR or experimental correlation  
* **`specific_heat()`**:  
  * **Gas Phase**: Ideal-gas heat capacity (Cp), DIPPR Eq. 107 with the constants of Perry's Chemical Engineers' Handbook, 8th ed., Table 2-156  
  * **Liquid Phase**: Perry's Table 2-153, Eq. (2), a function of reduced temperature  
* **`viscosity()`**:  
  * **Gas Phase**: Uses Sutherland’s Law  
  * **Liquid Phase**: Uses DIPPR correlation  
* **`thermal_conductivity()`**:  
  * **Gas Phase**: Vapor thermal conductivity (k), DIPPR Eq. 102 with the constants of Perry's 8th ed., Table 2-314  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-315)  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using an Antoine-type correlation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import Ethane
from processpi.units import *

c2h6 = Ethane(temperature=Temperature(25, "C"))
print(c2h6.density().to("kg/m3"))
print(c2h6.viscosity().to("Pa·s"))
print(c2h6.specific_heat().to("J/kgK"))
print(c2h6.thermal_conductivity().to("W/mK"))
print(c2h6.vapor_pressure().to("Pa"))
print(c2h6.enthalpy().to("J/kg"))
```