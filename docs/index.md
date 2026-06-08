---
title: Process PI
hide:
  - navigation
  - toc
---

<!-- Hero Section -->
<div class="hero" style="display: flex; align-items: center; justify-content: center; gap: 2rem; flex-wrap: wrap; padding: 3rem 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 60%); border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">

  <!-- Logo -->
  <img src="assets/logo.png" alt="Process PI Logo" width="600" style="flex-shrink: 0;"/>

  <!-- Heading + Subtitle -->
  <div style="max-width: 600px;">
    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: var(--md-primary-fg-color);">
      Process Modeling & Simulation in Python
    </h1>
    <div class="hero-subtitle" style="font-size: 1.2rem; margin-top: 1rem; line-height: 1.6; color: var(--md-typeset-color);">
      Build, simulate, and analyze chemical process systems with an open-source Python toolkit.<br><br>
      From pipelines and pumps to heat exchangers and mixers, <strong>Process PI</strong> provides engineers
      with the tools to model, optimize, and visualize complex process networks with precision and ease.
    </div>
    <div style="margin-top: 1.5rem;">
      <a class="md-button md-button--primary" href="installation/">
        Get Started
      </a>
      <a class="md-button" href="user-guide/introduction/">
        Learn More
      </a>
    </div>
  </div>
</div>

---

## Why ProcessPI?

| Feature | ProcessPI | Traditional Spreadsheets | Commercial Simulators |
|----------|----------|----------|----------|
| Open Source | ✅ | ⚠️ | ❌ |
| Python Native | ✅ | ❌ | ❌ |
| Version Control Friendly | ✅ | ❌ | ⚠️ |
| Automation Ready | ✅ | ❌ | ⚠️ |
| Cost | Free | Free | $$$$ |
| Engineering Calculations | ✅ | ⚠️ | ✅ |

ProcessPI bridges the gap between quick spreadsheet calculations and expensive process simulation software by providing engineers with a programmable engineering toolkit built entirely in Python.

---

## Quick Example

Calculate pressure drop through a carbon monoxide pipeline with valves and elbows.

```python
from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting

fluid = CarbonMonoxide(
    temperature=Temperature(50, "C")
)

mass_flow = MassFlowRate(1500, "kg/h")

pipe = Pipe(
    name="Main Pipe",
    length=Length(4, "km"),
    material="CS"
)

valves = Fitting(
    fitting_type="gate_valve",
    quantity=2
)

elbows_90 = Fitting(
    fitting_type="standard_elbow_90_deg",
    quantity=6
)

model = PipelineEngine()

model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[valves, elbows_90],
    available_dp=Pressure(50, "kPa")
)

results = model.run()

print(results.total_pressure_drop.to("atm"))
```

Example output:

```text
PIPELINE SUMMARY
----------------------------------
Fluid              : Carbon Monoxide
Mass Flow          : 1500 kg/h
Pipe Length        : 4 km
Available ΔP       : 50 kPa

Total Pressure Drop: 0.31 atm
```

---

## Key Features

<div class="grid cards" markdown>

-   :material-pipe: **Pipeline Networks**
    <p>Design, simulate, and analyze fluid flow through pipes, valves, pumps, and splitters.
    Optimize your process network with precise pressure drop and flow calculations.</p>

-   :material-fire: **Heat Transfer**
    <p>Compute heat flux, energy balances, and heat exchanger performance.
    Supports a wide range of unit operations for chemical process engineering.</p>

-   :material-flask: **Components Library**
    <p>Access a curated database of chemicals, mixtures, and equipment properties.
    Retrieve physical and thermodynamic data for accurate simulations.</p>

-   :material-chart-line: **Visualization & Analysis**
    <p>Generate schematics, performance plots, and interactive charts for process optimization.</p>

-   :material-cog: **Process Optimization**
    <p>Run simulations to optimize process parameters, energy efficiency, and system performance.</p>

-   :material-book: **Documentation & Examples**
    <p>Follow tutorials, examples, and API references to get started quickly.</p>

</div>

---

## Explore

<div class="grid cards" markdown>

-   :material-download: **[Installation](installation/)**
    Quick setup guide to install Process PI and get started with Python.

-   :material-book-open-variant: **[User Guide](user-guide/introduction/)**
    Step-by-step tutorials and detailed documentation for all features.

-   :material-lightbulb-on-outline: **[Examples](examples/index.md)**
    Real-world pipelines, heat transfer, and component simulations you can try immediately.

</div>

---

## Validation & Reliability

ProcessPI calculations are validated against established engineering references and published correlations including:

- Crane TP-410
- Perry's Chemical Engineers' Handbook
- GPSA Engineering Data Book
- Standard fluid mechanics correlations
- Industry-accepted pressure drop methodologies

Validation examples and benchmark studies will continue to expand with future releases.

---

## Dependencies

ProcessPI is built on top of powerful open-source libraries and AI tools.

---

## Mission

**To create the leading open-source Python platform for process and chemical engineering calculations.**

Whether you're a student, researcher, consultant, or plant engineer, ProcessPI provides transparent, reproducible, and extensible engineering tools without proprietary limitations.
