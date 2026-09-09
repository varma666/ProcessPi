---
title: 'ProcessPi: An Open-Source Python Library for Chemical Process Engineering Design and Simulation'
tags:
  - Python
  - chemical engineering
  - fluid mechanics
  - process simulation
  - heat transfer
  - unit operations
  - Bell-Delaware
authors:
  - name: Nadimpalli Raviteja Varma
    orcid: 0009-0007-4615-4223
    affiliation: 1
affiliations:
  - name: Independent Developer, India
    index: 1
date: 09 September 2026
bibliography: paper.bib
---

# Summary

Chemical and process engineering calculations require balancing physical property estimation, thermodynamic phase equilibrium, and detailed transport phenomena. Traditional commercial software packages (such as Aspen Plus and AVEVA PRO/II) provide comprehensive modeling suites but operate as closed-source, proprietary desktop platforms with high licensing costs and restricted programmatic extensibility. Conversely, ad-hoc engineering spreadsheets often lack strict automated testing, dimensional consistency checks, and modern version control.

`ProcessPi` is an open-source, developer-first Python library designed to bridge this divide. It provides modular, programmable calculation engines for pipeline hydraulics, unit operation rating and sizing, and physical property modeling. Built natively on Python and the scientific computing stack (NumPy, SciPy), `ProcessPi` provides automated design heuristics, dimensional validation, and calculation routines benchmarked against canonical literature, including Crane Technical Paper No. 410 and the Bell–Delaware method for shell-and-tube heat exchangers.

# Statement of Need

Modern chemical engineering workflows increasingly require programmatic integration into automated pipelines, sensitivity studies, optimization loops, and machine learning surrogates. While open-source suites like DWSIM provide comprehensive graphical flowsheeting environments, executing lightweight, standalone scripts or automated parameter sweeps often introduces unnecessary architectural overhead.

`ProcessPi` (`pip install processpi`) addresses this need by providing an idiomatic, modular Python framework featuring:
1. **Strongly Typed Engineering Units:** Explicit dimensional handling (`Length`, `MassFlowRate`, `Pressure`, `Temperature`, `HeatTransferCoefficient`) that prevents dimensional inconsistencies during calculations.
2. **Hydraulic Network Optimization:** Automated diameter selection, head loss, friction factor evaluation, and pressure drop profiling across complex line topologies and fittings.
3. **Rigorous Unit Operation Rating:** Detailed thermal-hydraulic ratings for equipment—such as condensers and reboilers—integrating industry-standard methods like Bell–Delaware alongside automated engineering diagnostic warnings (e.g., velocity thresholds, fouling risk, vapor blanketing).
4. **Transparent, Scriptable Architecture:** Seamless integration into CI/CD pipelines, Jupyter notebooks, and computational engineering workflows.

# Key Functionality and Implementation

`ProcessPi` employs an engine-based architecture (`PipelineEngine`, `HeatExchangerEngine`) separating process definitions from numerical solution algorithms. 

## 1. Pipeline Sizing & Hydraulics (`PipelineEngine`)

The following example demonstrates sizing a 4 km carbon monoxide transfer line to meet an allowable pressure drop of 50 kPa:

```python
from processpi.units import Temperature, Length, MassFlowRate, Pressure
from processpi.components import CarbonMonoxide
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

# Define fluid and process conditions
fluid = CarbonMonoxide(temperature=Temperature(50, "C"))
mass_flow = MassFlowRate(1500, "kg/h")

# Define geometry and inline fittings
pipe = Pipe(name="Main Pipe", length=Length(4, "km"), material="CS")
valves = Fitting(fitting_type="gate_valve", quantity=2)
elbows_45 = Fitting(fitting_type="standard_elbow_45_deg", quantity=3)
elbows_90 = Fitting(fitting_type="standard_elbow_90_deg", quantity=6)

# Execute optimization model
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbows_45, elbows_90, valves],
    available_dp=Pressure(50, "kPa")
)
results = model.run()
model.summary()
```

