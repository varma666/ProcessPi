# Heat Exchanger Engineering Guide

## Overview

ProcessPI implements heat-exchanger workflows under `processpi.equipment.heatexchangers` and supporting calculation primitives under `processpi.calculations.heat_transfer`. The implemented equipment layer is centered on `HeatExchangerEngine`, which selects an exchanger class, runs sizing or rating logic, and returns `HeatExchangerResults` with engineering summaries, detailed data, traces, warnings, and recommendations.

## Implemented exchanger models

| Model | Import path | Purpose | Status |
| --- | --- | --- | --- |
| Shell-and-tube | `processpi.equipment.heatexchangers.shell_and_tube.ShellAndTubeHX` | Kern-style thermal sizing/rating with geometry, velocity, pressure-drop, L/D, fouling, and feasibility checks. | Implemented |
| Condenser | `processpi.equipment.heatexchangers.condenser.CondenserHX` | Shell-and-tube condenser with latent duty, near-isothermal hot side, condensation HTC, orientation effects, and optional vertical static head. | Implemented |
| Evaporator | `processpi.equipment.heatexchangers.evaporator.EvaporatorHX` | Phase-change evaporator service derived from shell-and-tube logic. | Implemented |
| Reboiler | `processpi.equipment.heatexchangers.reboiler.ReboilerHX` | Reboiler-style service derived from evaporator behavior. | Implemented |
| Double pipe | `processpi.equipment.heatexchangers.double_pipe.DoublePipeHX` | Small-duty exchanger sizing/rating. | Implemented |
| Bell-Delaware | `processpi.equipment.heatexchangers.bell_delaware.BellDelawareHX` and `method="bell_delaware"` | Method name is accepted by the engine; correction-factor helper calculations are not a full standalone `BellDelawareHX.design()` implementation. | Partial/future-reserved |

!!! warning "Bell-Delaware scope"
    `HeatExchangerEngine(method="bell_delaware")` is accepted and routes shell-and-tube service through the current shell-and-tube model. The standalone `BellDelawareHX.design()` class raises `NotImplementedError`, so documentation should not present a complete TEMA/Bell-Delaware design package as implemented.

## Sizing workflow

1. Create `MaterialStream` objects for hot and cold inlet streams. Provide component, temperature, pressure, phase, and either mass flow or flow rate plus density.
2. Provide at least one thermal specification: hot outlet, cold outlet, explicit `Q`, or phase-change data such as `latent_heat`.
3. Choose `hx_type` explicitly or allow `HeatExchangerEngine` to infer it:
   - vapor hot inlet to liquid hot outlet: condenser;
   - cold outlet vapor: reboiler;
   - small flows: double pipe;
   - otherwise shell-and-tube.
4. The exchanger estimates or validates heat duty, outlet temperatures, LMTD, correction factor, corrected LMTD, assumed U, required area, tube geometry, shell geometry, velocities, heat-transfer coefficients, calculated U, and pressure drops.
5. The result object exposes:
   - `summary()` for a readable report;
   - `detailed_summary()` for the raw dictionary;
   - `trace()` for grouped engineering calculations;
   - `debug_summary()` for convergence, U, pressure-drop, and warning diagnostics.

## Engineering theory

### LMTD

The log mean temperature difference is used when the driving force changes along an exchanger:

\[
\Delta T_{lm}=\frac{\Delta T_1-\Delta T_2}{\ln(\Delta T_1/\Delta T_2)}
\]

ProcessPI uses the `LMTD` calculation primitive and stabilizes near-isothermal phase-change cases when terminal differences become too small.

### Correction factors

Shell-and-tube exchangers with multiple passes deviate from ideal countercurrent flow. `ShellAndTubeHX` evaluates one-shell and two-shell-pass correction factor formulas from R/S temperature ratios and searches common shell/tube pass combinations. If no candidate reaches the practical threshold used by the code, the result includes warnings and recommendations.

### Tube-side HTC

Tube-side convection uses Reynolds, Prandtl, and Nusselt relationships. For turbulent tube flow, ProcessPI includes Dittus-Boelter-style support via `DittusBoelter` and converts Nusselt number to heat-transfer coefficient with `ConvectiveH`:

\[
h=\frac{Nu\,k}{D}
\]

### Shell-side HTC

The shell-side path uses Kern-style shell Nusselt support through `KernShellNu`. Inputs are based on shell-equivalent geometry, mass velocity, fluid properties, baffle spacing, and tube layout assumptions. This is appropriate for preliminary engineering and screening, not a replacement for vendor thermal design.

### Condensation coefficients

`CondenserHX` calculates latent duty with `LatentDuty` and estimates condensation HTC with `CondensationHTC`. It applies orientation and condensing-side factors, and clips the coefficient to practical bounds to avoid unrealistic preliminary designs.

### Reynolds, Prandtl, and Nusselt numbers

- Reynolds number compares inertial and viscous forces and drives laminar/turbulent regime decisions.
- Prandtl number compares momentum and thermal diffusivity.
- Nusselt number converts dimensionless convection correlations into HTC.

