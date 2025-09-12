# **Class: `Vapor`**

## **Description**

The `Vapor` class represents the properties and constants for a generic vapor or gas phase substance.  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
This class is typically used for vapors of liquids, process gases, or user-defined gas mixtures.  

## **Properties**

* **`name`** (string): Vapor  
* **`formula`** (string): N/A (mixture or undefined)  
* **`molecular_weight`** (float): User-defined (default = None)  

## **Class Reference**

**`class Vapor()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(25,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  
* `molecular_weight`: `float`, default = `None` (required for calculations)  
* `density`: `Density`, default = `None`  
* `specific_heat`: `SpecificHeat`, default = `None`  
* `viscosity`: `Viscosity`, default = `None`  
* `thermal_conductivity`: `ThermalConductivity`, default = `None`  
* `vapor_pressure`: `Pressure`, default = `None`  
* `enthalpy`: `HeatOfVaporization`, default = `None`  

## **Methods**

The properties of the `Vapor` class are calculated using the following methods:

* **`phase()`**: Always returns `"gas"` under standard simulation conditions.  
* **`density()`**: Uses the Ideal Gas Law with user-provided molecular weight.  
* **`specific_heat()`**: User-defined or estimated using empirical correlations.  
* **`viscosity()`**: Uses Sutherland’s Law or user input.  
* **`thermal_conductivity()`**: User-defined or estimated using polynomial correlations.  
* **`vapor_pressure()`**: Not typically applicable for gases (default = None).  
* **`enthalpy()`**: Calculated using heat capacity correlation over temperature range.  

## **Examples**

```py
from processpi.components import Vapor
from processpi.units import *

# Define a vapor with approximate molecular weight (example: water vapor ~18.015 g/mol)
water_vapor = Vapor(
    temperature=Temperature(100, "C"),
    pressure=Pressure(1, "atm"),
    molecular_weight=18.015
)

print("Density:", water_vapor.density().to("kg/m3"))
print("Viscosity:", water_vapor.viscosity().to("Pa·s"))
print("Specific Heat:", water_vapor.specific_heat().to("J/kgK"))
print("Thermal Conductivity:", water_vapor.thermal_conductivity().to("W/mK"))
print("Enthalpy:", water_vapor.enthalpy().to("J/kg"))
print("Phase:", water_vapor.phase())
```