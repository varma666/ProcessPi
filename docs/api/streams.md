# `processpi.streams` API

## Overview

Material or energy stream object for equipment and flowsheet integration.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.streams.__init__`

**Source:** `processpi/streams/__init__.py`

**Purpose:** Material or energy stream object for equipment and flowsheet integration.

No public classes or functions discovered in this module.

### `processpi.streams.energy`

**Source:** `processpi/streams/energy.py`

**Purpose:** Material or energy stream object for equipment and flowsheet integration.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `EnergyStream` | `EnergyStream(self, name: str)` | Represents an energy stream (heat or work transfer). Can bind to equipment and log Q/W duties automatically. Notes ----- * Positive duty = energy input (to equipment) * Negative duty = energy output (from equipment) * Duties are stored with units (`Power`) to ensure consistency. | `bind_equipment()`, `record()`, `total_duty()` |

##### `EnergyStream`

Represents an energy stream (heat or work transfer). Can bind to equipment and log Q/W duties automatically. Notes ----- * Positive duty = energy input (to equipment) * Negative duty = energy output (from equipment) * Duties are stored with units (`Power`) to ensure consistency.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `bind_equipment` | `bind_equipment(self, equipment)` | Optionally keep reference to equipment if needed later. |
| `record` | `record(self, duty: Union[float, Power], tag: str, equipment: str)` | Log an energy duty. Parameters ---------- duty : float \| Power Energy duty (W). If float is given, assumed in watts. tag : str Label such as 'Q_in', 'Q_out', 'W_in', 'W_out'. equipment : str Name of equipment associated with this duty. |
| `total_duty` | `total_duty(self, tag: Optional[str]=None)` | Return cumulative duty as a Power object. Optionally filter by tag. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.streams.material`

**Source:** `processpi/streams/material.py`

**Purpose:** Material or energy stream object for equipment and flowsheet integration.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `MaterialStream` | `MaterialStream(self, name: str, component: Optional[object]=None, pressure: Optional[Pressure]=None, temperature: Optional[Temperature]=None, density: Optional[Density]=None, specific_heat: Optional[SpecificHeat]=None, flow_rate: Optional[VolumetricFlowRate]=None, mass_flow: Optional[MassFlowRate]=None, molar_flow: Optional[MolarFlowRate]=None, composition: Optional[Dict[str, float]]=None, basis: str='mole', molecular_weights: Optional[Dict[str, float]]=None, phase: Optional[str]=None)` | Represents a process material stream with thermodynamic state and composition information. Supports two initialization modes: ----------------------------------- 1) Component-based: from processpi.components import Water s1 = MaterialStream("Hot Water", component=Water(), temperature=Temperature(350, "K"), mass_flow=MassFlowRate(2, "kg/s")) 2) Manual property-based: s2 = MaterialStream("Custom Fluid", temperature=Temperature(350, "K"), pressure=Pressure(2, "bar"), density=Density(1000, "kg/m3"), cp=HeatCapacity(4200, "J/kg-K"), flow_rate=VolumetricFlowRate(0.001, "m3/s")) | `set_composition()`, `mass_flow()`, `molar_flow()`, `avg_mw()`, `copy()` |

##### `MaterialStream`

Represents a process material stream with thermodynamic state and composition information. Supports two initialization modes: ----------------------------------- 1) Component-based: from processpi.components import Water s1 = MaterialStream("Hot Water", component=Water(), temperature=Temperature(350, "K"), mass_flow=MassFlowRate(2, "kg/s")) 2) Manual property-based: s2 = MaterialStream("Custom Fluid", temperature=Temperature(350, "K"), pressure=Pressure(2, "bar"), density=Density(1000, "kg/m3"), cp=HeatCapacity(4200, "J/kg-K"), flow_rate=VolumetricFlowRate(0.001, "m3/s"))

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `set_composition` | `set_composition(self, components: Dict[str, float], basis: str='mole')` | No source docstring provided. |
| `mass_flow` | `mass_flow(self)` | No source docstring provided. |
| `molar_flow` | `molar_flow(self)` | No source docstring provided. |
| `avg_mw` | `avg_mw(self)` | Average molecular weight (kg/mol) from composition + MW dict |
| `copy` | `copy(self, name: str)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.
