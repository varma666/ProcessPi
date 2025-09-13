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

### **Parameters**
- **`name`** (`str`): Unique name of the pipe.  
- **`nominal_diameter`** (`Optional[Diameter]`): Nominal pipe size. If `None`, the pipe is considered a candidate for optimization.  
- **`schedule`** (`str`, default=`"STD"`): Pipe schedule.  
- **`material`** (`str`, default=`"CS"`): Pipe material.  
- **`length`** (`Optional[Length]`): Pipe length. Defaults to `1.0 m` if not provided.  
- **`inlet_pressure`** (`Optional[Pressure]`): Inlet pressure of the pipe.  
- **`outlet_pressure`** (`Optional[Pressure]`): Outlet pressure of the pipe.  
- **`internal_diameter`** (`Optional[Diameter]`): Explicit internal diameter. Overrides calculated internal diameter if given.  
- **`flow_rate`** (`Optional[VolumetricFlowRate]`): Initial flow rate for solver. Defaults to `0.001 m³/s`.  
- **`**kwargs`** (`Any`): Additional custom parameters stored in the base class.  

---

## **Attributes**
- **`is_optimization_target`** (`bool`): Whether this pipe is flagged for optimization (true if no diameter was provided).  
- **`nominal_diameter`** (`Optional[Diameter]`): Nominal pipe diameter.  
- **`schedule`** (`str`): Pipe schedule.  
- **`material`** (`str`): Pipe material.  
- **`length`** (`Length`): Pipe length.  
- **`roughness`** (`Variable`): Material roughness (from standards).  
- **`internal_diameter`** (`Optional[Diameter]`): Internal diameter.  
- **`inlet_pressure`** (`Optional[Pressure]`): Inlet pressure.  
- **`outlet_pressure`** (`Optional[Pressure]`): Outlet pressure.  
- **`flow_rate`** (`VolumetricFlowRate`): Flow rate through the pipe.  
- **`start_node`** (`Optional[Any]`): Start node (set externally in networks).  
- **`end_node`** (`Optional[Any]`): End node (set externally in networks).  

---

## **Methods**

### **`cross_sectional_area()`**
Returns the internal cross-sectional area of the pipe.  

**Returns:**  
- `Variable`: Area in square meters (`m²`), or `None` if no internal diameter is defined.

---

### **`surface_area()`**
Returns the external surface area of the pipe.  

**Returns:**  
- `Variable`: Surface area in square meters (`m²`), or `None` if no nominal diameter is defined.

---

### **`pressure_difference()`**
Computes the pressure difference between inlet and outlet.  

**Returns:**  
- `Pressure`: ΔP = Inlet - Outlet, or `None` if pressures are not defined.

---

### **`to_dict()`**
Exports all key pipe data as a dictionary.  

**Returns:**  
- `Dict[str, Any]`: Dictionary of all pipe attributes and calculated values.

---

### **`calculate()`**
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
    nominal_diameter=Diameter(0.1, "m"),
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
