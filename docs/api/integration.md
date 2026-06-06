# `processpi.integration` API

## Overview

Flowsheet integration layer for connecting equipment and streams.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.integration.__init__`

**Source:** `processpi/integration/__init__.py`

**Purpose:** Integration utilities such as flowsheet management.

No public classes or functions discovered in this module.

### `processpi.integration.flowsheet`

**Source:** `processpi/integration/flowsheet.py`

**Purpose:** Flowsheet integration layer for connecting equipment and streams.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Flowsheet` | `Flowsheet(self, name: str)` | A flowsheet manager for sequential simulation. Responsibilities: - Hold equipment + streams - Define explicit connections - Auto-build execution order from connections - Run equipment automatically - Collect results for summary | `add_equipment()`, `add_material_stream()`, `add_energy_stream()`, `connect()`, `run()`, `solve_sequential()`, `summary()` |

##### `Flowsheet`

A flowsheet manager for sequential simulation. Responsibilities: - Hold equipment + streams - Define explicit connections - Auto-build execution order from connections - Run equipment automatically - Collect results for summary

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `add_equipment` | `add_equipment(self, unit: Equipment)` | No source docstring provided. |
| `add_material_stream` | `add_material_stream(self, stream: MaterialStream)` | No source docstring provided. |
| `add_energy_stream` | `add_energy_stream(self, stream: EnergyStream)` | No source docstring provided. |
| `connect` | `connect(self, *args)` | Connect stream between units using named ports. Preferred signature: connect(stream, from_unit, from_port, to_unit, to_port) Backward-compatible signature: connect(stream, to_unit, to_port) |
| `run` | `run(self)` | Topologically sorted flowsheet solve. |
| `solve_sequential` | `solve_sequential(self)` | Simple sequential solve in registration order. |
| `summary` | `summary(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.
