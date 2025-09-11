# Components

Example usage of the ProcessPI `Component` interface.

This guide covers:

1. Acetone at 35 °C  
2. Acetone at 60 °C (unit conversion demo)  
3. Generic Organic Liquid  
4. Generic Inorganic Liquid  
5. Generic Gas  
6. Oil at elevated temperature  
7. Vapor with custom properties override  
8. Quick comparison between two fluids  
9. Water at room temperature  
10. Toluene at 50 °C  
11. Methanol at 30 °C  

---

## 1. Acetone at 35 °C

```python
from processpi.components.acetone import Acetone
from processpi.units import *

acetone = Acetone(temperature=Temperature(35, "C"))
print(acetone.density().to("kg/m3"))
print(acetone.viscosity().to("Pa·s"))
print(acetone.specific_heat().to("J/kgK"))
print(acetone.thermal_conductivity().to("W/mK"))
print(acetone.vapor_pressure().to("Pa"))
print(acetone.enthalpy().to("J/kg"))
```
---


## 2. Acetone at higher temperature (60 °C) with unit conversion
```python
acetone_high = Acetone(temperature=Temperature(60, "C"))
print(acetone_high.density().to("lb/ft3"))
print(acetone_high.viscosity().to("cP"))
```
---
## 3. Generic Organic Liquid
```python
from processpi.components.organic_liquid import OrganicLiquid

organic = OrganicLiquid(temperature=Temperature(40, "C"))
print(organic.density().to("kg/m3"))
print(organic.viscosity().to("Pa·s"))
print(organic.specific_heat().to("J/kgK"))
```
---
## 4. Generic Inorganic Liquid
```python
from processpi.components.inorganic_liquid import InorganicLiquid

inorganic = InorganicLiquid(temperature=Temperature(50, "C"))
print(inorganic.density().to("kg/m3"))
print(inorganic.viscosity().to("Pa·s"))
print(inorganic.specific_heat().to("J/kgK"))
```
---
## 5. Generic Gas
```python
from processpi.components.gas import Gas

gas = Gas(temperature=Temperature(100, "C"))
print(gas.density().to("kg/m3"))
print(gas.viscosity().to("Pa·s"))
print(gas.specific_heat().to("J/kgK"))
```
---
## 6. Oil at elevated temperature
```python
from processpi.components.oil import Oil

oil = Oil(temperature=Temperature(150, "C"))
print(oil.density().to("kg/m3"))
print(oil.viscosity().to("cP"))
print(oil.specific_heat().to("J/kgK"))
```
---
## 7. Vapor with custom overrides
```python
from processpi.components.vapor import Vapor
from processpi.units import Density, Viscosity, SpecificHeat

custom_vapor = Vapor(
    temperature=Temperature(120, "C"),
    density=Density(0.7, "kg/m3"),
    viscosity=Viscosity(0.00002, "Pa·s"),
    specific_heat=SpecificHeat(1900, "J/kgK"),
)
print(custom_vapor.density().to("kg/m3"))
print(custom_vapor.viscosity().to("Pa·s"))
print(custom_vapor.specific_heat().to("J/kgK"))
```
---
## 8. Quick comparison: Organic vs. Inorganic Liquid
```python
organic_50 = OrganicLiquid(temperature=Temperature(50, "C"))
inorganic_50 = InorganicLiquid(temperature=Temperature(50, "C"))

print(organic_50.density().to("kg/m3"))
print(inorganic_50.density().to("kg/m3"))
print(organic_50.viscosity().to("Pa·s"))
print(inorganic_50.viscosity().to("Pa·s"))
```
---
## 9. Water at room temperature
```python
from processpi.components.water import Water

water = Water(temperature=Temperature(25, "C"))
print(water.density().to("kg/m3"))
print(water.viscosity().to("Pa·s"))
print(water.specific_heat().to("J/kgK"))
print(water.thermal_conductivity().to("W/mK"))
print(water.vapor_pressure().to("Pa"))
```
---
## 10. Toluene at 50 °C
```python
from processpi.components.toluene import Toluene

toluene = Toluene(temperature=Temperature(50, "C"))
print(toluene.density().to("kg/m3"))
print(toluene.viscosity().to("Pa·s"))
print(toluene.specific_heat().to("J/kgK"))
print(toluene.vapor_pressure().to("Pa"))
```
---
## 11. Methanol at 30 °C
```python
from processpi.components.methanol import Methanol

methanol = Methanol(temperature=Temperature(30, "C"))
print(methanol.density().to("kg/m3"))
print(methanol.viscosity().to("Pa·s"))
print(methanol.specific_heat().to("J/kgK"))
print(methanol.thermal_conductivity().to("W/mK"))
print(methanol.vapor_pressure().to("Pa"))
```
---
## ✅ Summary
Every fluid is represented as a class (e.g., Water, Acetone, Oil, Gas).

Properties available: density(), viscosity(), specific_heat(), thermal_conductivity(), vapor_pressure(), enthalpy().

Values can be converted to engineering units via .to("<unit>").

Custom overrides are supported for flexibility.

This system supports realistic chemical & process engineering workflows.