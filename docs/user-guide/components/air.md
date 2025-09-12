# **Class: `Air`**

## **Description**

The `Air` class represents the properties and constants for Air (approximate composition: 78% N₂, 21% O₂, 1% Ar/others).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Air  
* **`formula`** (string): Mixture (≈ N₂₀.₇₈ O₂₀.₂₁ Ar₀.₀₁)  
* **`molecular_weight`** (float): 28.97 g/mol  

## **Class Reference**

**`class Air()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(35,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  
* `density`: `Density`, default = `None`  
* `specific_heat`: `SpecificHeat`, default = `None`  
* `viscosity`: `Viscosity`, default = `None`  
* `thermal_conductivity`: `ThermalConductivity`, default = `None`  
* `vapor_pressure`: `Pressure`, default = `None`  
* `enthalpy`: `HeatOfVaporization`, default = `None`  

## **Methods**

The properties of the `Air` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the calculated vapor pressure. (For air, this generally indicates `"gas"` at standard conditions.)  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law  
    * **Liquid Phase**: Approximations possible under cryogenic conditions  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Gas Phase**: Calculates viscosity using Sutherland's Law  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Not typically applicable to air (mixture) but correlation can be used at cryogenic temperatures  
* **`enthalpy()`**: Calculates enthalpy using correlations based on temperature and reference state  

## **Examples**

```py
from processpi.components import Air
from processpi.units import *

air = Air(temperature=Temperature(35, "C"))
print(air.density().to("kg/m3"))
print(air.viscosity().to("Pa·s"))
print(air.specific_heat().to("J/kgK"))
print(air.thermal_conductivity().to("W/mK"))
print(air.enthalpy().to("J/kg"))
```