The reusable primitives are documented in the heat-transfer API reference.

### Pressure-drop and hydraulic constraints

Tube and shell pressure drops use Darcy-style pressure-drop primitives, flow area estimates, tube-pass effects, shell velocity estimates, and practical velocity ranges by side/service. Results include `tube_dp`, `shell_dp`, `tube_velocity`, and `shell_velocity`. Treat outputs as preliminary hydraulic screening until project-specific fittings, nozzles, maldistribution, vibration, and vendor geometry are included.

### Fouling considerations

`get_fouling_factor()` in `processpi.equipment.heatexchangers.standards` provides a standards-helper lookup by fluid key, with optional velocity and temperature context. Overall U combines tube film, fouling resistance, and shell film resistances. Users can also provide explicit fouling assumptions through exchanger specs.

### Feasibility checks and optimization

The shell-and-tube workflow records warnings for nonphysical terminal temperatures, low correction factors, geometry clipping, L/D limits, velocity constraints, tube-count caps, and pressure-drop concerns. These diagnostics are returned with the result rather than hidden.

## Practical examples

### Water cooler

```python
from processpi.streams.material import MaterialStream
from processpi.units import Density, MassFlowRate, Pressure, SpecificHeat, Temperature
from processpi.equipment.heatexchangers.engine import HeatExchangerEngine

hot = MaterialStream(
    name="hot_water_in",
    temperature=Temperature(80, "C"),
    pressure=Pressure(2, "bar"),
    density=Density(971.8, "kg/m3"),
    specific_heat=SpecificHeat(4190, "J/kgK"),
    mass_flow=MassFlowRate(2.0, "kg/s"),
    phase="liquid",
)

cold = MaterialStream(
    name="cooling_water_in",
    temperature=Temperature(25, "C"),
    pressure=Pressure(2, "bar"),
    density=Density(997, "kg/m3"),
    specific_heat=SpecificHeat(4180, "J/kgK"),
    mass_flow=MassFlowRate(3.0, "kg/s"),
    phase="liquid",
)

hot_out = hot.copy("hot_water_out")
hot_out.temperature = Temperature(45, "C")

result = (
    HeatExchangerEngine(method="kern")
    .fit(hot_in=hot, cold_in=cold, hot_out=hot_out, hx_type="shell_and_tube")
    .run()
)
print(result.summary())
```

### Condenser

```python
from processpi.streams.material import MaterialStream
from processpi.units import Density, MassFlowRate, Pressure, SpecificHeat, Temperature
from processpi.equipment.heatexchangers.engine import HeatExchangerEngine

steam = MaterialStream(
    name="steam_in",
    temperature=Temperature(100, "C"),
    pressure=Pressure(1.0, "bar"),
    density=Density(0.60, "kg/m3"),
    specific_heat=SpecificHeat(2010, "J/kgK"),
    mass_flow=MassFlowRate(0.5, "kg/s"),
    phase="vapor",
)
condensate = steam.copy("condensate_out")
condensate.phase = "liquid"
condensate.temperature = Temperature(95, "C")
condensate.density = Density(962, "kg/m3")

cooling = MaterialStream(
    name="cooling_water",
    temperature=Temperature(25, "C"),
    pressure=Pressure(2, "bar"),
    density=Density(997, "kg/m3"),
    specific_heat=SpecificHeat(4180, "J/kgK"),
    mass_flow=MassFlowRate(5.0, "kg/s"),
    phase="liquid",
)

result = HeatExchangerEngine().fit(
    hot_in=steam,
    cold_in=cooling,
    hot_out=condensate,
    hx_type="condenser",
    latent_heat=2_257_000,
    condensing_side="shell",
    orientation="horizontal",
).run()
```

### Reboiler-style service

```python
result = HeatExchangerEngine().fit(
    hot_in=steam,
    cold_in=process_liquid,
    cold_out=process_vapor,
    hx_type="reboiler",
    latent_heat=350_000,
    latent_side="cold",
).run()
```

### Rating an existing exchanger

```python
result = HeatExchangerEngine(method="kern").fit(
    hot_in=hot,
    cold_in=cold,
    hot_out=hot_out,
    hx_type="shell_and_tube",
    tube_od=0.019,
    tube_id=0.016,
    tube_length=6.0,
    tube_count=120,
    tube_passes=2,
    shell_passes=1,
    shell_diameter=0.45,
).run()

print(result.detailed_summary()["U_calculated"])
print(result.trace())
```

### Pressure-drop estimation

```python
details = result.detailed_summary()
print("Tube-side ΔP:", details["tube_dp"].to("bar"))
print("Shell-side ΔP:", details["shell_dp"].to("bar"))
```

## Limitations

- Heat-exchanger results are preliminary engineering calculations.
- TEMA mechanical design, vibration checks, nozzle losses, detailed maldistribution, two-phase pressure-drop maps, and vendor rating are not complete.
- `BellDelawareHX.design()` is explicitly future-reserved.
- Stream properties are only as accurate as the supplied components and user overrides.
