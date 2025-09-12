# **Class: `CarbonMonoxide`**

## **Description**

The `CarbonMonoxide` class represents the properties and constants for Carbon Monoxide (CO).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Carbon Monoxide  
* **`formula`** (string): CO  
* **`molecular_weight`** (float): 28.01 g/mol  

## **Class Reference**

**`class CarbonMonoxide()`**

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

The properties of the `CarbonMonoxide` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the vapor pressure. (At standard conditions, CO is a gas.)  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law  
    * **Liquid Phase**: Uses DIPPR correlation (cryogenic conditions)  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Gas Phase**: Uses Sutherland’s Law  
    * **Liquid Phase**: Uses DIPPR correlation  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure using Antoine-type correlations (applicable in cryogenic range)  
* **`enthalpy()`**: Calculates enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import CarbonMonoxide
from processpi.units import *

co = CarbonMonoxide(temperature=Temperature(25, "C"))
print(co.density().to("kg/m3"))
print(co.viscosity().to("Pa·s"))
print(co.specific_heat().to("J/kgK"))
print(co.thermal_conductivity().to("W/mK"))
print(co.vapor_pressure().to("Pa"))
print(co.enthalpy().to("J/kg"))
```