# ProcessPI Pipeline Engine – Feature Sheet

## Overview
The `Pipeline Engine` in **ProcessPI** is a **steady-state, single-phase fluid solver** for designing and analyzing process pipelines and small-to-medium networks.  
It supports both quick calculations for sizing and more detailed network balancing using iterative or matrix methods.

---

## Key Features

### 1. Single Pipeline Analysis
- Pressure drop and flow rate calculations using:
  - **Darcy–Weisbach** for precise engineering.
  - **Hazen–Williams** for water and low-viscosity fluids.
- Includes effects of:
  - Elevation (static head)
  - Pipe roughness
  - Fittings and valves (via K-factors)

### 2. Network Analysis
- Handles **branched and looped networks**:
  - Hardy–Cross iteration method
  - Direct matrix solver for node balancing
- Suitable for:
  - Small-to-medium plant utility networks
  - Firewater loops
  - Cooling water distribution

### 3. Component Loss Modeling
- Supports inline equipment and fittings:
  - Gate valves, globe valves, bends, tees
  - Orifice meters and filters
- Uses **industry-standard K-factor** data for accurate loss modeling.

### 4. Elevation and Static Head
- Node elevations automatically included in pressure and head balance.
- Useful for:
  - Hilly terrain installations
  - Overhead storage tanks
  - Sump-to-tank transfers

### 5. Multiple Solver Options

| Solver | Best For | Notes |
|--------|----------|-------|
| **Darcy–Weisbach** | Engineering-grade precision | Supports custom fluid properties |
| **Hazen–Williams** | Quick checks for water lines | Assumes low viscosity |
| **Hardy–Cross** | Small/medium networks with ≤10 pipes | Easy to debug |
| **Matrix Solver** | Networks with moderate branching | Faster and more robust |

---

## Typical Use Cases
- Utility water network design  
- Chemical transfer line sizing  
- Cooling water loop balancing  
- Firewater ring main analysis  
- Static head impact studies

---

## Current Limitations
- Steady-state only (no transient or surge analysis)
- Single-phase fluids (no two-phase or slurry modeling)
- Assumes constant density and viscosity
- No integration with pump curves
- Limited scalability for very large networks (>50 pipes)

---

## Planned Roadmap

| Stage | Planned Feature |
|--------|----------------|
| **Short-term** | Newton–Raphson loop-and-node solver for larger networks |
| **Mid-term** | Pump curve integration and automatic pump-point calculation |
| **Mid-term** | Compressible (gas) network support |
| **Long-term** | Dynamic and transient simulation (surge, water hammer) |
| **Long-term** | Two-phase and slurry flow models |

---

## Why Use ProcessPI Pipeline Engine?
- **Open-source and extensible** – easy to adapt for custom chemical engineering needs  
- **Cross-platform** – works on Windows, Linux, and macOS  
- **Lightweight and fast** – ideal for engineering studies and quick design checks  
- **Integration-ready** – compatible with other ProcessPI tools and simulations  
