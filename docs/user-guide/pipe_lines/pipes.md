# **Class: `Pipe`**

## **Description**
The `Pipe` class represents a straight section of a process pipeline.  
It encapsulates geometry (diameter, length), material properties (roughness), and state (inlet/outlet pressure).  
This class is central to flow and pressure drop calculations and is compatible with optimization workflows.

---

## **Initialization**

```python
Pipe(
    name: str,
    nominal_diameter: Optional[Diameter] = None,
    schedule: str = "STD",
    material: str = "CS",
    length: Optional[Length] = None,
    inlet_pressure: Optional[Pressure] = None,
    outlet_pressure: Optional[Pressure] = None,
    internal_diameter: Optional[Diameter] = None,
    flow_rate: Optional[VolumetricFlowRate] = None,
    **kwargs: Any
)
```

**Parameters**
- **`name`** (`str`): Unique name of the pipe.  
- **`nominal_diameter`** (`Optional[Diameter]`): Nominal pipe size, a label: the NPS (`Diameter(4, "in")`) or the DN in millimetres (`Diameter(100, "mm")`, which is NPS 4). The internal diameter is looked up for `schedule` in the ASME B36.10M / B36.19M table. If neither diameter is given, the pipe is considered a candidate for optimization.  
- **`schedule`** (`str`, default=`"STD"`): Pipe schedule (`"STD"`, `"XS"`, `"40"`, `"Sch 40"`, `"40S"`...). `ValueError` if it is not tabulated for the nominal size.  
- **`material`** (`str`, default=`"CS"`): Pipe material.  
- **`length`** (`Optional[Length]`): Pipe length. Defaults to `1.0 m` if not provided.  
- **`inlet_pressure`** (`Optional[Pressure]`): Inlet pressure of the pipe.  
- **`outlet_pressure`** (`Optional[Pressure]`): Outlet pressure of the pipe.  
- **`internal_diameter`** (`Optional[Diameter]`): The bore used in the calculations. Given with `nominal_diameter`, it replaces the tabulated bore (a lined pipe, a non-standard wall) and must be smaller than that size's outside diameter (`ValueError` otherwise).  
- **`flow_rate`** (`Optional[VolumetricFlowRate]`): Initial flow rate for solver. Defaults to `0.001 m³/s`.  
- **`**kwargs`** (`Any`): Additional custom parameters stored in the base class.  

A diameter or length given as a bare number is read in metres, as before, with a `UserWarning`; pass `Diameter` and `Length` objects. A `nominal_diameter` that is not a standard size is used as the internal diameter, with a `UserWarning`. `Pipe` has no `diameter` input: `Pipe(diameter=...)` is ignored (kept in `params`), with a `UserWarning`.  

---

**Attributes**
- **`is_optimization_target`** (`bool`): Whether this pipe is flagged for optimization (true if no diameter was provided).  
- **`nominal_diameter`** (`Optional[Diameter]`): Nominal pipe size, as the NPS (a DN input is stored as its NPS).  
- **`schedule`** (`str`): Pipe schedule.  
- **`material`** (`str`): Pipe material.  
- **`length`** (`Length`): Pipe length.  
- **`roughness`** (`Variable`): Material roughness (from standards).  
- **`internal_diameter`** (`Optional[Diameter]`): Internal diameter (the bore every calculation uses).  
- **`inlet_pressure`** (`Optional[Pressure]`): Inlet pressure.  
- **`outlet_pressure`** (`Optional[Pressure]`): Outlet pressure.  
- **`flow_rate`** (`VolumetricFlowRate`): Flow rate through the pipe.  
- **`start_node`** (`Optional[Any]`): Start node (set externally in networks).  
- **`end_node`** (`Optional[Any]`): End node (set externally in networks).  

---

## **Methods**

**`cross_sectional_area()`**
Returns the internal cross-sectional area of the pipe.  

**Returns:**  
- `Variable`: Area in square meters (`m²`), or `None` if no internal diameter is defined.

---

**`surface_area()`**
Returns the external surface area of the pipe, on the outside diameter of the nominal size.  

**Returns:**  
- `Variable`: Surface area in square meters (`m²`), or `None` if no nominal diameter is defined.

---

**`pressure_difference()`**
Computes the pressure difference between inlet and outlet.  

**Returns:**  
- `Pressure`: ΔP = Inlet - Outlet, or `None` if pressures are not defined.

---

**`to_dict()`**
Exports all key pipe data as a dictionary.  

**Returns:**  
- `Dict[str, Any]`: Dictionary of all pipe attributes and calculated values.

---

**`calculate()`**
Compatibility hook for PipelineEngine. Returns the pipe data dictionary.  

**Returns:**  
- `Dict[str, Any]`: Same as `to_dict()`.

---

## **Examples**

```python
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, Pressure, VolumetricFlowRate

# Create a pipe with specified dimensions and pressures
pipe = Pipe(
    name="P-101",
    nominal_diameter=Diameter(4, "in"),   # NPS 4, STD bore 102.26 mm
    length=Length(5.0, "m"),
    inlet_pressure=Pressure(3.0, "bar"),
    outlet_pressure=Pressure(2.8, "bar"),
    flow_rate=VolumetricFlowRate(0.01, "m3/s")
)

print(pipe.cross_sectional_area())
print(pipe.pressure_difference())
print(pipe.to_dict())
```

---
