# **Class: `Oil`**

## **Description**

The `Oil` class represents the properties and constants for a generic oil.  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
This class is typically used for crude oils, lubricating oils, or user-specified oils in simulations.

## **Properties**

* **`name`** (string): Oil  
* **`formula`** (string): N/A (mixture or undefined)  
* **`molecular_weight`** (float): User-defined (default = None)  

## **Class Reference**

**`class Oil()`**

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

The properties of the `Oil` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Always `"liquid"` under standard conditions.  
* **`density()`**: User-defined or calculated from empirical correlations.  
* **`specific_heat()`**: User-defined or estimated based on empirical correlations.  
* **`viscosity()`**: User-defined or estimated using DIPPR or polynomial correlations.  
* **`thermal_conductivity()`**: User-defined or estimated using polynomial correlation.  
* **`vapor_pressure()`**: Calculated using Antoine-type correlation (if applicable).  
* **`enthalpy()`**: Estimated from heat capacity correlation and integration over temperature range.  

## **Examples**

```py
from processpi.components import Oil
from processpi.units import *

# Define a generic oil
generic_oil = Oil(
    temperature=Temperature(25, "C"),
    pressure=Pressure(1, "atm"),
    density=900  # Example density in kg/m3
)

print(generic_oil.density().to("kg/m3"))
print(generic_oil.viscosity().to("Pa·s"))
print(generic_oil.specific_heat().to("J/kgK"))
print(generic_oil.thermal_conductivity().to("W/mK"))
print(generic_oil.vapor_pressure().to("Pa"))
print(generic_oil.enthalpy().to("J/kg"))
```