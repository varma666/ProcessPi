# `processpi.cli` API

## Overview

ProcessPI module.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.cli`

**Source:** `processpi/cli.py`

**Purpose:** Command line interface for ProcessPI.

#### Functions

| Function | Signature | Description |
| --- | --- | --- |
| `build_parser` | `build_parser()` | No source docstring provided. |
| `main` | `main(argv: list[str] | None=None)` | No source docstring provided. |
