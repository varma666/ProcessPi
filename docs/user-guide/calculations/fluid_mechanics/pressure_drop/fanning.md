# Class: `PressureDropFanning`

The `PressureDropFanning` class calculates the **pressure drop (ΔP)** in a pipe using the **Fanning equation**.  
It is part of the **ProcessPI Calculations** module and inherits from `CalculationBase`.

---

## 📖 Description

The **Fanning friction factor** is a dimensionless number that relates the **shear stress at the pipe wall** to the **kinetic energy of the fluid**.  
The **Fanning equation** is widely used in chemical and process engineering to calculate pipe pressure drops.

---

## 📊 Formula

The pressure drop is given by:

$$
\Delta P = 4 \cdot f_F \cdot \frac{L}{D} \cdot \frac{\rho \cdot v^2}{2}
$$

Where:

| Symbol   | Description                    | Units   |
|----------|--------------------------------|---------|
| ΔP       | Pressure drop                  | Pa      |
| f<sub>F</sub>      | Fanning friction factor        | –       |
| L        | Pipe length                    | m       |
| D        | Pipe diameter                  | m       |
| ρ        | Fluid density                  | kg/m³   |
| v        | Fluid velocity                 | m/s     |

---

## ⚙️ Inputs

- `friction_factor` → Fanning friction factor (dimensionless)  
- `length` → Pipe length  
- `diameter` → Pipe internal diameter  
- `density` → Fluid density  
- `velocity` → Fluid velocity  

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
Performs the Fanning pressure drop calculation:

$$
\Delta P = 4 \cdot f_F \cdot \frac{L}{D} \cdot \frac{\rho \cdot v^2}{2}
$$

**Returns:**  
`Pressure`: The computed pressure drop in Pascals.

---

## 💻 Example Usage

**Using the `PressureDropFanning`**

```python
from processpi.calculations.fluids.pressure_drop_fanning import PressureDropFanning
from processpi.units import Pressure, Length, Diameter, Density, Velocity, Dimensionless

# Define fluid and pipe properties
friction_factor = Dimensionless(0.005)    # Example fanning friction factor
length = Length(50, "m")                  # Pipe length
diameter = Diameter(0.1, "m")             # Pipe diameter
density = Density(998, "kg/m3")           # Water density
velocity = Velocity(2.5, "m/s")           # Flow velocity

# Create calculation instance
pd_calc = PressureDropFanning(
    friction_factor=friction_factor,
    length=length,
    diameter=diameter,
    density=density,
    velocity=velocity
)

# Perform calculation
deltaP = pd_calc.calculate()

print(f"Pressure Drop (Fanning): {deltaP}")
```

**Using the `CalculationEngine`**

```py
from processpi.calculations import CalculationEngine
from processpi.units import Pressure, Length, Diameter, Density, Velocity, Dimensionless

# Initialize engine
engine = CalculationEngine()

# Define fluid and pipe properties
friction_factor = Dimensionless(0.005)    # Example fanning friction factor
length = Length(50, "m")                  # Pipe length
diameter = Diameter(0.1, "m")             # Pipe diameter
density = Density(998, "kg/m3")           # Water density
velocity = Velocity(2.5, "m/s")           # Flow velocity

# Perform Fanning pressure drop calculation using the engine
deltaP = engine.calculate(
    "pressure_drop_fanning",
    friction_factor=friction_factor,
    length=length,
    diameter=diameter,
    density=density,
    velocity=velocity
)

print(f"Pressure Drop (via Engine): {deltaP}")
```