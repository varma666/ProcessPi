# Class: `FluidVelocity`

The `FluidVelocity` class calculates the **average fluid velocity (v)** in a circular pipe.  
It is part of the **ProcessPI Calculations** module and inherits from `CalculationBase`.

---

## 📖 Description

The **fluid velocity** determines how fast a fluid moves through a pipe.  
It is calculated from the **volumetric flow rate** and the **cross-sectional area** of the pipe.  

This calculation is fundamental in **fluid dynamics** and is used in many pressure drop and flow analyses.

---

## 📊 Formula

$$
v = \frac{Q}{A} = \frac{4 \cdot Q}{\pi \cdot D^2}
$$

Where:

| Symbol | Description                     | Units        |
|--------|---------------------------------|--------------|
| \( v \) | Fluid velocity                  | m/s          |
| \( Q \) | Volumetric flow rate            | m³/s         |
| \( A \) | Cross-sectional area of pipe    | m²           |
| \( D \) | Pipe diameter                   | m            |

---

## ⚙️ Inputs

- `volumetric_flow_rate` → Volumetric flow rate (m³/s)  
- `diameter` → Pipe internal diameter (m)  

---

## 📤 Output

Returns a **`Velocity`** object containing the fluid velocity in meters per second (**m/s**).

---

## 🛠️ Methods

**`validate_inputs()`**  
Ensures the required inputs (`volumetric_flow_rate`, `diameter`) are provided.  
Raises `ValueError` if any are missing.

---

**`calculate()`**  
Performs the fluid velocity calculation:

1. Computes the **cross-sectional area** of the pipe: \( A = \pi \cdot D^2 / 4 \)  
2. Calculates the **average fluid velocity**: \( v = Q / A \)  

**Returns:**  
`Velocity`: The computed fluid velocity in m/s.

---

## 💻 Example Usage

**Using the `FluidVelocity`**

```python
from processpi.calculations.fluids.velocity import FluidVelocity
from processpi.units import Velocity, VolumetricFlowRate, Diameter

# Define pipe and flow properties
Q = VolumetricFlowRate(0.05, "m3/s")   # Volumetric flow rate
D = Diameter(0.1, "m")       # Pipe diameter

# Create calculation instance
velocity_calc = FluidVelocity(
    volumetric_flow_rate=Q,
    diameter=D
)

# Perform calculation
v = velocity_calc.calculate()

print(f"Fluid Velocity: {v}")
```

**Using the `CalculationEngine`
```py

from processpi.calculations import CalculationEngine
from processpi.units import VolumetricFlowRate, Diameter

# Initialize engine
engine = CalculationEngine()

# Define pipe and flow properties
Q = VolumetricFlowRate(0.05, "m3/s")
D = Diameter(0.1, "m")

# Perform fluid velocity calculation using the engine
v = engine.calculate(
    "fluid_velocity",
    volumetric_flow_rate=Q,
    diameter=D
)

print(f"Fluid Velocity (via Engine): {v}")
```