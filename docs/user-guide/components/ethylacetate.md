# **Class: `EthylAcetate`**

## **Description**

The `EthylAcetate` class represents the properties and constants for Ethyl Acetate (C₄H₈O₂).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Ethyl Acetate  
* **`formula`** (string): C₄H₈O₂  
* **`molecular_weight`** (float): 88.11 g/mol  

## **Class Reference**

**`class EthylAcetate()`**

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

The properties of the `EthylAcetate` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system temperature and vapor pressure. (At standard conditions, ethyl acetate is a liquid.)  
* **`density()`**:  
  * **Gas Phase**: Uses the Ideal Gas Law  
  * **Liquid Phase**: Uses DIPPR or experimental correlation  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
  * **Gas Phase**: Uses Sutherland’s Law  
  * **Liquid Phase**: Uses DIPPR correlation  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using an Antoine-type correlation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import EthylAcetate
from processpi.units import *

c4h8o2 = EthylAcetate(temperature=Temperature(25, "C"))
print(c4h8o2.density().to("kg/m3"))
print(c4h8o2.viscosity().to("Pa·s"))
print(c4h8o2.specific_heat().to("J/kgK"))
print(c4h8o2.thermal_conductivity().to("W/mK"))
print(c4h8o2.vapor_pressure().to("Pa"))
print(c4h8o2.enthalpy().to("J/kg"))
```