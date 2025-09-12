# **Class: `OrganicLiquid`**

## **Description**

The `OrganicLiquid` class represents the properties and constants for generic organic liquids.  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
This class is typically used for alcohols, ketones, esters, or user-defined organic liquids in simulations.

## **Properties**

* **`name`** (string): Organic Liquid  
* **`formula`** (string): N/A (mixture or undefined)  
* **`molecular_weight`** (float): User-defined (default = None)  

## **Class Reference**

**`class OrganicLiquid()`**

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

The properties of the `OrganicLiquid` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Always `"liquid"` under standard conditions.  
* **`density()`**: User-defined or calculated from empirical correlations.  
* **`specific_heat()`**: User-defined or estimated based on empirical correlations.  
* **`viscosity()`**: User-defined or estimated using DIPPR or polynomial correlations.  
* **`thermal_conductivity()`**: User-defined or estimated using polynomial correlation.  
* **`vapor_pressure()`**: Calculated using Antoine-type correlation (if applicable).  
* **`enthalpy()`**: Estimated from heat capacity correlation and integration over temperature range.  

## **Examples**

```py
from processpi.components import OrganicLiquid
from processpi.units import *

# Define a generic organic liquid (example: acetic acid)
organic_liquid = OrganicLiquid(
    temperature=Temperature(25, "C"),
    pressure=Pressure(1, "atm"),
    molecular_weight=60.05  # Example molecular weight
)

print(organic_liquid.density().to("kg/m3"))
print(organic_liquid.viscosity().to("Pa·s"))
print(organic_liquid.specific_heat().to("J/kgK"))
print(organic_liquid.thermal_conductivity().to("W/mK"))
print(organic_liquid.vapor_pressure().to("Pa"))
print(organic_liquid.enthalpy().to("J/kg"))
```