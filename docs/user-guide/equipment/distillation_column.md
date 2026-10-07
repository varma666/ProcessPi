# Distillation Columns

`DistillationEngine` designs a simple distillation column (one feed, a total
condenser, a partial reboiler, a distillate and a bottoms product) with the
same `fit()` / `run()` interface as the pipeline and heat exchanger engines.
`DistillationColumn` is the same column as a flowsheet unit.

It runs the Fenske-Underwood-Gilliland-Kirkbride shortcut (any number of
components), checks a binary design by McCabe-Thiele stepping, and then sizes
a tray column: overall efficiency, actual trays, diameter, tray-section
height and the condenser and reboiler duties.

```python
from processpi.components import Benzene, Toluene
from processpi.equipment import DistillationEngine
from processpi.streams import MaterialStream
from processpi.units import MolarFlowRate, Pressure, Temperature

feed = MaterialStream(
    "Feed",
    composition={"Benzene": 0.4, "Toluene": 0.6},
    molar_flow=MolarFlowRate(100, "kmol/h"),
    temperature=Temperature(95, "C"),
    pressure=Pressure(1.01325, "bar"),
)
model = DistillationEngine(name="T-101")
model.fit(
    feed=feed,
    components=[Benzene(), Toluene()],
    light_key="Benzene",
    heavy_key="Toluene",
    distillate_lk_fraction=0.97,
    bottoms_lk_fraction=0.02,
)
result = model.run()
print(result.summary())
```

```text
==========================
DISTILLATION COLUMN: T-101
==========================
Method              : Fenske-Underwood-Gilliland-Kirkbride (Gilliland: molokanov)
Keys                : light Benzene, heavy Toluene
Pressure            : 1.0132 bar

Material balance
----------------
Component    Feed z  Distillate x   Bottoms x  alpha (to HK)
Benzene      0.4000        0.9700      0.0200         2.4701
Toluene      0.6000        0.0300      0.9800         1.0000
Feed F              : 100.000 kmol/h  (q = 1.001, subcooled liquid feed)
Distillate D        : 40.000 kmol/h
Bottoms B           : 60.000 kmol/h
Key recoveries      : 97.00 % LK to distillate, 98.00 % HK to bottoms

Stages and reflux
-----------------
Minimum stages      : 8.15 (Fenske, reboiler included)
Minimum reflux      : 1.565 (Underwood)
Reflux ratio        : 2.034 (1.3 x R_min, R/Rmin = 1.30)
Theoretical stages  : 17.32 (Gilliland, reboiler included)
Rectifying/stripping: 8.66 / 8.66 (Kirkbride)
Feed stage          : 10 from the top (theoretical)
McCabe-Thiele check : 17 stages (16.64 fractional), feed on stage 8 (ideal VLE at column pressure)

Trays
-----
Tray efficiency     : 54.8 % (O'Connell)
Actual trays        : 30
Feed tray           : 18 from the top

Temperatures and duties
-----------------------
Condenser           : 80.73 C
Top stage           : 81.65 C
Reboiler            : 109.74 C
Condenser duty      : 1041.6 kW
Reboiler duty       : 1124.5 kW

Column sizing (tray column)
---------------------------
Top     F_LV 0.039, C_sb 0.103 m/s, u_flood 1.788 m/s, D 0.996 m
Bottom  F_LV 0.092, C_sb 0.094 m/s, u_flood 1.539 m/s, D 1.116 m
Column diameter     : 1.116 m (governed by the bottom section)
Tray spacing        : 0.60 m, design at 80 % of flooding
Tray section height : 18.00 m (without top and bottom allowances)

Assumptions
-----------
- Constant molar overflow, total condenser, partial reboiler counted as a theoretical stage.
- Column pressure taken as uniform top to bottom.
- Ideal vapour-liquid equilibrium (Raoult's law) from the components' DIPPR vapour pressures.
- Duties from latent heats only (saturated reflux, sensible heat of products neglected).
- Surface tension 0.020 N/m (no component data); give `surface_tension` to correct the flooding velocity.
- Tray spacing 0.6 m (default).
- Design at 80 % of flooding (default).
- Downcomer area 12 % of column area (default).
```

Every number is also in `result.data` (or `result["key"]`), as ProcessPI unit
objects where the quantity has a unit: for example `result["diameter"]`,
`result["condenser_duty"].to("kW")`, `result["distillate"]["x"]`.

`fit()` also takes optional `distillate` and `bottoms` streams; when both are
given, `run()` writes the products to them. `model.summary()` and
`model.results()` return the last run, as in the other engines.

## Specifications

