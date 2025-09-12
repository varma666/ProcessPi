# **Class: `Cyanogen`**

## **Description**

The `Cyanogen` class represents the properties and constants for Cyanogen (C₂N₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Cyanogen  
* **`formula`** (string): C₂N₂  
* **`molecular_weight`** (float): 52.04 g/mol  

## **Class Reference**

**`class Cyanogen()`**

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

The properties of the `Cyanogen` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system temperature and vapor pressure. (At standard conditions, cyanogen is a gas.)  
* **`density()`**:  
  * **Gas Phase**: Uses the Ideal Gas Law  
  * **Liquid Phase**: Uses DIPPR or experimental correlation  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
  * **Gas Phase**: Uses Sutherland’s Law  
  * **Liquid Phase**: Uses DIPPR correlation  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using an Antoine-type correlation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import Cyanogen
from processpi.units import *

c2n2 = Cyanogen(temperature=Temperature(25, "C"))
print(c2n2.density().to("kg/m3"))
print(c2n2.viscosity().to("Pa·s"))
print(c2n2.specific_heat().to("J/kgK"))
print(c2n2.thermal_conductivity().to("W/mK"))
print(c2n2.vapor_pressure().to("Pa"))
print(c2n2.enthalpy().to("J/kg"))
```