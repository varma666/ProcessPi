# HeatExchanger Engine

The **`HeatExchangerEngine`** is the central interface for all heat
exchanger calculations in **ProcessPI**. It provides a unified workflow
for designing, rating, and analyzing multiple classes of heat exchangers
while maintaining a consistent API.

The engine automatically selects an appropriate exchanger type when one
is not explicitly specified, performs thermal and hydraulic
calculations, validates engineering inputs, and returns structured
engineering reports suitable for design studies and troubleshooting.

------------------------------------------------------------------------

# Capabilities

## Unified Engineering Interface

-   Single API for all supported heat exchangers
-   Design and Rating modes
-   Automatic exchanger selection
-   Multiple design methodologies
-   Structured engineering reports
-   Automatic unit handling
-   Engineering validation and warnings

------------------------------------------------------------------------

## Supported Heat Exchanger Types

The engine currently supports:

-   Shell & Tube Heat Exchangers
-   Double Pipe Heat Exchangers
-   Condensers
-   Evaporators
-   Reboilers

Future releases will add Plate, Air-Cooled, Spiral and Compact Heat
Exchangers.

------------------------------------------------------------------------

# Design Methodologies

## Kern Method

Suitable for preliminary thermal design and sizing.

## Bell--Delaware Method

Improved shell-side analysis accounting for leakage, bypass streams and
shell-side correction factors.

------------------------------------------------------------------------

# Engine Workflow

## `fit()`

Configures the engine by accepting inlet and outlet material streams
together with equipment specifications.

### Parameters

-   `hot_in`
-   `cold_in`
-   `hot_out`
-   `cold_out`
-   `hx_type`
-   Additional design specifications

### Functionality

-   Validates MaterialStream objects
-   Stores process specifications
-   Selects calculation method
-   Supports Design and Rating workflows
-   Enables method chaining

Returns:

``` python
HeatExchangerEngine
```

------------------------------------------------------------------------

## Automatic Heat Exchanger Selection

When `hx_type` is omitted, the engine automatically determines the most
appropriate exchanger.

Decision logic includes:

-   Vapor → Liquid → Condenser
-   Liquid → Vapor → Reboiler
-   Small flowrates → Double Pipe
-   Otherwise → Shell & Tube

This allows rapid preliminary studies with minimal user input.

------------------------------------------------------------------------

## `run()`

Executes the complete engineering calculation.

### Design Mode

Performs:

-   Heat duty calculations
-   LMTD evaluation
-   Overall heat transfer coefficient estimation
-   Area sizing
-   Tube count estimation
-   Tube length estimation
-   Tube and shell velocities
-   Tube-side pressure drop
-   Shell-side pressure drop
-   Engineering assessment
-   Design recommendations

### Rating Mode

Evaluates existing equipment using known geometry.

Required geometry typically includes:

-   Tube OD
-   Tube ID
-   Tube Length

Returns a `HeatExchangerResults` object.

------------------------------------------------------------------------

## `summary()`

Produces a concise engineering report including:

-   Heat Duty
-   Area
-   U Value
-   Velocities
-   Pressure Drops
-   Tube Count
-   Tube Length
-   Engineering Status
-   Assessment
-   Warnings
-   Recommendations

------------------------------------------------------------------------

# HeatExchangerResults

The engine returns a structured results object providing several
reporting utilities.

## `summary()`

Human-readable engineering report.

## `detailed_summary()`

Returns the complete calculation dictionary.

## `trace()`

Displays the engineering calculation trace grouped into sections:

-   Thermal
-   Geometry
-   Hydraulics
-   Dimensionless Numbers
-   Phase Change
-   General

Useful for debugging and validation.

## `debug_summary()`

Returns diagnostic information including:

-   Solver status
-   Iteration count
-   U-values
-   Velocities
-   Pressure drops
-   Warning count
-   Optimization actions

------------------------------------------------------------------------

# Engineering Capabilities

Current capabilities include:

## Thermal Design

-   Heat Duty
-   LMTD
-   Overall Heat Transfer Coefficient
-   Required Area
-   Heat Balance

## Hydraulic Design

-   Tube-side velocity
-   Shell-side velocity
-   Tube pressure drop
-   Shell pressure drop

## Geometry

-   Tube sizing
-   Tube count
-   Tube length
-   Bundle sizing

## Phase Change

-   Condensation
-   Evaporation
-   Reboiling

## Engineering Validation

The engine performs automatic validation and generates:

-   Engineering warnings
-   Design assessments
-   Recommendations
-   Calculation trace

------------------------------------------------------------------------

# Integration

The HeatExchangerEngine integrates directly with:

-   Streams Module
-   Components Module
-   Units Module
-   Calculation Engine
-   Equipment Module

Material properties are obtained directly from `MaterialStream` objects,
allowing realistic process simulations.

------------------------------------------------------------------------

# Key Features

-   Unified API
-   Automatic exchanger selection
-   Design & Rating modes
-   Kern and Bell--Delaware methods
-   Multiple exchanger types
-   Engineering validation
-   Structured reporting
-   Calculation tracing
-   Debug summaries
-   Unit-aware calculations
-   Extensible architecture

------------------------------------------------------------------------

# Current Limitations

-   Steady-state calculations only
-   Single-pass design focus
-   No mechanical design calculations
-   No vibration analysis
-   No fouling lifecycle prediction
-   Limited optimization algorithms

------------------------------------------------------------------------

# Future Roadmap

Short Term

-   Plate Heat Exchangers
-   Air-Cooled Heat Exchangers
-   Extended optimization

Mid Term

-   Mechanical design utilities
-   Cost estimation
-   Automatic exchanger selection improvements

Long Term

-   Multi-stream exchangers
-   Dynamic simulation
-   Fouling prediction
-   Pinch-analysis integration
-   AI-assisted design optimization

------------------------------------------------------------------------

# Example

``` python
from processpi.equipment import HeatExchangerEngine

hx = HeatExchangerEngine(method="kern")

hx.fit(
    hot_in=hot_stream,
    cold_in=cold_stream,
    mode="design"
)

results = hx.run()

print(results.summary())
```
