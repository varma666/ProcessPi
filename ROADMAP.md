
# ProcessPI Master Roadmap

## Release Cadence
- **New version every 3 months** (Quarterly release)
- Includes updates to:
  - **Pipeline Engine** (Pipeline hydraulics, multiphase, compressors, etc.)
  - **Heat Transfer** (Heat transfer modeling and Equipment Design)
  - **Future modules** (mass transfer, equipment sizing, etc.)

---

## Version Plan

| Version | Release Window | Key Deliverables |
|----------|---------------|------------------|
| **v0.3 – Foundation** | **Q4 2025 (Nov)** | Real-gas support, energy balance, steam & cryogenic support, pumps & compressors |
| **v0.4 – Network Solver** | **Q1 2026 (Feb)** | Newton–Raphson solver for large networks, hybrid solver modes, basic heat transfer module |
| **v0.5 – Complex Fluids** | **Q2 2026 (May)** | Multiphase support, non-Newtonian models, flow regime detection, heat transfer enhancements |
| **v0.6 – Transients & Dynamics** | **Q3 2026 (Aug)** | Water hammer, pump/compressor dynamic models, transient heat transfer cases |
| **v1.0 – Stable Release** | **Q4 2026 (Nov)** | Full API, visualization, component libraries, GUI hooks, stable heat transfer + unit operations |

---

## Phase 1 (v0.3) Detailed Plan – Q4 2025

| Month | Tasks |
|--------|-------|
| **Month 1** | Real-gas Z-factor, EOS integration, energy balance |
| **Month 2** | Steam tables (IAPWS), cryogenic fluids, validation |
| **Month 3** | Pumps & compressors module, unit tests, API docs, example notebooks |

---

## Phase 2 (v0.4) Draft Plan – Q1 2026

| Month | Tasks |
|--------|-------|
| **Month 1** | Network topology parser, incidence matrix builder |
| **Month 2** | Newton–Raphson solver, hybrid solver logic |
| **Month 3** | Heat transfer base module (shell-tube, plate exchangers), documentation, benchmarks |

---

## GitHub Milestones

| Milestone | Branch/Tag | Notes |
|------------|------------|-------|
| **v0.3** | `release/v0.3` | Focus on single-pipe robustness & energy balance |
| **v0.4** | `release/v0.4` | Network solver + htransfer base |
| **v0.5** | `release/v0.5` | Complex fluid support |
| **v0.6** | `release/v0.6` | Dynamic transient simulations |
| **v1.0** | `main` | Stable, production-ready package |
