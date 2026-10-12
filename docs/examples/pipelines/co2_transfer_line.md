# CO₂ Transfer Line Between Plants

**Problem**  
Carbon dioxide is to be conveyed from an ammonia plant stripper to a urea plant.

**Given Data**
- Flow rate: 1000 t/day  
- Pipe length: 800 m  
- Inlet pressure: 24 kPa(g), outlet: atm  
- 8 × 90° elbows, 1 × gate valve, 1 × nozzle  
- Temperature: 60 °C  
- Viscosity: 0.016 mPa·s  

---

## Code

```python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

# Define fluid
fluid = Carbondioxide(temperature=Temperature(60, "C"))
print("Density:", fluid.density(), "Viscosity:", fluid.viscosity().to("cP"))

# Define mass flow
mass_flow = MassFlowRate(1000, "t/day")

# Pipe and fittings
pipe = Pipe(name="Main Pipe", length=Length(800, "m"), material="CS")
elbow = Fitting(fitting_type="standard_elbow_90_deg", quantity=8)
valve = Fitting(fitting_type="gate_valve", quantity=1)
nozzle = Fitting(fitting_type="exit", quantity=1)

# Pipeline engine
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbow, valve, nozzle],
    available_dp=Pressure(24, "kPa")
)
results = model.run()

# Summaries
model.summary()
results.detailed_summary()
```
## Output

```py
Density: 1.609882 kg/m3 Viscosity: 0.019523 cP (dynamic)
✅ Found optimal diameter for available pressure drop.
   Selected Diameter: 22.0 in (0.5399 m internal)
   Calculated Pressure Drop: 21700.71 Pa (allowed: 24000.00 Pa)
⚠️ Warning: Final velocity 31.40 m/s outside recommended range (8.00-15.00 m/s) for Carbon Dioxide.

# Summary
=== Pipeline Result 1 (Main Pipe) ===
Mode: Single_pipe
Nominal Pipe Size: 22 in
Internal Diameter: 539.94 mm
Inlet Flow: 7.189 m3/s 
Outlet Flow: 7.189 m3/s 
Total Pressure Drop: 21.70 kPa
Total Head Loss: 1374.55 m
Total Power Required: 222.88 kW
Velocity: 31.399 m/s
Reynolds Number: 1397955 (dimensionless)
Friction Factor: 0.0128 (dimensionless)

# Detailed Summary
=== Detailed Components for Result 1 (Main Pipe) ===
+-----------+--------+-----------------+------------+-------------+-------------------+----------------+---------------------+
| Name      | Type   |   Pressure Drop |   Velocity |    Reynolds |   Friction Factor | Nominal Size   | Internal Diameter   |
+===========+========+=================+============+=============+===================+================+=====================+
| Main Pipe | pipe   |         21700.7 |       31.4 | 1.39796e+06 |            0.0128 | 22 in          | 539.94 mm           |
+-----------+--------+-----------------+------------+-------------+-------------------+----------------+---------------------+

```