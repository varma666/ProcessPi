# **Class: `Methanol`**

## **Description**

The `Methanol` class represents the properties and constants for Methanol (CH₃OH).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Methanol  
* **`formula`** (string): CH₃OH  
* **`molecular_weight`** (float): 32.04 g/mol  

## **Class Reference**

**`class Methanol()`**

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

The properties of the `Methanol` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system temperature and vapor pressure. (At standard conditions, methanol is a liquid.)  
* **`density()`**:  
  * **Liquid Phase**: Uses DIPPR or experimental correlation  
  * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
  * **Liquid Phase**: Uses DIPPR correlation  
  * **Gas Phase**: Uses Sutherland’s Law  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using an Antoine-type correlation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import Methanol
from processpi.units import *

ch3oh = Methanol(temperature=Temperature(25, "C"))
print(ch3oh.density().to("kg/m3"))
print(ch3oh.viscosity().to("Pa·s"))
print(ch3oh.specific_heat().to("J/kgK"))
print(ch3oh.thermal_conductivity().to("W/mK"))
print(ch3oh.vapor_pressure().to("Pa"))
print(ch3oh.enthalpy().to("J/kg"))
```