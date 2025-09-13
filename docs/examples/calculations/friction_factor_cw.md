# Friction Factor (Colebrook-White, US Units)

**Problem**

A water flow of **3000 gal/min** passes through a **15.25 in** diameter pipe with an internal roughness of **0.002 in**.  
Given fluid properties of **ρ = 998 kg/m³** and **μ = 1.0 cP**, compute:

- Fluid velocity  
- Reynolds number  
- Friction factor using the **Colebrook–White equation**

---

## Code

```python
from processpi.units import VolumetricFlowRate, Diameter, Density, Viscosity, Length
from processpi.calculations import CalculationEngine

# Initialize engine
engine = CalculationEngine()

# Define flow and pipe conditions (US Units)
volumetric_flow_rate = VolumetricFlowRate(3000, "gal/min")
diameter = Diameter(15.25, "in")
roughness = Length(0.002, "in")

# Fluid properties
density = Density(998, "kg/m3")
viscosity = Viscosity(1.0, "cP")

# Velocity
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)

# Reynolds number
nre = engine.calculate("reynolds_number", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)

# Friction factor (Colebrook-White)
friction_factor = engine.calculate(
    "friction_factor_colebrookwhite",
    diameter=diameter,
    roughness=roughness,
    reynolds_number=nre
)

# Display results
print(f"Velocity: {velocity}")
print(f"Reynolds Number: {nre}")
print(f"Friction Factor: {friction_factor}")
```
## Output
```py
# Output
Velocity: 1.606153597 m/s
Reynolds Number: 620899.308606354 (dimensionless)
Friction Factor: 0.012658141727742982 (dimensionless)
```