# Class: `TypeOfFlow`

The `TypeOfFlow` class determines the **type of fluid flow** based on the **Reynolds number (Re)**.  
It is part of the **ProcessPI Calculations** module and inherits from `CalculationBase`.

---

## 📖 Description

The **flow regime** describes how fluid moves through a pipe or channel.  
It is classified into **Laminar**, **Transitional**, or **Turbulent** flow, depending on the **Reynolds number**.  

- **Laminar Flow** → Smooth, orderly flow with little mixing (`Re < 2000`)  
- **Transitional Flow** → Unstable regime, switching between laminar & turbulent (`2000 ≤ Re ≤ 4000`)  
- **Turbulent Flow** → Chaotic, highly mixed flow (`Re > 4000`)  

---

## 📊 Formula / Criteria

The classification is based on the Reynolds number:

$$
Re = \frac{\rho \cdot v \cdot D}{\mu}
$$

Where:

| Symbol   | Description             | Units      |
|----------|-------------------------|------------|
| \( Re \) | Reynolds number         | – (dimensionless) |
| \( \rho \) | Fluid density          | kg/m³      |
| \( v \)  | Fluid velocity          | m/s        |
| \( D \)  | Pipe diameter           | m          |
| \( \mu \) | Dynamic viscosity       | Pa·s       |

---

## ⚙️ Inputs

- `reynolds_number` → Reynolds number (dimensionless)  

---

## 📤 Output

Returns a **`StringUnit`** object containing the determined flow type:  
- `"Laminar"`  
- `"Transitional"`  
- `"Turbulent"`  

---

## 🛠️ Methods

**`validate_inputs()`**  
Ensures the required input `reynolds_number` is provided.  
Raises `ValueError` if missing.

---

**`calculate()`**  
Classifies the flow regime based on Reynolds number:  

- If `Re < 2000` → `"Laminar"`  
- If `2000 ≤ Re ≤ 4000` → `"Transitional"`  
- If `Re > 4000` → `"Turbulent"`  

**Returns:**  
`StringUnit`: The computed flow type.

---

## 💻 Example Usage

**Using the `TypeOfFlow`**

```python
from processpi.calculations.fluids.flow_type import TypeOfFlow
from processpi.units import Dimensionless

# Example Reynolds number
Re = Dimensionless(3500)

# Create calculation instance
flow_calc = TypeOfFlow(reynolds_number=Re)

# Perform calculation
flow_type = flow_calc.calculate()

print(f"Flow Type: {flow_type}")
```

**Using the `CalculationEngine`

```py
from processpi.calculations import CalculationEngine
from processpi.units import Dimensionless

# Initialize engine
engine = CalculationEngine()

# Example Reynolds number
Re = Dimensionless(3500)

# Perform flow type classification using the engine
flow_type = engine.calculate(
    "type_of_flow",
    reynolds_number=Re
)

print(f"Flow Type (via Engine): {flow_type}")
```