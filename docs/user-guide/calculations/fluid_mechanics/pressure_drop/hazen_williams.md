# Class: `PressureDropHazenWilliams`

The `PressureDropHazenWilliams` class calculates the **pressure drop (ΔP)** in a pipe using the **Hazen–Williams equation**.  
It is part of the **ProcessPI Calculations** module and inherits from `CalculationBase`.

---

## 📖 Description

The **Hazen–Williams equation** is an **empirical formula** for estimating **head loss due to friction** in water distribution systems.  
It is simpler than the **Darcy–Weisbach equation** since it avoids iterative calculations for friction factors.  

This method is mainly used for **water flow in pipes**.

---

## 📊 Formula

### Head Loss (SI Units):

$$
h_f = 10.67 \cdot \frac{L \cdot Q^{1.852}}{C^{1.852} \cdot D^{4.87}}
$$

### Pressure Drop:

$$
\Delta P = \rho \cdot g \cdot h_f
$$

Where:

| Symbol   | Description                          | Units   |
|----------|--------------------------------------|---------|
| \( h_f \) | Head loss                           | m       |
| \( \Delta P \) | Pressure drop                  | Pa      |
| \( L \)  | Pipe length                          | m       |
| \( Q \)  | Volumetric flow rate                 | m³/s    |
| \( C \)  | Hazen–Williams roughness coefficient | –       |
| \( D \)  | Pipe diameter                        | m       |
| \( \rho \) | Fluid density                      | kg/m³   |
| \( g \)  | Gravitational acceleration           | 9.81 m/s² |

---

## ⚙️ Inputs

- `length` → Pipe length (m)  
- `flow_rate` → Volumetric flow rate (m³/s)  
- `coefficient` → Hazen–Williams roughness coefficient (dimensionless)  
- `diameter` → Pipe internal diameter (m)  
- `density` → Fluid density (kg/m³)  

---

## 📤 Output

Returns a **`Pressure`** object containing the pressure drop in Pascals (**Pa**).

---

## 🛠️ Methods

**`validate_inputs()`**  
Ensures all required inputs (`length`, `flow_rate`, `coefficient`, `diameter`, `density`) are provided.  
Raises `ValueError` if any are missing.

---

**`calculate()`**  
Performs the Hazen–Williams pressure drop calculation:

1. Computes head loss (\(h_f\))  
2. Converts \(h_f\) into pressure drop using \( \Delta P = \rho \cdot g \cdot h_f \)  

**Returns:**  
`Pressure`: The computed pressure drop in Pascals.

---

## 💻 Example Usage

**Using the `PressureDropHazenWilliams`**

```python
from processpi.calculations import PressureDropHazenWilliams
from processpi.units import Pressure, Length, Diameter, Density, FlowRate, Dimensionless

# Define pipe and fluid properties
length = Length(100, "m")                 # Pipe length
flow_rate = FlowRate(0.05, "m3/s")        # Volumetric flow rate
coefficient = Dimensionless(130)          # Hazen–Williams coefficient for water
diameter = Diameter(0.15, "m")            # Pipe diameter
density = Density(998, "kg/m3")           # Water density

# Create calculation instance
pd_calc = PressureDropHazenWilliams(
    length=length,
    flow_rate=flow_rate,
    coefficient=coefficient,
    diameter=diameter,
    density=density
)

# Perform calculation
deltaP = pd_calc.calculate()

print(f"Pressure Drop (Hazen-Williams): {deltaP}")
```

**Using the `CalculationEngine`
```py
from processpi.engine import CalculationEngine
from processpi.units import Pressure, Length, Diameter, Density, FlowRate, Dimensionless

# Initialize engine
engine = CalculationEngine()

# Define pipe and fluid properties
length = Length(100, "m")
flow_rate = FlowRate(0.05, "m3/s")
coefficient = Dimensionless(130)
diameter = Diameter(0.15, "m")
density = Density(998, "kg/m3")

# Perform Hazen-Williams pressure drop calculation using the engine
deltaP = engine.calculate(
    "pressure_drop_hazen_williams",
    length=length,
    flow_rate=flow_rate,
    coefficient=coefficient,
    diameter=diameter,
    density=density
)

print(f"Pressure Drop (via Engine): {deltaP}")
```