These are the keyword arguments of `fit()` (and of `DistillationColumn`).

| Spec | Meaning |
|------|---------|
| `light_key`, `heavy_key` | Key components, by name. Names match loosely: `"chlorobenzene"`, `"ChloroBenzene"` and `"Chloro Benzene"` are the same component. |
| `light_key_recovery`, `heavy_key_recovery` | Fraction of the feed light key that leaves in the distillate, and of the heavy key in the bottoms. |
| `distillate_lk_fraction`, `bottoms_lk_fraction` | Binary feeds only: light-key mole fraction in each product, instead of recoveries. |
| `components` | ProcessPI components; equilibrium from Raoult's law with their vapour pressures. Needed for temperatures, duties, efficiency and diameter. |
| `relative_volatility` | Instead of `components`: constant volatilities (any reference). Gives the stage and reflux design only. |
| `pressure` | Column pressure; default is the feed pressure. |
| `q` | Feed thermal condition. By default it comes from the feed temperature (subcooled or two-phase feed); a superheated feed needs `q`. |
| `reflux_ratio` or `reflux_ratio_factor` | Operating L/D, or R/R<sub>min</sub> (default 1.3). |
| `gilliland_correlation` | `"molokanov"` (default) or `"eduljee"`. |
| `tray_efficiency` | Overall efficiency; overrides O'Connell. |
| `tray_spacing` | Default 0.6 m. |
| `flood_fraction` | Design fraction of the flooding velocity; default 0.80 (warning above 0.85). |
| `downcomer_area_fraction` | Default 0.12. |
| `surface_tension` | N/m; default 0.020, the reference value of Fair's correlation. |
| `flooding_k_factor` | Tray-geometry factor on the flooding velocity; default 1.0. |

## In a flowsheet

`DistillationColumn` is an `Equipment` with the inlet port `feed` and the
outlet ports `distillate` and `bottoms`. `simulate()` runs the design and
writes the products (composition, molar and mass flow, pressure, and the
condenser and reboiler temperatures) to the outlet streams.

```python
from processpi.integration.flowsheet import Flowsheet

distillate, bottoms = MaterialStream("Distillate"), MaterialStream("Bottoms")
column = DistillationColumn(
    name="T-101", components=[Benzene(), Toluene()],
    light_key="Benzene", heavy_key="Toluene",
    distillate_lk_fraction=0.97, bottoms_lk_fraction=0.02,
)
fs = Flowsheet("BTX")
fs.connect(feed, column, "feed")
column.connect_outlet("distillate", distillate)
column.connect_outlet("bottoms", bottoms)
fs.run()
```

## Methods and sources

| Step | Method | Source |
|------|--------|--------|
| Minimum stages, component split at total reflux | Fenske, with the geometric mean of the top and bottom volatilities | [OpenExamPrep PE Chemical 11.4](https://open-exam-prep.com/study-guides/pe-chemical/distillation-operations/multicomponent-distillation) |
| Minimum reflux | Underwood; one root per volatility gap between the keys, so components between the keys distribute | same |
| Theoretical stages | Gilliland, Molokanov et al. (1972) form; Eduljee form optional | M. A. Soliman, J. King Saud Univ. Eng. Sci. 21(1) (2009) 1-5, eq. (1); OpenExamPrep (Eduljee) |
| Feed stage | Kirkbride | OpenExamPrep |
| Overall efficiency | O'Connell, 0.503 (&mu;<sub>L</sub> &alpha;)<sup>-0.226</sup> | M. Duss, R. Taylor, *Chem. Eng. Prog.*, July 2018, eq. (2) |
| Flooding velocity | Fair, C<sub>sb</sub> from the Lygeros-Magoulas fit, (&sigma;/0.02)<sup>0.2</sup> correction | C. A. P. Souza et al., *Ind. Eng. Chem. Res.* 64 (2025) 2256, eqs. (1)-(3), (5), Table 1 |

The OpenExamPrep worked example (ethane/propane/n-butane/n-pentane) is
reproduced in `tests/test_distillation_shortcut.py` and
`tests/test_distillation_column.py`.

## Limits

- Ideal VLE only: right for similar molecules (aromatics, light hydrocarbons),
  wrong for non-ideal mixtures such as ethanol/water. Use `relative_volatility`
  for those, with values you trust.
- Components whose vapour-pressure constants are inconsistent with their
  critical point are refused with an error rather than used.
- Constant molar overflow and a uniform column pressure; duties from latent
  heats only.
- Tray columns only; packed columns are not covered yet.
- The tray-section height leaves out the top disengagement space and the
  bottom sump.
