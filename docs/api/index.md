# API Reference


This reference was regenerated from the Python source inventory. It is intentionally module-oriented so every public package, module, class, function, and method discovered under `processpi/` is discoverable from the documentation.

## Packages

- [__init__](./__init__.md)
- [calculations](./calculations.md)
- [cli](./cli.md)
- [components](./components.md)
- [constants](./constants.md)
- [equipment](./equipment.md)
- [integration](./integration.md)
- [pipelines](./pipelines.md)
- [streams](./streams.md)
- [units](./units.md)

## Source-of-truth audit notes

- The implemented top-level packages are `calculations`, `components`, `equipment`, `integration`, `pipelines`, `streams`, and `units`.
- Requested names such as `processpi.hx`, `processpi.thermo`, `processpi.fluids`, `processpi.hydraulics`, `processpi.piping`, `processpi.pumps`, `processpi.correlations`, `processpi.materials`, and `processpi.properties` are not implemented as importable top-level packages in this repository; equivalent capabilities live under `processpi.equipment.heatexchangers`, `processpi.calculations.*`, `processpi.pipelines.*`, and `processpi.components`.
- Public API includes class methods and module functions that do not start with an underscore; internal helper methods are intentionally excluded from the tabular reference.