The engine automatically selects an optimal 8-inch nominal diameter, calculating a total pressure drop of 28.66 kPa (0.283 atm), Reynolds number of 137,230, and Darcy friction factor of 0.0182.

## 2. Shell-and-Tube Condenser Rating (`HeatExchangerEngine`)

`ProcessPi` supports rating existing equipment using rigorous empirical methods. Below, an existing horizontal shell-and-tube condenser condensing n-propanol vapor against cooling water is rated via the Bell–Delaware method:

```python
from processpi.units import Temperature, Pressure, MassFlowRate, Length, HeatTransferCoefficient
from processpi.components import Water, OrganicLiquid
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchangerEngine

# Define streams
hot_in = MaterialStream(
    "npropanol_vapor_in",
    component=OrganicLiquid(),
    phase="vapor",
    temperature=Temperature(118, "C"),
    pressure=Pressure(2.03, "bar"),
    mass_flow=MassFlowRate(60000, "lb/h")
)
hot_out = MaterialStream(
    "npropanol_liquid_out",
    component=OrganicLiquid(),
    phase="liquid",
    temperature=Temperature(118, "C")
)

cold_in = MaterialStream(
    "cooling_water_in",
    component=Water(),
    phase="liquid",
    temperature=Temperature(29.4, "C"),
    pressure=Pressure(1, "bar")
)
cold_out = MaterialStream(
    "cooling_water_out",
    component=Water(),
    temperature=Temperature(40.6, "C")
)

# Rate existing geometry via Bell-Delaware method
hx = HeatExchangerEngine(method="bell_delaware")
hx.fit(
    hx_type="condenser",
    hot_in=hot_in,
    hot_out=hot_out,
    cold_in=cold_in,
    cold_out=cold_out,
    latent_heat=663000, # J/kg
    orientation="horizontal",
    shell_passes=1,
    tube_passes=4,
    tube_length=Length(8, "ft").to("m").value,
    tube_od=Length(0.75, "in").to("m").value,
    tube_id=Length(0.70, "in").to("m").value,
    tube_count=766,
    shell_diameter=Length(31, "in").to("m").value,
    tube_pitch=Length(1.0625, "in").to("m").value,
    tube_layout="triangular",
    shell_dp=Pressure(2, "psi"),
    tube_dp=Pressure(10, "psi"),
    U=HeatTransferCoefficient(568, "W/m2K"),
    mode="rate"
)
results = hx.run()
print(results.summary())
```

Beyond returning raw numerical outputs (calculated heat duty of 5,012 kW, calculated overall heat transfer coefficient of 123.6 W/m²·K), `ProcessPi` provides automated engineering diagnostics—highlighting that the exchanger is hydraulic-limited and issuing warnings for low tube velocity (0.11 m/s) and shell velocity (0.02 m/s), indicating severe fouling risk and potential vapor blanketing.

# AI-Assisted Development and Acknowledgements

In accordance with open science guidelines, the development of `ProcessPi` utilized large language models, including OpenAI's ChatGPT and Google's Gemini. These AI tools were used collaboratively for code scaffolding, numerical equation transcription, unit test generation, and documentation drafting. All algorithmic implementations, empirical correlations, convergence tolerances, and engineering diagnostics were independently designed, verified, and benchmarked against reference physical literature.

# Availability and Documentation

`ProcessPi` is open-source under an OSI-approved license and is distributed via PyPI (`pip install processpi`). Code repositories, issue trackers, and interactive documentation examples are available at `https://processpi.org`.

# References

* Bell, K. J. (1981). Delaware Method for Shell-and-Tube Heat Exchanger Design. In Kakac, S., Bergles, A. E., & Mayinger, F. (Eds.), *Heat Exchangers: Thermal-Hydraulic Fundamentals and Design* (pp. 581–618). Hemisphere Publishing Corp.
* Crane Co. (1988). *Flow of Fluids Through Valves, Fittings, and Pipe* (Technical Paper No. 410). Crane Co.
* Green, D. W., & Southard, M. Z. (Eds.). (2019). *Perry's Chemical Engineers' Handbook* (9th ed.). McGraw-Hill Education.
