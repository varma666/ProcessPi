# **Class: `Chloromethane`**

## **Description**

The `Chloromethane` class represents the properties and constants for Chloromethane (CH₃Cl).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Chloromethane  
* **`formula`** (string): CH₃Cl  
* **`molecular_weight`** (float): 50.49 g/mol  

## **Class Reference**

**`class Chloromethane()`**

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

The properties of the `Chloromethane` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system temperature and vapor pressure.  
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
from processpi.components import Chloromethane
from processpi.units import *

ch3cl = Chloromethane(temperature=Temperature(25, "C"))
print(ch3cl.density().to("kg/m3"))
print(ch3cl.viscosity().to("Pa·s"))
print(ch3cl.specific_heat().to("J/kgK"))
print(ch3cl.thermal_conductivity().to("W/mK"))
print(ch3cl.vapor_pressure().to("Pa"))
print(ch3cl.enthalpy().to("J/kg"))
```