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
- Overall heat-transfer coefficient (U): **575 W/m²·K**
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
    U=HeatTransferCoefficient(575, "W/m2K"),
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

---

## Output

```text
Heat Exchanger Summary
------------------------------
Type                  : shell_and_tube
Method                : bell_delaware
Heat Duty             : 611.560 kW
Area                  : 24.712 m²
U Calculated          : 722.780 W/m²·K
Tube Velocity         : 1.445 m/s
Shell Velocity        : 1.321 m/s
Tube Pressure Drop    : 1.156 psi
Shell Pressure Drop   : 48.53 kPa
Tube Count            : 138
Tube Length           : 3.0 m
Status                : UNKNOWN

Engineering Insights
------------------------------
• Heat-transfer coefficient within acceptable range.
• Tube-side velocity within recommended range.
• Shell-side velocity acceptable.
```

---

## Discussion

The **HeatExchangerEngine** automatically performs a complete thermal and hydraulic design of the exchanger.

For this case, ProcessPI selected a **Shell & Tube Heat Exchanger** using the **Bell–Delaware** design methodology.

### Design Results

| Parameter | Value |
|-----------|-------|
| Heat Exchanger Type | Shell & Tube |
| Design Method | Bell–Delaware |
| Heat Duty | 611.56 kW |
| Required Heat Transfer Area | 24.71 m² |
| Calculated Overall U | 722.78 W/m²·K |
| Tube Count | 138 |
| Tube Length | 3.0 m |
| Tube Velocity | 1.445 m/s |
| Shell Velocity | 1.321 m/s |

The calculated tube and shell velocities fall within commonly recommended industrial design ranges, while the required heat-transfer area satisfies the specified duty.

The engineering assessment also indicates that the calculated overall heat-transfer coefficient is acceptable for this service.

For additional design information, use:

```python
results.detailed_summary()
```

to obtain the complete calculation results, or

```python
results.trace()
```

to view the engineering calculation trace generated during the design process.
