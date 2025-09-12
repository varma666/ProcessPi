# ProcessPI CalculationEngine

The `CalculationEngine` module acts as the central hub for performing calculations in the **ProcessPI** library. It provides a unified interface to execute any registered calculation by name, without needing to directly import or instantiate each calculation class.

---

Class: `CalculationEngine`

The `CalculationEngine` class maintains a registry of calculation classes and provides methods to register new calculations or execute existing ones dynamically. It is the main entry point for performing calculations across multiple domains, including fluids, heat transfer, mass transfer, thermodynamics, and reaction engineering.

## Constructor

```python
CalculationEngine()
```

**Description:**
Initializes a new `CalculationEngine` instance and loads the default calculations into the registry.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `registry` | `Dict[str, Type]` | Maps calculation names and aliases to their corresponding calculation classes. |

---

## Methods

`_load_default_calculations()`

```python
_load_default_calculations()
```

**Description:**
Private method that populates the registry with the default set of calculation classes and their aliases. Called automatically during initialization.

`register_calculation(name: str, calc_class: Type)`

```python
register_calculation(name: str, calc_class: Type)
```

**Description:**
Registers a new calculation dynamically, allowing the engine to be extended at runtime.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | String name or alias for the calculation. |
| `calc_class` | `Type` | The calculation class to register. |

**Example:**

```python
from processpi.calculations import FluidVelocity

engine = CalculationEngine()
engine.register_calculation("fluid_velocity", FluidVelocity)
```

`calculate(name: str, **kwargs) -> Any`

```python
calculate(name: str, **kwargs) -> Any
```

**Description:**
Executes a calculation by its registered name. Instantiates the class with the provided keyword arguments and returns the result.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Name of the registered calculation. |
| `**kwargs` | `Any` | Inputs to pass to the calculation class. |

**Returns:**
`Any` — Result from the calculation class.

**Raises:**

| Exception | Condition |
|-----------|-----------|
| `ValueError` | If the calculation name is not found in the registry. |

## Example

```python
from processpi.units import VolumetricFlowRate, Diameter

engine = CalculationEngine()
velocity = engine.calculate(
    "fluid_velocity",
    volumetric_flow_rate=VolumetricFlowRate(3000, "gal/min"),
    diameter=Diameter(15.5, "in")
)

print(velocity)
```

---

## Default Registered Calculations

| Name / Alias | Class |
|--------------|-------|
| `fluid_velocity`, `velocity`, `v`, `volumetric_flow_rate` | `FluidVelocity` |
| `nre`, `reynolds_number`, `re`, `reynoldsnumber` | `ReynoldsNumber` |
| `colebrook_white`, `friction_factor_colebrookwhite`, `friction_factor`, `ff` | `ColebrookWhite` |
| `pressure_drop_darcy`, `pd`, `pressure_drop` | `PressureDropDarcy` |
| `pressure_drop_fanning` | `PressureDropFanning` |
| `pressure_drop_hazen_williams` | `PressureDropHazenWilliams` |

Additional calculations can be registered dynamically as needed.

---

## Summary

The `CalculationEngine` provides:

- Centralized API for ProcessPI calculations.
- Dynamic registry for extension and alias support.
- Consistent interface for multiple engineering domains: fluids, heat transfer, mass transfer, thermodynamics, and reaction engineering.

