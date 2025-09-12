# **Class: `Toluene`**

## **Description**

The `Toluene` class represents the properties and constants for Toluene (C₇H₈).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
Properties can be obtained using correlations or CoolProp for accurate results.

## **Properties**

* **`name`** (string): Toluene  
* **`formula`** (string): C₇H₈  
* **`molecular_weight`** (float): 92.14 g/mol  

## **Class Reference**

**`class Toluene()`**

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

The properties of the `Toluene` class are calculated using correlations or **CoolProp**:

* **`phase()`**: Returns `"liquid"` or `"gas"` depending on temperature and pressure.  
* **`density()`**: Returns the density (ρ) of Toluene.  
* **`specific_heat()`**: Returns specific heat capacity (Cp) as a function of temperature.  
* **`viscosity()`**: Returns dynamic viscosity (μ) using empirical correlations.  
* **`thermal_conductivity()`**: Returns thermal conductivity (k).  
* **`vapor_pressure()`**: Returns the vapor pressure at the given temperature using Antoine correlation.  
* **`enthalpy()`**: Returns enthalpy (h) or enthalpy of vaporization (ΔHvap) based on temperature.  

## **Examples**

```py
from processpi.components import Toluene
from processpi.units import *

toluene = Toluene(temperature=Temperature(25, "C"))

print("Density:", toluene.density().to("kg/m3"))
print("Viscosity:", toluene.viscosity().to("Pa·s"))
print("Specific Heat:", toluene.specific_heat().to("J/kgK"))
print("Thermal Conductivity:", toluene.thermal_conductivity().to("W/mK"))
print("Vapor Pressure:", toluene.vapor_pressure().to("Pa"))
print("Enthalpy:", toluene.enthalpy().to("J/kg"))
print("Phase:", toluene.phase())
```