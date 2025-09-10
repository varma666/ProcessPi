# 📐 Units Module

The `processpi.units` module provides a **consistent framework** to handle unit conversions across SI, CGS, and Imperial systems.  
Every physical property is represented as a Python class with built-in `.to()` methods for easy conversion.

---

## 🔧 Usage Pattern

```python
from processpi.units import Length

length = Length(10, "m")     # define length in meters
print(length.to("ft"))  # convert to feet
```
---
## 🚀 Examples
Below are some examples covering the most common engineering quantities.

## 1. Velocity
```python
from processpi.units import Velocity

v = Velocity(1.55, "m/s")
print(v.to("ft/s"))
# Output: 5.085 ft/s
```

## 2. Diameter
```python
from processpi.units import Diameter

d = Diameter(10, "in")
print(d.to("cm"))
# Output: 25.4 cm
```

## 3. Density
```python
from processpi.units import Density
den = Density(1000, "kg/m3")
print(den.to("g/cm3"))
# Output: 1.0 g/cm3
```

## 4. Heat Flux
```python
from processpi.units import HeatFlux
q = HeatFlux(5000, "W/m2")
print(q.to("BTU/hft2"))
```
## 5. Heat of Vaporization
```python
from processpi.units import HeatOfVaporization
hv = HeatOfVaporization(2260, "J/kg")
print(hv.to("BTU/lb"))
```
## 6. Heat Transfer Coefficient
```python
from processpi.units import HeatTransferCoefficient

htc = HeatTransferCoefficient(1000, "W/m2K")
print(htc.to("BTU/hft2F"))
```
## 7. Length
```python
from processpi.units import Length

L = Length(5, "m")
print(L.to("ft"))
```
## 8. Mass Flow Rate
```python
from processpi.units import MassFlowRate

mf = MassFlowRate(100, "kg/s")
print(mf.to("lb/min"))
```
## 9. Mass
```python
from processpi.units import Mass

m = Mass(10, "kg")
print(m.to("lb"))
```
## 10. Power
```python
from processpi.units import Power

P = Power(1000, "W")
print(P.to("BTU/h"))
```
## 11. Pressure
```python
from processpi.units import Pressure

p = Pressure(101325, "Pa")
print(p.to("psi"))
```
## 12. Specific Heat
```python
from processpi.units import SpecificHeat

cp = SpecificHeat(4184, "J/kgK")
print(cp.to("BTU/lbF"))
```
## 13. Temperature
```python
from processpi.units import Temperature

T = Temperature(100, "C")
print(T.to("F"))
```
## 14. Thermal Conductivity
```python
from processpi.units import ThermalConductivity

k = ThermalConductivity(200, "W/mK")
print(k.to("BTU/hftF"))
```
## 15. Viscosity
```python
from processpi.units import Viscosity

mu = Viscosity(1.55, "Pa·s")
print(mu.to("cP"))
```
## 16. Volume
```python
from processpi.units import Volume

V = Volume(1, "L")
print(V.to("m3"))
```
## 17. Volumetric Flow Rate
```python
from processpi.units import VolumetricFlowRate

Q = VolumetricFlowRate(3000, "gal/min")
print(Q.to("m3/s"))
```
## ✨ Bonus Examples
---
## 18. Time
```python
from processpi.units import Time

t = Time(3600, "s")
print(t.to("h"))
# Output: 1 h
```

## 19. Molar Flow Rate
```python
from processpi.units import MolarFlowRate

n_dot = MolarFlowRate(100, "mol/s")
print(n_dot.to("kmol/h"))
```


## ✅ Summary
Every unit is a class (e.g., Length, Pressure, Viscosity).

Values can be converted with .to("<unit>").

The system supports engineering-friendly units across SI, Imperial, and practical process units.

Use this module as the foundation for all your chemical/process engineering calculations in ProcessPI.
