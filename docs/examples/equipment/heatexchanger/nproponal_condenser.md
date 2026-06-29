# Horizontal n-Propanol Condenser Rating

**Problem**

Evaluate the thermal and hydraulic performance of an existing **horizontal shell & tube condenser** used to condense **n-propanol vapor**. Unlike the previous design examples, this case operates in **Rating Mode**, where the exchanger geometry is already known and ProcessPI predicts its operating performance under the specified process conditions.

The condenser has the following specifications:

- Service: **Total Condenser**
- Hot fluid: **n-Propanol Vapor**
- Hot fluid flow rate: **60,000 lb/h**
- Condensing temperature: **118°C**
- Operating pressure: **2.03 bar**
- Cooling medium: **Water**
- Cooling water inlet temperature: **29.4°C**
- Cooling water outlet temperature: **40.6°C**
- Latent heat of condensation: **663 kJ/kg**
- Tube length: **8 ft**
- Tube OD: **0.75 in**
- Tube ID: **0.70 in**
- Number of tubes: **766**
- Shell diameter: **31 in**
- Tube passes: **4**
- Shell passes: **1**
- Tube layout: **Triangular**
- Overall Heat Transfer Coefficient (U): **568 W/m²·K**
- Design Method: **Bell–Delaware**

---

## Code

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s"
)

from processpi.units import *
from processpi.components import *
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchangerEngine


# ============================================
# COMPONENTS
# ============================================

water = Water()
n_propanol = OrganicLiquid()


# ============================================
# HOT SIDE
# ============================================

hot_in = MaterialStream(
    "npropanol_vapor_in",
    component=n_propanol,
    phase="vapor",
    temperature=Temperature(118, "C"),
    pressure=Pressure(2.03, "bar"),
    mass_flow=MassFlowRate(60000, "lb/h"),
)

hot_out = MaterialStream(
    "npropanol_liquid_out",
    component=n_propanol,
    phase="liquid",
    temperature=Temperature(118, "C"),
)


# ============================================
# COLD SIDE
# ============================================

cold_in = MaterialStream(
    "cooling_water_in",
    component=water,
    phase="liquid",
    temperature=Temperature(29.4, "C"),
    pressure=Pressure(1, "bar"),
)

cold_out = MaterialStream(
    "cooling_water_out",
    component=water,
    temperature=Temperature(40.6, "C"),
)


# ============================================
# RATE EXISTING CONDENSER
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

    latent_heat=663000,

    orientation="horizontal",

    shell_passes=1,
    tube_passes=4,

    tube_length=Length(8, "ft").to("m").value,
    tube_od=Length(0.75, "in").to("m").value,
    tube_id=Length(0.70, "in").to("m").value,

    tube_count=766,

    shell_diameter=Length(31, "in").to("m").value,

    tube_pitch=Length(1.0625, "in").to("m").value,
    tube_layout="triangular",

    shell_dp=Pressure(2, "psi"),
    tube_dp=Pressure(10, "psi"),

    U=HeatTransferCoefficient(568, "W/m2K"),

    mode="rate",

    verbose=True,
)

results = hx.run()

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
Heat Duty             : 5012.192 kW
Area                  : 111.784 m²
U Calculated          : 123.561 W/m²·K
Tube Velocity         : 0.111 m/s
Shell Velocity        : 0.022 m/s
Tube Pressure Drop    : 0.052 psi
Shell Pressure Drop   : 0.0002 psi
Tube Count            : 766
Tube Length           : 2.438 m
Status                : HYDRAULIC_LIMITED

Engineering Insights
------------------------------
• Moderate heat-transfer coefficient. Thermal performance may be limited.
• Tube-side velocity extremely low. High fouling risk and poor turbulence expected.
• Shell-side velocity extremely low. Possible vapor blanketing and poor shell-side heat transfer.
• Exchanger appears significantly oversized for the current operating conditions.

Warnings
------------------------------
• Tube velocity low (0.11 m/s)
• Shell velocity low (0.02 m/s)
```

---

## Discussion

This example demonstrates the **Rating Mode** capabilities of the **ProcessPI HeatExchangerEngine**.

Unlike **Design Mode**, where the exchanger geometry is determined automatically, **Rating Mode** evaluates the performance of an existing exchanger using its known mechanical dimensions.

The engine performs a complete thermal and hydraulic assessment while preserving the specified geometry.

During the evaluation, ProcessPI calculates:

- Heat duty
- Heat-transfer area
- Overall heat-transfer coefficient
- Tube-side heat-transfer coefficient
- Shell-side heat-transfer coefficient
- LMTD
- Reynolds number
- Tube velocity
- Shell velocity
- Tube-side pressure drop
- Shell-side pressure drop
- Engineering feasibility
- Hydraulic limitations
- Design warnings
- Engineering insights

---

## Rating Results

| Parameter | Value |
|-----------|-------|
| Service | Total Condenser |
| Mode | Rating |
| Method | Bell–Delaware |
| Heat Duty | 5012.19 kW |
| Heat Transfer Area | 111.78 m² |
| Overall U (Calculated) | 123.56 W/m²·K |
| Tube Count | 766 |
| Tube Length | 2.438 m |
| Tube Velocity | 0.111 m/s |
| Shell Velocity | 0.022 m/s |
| Tube Pressure Drop | 0.052 psi |
| Shell Pressure Drop | 0.0002 psi |
| Status | **HYDRAULIC_LIMITED** |

---

## Engineering Assessment

Although the condenser satisfies the required thermal duty, the hydraulic evaluation reveals that the exchanger is **significantly oversized** for the specified operating conditions.

The engine automatically identifies several performance concerns:

- Extremely low tube-side velocity
- Extremely low shell-side velocity
- Increased fouling potential
- Reduced turbulence
- Lower overall heat-transfer coefficient
- Possible vapor blanketing on the shell side

Because of these hydraulic limitations, the exchanger status is reported as **HYDRAULIC_LIMITED**.

This demonstrates one of the strengths of the ProcessPI HeatExchangerEngine—it evaluates **both thermal and hydraulic performance**, rather than relying solely on heat duty calculations.

---

## Raw Engineering Data

In addition to the summary report, the engine returns an extensive engineering dataset, including:

- Heat duty
- LMTD
- Overall U (assumed and calculated)
- Tube and shell heat-transfer coefficients
- Tube and shell Reynolds numbers
- Pressure drops
- Fluid assignment
- Feasibility summary
- Warning details
- Optimization history
- Convergence history
- Engineering insights
- Calculation trace

These values are available through:

```python
results.detailed_summary()
```

---

## Diagnostic Utilities

ProcessPI provides several reporting utilities for engineering analysis:

```python
results.summary()
```

Produces a concise engineering report.

```python
results.detailed_summary()
```

Returns the complete calculation dictionary.

```python
results.trace()
```

Displays the engineering calculation trace grouped by thermal, hydraulic, geometry, and phase-change calculations.

```python
results.debug_summary()
```

Returns diagnostic information including solver status, warnings, optimization actions, convergence information, and engineering validation results.

---

## Conclusion

This example illustrates how **Rating Mode** can be used to assess existing heat exchangers during plant revamps, debottlenecking studies, troubleshooting, and performance monitoring.

Rather than redesigning the equipment, the ProcessPI HeatExchangerEngine predicts how an existing exchanger will perform under current operating conditions and clearly identifies thermal and hydraulic limitations that may affect long-term operation.
