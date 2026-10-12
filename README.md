<p align="center">
  <img src="https://img.shields.io/badge/Process_PI-🧪-blue?style=for-the-badge&logo=python" alt="Process PI Logo" height="40"/>
</p>

<h1 align="center">Process PI</h1>
<p align="center">
  <a href="https://pepy.tech/projects/processpi">
    <img src="https://static.pepy.tech/personalized-badge/processpi?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads"/>
  </a>
</p>
<p align="center">
  <strong>Python toolkit for chemical engineering simulations, equipment design, and unit conversions</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/🛠_Unit_Conversions-blue?style=for-the-badge" alt="Unit Conversions"/>
  <img src="https://img.shields.io/badge/💧_Components-blue?style=for-the-badge" alt="Components"/>
  <img src="https://img.shields.io/badge/🏭_Pipelines_&_Network_Engine-blue?style=for-the-badge" alt="Pipelines & Network Engine"/>
  <img src="https://img.shields.io/badge/♨️_Heat_Transfer_(WIP)-blue?style=for-the-badge" alt="Heat Transfer"/>
  <img src="https://img.shields.io/badge/⚗️_Reaction_&_Mass_Transfer_(WIP)-blue?style=for-the-badge" alt="Reaction & Mass Transfer"/>
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
  <a href="https://colab.research.google.com/github/varma666/ProcessPi/blob/main/notebooks/getting_started.ipynb">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>
  </a>
  <a href="https://mybinder.org/v2/gh/varma666/ProcessPi/HEAD?filepath=notebooks/getting_started.ipynb">
    <img src="https://mybinder.org/badge_logo.svg" alt="Launch Binder"/>
  </a>
</p>


<p align="center">
  <em>Built with ❤️ for chemical engineers.</em>
</p>

---

## 📖 Overview

**Process PI** is a modular **Python toolkit** for chemical engineering that enables:

- **Pipeline network simulations**
- **Unit conversions across SI, CGS, and Imperial systems**
- **Component-based property calculations**
- And more, with advanced features under active development.

---

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Getting Started](#-getting-started)
  - [Unit Conversions](#1-unit-conversions)
  - [Components](#2-components)
  - [Pipeline Network Engine](#3-pipeline-network-engine)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## ⚡ Features

- ⚙️ **Unit Conversion System** – Instant conversions between engineering unit systems.  
- 🧪 **Components Library** – Access educational thermodynamic properties for 25+ fluids and growing.  
- 🌐 **Pipeline Network Engine** – Build and simulate simple pipelines or complex interconnected networks, analyzing:
  - Pressure drops
  - Flow rates
  - Reynolds number
  - Pump requirements  
- 🧮 **Calculation Modules (WIP)** – Heat transfer, mass transfer, and reaction engineering models in progress.  
- 📊 **Simulation Tools (Planned)** – Transient dynamics, optimization, and interactive visualizations.  

---

## 📦 Installation

Install from **PyPI**:

```bash
pip install processpi
```

For development:

```bash
git clone https://github.com/varma666/ProcessPi.git
cd ProcessPi
pip install -e .
```

---

## 🚀 Getting Started

### 1. Unit Conversions

```python
from processpi.units import Length, Pressure, Temperature

# Length conversion
length = Length(1.5, "m")
print(length.to("ft"))  # Feet output

# Pressure conversion
p = Pressure(2, "bar")
print(p.to("psi"))      # PSI output

# Temperature conversion
t = Temperature(100, "C")
print(t.to("K"))        # Kelvin output
```

### 2. Components

```python
from processpi.components import Water, Ethanol

water = Water()
ethanol = Ethanol()

print(f"Water density: {water.density()}")
print(f"Ethanol viscosity: {ethanol.viscosity()}")
```

⚠ **Note**: Component data is for educational/demo purposes only. Extended property support is in progress.

### 3. Pipeline Network Engine

Perform single-pipe or multi-pipe network simulations.

```python
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.components import Water
from processpi.units import VolumetricFlowRate, Diameter, Length

# Define pipe and fluid
pipe = Pipe(
    name="Main Pipe",
    internal_diameter=Diameter(50, "mm"),
    length=Length(10, "m")
)
water = Water()

# Set up engine
engine = PipelineEngine()
engine.fit(
    flowrate=VolumetricFlowRate(0.001, "m3/s"),
    pipe=pipe,
    fluid=water
)

# Run calculations
results = engine.run()
engine.summary()
```

Planned upgrades:
- Dynamic simulations  
- Branching/parallel pipeline analysis  
- Integrated cost and energy optimization  

---

## 🛣 Roadmap

- ✅ Pipeline Network Engine – Functional for single and multi-segment networks  
- 🚧 Heat Transfer Modules – In progress for exchangers, conduction, and convection models  
- 🚧 Mass Transfer & Reaction Modules – Basic structure in place, calculations coming soon  
- 🔮 Advanced Features – Transient analysis, energy optimization, and GUI/web interfaces  

---

## 📜 License

This project is licensed under the **MIT License** – see the LICENSE file for details.

<p align="center"> <em>ProcessPI – Built with ❤️ for chemical engineers.</em> </p>
