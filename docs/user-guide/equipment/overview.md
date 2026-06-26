# ProcessPI Equipment Overview

The **ProcessPI Equipment Module** provides a comprehensive collection
of engineering models for the design, sizing, rating, analysis, and
performance evaluation of process equipment used throughout the
chemical, petrochemical, oil & gas, pharmaceutical, food, water
treatment, and power industries.

Built around real engineering principles, the module enables engineers,
students, and researchers to perform reliable equipment calculations
using a consistent, unit-aware Python interface. Every equipment model
is designed to integrate seamlessly with the ProcessPI ecosystem,
allowing interaction with process streams, thermodynamic properties,
fluid calculations, and engineering utilities.

------------------------------------------------------------------------

## Capabilities

### Equipment Design

-   Perform preliminary and detailed equipment sizing.
-   Design equipment using established engineering correlations.
-   Support thermal and hydraulic design calculations.
-   Generate engineering design reports.
-   Evaluate equipment under multiple operating conditions.

### Equipment Rating

-   Analyze existing equipment performance.
-   Calculate operating capacities and efficiencies.
-   Compare design versus actual operating conditions.
-   Identify bottlenecks and performance limitations.

### Performance Analysis

-   Calculate heat duties, pressure drops, flow characteristics, and
    operating parameters.
-   Perform steady-state engineering evaluations.
-   Validate process operating conditions.
-   Support debottlenecking and optimization studies.

### Engineering Utilities

-   Automatic SI and Imperial unit conversion.
-   Structured calculation results.
-   Engineering warnings and validation checks.
-   Modular architecture for custom equipment development.
-   Integration with ProcessPI Streams, Components, Fluids, and
    Calculation Engine.

------------------------------------------------------------------------

## Available Equipment Categories

### Heat Exchangers

Models for thermal equipment used in heat transfer applications.

Includes support for: - Shell & Tube Heat Exchangers - Double Pipe Heat
Exchangers - Plate Heat Exchangers - Air-Cooled Heat Exchangers -
Condensers - Evaporators - Reboilers

Typical calculations include: - Heat duty - Overall heat transfer
coefficient - Log Mean Temperature Difference (LMTD) - Effectiveness-NTU
methods - Pressure drop - Thermal rating

------------------------------------------------------------------------

### Pressure Vessels

Utilities for vessel geometry and engineering calculations.

Includes: - Horizontal Pressure Vessels - Vertical Pressure Vessels -
Storage Tanks - Vessel Geometry - Volume Calculations

Typical calculations include: - Total volume - Liquid volume - Wetted
area - Vessel dimensions - Liquid level estimation

------------------------------------------------------------------------

### Separation Equipment

Engineering models for common process separation units.

Includes: - Flash Drums - Knock-Out Drums - Gas-Liquid Separators -
Liquid-Liquid Separators - Decanters - Cyclone Separators

------------------------------------------------------------------------

### Rotating Equipment

Performance calculations for rotating machinery.

Includes: - Pumps - Compressors - Blowers - Fans - Turbines

Typical calculations include: - Hydraulic power - Shaft power -
Efficiency - NPSH - Performance curves

------------------------------------------------------------------------

### Mass Transfer Equipment

Models for mass transfer operations.

Includes: - Distillation Columns - Absorption Columns - Stripping
Columns - Packed Columns - Tray Columns

Future capabilities will include tray hydraulics, packing correlations,
flooding analysis, and column sizing.

------------------------------------------------------------------------

### Mixing & Agitation

Calculations for mixing systems and stirred vessels.

Includes: - Agitated Tanks - Mixing Power - Impeller Selection -
Agitator Sizing - Power Number correlations

------------------------------------------------------------------------

## Module Integration

The Equipment Module is designed to work seamlessly with other ProcessPI
modules.

-   **Streams Module** for material and energy stream connections.
-   **Components Module** for physical property calculations.
-   **Fluids Module** for fluid properties and hydraulics.
-   **Calculations Module** for reusable engineering calculations.
-   **Units Module** for automatic unit conversion.

------------------------------------------------------------------------

## Design Philosophy

Every equipment model follows the same engineering-first approach:

-   Object-oriented architecture
-   Consistent API across equipment classes
-   Automatic unit handling
-   Engineering validation
-   Extensible design
-   Production-ready calculations
-   Clear, structured output suitable for reporting

This consistency makes it easy to move from one equipment type to
another without learning a different workflow.

------------------------------------------------------------------------

## Future Development

The Equipment Module will continue to expand with:

-   Mechanical design utilities
-   Cost estimation methods
-   Equipment selection tools
-   Design code support
-   Optimization algorithms
-   Equipment networks
-   Interactive engineering reports
-   Additional industrial equipment models

The goal is to provide a complete open-source engineering toolkit
capable of supporting the majority of process equipment calculations
encountered in industrial practice.
