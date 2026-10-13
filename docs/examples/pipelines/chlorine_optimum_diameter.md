# Optimum Pipe Diameter for Chlorine Gas

**Problem**  
Estimate the optimum pipe diameter for a flow of dry chlorine gas of **10 000 kg/h**  
at **6 atm(a)** and **20 °C** through a carbon steel pipe.

---

## Code

```python
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine

# Define fluid and mass flow
fluid = Chlorine(temperature=Temperature(20, "C"), pressure=Pressure(6, "atm"))
mass_flow = MassFlowRate(10000, "kg/h")

print("Density:", fluid.density())

# Create engine without explicit network
model = PipelineEngine()
model.fit(fluid=fluid, mass_flow=mass_flow)
results = model.run()

results.summary()
results.detailed_summary()
```

## Output
```py
# Summary
Density: 17.685884 kg/m3
✅ Found optimal diameter based on recommended velocity.
   Selected Diameter: 6.0 in 
   Calculated Pressure Drop: 62.85 Pa

=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Nominal Pipe Size: 6 in
Internal Diameter: 154.08 mm
Inlet Flow: 0.157 m3/s 
Outlet Flow: 0.157 m3/s 
Total Pressure Drop: 0.06 kPa
Total Head Loss: 0.36 m
Total Power Required: 0.01 kW
Velocity: 8.423 m/s
Reynolds Number: 1298657 (dimensionless)
Friction Factor: 0.0154 (dimensionless)

# Detailed Summary
=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+-------------+-------------------+----------------+---------------------+
| Name      | Type   |   Pressure Drop |   Velocity |    Reynolds |   Friction Factor | Nominal Size   | Internal Diameter   |
+===========+========+=================+============+=============+===================+================+=====================+
| Main Pipe | pipe   |           62.85 |       8.42 | 1.29866e+06 |            0.0154 | 6 in           | 154.08 mm           |
+-----------+--------+-----------------+------------+-------------+-------------------+----------------+---------------------+

```