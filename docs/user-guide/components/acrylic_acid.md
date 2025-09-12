# **Class: `AcrylicAcid`**

## **Description**

The `AcrylicAcid` class represents the properties and constants for Acrylic Acid (C₃H₄O₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Acrylic Acid  
* **`formula`** (string): C₃H₄O₂  
* **`molecular_weight`** (float): 72.06 g/mol  

## **Class Reference**

**`class AcrylicAcid()`**

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

The properties of the `AcrylicAcid` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the calculated vapor pressure. The rule is: `"gas"` if **P < P<sub>vap</sub>,​** otherwise `"liquid"`.  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law  
    * **Liquid Phase**: Calculates density using the DIPPR correlation  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Liquid Phase**: Calculates viscosity (μ) using the DIPPR correlation  
    * **Gas Phase**: Calculates viscosity using Sutherland's Law  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using the Antoine-style equation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import AcrylicAcid
from processpi.units import *

acrylic = AcrylicAcid(temperature=Temperature(35, "C"))
print(acrylic.density().to("kg/m3"))
print(acrylic.viscosity().to("Pa·s"))
print(acrylic.specific_heat().to("J/kgK"))
print(acrylic.thermal_conductivity().to("W/mK"))
print(acrylic.vapor_pressure().to("Pa"))
print(acrylic.enthalpy().to("J/kg"))
```