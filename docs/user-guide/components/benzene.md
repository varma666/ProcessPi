# **Class: `Benzene`**

## **Description**

The `Benzene` class represents the properties and constants for Benzene (C₆H₆).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.

## **Properties**

* **`name`** (string): Benzene  
* **`formula`** (string): C₆H₆  
* **`molecular_weight`** (float): 78.11 g/mol  

## **Class Reference**

**`class Benzene()`**

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

The properties of the `Benzene` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the calculated vapor pressure.  
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
from processpi.components import Benzene
from processpi.units import *

benzene = Benzene(temperature=Temperature(35, "C"))
print(benzene.density().to("kg/m3"))
print(benzene.viscosity().to("Pa·s"))
print(benzene.specific_heat().to("J/kgK"))
print(benzene.thermal_conductivity().to("W/mK"))
print(benzene.vapor_pressure().to("Pa"))
print(benzene.enthalpy().to("J/kg"))
```