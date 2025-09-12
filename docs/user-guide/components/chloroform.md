# **Class: `Chloroform`**

## **Description**

The `Chloroform` class represents the properties and constants for Chloroform (CHCl₃).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Chloroform  
* **`formula`** (string): CHCl₃  
* **`molecular_weight`** (float): 119.38 g/mol  

## **Class Reference**

**`class Chloroform()`**

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

The properties of the `Chloroform` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system temperature and vapor pressure.  
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
from processpi.components import Chloroform
from processpi.units import *

chcl3 = Chloroform(temperature=Temperature(25, "C"))
print(chcl3.density().to("kg/m3"))
print(chcl3.viscosity().to("Pa·s"))
print(chcl3.specific_heat().to("J/kgK"))
print(chcl3.thermal_conductivity().to("W/mK"))
print(chcl3.vapor_pressure().to("Pa"))
print(chcl3.enthalpy().to("J/kg"))
```