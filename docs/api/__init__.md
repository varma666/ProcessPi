# `processpi.__init__` API

## Overview

ProcessPI module.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.__init__`

**Source:** `processpi/__init__.py`

**Purpose:** ProcessPI: Chemical & Process Engineering Tools ============================================== A Python library for process engineers to: - Perform fluid mechanics and hydraulic calculations - Simulate and visualize pipeline networks - Manage chemical and physical properties - Handle engineering units and conversions

No public classes or functions discovered in this module.
