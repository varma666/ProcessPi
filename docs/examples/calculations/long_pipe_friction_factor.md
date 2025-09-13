# Long Pipeline Pressure Drop (Metric Units)

**Problem**

A long water pipeline transports **34,000 m³/h** of liquid water.  
The pipe has a **diameter of 2.0 m**, a **length of 5 km**, and an **absolute roughness of 0.05 mm**.  
At 20 °C, the water has a **density of 998 kg/m³** and a **viscosity of 1.0 cP**.  

We want to calculate:
- Flow velocity  
- Reynolds number  
- Friction factor (Colebrook–White)  
- Pressure drop using the Darcy–Weisbach equation  

---

## Code

```python
from processpi.calculations import CalculationEngine
from processpi.units import VolumetricFlowRate, Diameter, Density, Viscosity, Length

# Initialize engine
engine = CalculationEngine()

# Given parameters
volumetric_flow_rate = VolumetricFlowRate(34000, "m3/h")
diameter = Diameter(2, "m")
roughness = Length(0.05, "mm")
density = Density(998, "kg/m3")
viscosity = Viscosity(1.0, "cP")
length = Length(5, "km")

# Step 1: Velocity
velocity = engine.calculate(
    "fluid_velocity",
    volumetric_flow_rate=volumetric_flow_rate,
    diameter=diameter
)

# Step 2: Reynolds Number
nre = engine.calculate(
    "nre",
    density=density,
    velocity=velocity,
    diameter=diameter,
    viscosity=viscosity
)

# Step 3: Friction Factor (Colebrook-White)
friction_factor = engine.calculate(
    "friction_factor_colebrookwhite",
    diameter=diameter,
    roughness=roughness,
    reynolds_number=nre
)

# Step 4: Darcy–Weisbach Pressure Drop
pressure_drop = engine.calculate(
    "pressure_drop_darcy",
    friction_factor=friction_factor,
    length=length,
    diameter=diameter,
    density=density,
    velocity=velocity
)

# Results
print(f"Velocity: {velocity}")
print(f"Reynolds Number: {nre}")
print(f"Friction Factor: {friction_factor}")
print(f"Pressure Drop: {pressure_drop.to('kPa')}")
```

## Output
```py
# Output
Velocity: 3.006259895 m/s
Reynolds Number: 6000494.7504199995 (dimensionless)
Friction Factor: 0.008738971889204653 (dimensionless)
Pressure Drop: 98.526701 kPa
```