---
title: 'ProcessPi: An Open-Source Python Library for Chemical Process Engineering Design and Simulation'
tags:
  - Python
  - chemical engineering
  - fluid mechanics
  - process simulation
  - thermodynamics
  - unit operations
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

Chemical and process engineering calculations often require balancing physical property retrieval, thermodynamic phase behavior, and hydraulic network modeling. Traditional commercial software packages provide comprehensive environments for these tasks but operate as closed-source desktop platforms with proprietary interfaces, high per-seat licensing costs, and limited extensibility into programmatic workflows. Conversely, engineers frequently rely on ad-hoc spreadsheets, which are prone to formula errors, lack automated verification, and resist version control.

`ProcessPi` is an open-source Python package developed to provide a modular, developer-first framework for process engineering design, hydraulics, and unit operation modeling. Designed to operate smoothly within modern computational scientific workflows, `ProcessPi` provides explicit calculation modules benchmarked against standard engineering literature, including Crane Technical Paper No. 410 and *Perry's Chemical Engineers' Handbook*.

# Statement of Need

Modern engineering workflows increasingly demand automation, reproducible design audits, and continuous integration pipelines for process modeling. While software such as Aspen Plus, HYSYS, and AVEVA PRO/II dominate large-scale industrial deployment, their closed ecosystems hinder lightweight scripting, automated batch parameter sweeps, and algorithmic optimization. 

Open-source alternatives like DWSIM provide substantial desktop GUI simulation environments; however, embedding them as lightweight dependencies in minimalist Python scripts or specialized automated routines can introduce unnecessary architectural overhead. `ProcessPi` addresses this gap by offering a clean, standard Python API (`pip install processpi`) specifically structured for engineers who want direct, programmatic access to:

1. **Hydraulic Network Analysis:** Evaluating single-phase and multiphase pressure gradients, equivalent lengths, and friction factors across complex piping networks and fittings.
2. **Physical and Thermodynamic Properties:** Accessing temperature- and pressure-dependent property correlations (such as vapor viscosity, thermal conductivity, and liquid density) for pure components and defined mixtures.
3. **Unit Operation Modules:** Executing modular rating and sizing calculations for common equipment, including shell-and-tube heat exchangers, pressure vessels, and flash separators.
4. **Dimensional Consistency:** Managing automated unit conversions and dimensional integrity across standard SI and imperial engineering unit systems.

# Key Functionality and Implementation

`ProcessPi` is written purely in Python and leverages NumPy and SciPy for robust numerical convergence and regression operations. Equipment models utilize structured connectivity architectures—such as explicit port mapping—to facilitate clear stream definitions and energy/mass balances.

The following example demonstrates setting up a shell-and-tube heat exchanger evaluation using named port mappings:

```python
import processpi as pi
from processpi.equipment import ShellAndTube
from processpi.core import PortMap

# Define port mapping and stream connections
ports = PortMap({
    'tube_in': {'fluid': 'water', 'flow_rate': 12.5, 'temp': 300.0, 'press': 200.0},
    'shell_in': {'fluid': 'steam', 'flow_rate': 2.0, 'temp': 410.0, 'press': 150.0}
})

# Instantiate and rate a shell-and-tube heat exchanger
hx = ShellAndTube(
    name="E-101",
    tube_passes=2,
    shell_passes=1,
    port_map=ports
)

results = hx.evaluate()
print(f"Heat Duty: {results.duty:.2f} kW | Shell Pressure Drop: {results.shell_dp:.3f} bar")
```

The library includes an automated test suite executed via `pytest` to continuously validate calculated friction factors, Reynolds numbers, and thermophysical properties against canonical engineering test cases and published empirical datasets.

# AI-Assisted Development and Acknowledgements

In accordance with open science transparency guidelines, the architecture, test generation, and code refactoring for `ProcessPi` were developed with the assistance of large language models, including OpenAI's ChatGPT and Google's Gemini. These AI tools were used collaboratively to scaffold boilerplate interfaces, implement mathematical algorithms derived from reference literature, and assist with API consistency and documentation review. All underlying engineering formulations, numerical convergence criteria, and benchmark outputs were manually designed, reviewed, and validated against reference physical data.

# Availability and Documentation

`ProcessPi` is open-source under an OSI-approved license and distributed through the Python Package Index (PyPI). Comprehensive documentation, interactive tutorials, and API references are hosted at `https://processpi.org`, with source code and issue tracking available on GitHub.

# References

* Crane Co. (1988). *Flow of Fluids Through Valves, Fittings, and Pipe* (Technical Paper No. 410). Crane Co.
* Green, D. W., & Southard, M. Z. (Eds.). (2019). *Perry's Chemical Engineers' Handbook* (9th ed.). McGraw-Hill Education.
* Poling, B. E., Prausnitz, J. M., & O'Connell, J. P. (2001). *The Properties of Gases and Liquids* (5th ed.). McGraw-Hill.
