# **Class: `CarbonDioxide`**

## **Description**

The `CarbonDioxide` class represents the properties and constants for Carbon Dioxide (CO₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Carbon Dioxide  
* **`formula`** (string): CO₂  
* **`molecular_weight`** (float): 44.01 g/mol  

## **Class Reference**

**`class CarbonDioxide()`**

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

The properties of the `CarbonDioxide` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"solid"`, `"gas"`, or `"liquid"`) by comparing the system temperature and pressure to sublimation/vapor pressure.  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law  
    * **Liquid Phase**: Uses DIPPR correlation  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Gas Phase**: Uses Sutherland’s Law  
    * **Liquid Phase**: Uses DIPPR correlation  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates sublimation or vapor pressure (Pvap​) using Antoine-type correlations  
* **`enthalpy()`**: Calculates enthalpy of vaporization or sublimation (ΔHvap/ΔHsub​) depending on phase  

## **Examples**

```py
from processpi.components import CarbonDioxide
from processpi.units import *

co2 = CarbonDioxide(temperature=Temperature(25, "C"))
print(co2.density().to("kg/m3"))
print(co2.viscosity().to("Pa·s"))
print(co2.specific_heat().to("J/kgK"))
print(co2.thermal_conductivity().to("W/mK"))
print(co2.vapor_pressure().to("Pa"))
print(co2.enthalpy().to("J/kg"))
```