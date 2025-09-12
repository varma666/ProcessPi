# **Class: `Water`**

## **Description**

The `Water` class represents water in liquid or vapor (steam) phase.  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All properties can be retrieved from **CoolProp** for accurate temperature- and pressure-dependent values.

## **Properties**

* **`name`** (string): Water  
* **`formula`** (string): H₂O  
* **`molecular_weight`** (float): 18.015 g/mol  

## **Class Reference**

**`class Water()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(25,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  

## **Methods**

The properties of the `Water` class are obtained using **CoolProp**:

* **`phase()`**: Returns `"liquid"`, `"gas"`, or `"two-phase"` depending on temperature and pressure.  
* **`density()`**: Returns the density (ρ) at the given temperature and pressure.  
* **`specific_heat()`**: Returns the specific heat capacity at constant pressure (Cp).  
* **`viscosity()`**: Returns the dynamic viscosity (μ).  
* **`thermal_conductivity()`**: Returns the thermal conductivity (k).  
* **`vapor_pressure()`**: Returns the saturation pressure at the given temperature.  
* **`enthalpy()`**: Returns the enthalpy (h) per unit mass.  

All calculations are accurate and sourced directly from **CoolProp**.

## **Examples**

```py
from processpi.components import Water
from processpi.units import *

# Create a Water object at 150°C
water = Water(temperature=Temperature(150, "C"))

print("Density:", water.density().to("kg/m3"))
print("Viscosity:", water.viscosity().to("Pa·s"))
print("Specific Heat:", water.specific_heat().to("J/kgK"))
print("Thermal Conductivity:", water.thermal_conductivity().to("W/mK"))
print("Vapor Pressure:", water.vapor_pressure().to("Pa"))
print("Enthalpy:", water.enthalpy().to("J/kg"))
print("Phase:", water.phase())
```