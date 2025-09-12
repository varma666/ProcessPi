# **Class: `InorganicLiquid`**

## **Description**

The `InorganicLiquid` class represents the properties and constants for generic inorganic liquids.  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
This class is typically used as a placeholder or for defining user-specified inorganic liquids in simulations.

## **Properties**

* **`name`** (string): Inorganic Liquid  
* **`formula`** (string): N/A (mixture or undefined)  
* **`molecular_weight`** (float): User-defined (default = None)  

## **Class Reference**

**`class InorganicLiquid()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(25,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  
* `molecular_weight`: `float`, default = `None` (must be set for calculations)  
* `density`: `Density`, default = `None`  
* `specific_heat`: `SpecificHeat`, default = `None`  
* `viscosity`: `Viscosity`, default = `None`  
* `thermal_conductivity`: `ThermalConductivity`, default = `None`  
* `vapor_pressure`: `Pressure`, default = `None`  
* `enthalpy`: `HeatOfVaporization`, default = `None`  


## **Methods**

The properties of the `InorganicLiquid` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Always `"liquid"` under standard simulation conditions.  
* **`density()`**: User-defined or calculated from empirical correlations.  
* **`specific_heat()`**: User-defined or estimated based on empirical correlations.  
* **`viscosity()`**: User-defined or estimated using DIPPR correlations.  
* **`thermal_conductivity()`**: User-defined or estimated using polynomial correlation.  
* **`vapor_pressure()`**: Calculated using Antoine-type correlation (if applicable).  
* **`enthalpy()`**: Estimated from heat capacity correlation and integration over temperature range.  

## **Examples**

```py
from processpi.components import InorganicLiquid
from processpi.units import *

# Define a generic inorganic liquid (example: water)
water_liquid = InorganicLiquid(
    temperature=Temperature(25, "C"),
    pressure=Pressure(1, "atm"),
    molecular_weight=18.015
)

print(water_liquid.density().to("kg/m3"))
print(water_liquid.viscosity().to("Pa·s"))
print(water_liquid.specific_heat().to("J/kgK"))
print(water_liquid.thermal_conductivity().to("W/mK"))
print(water_liquid.vapor_pressure().to("Pa"))
print(water_liquid.enthalpy().to("J/kg"))
```