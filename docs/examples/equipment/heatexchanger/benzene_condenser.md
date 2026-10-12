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
==============================
Type                  : condenser
Type Selection        : explicit
Method                : bell_delaware
Heat Duty             : 1313.333 kW
Area                  : 41.783 m2
U Calculated          : 707.075 W/m2K
U Basis               : calculated
Tube Velocity         : 1.997 m/s
Shell Velocity        : 25.587 m/s
Tube Pressure Drop    : 84.059 kPa
Shell Pressure Drop   : 205.147 kPa
Tube Count            : 140
Tube Length           : 5.000 m
Status                : PRESSURE_DROP_FAILURE

Pressure Drop Assessment
------------------------------
Tube ΔP Limit        : 50.000 kPa
Tube ΔP Actual       : 84.059 kPa
Shell ΔP Limit       : 50.000 kPa
Shell ΔP Actual      : 205.147 kPa

Engineering Feasibility
------------------------------
Thermal Performance  : PASS
Hydraulic Performance: PASS
Pressure Drop        : FAIL

Engineering Insights
------------------------------
• Heat-transfer coefficient within acceptable range.
• Tube-side velocity 2.00 m/s is within the 0.6-2 m/s range.
• Shell-side velocity 25.59 m/s is within the 10-30 m/s range.
• Tube-side pressure drop exceeds allowable limit.
• Shell-side pressure drop exceeds allowable limit.

Warnings
------------------------------
• [ASSUMPTION_WARNING] Sieder-Tate (mu/mu_w)^0.14 taken as 1 on the shell side: no hot_wall_viscosity given
• [ASSUMPTION_WARNING] Sieder-Tate (mu/mu_w)^0.14 taken as 1 on the tube side: no cold_wall_viscosity given
• Tube-side pressure drop 84059.4 Pa exceeds limit 50000.0 Pa
• Shell-side pressure drop 205147.0 Pa exceeds limit 50000.0 Pa
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
| Heat Transfer Area | 41.78 m² |
| Calculated Overall U | 707.08 W/m²·K |
| Tube Count | 140 |
| Tube Length | 5.0 m |
| Tube Velocity | 1.997 m/s |
| Shell Velocity | 25.587 m/s |

The calculated overall heat-transfer coefficient is within the expected range for a shell-and-tube condenser operating with water as the cooling medium.

The tube count is set so that the cooling water stays within the 0.6-2.0 m/s band of condenser service (1.997 m/s), and the benzene vapor crosses the shell at 25.59 m/s, within the 10-30 m/s vapor band. Both pressure drops exceed the 0.5 bar limits (84.1 kPa on the tube side, 205.1 kPa on the shell side), so the engine reports the status as PRESSURE_DROP_FAILURE instead of a feasible design.

### Engineering Assessment

The thermal check passes, but the pressure-drop check fails on both sides, and the warnings list the two exceedances. The warnings also record that the Sieder-Tate viscosity ratio was taken as 1 on both sides because no wall viscosities were given.

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
