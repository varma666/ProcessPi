# Shell & Tube Heat Exchanger — Benzene Cooler

**Problem**

Design a **Shell & Tube Heat Exchanger** to cool liquid benzene under the following operating conditions:

- Hot fluid: **Benzene**
- Hot fluid flow rate: **21,000 kg/h**
- Inlet temperature: **90°C**
- Outlet temperature: **30°C**
- Cold fluid: **Cooling Water**
- Cooling water flow rate: **60,500 kg/h**
- Cooling water inlet temperature: **15°C**
- Starting estimate of the overall heat-transfer coefficient (`assumed_U`): **575 W/m²·K**
- Maximum allowable tube-side pressure drop: **1 bar**
- Maximum allowable shell-side pressure drop: **1 bar**
- Heat exchanger mode: **Design**

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
# DEFINE MATERIAL STREAMS
# ============================================

hot_in = MaterialStream(
    "hot_in",
    component=benzene,
    temperature=Temperature(90, "C"),
    mass_flow=MassFlowRate(21000, "kg/h"),
)

hot_out = MaterialStream(
    "hot_out",
    component=benzene,
    temperature=Temperature(30, "C"),
)

cold_in = MaterialStream(
    "cold_in",
    component=water,
    temperature=Temperature(15, "C"),
    mass_flow=MassFlowRate(60500, "kg/h"),
)

# Outlet temperature will be calculated
cold_out = MaterialStream(
    "cold_out",
    component=water
)


# ============================================
# CREATE HEAT EXCHANGER MODEL
# ============================================

hx = HeatExchangerEngine()

hx.fit(
    hot_in=hot_in,
    hot_out=hot_out,
    cold_in=cold_in,
    cold_out=cold_out,
    assumed_U=HeatTransferCoefficient(575, "W/m2K"),
    shell_dp=Pressure(1, "bar"),
    tube_dp=Pressure(1, "bar"),
    mode="design"
)

results = hx.run()


# ============================================
# OUTPUT
# ============================================

print(results.summary())

# Complete calculation dictionary
results.detailed_summary()
```

`assumed_U` is only the first guess: the engine calculates U from the film
coefficients and resizes the area until U converges. Pass `specified_U`
instead to size the area at a fixed U.

---

## Output

```text
Heat Exchanger Summary
==============================
Type                  : shell_and_tube
Type Selection        : auto
Reason                : no hx_type given; larger inlet mass flow 16.81 kg/s > double pipe limit 1 kg/s
Method                : kern
Heat Duty             : 649.113 kW
Area                  : 30.084 m2
U Calculated          : 706.159 W/m2K
U Basis               : assumed
Tube Velocity         : 1.997 m/s
Shell Velocity        : 0.535 m/s
Tube Pressure Drop    : 67.313 kPa
Shell Pressure Drop   : 18.005 kPa
Tube Count            : 168
Tube Length           : 3.000 m
Status                : MARGINAL

Pressure Drop Assessment
------------------------------
Tube ΔP Limit        : 100.000 kPa
Tube ΔP Actual       : 67.313 kPa
Shell ΔP Limit       : 100.000 kPa
Shell ΔP Actual      : 18.005 kPa

Engineering Feasibility
------------------------------
Thermal Performance  : PASS
Hydraulic Performance: PASS
Pressure Drop        : PASS

Engineering Insights
------------------------------
• Heat-transfer coefficient within acceptable range.
• Tube-side velocity 2.00 m/s is within the 1-2.5 m/s range.
• Shell-side velocity 0.53 m/s is within the 0.5-1.5 m/s range.

Warnings
------------------------------
• [ASSUMPTION_WARNING] Sieder-Tate (mu/mu_w)^0.14 taken as 1 on the shell side: no hot_wall_viscosity given
• [ASSUMPTION_WARNING] Sieder-Tate (mu/mu_w)^0.14 taken as 1 on the tube side: no cold_wall_viscosity given
```

---

## Discussion

The **HeatExchangerEngine** automatically performs a complete thermal and hydraulic design of the exchanger.

For this case, ProcessPI selected a **Shell & Tube Heat Exchanger** (no `hx_type` was given, and the inlet flow is above the double pipe limit) and sized it with the **Kern** method, the engine's default. Pass `method="bell_delaware"` to `HeatExchangerEngine` for the Bell-Delaware shell-side method.

### Design Results

| Parameter | Value |
|-----------|-------|
| Heat Exchanger Type | Shell & Tube |
| Design Method | Kern |
| Heat Duty | 649.11 kW |
| Heat Transfer Area | 30.08 m² (29.57 m² required) |
| Calculated Overall U | 706.16 W/m²·K |
| Tube Count | 168 |
| Tube Length | 3.0 m |
| Tube Velocity | 1.997 m/s |
| Shell Velocity | 0.535 m/s |

The calculated tube and shell velocities fall within commonly recommended industrial design ranges, while the required heat-transfer area satisfies the specified duty.

The engineering assessment also indicates that the calculated overall heat-transfer coefficient is acceptable for this service. The status is MARGINAL because the area, 30.08 m², is less than 5% above the 29.57 m² the duty requires.

For additional design information, use:

```python
results.detailed_summary()
```

to obtain the complete calculation results, or

```python
results.trace()
```

to view the engineering calculation trace generated during the design process.
