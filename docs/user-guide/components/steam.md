# **Class: `Steam`**

## **Description**

The `Steam` class represents water vapor (steam) and provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All properties are retrieved from **CoolProp**, ensuring accurate and temperature/pressure-dependent values.

## **Properties**

* **`name`** (string): Steam  
* **`formula`** (string): H₂O  
* **`molecular_weight`** (float): 18.015 g/mol  

## **Class Reference**

**`class Steam()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(100,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  

## **Methods**

The properties of the `Steam` class are obtained using **CoolProp**:

* **`phase()`**: Returns `"gas"`, `"liquid"`, or `"two-phase"` depending on temperature and pressure.  
* **`density()`**: Returns the density (ρ) of steam at the given temperature and pressure.  
* **`specific_heat()`**: Returns the specific heat capacity at constant pressure (Cp).  
* **`viscosity()`**: Returns the dynamic viscosity (μ).  
* **`thermal_conductivity()`**: Returns the thermal conductivity (k).  
* **`vapor_pressure()`**: Returns the saturation pressure at the given temperature.  
* **`enthalpy()`**: Returns the enthalpy (h) per unit mass.  

All calculations are accurate and sourced directly from **CoolProp** for water.

## **Examples**

```py
from processpi.components import Steam
from processpi.units import *

# Create a Steam object at 150°C
steam = Steam(temperature=Temperature(150, "C"))

print("Density:", steam.density().to("kg/m3"))
print("Viscosity:", steam.viscosity().to("Pa·s"))
print("Specific Heat:", steam.specific_heat().to("J/kgK"))
print("Thermal Conductivity:", steam.thermal_conductivity().to("W/mK"))
print("Vapor Pressure:", steam.vapor_pressure().to("Pa"))
print("Enthalpy:", steam.enthalpy().to("J/kg"))
print("Phase:", steam.phase())
```