# Darcy Pressure Drop (US Units)

**Problem** 

Water flows at **3000 gal/min** through a **15.25 in** diameter pipe of length **1000 ft**.  
The pipe roughness is **0.002 in**, and the fluid has **ρ = 998 kg/m³** and **μ = 1.0 cP**.  

Compute the **Darcy–Weisbach pressure drop** using the previously calculated:

- Velocity  
- Reynolds number  
- Friction factor (Colebrook–White equation)  

---

## Code

```python
from processpi.units import VolumetricFlowRate, Diameter, Density, Viscosity, Length
from processpi.calculations import CalculationEngine

# Initialize engine
engine = CalculationEngine()

# Flow and pipe conditions (US Units)
volumetric_flow_rate = VolumetricFlowRate(3000, "gal/min")
diameter = Diameter(15.25, "in")
roughness = Length(0.002, "in")
length = Length(1000, "ft")

# Fluid properties
density = Density(998, "kg/m3")
viscosity = Viscosity(1.0, "cP")

# Velocity
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)

# Reynolds number
nre = engine.calculate("reynolds_number", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)

# Friction factor (Colebrook–White)
friction_factor = engine.calculate(
    "friction_factor_colebrookwhite",
    diameter=diameter,
    roughness=roughness,
    reynolds_number=nre
)

# Darcy pressure drop
pressure_drop = engine.calculate(
    "pressure_drop_darcy",
    friction_factor=friction_factor,
    length=length,
    diameter=diameter,
    density=density,
    velocity=velocity
)

# Display results

print(f"Pressure Drop: {pressure_drop.to('psi')}")
```

## Output
```py
# Output
Pressure Drop: 1.859674 psi
```