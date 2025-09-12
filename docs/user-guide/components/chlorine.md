# **Class: `Chlorine`**

## **Description**

The `Chlorine` class represents the properties and constants for Chlorine (Cl₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Chlorine  
* **`formula`** (string): Cl₂  
* **`molecular_weight`** (float): 70.90 g/mol  

## **Class Reference**

**`class Chlorine()`**

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

The properties of the `Chlorine` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing system temperature and pressure to chlorine’s vapor pressure. (At standard conditions, chlorine is a gas.)  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law  
    * **Liquid Phase**: Uses DIPPR correlation (cryogenic/refrigerated conditions)  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Gas Phase**: Uses Sutherland’s Law  
    * **Liquid Phase**: Uses DIPPR correlation  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure using Antoine-type correlations  
* **`enthalpy()`**: Calculates enthalpy of vaporization (ΔHvap​) using correlations based on reduced temperature  

## **Examples**

```py
from processpi.components import Chlorine
from processpi.units import *

cl2 = Chlorine(temperature=Temperature(25, "C"))
print(cl2.density().to("kg/m3"))
print(cl2.viscosity().to("Pa·s"))
print(cl2.specific_heat().to("J/kgK"))
print(cl2.thermal_conductivity().to("W/mK"))
print(cl2.vapor_pressure().to("Pa"))
print(cl2.enthalpy().to("J/kg"))
```