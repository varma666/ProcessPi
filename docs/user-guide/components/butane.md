# **Class: `Butane`**

## **Description**

The `Butane` class represents the properties and constants for Butane (C₄H₁₀).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Butane  
* **`formula`** (string): C₄H₁₀  
* **`molecular_weight`** (float): 58.12 g/mol  

## **Class Reference**

**`class Butane()`**

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

The properties of the `Butane` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the calculated vapor pressure.  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law  
    * **Liquid Phase**: Calculates density using the DIPPR correlation  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Liquid Phase**: Calculates viscosity (μ) using DIPPR correlation  
    * **Gas Phase**: Uses Sutherland’s Law  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using an Antoine-type correlation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import Butane
from processpi.units import *

c4 = Butane(temperature=Temperature(25, "C"))
print(c4.density().to("kg/m3"))
print(c4.viscosity().to("Pa·s"))
print(c4.specific_heat().to("J/kgK"))
print(c4.thermal_conductivity().to("W/mK"))
print(c4.vapor_pressure().to("Pa"))
print(c4.enthalpy().to("J/kg"))
```