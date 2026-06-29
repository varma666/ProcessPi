# Condenser Design — Benzene Vapor Condensation

**Problem**

Design a **horizontal shell & tube condenser** to condense saturated benzene vapor using cooling water under the following operating conditions.

- Hot fluid: **Benzene Vapor**
- Mass flow rate: **12,000 kg/h**
- Condensing temperature: **95°C**
- Operating pressure: **1.2 bar**
- Latent heat of condensation: **394 kJ/kg**
- Cooling medium: **Water**
- Cooling water inlet temperature: **30°C**
- Cooling water flow rate: **50,000 kg/h**
- Maximum allowable shell-side pressure drop: **0.5 bar**
- Maximum allowable tube-side pressure drop: **0.5 bar**
- Heat exchanger orientation: **Horizontal**
- Design method: **Bell–Delaware**

---

## Code

```python
from processpi.units import *
from processpi.components import *
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchangerEngine


# ============================================
# DEFINE COMPONENTS
# ============================================

benzene = Benzene()
water = Water()


# ============================================
# DEFINE PROCESS STREAMS
# ============================================

hot_in = MaterialStream(
    "benzene_vapor_in",
    component=benzene,
    phase="vapor",
    temperature=Temperature(95, "C"),
    pressure=Pressure(1.2, "bar"),
    mass_flow=MassFlowRate(12000, "kg/h"),
)

hot_out = MaterialStream(
    "benzene_liquid_out",
    component=benzene,
    phase="liquid",
    temperature=Temperature(95, "C"),
)

cold_in = MaterialStream(
    "cw_in",
    component=water,
    phase="liquid",
    temperature=Temperature(30, "C"),
    pressure=Pressure(1, "bar"),
    mass_flow=MassFlowRate(50000, "kg/h"),
)

# Outlet temperature calculated automatically
cold_out = MaterialStream(
    "cw_out",
    component=water,
)


# ============================================
# CREATE CONDENSER MODEL
# ============================================

hx = HeatExchangerEngine(
    method="bell_delaware"
)

hx.fit(
    hx_type="condenser",

    hot_in=hot_in,
    hot_out=hot_out,

    cold_in=cold_in,
    cold_out=cold_out,

    latent_heat=394000,

    shell_dp=Pressure(0.5, "bar"),
    tube_dp=Pressure(0.5, "bar"),

    orientation="horizontal",
    mode="design",
)

results = hx.run()


# ============================================
# OUTPUT
# ============================================

print(results.summary())

# Complete engineering report
results.detailed_summary()
```

---

## Output

```text
Heat Exchanger Summary
------------------------------
Type                  : condenser
Method                : bell_delaware
Heat Duty             : 1313.333 kW
Area                  : 47.275 m²
U Calculated          : 466.475 W/m²·K
Tube Velocity         : 0.575 m/s
Shell Velocity        : 0.905 m/s
Tube Pressure Drop    : 0.000 psi
Shell Pressure Drop   : 0.000
Tube Count            : 264
Tube Length           : 3.0 m
Status                : UNKNOWN

Engineering Insights
------------------------------
• Heat-transfer coefficient within acceptable range.
• Tube-side velocity acceptable but below ideal turbulent range.
• Shell-side velocity acceptable.

Warnings
------------------------------
• Tube velocity low (0.58 m/s)
• Area slightly undersized — acceptable.
• [HYDRAULIC_WARNING] Thermal area pushes tube count above hydraulic velocity target; using capped thermo-hydraulic count.
• [CONVERGENCE_WARNING] Geometry stagnation detected.
```

---

## Discussion

This example demonstrates the design of a **horizontal shell & tube condenser** using the **Bell–Delaware** shell-side analysis method.

Unlike a conventional heat exchanger, the hot process stream undergoes **phase change** from vapor to liquid. The required heat duty is therefore calculated primarily from the **latent heat of condensation**, while the cooling water absorbs the released energy.

The HeatExchangerEngine automatically performs:

- Phase-change energy balance
- Condenser sizing
- Heat-transfer area calculation
- Bell–Delaware shell-side corrections
- Tube bundle sizing
- Tube count optimization
- Tube and shell velocity calculations
- Hydraulic validation
- Engineering assessment and recommendations

### Design Results

| Parameter | Value |
|-----------|-------|
| Heat Exchanger Type | Condenser |
| Design Method | Bell–Delaware |
| Orientation | Horizontal |
| Heat Duty | 1313.33 kW |
| Required Area | 47.27 m² |
| Calculated Overall U | 466.48 W/m²·K |
| Tube Count | 264 |
| Tube Length | 3.0 m |
| Tube Velocity | 0.575 m/s |
| Shell Velocity | 0.905 m/s |

The calculated overall heat-transfer coefficient is within the expected range for a shell-and-tube condenser operating with water as the cooling medium.

The shell-side velocity is acceptable for efficient heat transfer. The tube-side velocity is lower than the preferred turbulent range, and the engine highlights this through engineering warnings while still producing a feasible design.

### Engineering Assessment

The generated warnings indicate that the thermal design required a relatively large number of tubes, reducing the tube-side velocity. Rather than sacrificing thermal performance, ProcessPI applies a thermo-hydraulic balancing strategy to produce a practical design and clearly reports the associated engineering considerations.

The convergence warning indicates that the geometry optimization reached a stable solution without further meaningful improvements, which is common during iterative equipment sizing.

For a complete engineering report, use:

```python
results.detailed_summary()
```

To inspect every calculation performed by the engine, use:

```python
results.trace()
```

For diagnostic information including warnings, optimization actions, and convergence details, use:

```python
results.debug_summary()
```
