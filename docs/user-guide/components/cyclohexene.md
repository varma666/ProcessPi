# **Class: `Cyclohexane`**

## **Description**

The `Cyclohexane` class represents the properties and constants for Cyclohexane (C₆H₁₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Cyclohexane  
* **`formula`** (string): C₆H₁₂  
* **`molecular_weight`** (float): 84.16 g/mol  

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