# Class: `ReynoldsNumber`

The `ReynoldsNumber` class calculates the **Reynolds number (Re)** for fluid flow inside a pipe.  
It is part of the **ProcessPI Calculations** module and inherits from `CalculationBase`.

---

## 📖 Description

The **Reynolds number** is a **dimensionless quantity** that predicts fluid flow behavior by comparing inertial forces to viscous forces.  

- **Laminar flow** → occurs at low Re.  
- **Turbulent flow** → occurs at high Re.  

This class supports calculations using either **dynamic viscosity (μ)** or **kinematic viscosity (ν)**.

---

## 📊 Variables

| Symbol | Description                 | Units        |
|--------|-----------------------------|--------------|
| ρ      | Fluid density               | kg/m³        |
| v      | Fluid velocity              | m/s          |
| D      | Pipe diameter               | m            |
| μ      | Dynamic viscosity           | Pa·s         |
| ν      | Kinematic viscosity         | m²/s         |

---

## ⚙️ Inputs

- `density` → Fluid density  
- `velocity` → Fluid velocity  
- `diameter` → Pipe internal diameter  
- `viscosity` → Fluid viscosity (dynamic or kinematic)  

---

## 📤 Output

- Returns a **`Dimensionless`** object containing the Reynolds number value.

---

## 🛠️ Methods

**`validate_inputs()`**
Validates that all required inputs (`density`, `velocity`, `diameter`, `viscosity`) are provided.  
Raises `ValueError` if any input is missing.

---

**`calculate()`**
Performs the Reynolds number calculation:

- If **dynamic viscosity** is provided → uses:

$$
Re = \frac{\rho \cdot v \cdot D}{\mu}
$$

- If **kinematic viscosity** is provided → uses:

$$
Re = \frac{v \cdot D}{\nu}
$$

**Returns:**  
- `Dimensionless`: The computed Reynolds number.

---

## 💻 Example Usage


**Using the `ReynoldsNumber`**

```python
from processpi.calculations.fluids.reynolds_number import ReynoldsNumber
from processpi.units import Density, Velocity, Diameter, Viscosity

# Define fluid properties
density = Density(998, "kg/m3")          # Water density
velocity = Velocity(2.5, "m/s")          # Flow velocity
diameter = Diameter(0.1, "m")            # Pipe diameter
viscosity = Viscosity(1.0, "cP")         # Dynamic viscosity

# Create calculation instance
re_calc = ReynoldsNumber(
    density=density,
    velocity=velocity,
    diameter=diameter,
    viscosity=viscosity
)

# Perform calculation
Re = re_calc.calculate()

print(f"Reynolds Number: {Re}")
```

**Using the `CalculationEngine`**

```py
from processpi.engine.calculation_engine import CalculationEngine
from processpi.units import Density, Velocity, Diameter, Viscosity

# Initialize engine
engine = CalculationEngine()

# Define fluid properties
density = Density(998, "kg/m3")          # Water density
velocity = Velocity(2.5, "m/s")          # Flow velocity
diameter = Diameter(0.1, "m")            # Pipe diameter
viscosity = Viscosity(1.0, "cP")         # Dynamic viscosity

# Perform Reynolds number calculation using the engine
Re = engine.calculate(
    "reynolds_number",
    density=density,
    velocity=velocity,
    diameter=diameter,
    viscosity=viscosity
)

print(f"Reynolds Number (via Engine): {Re}")
```