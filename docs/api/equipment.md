# `processpi.equipment` API

## Overview

ProcessPI module.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.equipment.__init__`

**Source:** `processpi/equipment/__init__.py`

**Purpose:** Equipment package for ProcessPI v0.3.0.

No public classes or functions discovered in this module.

### `processpi.equipment.base`

**Source:** `processpi/equipment/base.py`

**Purpose:** ProcessPI module.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PortMap` | `PortMap(self, names: Optional[Iterable[str]]=None)` | Dict-like port container with backward compatibility for list-style indexing. - Preferred usage: map by port name, e.g. ``ports['in']``. - Legacy compatibility: integer index access remains supported, e.g. ``ports[0]``. - Iteration yields stream values (legacy list-like behavior). | `add_port()`, `has_port()`, `values_ordered()` |
| `Equipment` | `Equipment(self, name: str, inlet_ports: int=0, outlet_ports: int=0, inlet_names: Optional[List[str]]=None, outlet_names: Optional[List[str]]=None)` | Base class for all equipment units. Canonical interface: - self.inlets: dict[str, MaterialStream\|None] - self.outlets: dict[str, MaterialStream\|None] Backward compatibility: - list-style indexing (e.g., ``self.inlets[0]``) still works via PortMap. | `connect_inlet()`, `connect_outlet()`, `attach_stream()` |

##### `PortMap`

Dict-like port container with backward compatibility for list-style indexing. - Preferred usage: map by port name, e.g. ``ports['in']``. - Legacy compatibility: integer index access remains supported, e.g. ``ports[0]``. - Iteration yields stream values (legacy list-like behavior).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `add_port` | `add_port(self, name: str)` | No source docstring provided. |
| `has_port` | `has_port(self, name: str)` | No source docstring provided. |
| `values_ordered` | `values_ordered(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `Equipment`

Base class for all equipment units. Canonical interface: - self.inlets: dict[str, MaterialStream|None] - self.outlets: dict[str, MaterialStream|None] Backward compatibility: - list-style indexing (e.g., ``self.inlets[0]``) still works via PortMap.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `connect_inlet` | `connect_inlet(self, port_name: str, stream: MaterialStream)` | No source docstring provided. |
| `connect_outlet` | `connect_outlet(self, port_name: str, stream: MaterialStream)` | No source docstring provided. |
| `attach_stream` | `attach_stream(self, stream: MaterialStream, port: Literal['inlet', 'outlet'], index: int=0)` | Backward-compatible stream attach by indexed port. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.__init__`

