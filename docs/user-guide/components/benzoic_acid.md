# **Class: `BenzoicAcid`**

## **Description**

The `BenzoicAcid` class represents the properties and constants for Benzoic Acid (C₆H₅COOH).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Benzoic Acid  
* **`formula`** (string): C₆H₅COOH  
* **`molecular_weight`** (float): 122.12 g/mol  

## **Class Reference**

**`class BenzoicAcid()`**

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

The properties of the `BenzoicAcid` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"solid"`, `"liquid"` or `"gas"`) by comparing the system temperature and vapor pressure.  
* **`density()`**:  
    * **Solid/Liquid Phase**: Uses DIPPR or empirical correlations  
    * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  
* **`viscosity()`**:  
    * **Liquid Phase**: Calculates viscosity (μ) using DIPPR correlation  
    * **Gas Phase**: Uses Sutherland’s Law  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using an Antoine-type correlation  
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  

## **Examples**

```py
from processpi.components import BenzoicAcid
from processpi.units import *

ba = BenzoicAcid(temperature=Temperature(25, "C"))
print(ba.density().to("kg/m3"))
print(ba.viscosity().to("Pa·s"))
print(ba.specific_heat().to("J/kgK"))
print(ba.thermal_conductivity().to("W/mK"))
print(ba.vapor_pressure().to("Pa"))
print(ba.enthalpy().to("J/kg"))
```