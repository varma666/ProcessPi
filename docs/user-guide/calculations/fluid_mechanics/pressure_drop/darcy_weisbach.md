# Class: `PressureDropDarcy`

The `PressureDropDarcy` class calculates the **pressure drop (ΔP)** in a pipe using the **Darcy–Weisbach equation**.  
It is part of the **ProcessPI Calculations** module and inherits from `CalculationBase`.

---

## 📖 Description

The **Darcy–Weisbach equation** is a **fundamental relation in fluid dynamics** for estimating **pressure loss due to friction** in pipes.  
It is valid for both **laminar** and **turbulent** flows, making it more versatile than empirical formulas like Hazen–Williams.  

This method requires knowledge of the **Darcy friction factor**, which may be obtained from correlations such as **Moody chart** or the **Colebrook–White equation**.

---

## 📊 Formula

### Pressure Drop:

$$
\Delta P = f \cdot \frac{L}{D} \cdot \frac{\rho \cdot v^2}{2}
$$

Where:

| Symbol   | Description             | Units   |
|----------|-------------------------|---------|
| \( \Delta P \) | Pressure drop     | Pa      |
| \( f \)  | Darcy friction factor   | –       |
| \( L \)  | Pipe length             | m       |
| \( D \)  | Pipe diameter           | m       |
| \( \rho \) | Fluid density         | kg/m³   |
| \( v \)  | Fluid velocity          | m/s     |

---

## ⚙️ Inputs

- `friction_factor` → Darcy friction factor (dimensionless)  
- `length` → Pipe length (m)  
- `diameter` → Pipe internal diameter (m)  
- `density` → Fluid density (kg/m³)  
- `velocity` → Fluid velocity (m/s)  

---

## 📤 Output

Returns a **`Pressure`** object containing the pressure drop in Pascals (**Pa**).

---

## 🛠️ Methods

**`validate_inputs()`**  
Ensures all required inputs (`friction_factor`, `length`, `diameter`, `density`, `velocity`) are provided.  
Raises `ValueError` if any are missing.

---

**`calculate()`**  
Performs the Darcy–Weisbach pressure drop calculation:

1. Retrieves the inputs  
2. Applies the formula  
3. Returns the result as a `Pressure` object  

**Returns:**  
`Pressure`: The computed pressure drop in Pascals.

---

## 💻 Example Usage

**Using the `PressureDropDarcy`**

```python
from processpi.calculations.fluids.pressure_drop_darcy import PressureDropDarcy
from processpi.units import Pressure, Length, Diameter, Density, Velocity, Dimensionless

# Define pipe and fluid properties
friction_factor = Dimensionless(0.02)     # Example Darcy friction factor
length = Length(100, "m")                 # Pipe length
diameter = Diameter(0.15, "m")            # Pipe diameter
density = Density(998, "kg/m3")           # Water density
velocity = Velocity(2.5, "m/s")           # Fluid velocity

# Create calculation instance
pd_calc = PressureDropDarcy(
    friction_factor=friction_factor,
    length=length,
    diameter=diameter,
    density=density,
    velocity=velocity
)

# Perform calculation
deltaP = pd_calc.calculate()

print(f"Pressure Drop (Darcy–Weisbach): {deltaP}")
```

**Using the `CalculationEngine`
```py

from processpi.calculations import CalculationEngine
from processpi.units import Pressure, Length, Diameter, Density, Velocity, Dimensionless

# Initialize engine
engine = CalculationEngine()

# Define pipe and fluid properties
friction_factor = Dimensionless(0.02)
length = Length(100, "m")
diameter = Diameter(0.15, "m")
density = Density(998, "kg/m3")
velocity = Velocity(2.5, "m/s")

# Perform Darcy–Weisbach pressure drop calculation using the engine
deltaP = engine.calculate(
    "pressure_drop_darcy",
    friction_factor=friction_factor,
    length=length,
    diameter=diameter,
    density=density,
    velocity=velocity
)

print(f"Pressure Drop (via Engine): {deltaP}")
```