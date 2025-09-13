# Velocity and Reynolds Number (Metric Units)

**Problem**

A pipeline carries **640 m³/h** of water through a pipe with a **380 mm diameter**.  
The water has a density of **998 kg/m³** and a kinematic viscosity of **1.0 cSt**.  

We want to calculate the **fluid velocity** and the **Reynolds number** to assess the flow regime.

---

## Code

```python
from processpi.units import *
from processpi.calculations import CalculationEngine

# Initialize engine
engine = CalculationEngine()

# Define flow conditions (Metric Units)
volumetric_flow_rate = VolumetricFlowRate(640, 'm3/h')
diameter = Diameter(380, 'mm')

# Calculate velocity
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)

# Define fluid properties
density = Density(998, 'kg/m3')
viscosity = Viscosity(1.0, 'cSt')

# Calculate Reynolds number
nre = engine.calculate("reynolds_number", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)

# Display results
print(f"Velocity: {velocity}")
print(f"Reynolds Number: {nre}")
```
## Output
```py
# Output
Velocity: 1.567548336 m/s
Reynolds Number: 595668.36768 (dimensionless)
```