# **Class: `Gas`**

## **Description**

The `Gas` class represents the properties and constants for a generic gas mixture.  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
This class is typically used as a placeholder or for defining user-specified gases in simulations.

## **Properties**

* **`name`** (string): Gas  
* **`formula`** (string): N/A (mixture or undefined)  
* **`molecular_weight`** (float): User-defined (default = None)  

## **Class Reference**

**`class Gas()`**

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

The properties of the `Gas` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Always `"gas"` under standard simulation conditions.  
* **`density()`**: Uses the Ideal Gas Law with user-provided molecular weight.  
* **`specific_heat()`**: User-defined or estimated based on empirical correlations.  
* **`viscosity()`**: Uses Sutherland’s Law or user input.  
* **`thermal_conductivity()`**: User-defined or estimated with polynomial correlation.  
* **`vapor_pressure()`**: Not typically applicable for gas mixtures (default = None).  
* **`enthalpy()`**: Estimated from heat capacity correlation and integration over temperature range.  

## **Examples**

```py
from processpi.components import Gas
from processpi.units import *

# Define a gas with approximate molecular weight (example: Nitrogen ~28.0 g/mol)
custom_gas = Gas(temperature=Temperature(25, "C"), pressure=Pressure(1, "atm"), molecular_weight=28.0)

print(custom_gas.density().to("kg/m3"))
print(custom_gas.viscosity().to("Pa·s"))
print(custom_gas.specific_heat().to("J/kgK"))
print(custom_gas.thermal_conductivity().to("W/mK"))
print(custom_gas.enthalpy().to("J/kg"))
```