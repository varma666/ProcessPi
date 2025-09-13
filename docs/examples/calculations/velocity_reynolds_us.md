# Velocity and Reynolds Number (US Units)


**Problem**

Calculate the **fluid velocity** and **Reynolds number** for a flow in US customary units:

- Volumetric flow rate = 6000 gal/min  
- Pipe diameter = 19.25 in  
- Fluid density = 998 kg/m³  
- Kinematic viscosity = 1.0 cSt  

This demonstrates multiple property calculations in a single workflow.

## Code

```python
from processpi.calculations import CalculationEngine
from processpi.units import VolumetricFlowRate, Diameter, Density, Viscosity

# Initialize the engine
engine = CalculationEngine()

# Inputs
volumetric_flow_rate = VolumetricFlowRate(6000, "gal/min")
diameter = Diameter(19.25, "in")

# Velocity
velocity = engine.calculate(
    "fluid_velocity",
    volumetric_flow_rate=volumetric_flow_rate,
    diameter=diameter
)

# Reynolds number
density = Density(998, "kg/m3")
viscosity = Viscosity(1.0, "cSt")
nre = engine.calculate(
    "reynolds_number",
    density=density,
    velocity=velocity,
    diameter=diameter,
    viscosity=viscosity
)


print(f"Velocity: {velocity.to('ft/s')}")
print(f"Reynolds Number: {nre}")
```

## Output
```py
# Output
Velocity: 6.614228284 ft/s
Reynolds Number: 985731.40506995 (dimensionless)
```