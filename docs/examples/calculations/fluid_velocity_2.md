# Fluid Velocity (Metric Units)

**Problem**

Calculate the fluid velocity in a pipe given:  

- Volumetric flow rate = 75 L/s  
- Pipe diameter = 180 mm  

This demonstrates the use of the **CalculationEngine** in SI metric units.

## Code

```python
from processpi.calculations import CalculationEngine
from processpi.units import VolumetricFlowRate, Diameter

# Initialize the engine (reuse from Example 1)
engine = CalculationEngine()

# Inputs
volumetric_flow_rate = VolumetricFlowRate(75, "L/s")
diameter = Diameter(180, "mm")

# Perform calculation
velocity = engine.calculate(
    "fluid_velocity",
    volumetric_flow_rate=volumetric_flow_rate,
    diameter=diameter
)


print(f"Velocity: {velocity}")
```
## Output
```py
# Output
Velocity: 2.947313761 m/s
```