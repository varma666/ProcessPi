# Fluid Velocity (US Units)

**Problem**

Calculate the fluid velocity in a pipe given:  

- Volumetric flow rate = 3000 gal/min  
- Pipe diameter = 15.5 in  

This demonstrates the use of the **CalculationEngine** for simple hydraulic calculations.

## Code

```python
from processpi.calculations import CalculationEngine
from processpi.units import VolumetricFlowRate, Diameter

# Initialize the engine
engine = CalculationEngine()

# Inputs
volumetric_flow_rate = VolumetricFlowRate(3000, "gal/min")
diameter = Diameter(15.5, "in")

# Perform calculation
velocity = engine.calculate(
    "fluid_velocity",
    volumetric_flow_rate=volumetric_flow_rate,
    diameter=diameter
)


print(f"Velocity: {velocity.to('ft/s')}")
```
## Output
```py
# Output
Velocity: 5.100918717 ft/s
```