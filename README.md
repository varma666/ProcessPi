
<p align="center">
  <img src="https://img.shields.io/badge/Process_PI-🧪-blue?style=for-the-badge&logo=python" alt="Process PI Logo" height="40"/>
</p>

<h1 align="center">Process PI</h1>

<p align="center">
  <strong>Python toolkit for chemical engineering simulations, equipment design, and unit conversions</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/🛠_Unit_Conversions-blue?style=for-the-badge" alt="Unit Conversions"/>
  <img src="https://img.shields.io/badge/💧_Components-blue?style=for-the-badge" alt="Components"/>
  <img src="https://img.shields.io/badge/🏭_Pumps-Pipelines-blue?style=for-the-badge" alt="Pumps & Pipelines"/>
  <img src="https://img.shields.io/badge/♨️_Heat_Exchangers-blue?style=for-the-badge" alt="Heat Exchangers"/>
  <img src="https://img.shields.io/badge/⚗️_Chemical_Flasks-blue?style=for-the-badge" alt="Chemical Flasks"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/processpi/">
    <img src="https://img.shields.io/pypi/v/processpi?style=for-the-badge&logo=pypi" alt="PyPI Version"/>
  </a>
  <a href="https://github.com/varma666/ProcessPi/stargazers">
    <img src="https://img.shields.io/github/stars/varma666/ProcessPi?style=for-the-badge&logo=github" alt="GitHub Stars"/>
  </a>
  <a href="https://github.com/varma666/ProcessPi/network/members">
    <img src="https://img.shields.io/github/forks/varma666/ProcessPi?style=for-the-badge&logo=github" alt="GitHub Forks"/>
  </a>
  <a href="https://github.com/varma666/ProcessPi/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/varma666/ProcessPi/python-package.yml?branch=main&style=for-the-badge" alt="Build Status"/>
  </a>
</p>

<p align="center">
  <em>Built with ❤️ for chemical engineers.</em>
</p>

---

## 📖 Overview

**Process PI** is a cross-platform **Python toolkit** for chemical engineering equipment design, simulations, and unit conversions.  
It provides a **modular framework** for learning, experimenting, and simulating process systems.

---

## 📑 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Getting Started](#-getting-started)
  - [Unit Conversions](#1-unit-conversions)
  - [Components](#2-components)
  - [Pipeline Network Analysis](#3-pipeline-network-analysis)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## ⚡ Features

- ⚙️ **Unit Conversion System** – Seamless conversion across SI, CGS, and Imperial units.  
- 🧪 **Components Database (Work in Progress)** – Educational thermodynamic properties of 25+ components (Water, Ethanol, CO₂, etc.), expanding regularly.  
- 🏭 **Equipment Design Modules (WIP)** – Pumps, pipelines, heat exchangers, reactors, and more.  
- 🌐 **Pipeline Networks** – Analyze single pipes and complex networked systems, calculate flow, pressure drops, velocity, and Reynolds numbers.  
- 📊 **Simulation Tools (Upcoming)** – Steady-state/dynamic process analysis, flow optimization, and energy management.

---

## 📦 Installation

Install via **PyPI**:

```bash
pip install processpi
```

---

## 🚀 Getting Started

### 1. Unit Conversions

Easily convert between SI, CGS, and Imperial units.

```python
from processpi.units import Length, Pressure, Temperature

# Length
l1 = Length(1.5, "m")
print(l1.to("ft"))   # Output in feet

# Pressure
p = Pressure(2, "bar")
print(p.to("Pa"))    # Output in Pascals

# Temperature
t = Temperature(100, "C")
print(t.to("K"))     # Output in Kelvin
```

---

### 2. Components

Access educational thermodynamic properties of chemical components.

```python
from processpi.components import Water, Ethanol

water = Water()
ethanol = Ethanol()

print(f"Water density: {water.density()} kg/m³")
print(f"Ethanol viscosity: {ethanol.viscosity()} Pa·s")
```

⚠️ **Note**: Component data is provided for **educational and demonstration purposes**. The database is continuously expanding.

---

### 3. Pipeline Network Analysis

Perform hydraulic calculations for pipelines and network systems.

```python
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.components import Water
from processpi.units import VolumetricFlowRate, Diameter, Length

pipe = Pipe(
    internal_diameter=Diameter(50, "mm"),
    length=Length(10, "m")
)

engine = PipelineEngine()
engine.fit(
    flowrate=VolumetricFlowRate(0.001, "m^3/s"),
    pipe=pipe,
    fluid=Water()
)

results = engine.run()
engine.summary()
```

#### Planned Enhancements

- Support for branching and parallel pipeline networks  
- Dynamic flow simulations and transient analysis  
- Cost and energy optimization tools for network layouts  

---

## 🛣 Roadmap

- Expand the Components Database to 50+ chemicals and fluids  
- Add steady-state and dynamic simulation modules  
- Implement energy optimization and cost analysis tools  
- Build a GUI/web interface for interactive simulations  
- Enable integration with real process data and sensor-driven workflows  

---

## 📜 License

This project is licensed under the **MIT License** – see the LICENSE file for details.

---

<p align="center">
  <em>Process PI – Built with ❤️ for chemical engineers.</em>
</p>
