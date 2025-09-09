# API Reference

This section documents the main classes and functions in **ProcessPI**.

## Units
- `Velocity(value, unit)`
- `Diameter(value, unit)`
- `Density(value, unit)`
- `Viscosity(value, unit)`
- `Temperature(value, unit)`
- `Pressure(value, unit)`
- `SpecificHeat(value, unit)`
- `ThermalConductivity(value, unit)`
- `HeatFlux(value, unit)`
- `HeatTransferCoefficient(value, unit)`
- `HeatOfVaporization(value, unit)`
- `Time(value, unit)`
- `Mass(value, unit)`
- `MassFlowRate(value, unit)`
- `MolarFlowRate(value, unit)`
- `Volume(value, unit)`
- `VolumetricFlowRate(value, unit)`

## Components
- `Acetone(temperature=Temperature(...))`
- `Water(temperature=Temperature(...))`
- `Toluene(temperature=Temperature(...))`
- `Methanol(temperature=Temperature(...))`
- `OrganicLiquid(...)`
- `InorganicLiquid(...)`
- `Gas(...)`
- `Oil(...)`
- `Vapor(...)`

## Calculations
- `CalculationEngine()`
  - `.calculate("fluid_velocity", volumetric_flow_rate, diameter)`
  - `.calculate("reynolds_number", density, velocity, diameter, viscosity)`
  - `.calculate("friction_factor_colebrookwhite", diameter, roughness, reynolds_number)`
  - `.calculate("pressure_drop_darcy", friction_factor, length, diameter, density, velocity)`
  - `.calculate("pressure_drop_hazen_williams", length, flow_rate, diameter, density, coefficient)`

## Pipelines
- `PipelineNetwork(...)`
- `.add_pipe(start, end, diameter, length, roughness)`
- `.describe()`
- `.schematic()`
- `.visualize_network()`
