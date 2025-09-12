# **Class: `CarbonTetrachloride`**

## **Description**

The `CarbonTetrachloride` class represents the properties and constants for Carbon Tetrachloride (CCl₄).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Carbon Tetrachloride  
* **`formula`** (string): CCl₄  
* **`molecular_weight`** (float): 153.82 g/mol  

## **Class Reference**

**`class CarbonTetrachloride()`**

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

The properties of the `CarbonTetrachloride` class are calculated using the following methods, which are inherited from the base `Component` class.

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
from processpi.components import CarbonTetrachloride
from processpi.units import *

ccl4 = CarbonTetrachloride(temperature=Temperature(25, "C"))
print(ccl4.density().to("kg/m3"))
print(ccl4.viscosity().to("Pa·s"))
print(ccl4.specific_heat().to("J/kgK"))
print(ccl4.thermal_conductivity().to("W/mK"))
print(ccl4.vapor_pressure().to("Pa"))
print(ccl4.enthalpy().to("J/kg"))
```