**Source:** `processpi/equipment/heatexchangers/__init__.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

No public classes or functions discovered in this module.

### `processpi.equipment.heatexchangers.base`

**Source:** `processpi/equipment/heatexchangers/base.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatExchangerBaseMixin` | `HeatExchangerBaseMixin(...)` | No source docstring provided. See module purpose and examples. | — |
| `HeatExchanger` | `HeatExchanger(self, hot_in: MaterialStream, cold_in: MaterialStream, hot_out: Optional[MaterialStream]=None, cold_out: Optional[MaterialStream]=None, **specs: Any)` | No source docstring provided. See module purpose and examples. | `heat_duty()`, `lmtd()`, `area()`, `overall_u()`, `design()` |

##### `HeatExchangerBaseMixin`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `HeatExchanger`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `heat_duty` | `heat_duty(self, hot: Dict[str, float], cold: Dict[str, float])` | No source docstring provided. |
| `lmtd` | `lmtd(self, th_in: float, th_out: float, tc_in: float, tc_out: float)` | No source docstring provided. |
| `area` | `area(self, q_w: float, u: float, dtlm: float)` | No source docstring provided. |
| `overall_u` | `overall_u(self, h_tube: float, h_shell: float, fouling_factor: float=0.0)` | No source docstring provided. |
| `design` | `design(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.bell_delaware`

**Source:** `processpi/equipment/heatexchangers/bell_delaware.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `BellDelawareHX` | `BellDelawareHX(...)` | No source docstring provided. See module purpose and examples. | `design()` |

##### `BellDelawareHX`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `design` | `design(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.condenser`

**Source:** `processpi/equipment/heatexchangers/condenser.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CondenserHX` | `CondenserHX(self, *args: Any, method: str='kern', **kwargs: Any)` | Production-oriented shell-and-tube condenser with phase-change safeguards. | `design()`, `rate()` |

##### `CondenserHX`

Production-oriented shell-and-tube condenser with phase-change safeguards.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `design` | `design(self)` | No source docstring provided. |
| `rate` | `rate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.double_pipe`

**Source:** `processpi/equipment/heatexchangers/double_pipe.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `DoublePipeHX` | `DoublePipeHX(...)` | No source docstring provided. See module purpose and examples. | `design()`, `rate()` |

##### `DoublePipeHX`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `design` | `design(self)` | No source docstring provided. |
| `rate` | `rate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.engine`

**Source:** `processpi/equipment/heatexchangers/engine.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatExchangerResults` | `HeatExchangerResults(...)` | No source docstring provided. See module purpose and examples. | `summary()`, `detailed_summary()`, `trace()`, `debug_summary()` |
| `HeatExchangerEngine` | `HeatExchangerEngine(self, name: Optional[str]=None, method: str='kern', **kwargs: Any)` | No source docstring provided. See module purpose and examples. | `fit()`, `run()`, `summary()`, `results()` |

##### `HeatExchangerResults`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `summary` | `summary(self)` | No source docstring provided. |
| `detailed_summary` | `detailed_summary(self)` | No source docstring provided. |
| `trace` | `trace(self)` | No source docstring provided. |
| `debug_summary` | `debug_summary(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `HeatExchangerEngine`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `fit` | `fit(self, hot_in: MaterialStream, cold_in: MaterialStream, hot_out: Optional[MaterialStream]=None, cold_out: Optional[MaterialStream]=None, hx_type: Optional[str]=None, **kwargs: Any)` | No source docstring provided. |
| `run` | `run(self)` | No source docstring provided. |
| `summary` | `summary(self)` | No source docstring provided. |
| `results` | `results(self)` | Return design results |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.evaporator`

**Source:** `processpi/equipment/heatexchangers/evaporator.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `EvaporatorHX` | `EvaporatorHX(self, *args: Any, method: str='kern', **kwargs: Any)` | No source docstring provided. See module purpose and examples. | `design()`, `rate()` |

##### `EvaporatorHX`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `design` | `design(self)` | No source docstring provided. |
| `rate` | `rate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.reboiler`

**Source:** `processpi/equipment/heatexchangers/reboiler.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ReboilerHX` | `ReboilerHX(self, *args: Any, method: str='kern', **kwargs: Any)` | Shell-and-tube reboiler built from Evaporator phase-change architecture. | `design()`, `rate()` |

##### `ReboilerHX`

Shell-and-tube reboiler built from Evaporator phase-change architecture.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `design` | `design(self)` | No source docstring provided. |
| `rate` | `rate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.shell_and_tube`

**Source:** `processpi/equipment/heatexchangers/shell_and_tube.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ShellAndTubeHX` | `ShellAndTubeHX(self, *args: Any, method: str='kern', **kwargs: Any)` | No source docstring provided. See module purpose and examples. | `rate()`, `design()` |

##### `ShellAndTubeHX`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `rate` | `rate(self)` | No source docstring provided. |
| `design` | `design(self)` | Main design entry point for Shell & Tube HX. Supports: - Kern method - Bell-Delaware method Returns: Dict[str, Any] |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.equipment.heatexchangers.standards`

**Source:** `processpi/equipment/heatexchangers/standards.py`

**Purpose:** Heat-exchanger equipment models for thermal sizing, hydraulic checks, rating, and phase-change services.

#### Functions

| Function | Signature | Description |
| --- | --- | --- |
| `get_u_range` | `get_u_range(hx_type: str, service_type: str, hot_type: str, cold_type: str)` | No source docstring provided. |
| `get_velocity_range` | `get_velocity_range(component)` | No source docstring provided. |
| `select_tube_configuration` | `select_tube_configuration(area_required, hot, cold)` | No source docstring provided. |
| `tube_length_select` | `tube_length_select(tube_length, ld)` | No source docstring provided. |
| `get_fouling_factor` | `get_fouling_factor(fluid_key: str, velocity: float | None=None, temperature: float | None=None, database: dict | None=None, debug: bool=True)` | Returns fouling factor based on ProcessPI fouling standards. Parameters ---------- fluid_key : str Fluid/service lookup key. Example: "water" "treated_water" "hydrocarbons" "crude" velocity : float, optional Fluid velocity in m/s. temperature : float, optional Fluid temperature in °C. database : dict, optional Fouling factor database. debug : bool Print debug messages. Returns ------- float Fouling factor in m2.K/W |
