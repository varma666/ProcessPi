# Class: `Fitting`

The **`Fitting`** class represents a pipe fitting used in hydraulic calculations.  
It provides access to **equivalent length (Le)** and **K-factor** values for fittings,  
which are essential in computing minor losses in pipelines.

---

## Parameters

- **`fitting_type`** (`str`)  
  The type of fitting (e.g., `"elbow_90"`, `"tee_branch"`, `"valve_gate"`).  
  Must be recognized by the standards database (`processpi.pipelines.standards`).
  **Standard Fitting Strings**

    The following `fitting_type` are supported in **ProcessPI**:
    
    - `gate_valve`  
    - `globe_valve`  
    - `angle_valve`  
    - `ball_valve`  
    - `plug_valve_straightway`  
    - `plug_valve_3_way_through_flow`  
    - `plug_valve_branch_flow`  
    - `swing_check_valve`  
    - `lift_check_valve`  
    - `standard_elbow_90_deg`  
    - `standard_elbow_45_deg`  
    - `long_radius_90_deg`  
    - `standard_tee_through_flow`  
    - `standard_tee_through_branch`  
    - `miter_bends_alpha_0`  
    - `miter_bends_alpha_30`  
    - `miter_bends_alpha_60`  
    - `miter_bends_alpha_90`  
    - `sudden_contraction`  
    - `sudden_expansion`  
    - `entrance_sharp`  
    - `entrance_rounded`  
    - `exit`   

- **`diameter`** (`Optional[Diameter]`, default=`None`)  
  Internal diameter of the pipe associated with this fitting.  
  Required for fittings where loss coefficients depend on pipe size.  

- **`quantity`** (`int`, default=`1`)  
  Number of identical fittings of this type.  
  Must be a positive integer.  

---

## Attributes

- **`fitting_type`** (`str`) – Name/type of fitting.  
- **`diameter`** (`Optional[Diameter]`) – Pipe diameter associated with the fitting.  
- **`quantity`** (`int`) – Count of fittings.  

---

## Methods

**`equivalent_length()`**
Computes the **equivalent length (Le)** of the fitting.  
This is the effective pipe length that produces the same pressure drop as the fitting.

**Returns**  
- `Length` (in meters) if available.  
- `None` if not applicable.  

**Raises**  
- `ValueError`: If the equivalent length requires a diameter but none is provided.  

---

**`k_factor()`**
Retrieves the **K-factor** (dimensionless loss coefficient) of the fitting.  

**Returns**  
- `float`: K-factor value.  
- `None`: If not applicable.  

**Raises**  
- `ValueError`: If diameter is required but not provided.  

---

**`calculate()`**
Returns a **dictionary summary** of the fitting, including geometry and loss data.

**Returns**  
```python
{
  "fitting_type": str,
  "quantity": int,
  "diameter_in": float or None,       # diameter in inches
  "diameter_m": float or None,        # diameter in meters
  "equivalent_length_m": float or None,
  "k_factor": float or None
}
```

✅ Example Usage
```py
from processpi.units import Diameter
from processpi.pipelines.fittings import Fitting

# Define a 90-degree elbow fitting for a 4-inch pipe
elbow = Fitting(fitting_type="standard_elbow_90_deg", diameter=Diameter(4, "in"), quantity=2)

# Get equivalent length and K-factor
print(elbow.equivalent_length())
print(elbow.k_factor())

# Export fitting details
print(elbow.calculate())
```
