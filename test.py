# ============================================================
# DEBUG LOGGING
# ============================================================
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s"
)

# ============================================================
# PROCESSPI — HORIZONTAL n-PROPANOL CONDENSER
# Example 12.1 Conversion
# ============================================================

from processpi.units import *
from processpi.components import *
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchangerEngine


# ============================================================
# COMPONENTS
# ============================================================

water = Water()
n_propanol = OrganicLiquid()


# ============================================================
# HOT SIDE — n-PROPANOL VAPOR
# ============================================================

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


# ============================================================
# COLD SIDE — COOLING WATER
# ============================================================

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


# ============================================================
# CONDENSER
# ============================================================

hx = HeatExchangerEngine(
    method="bell_delaware"
)

hx.fit(

    hx_type="condenser",

    hot_in=hot_in,
    hot_out=hot_out,

    cold_in=cold_in,
    cold_out=cold_out,

    # 285 Btu/lb ≈ 663000 J/kg
    latent_heat=663000,

    orientation="horizontal",

    shell_passes=1,
    tube_passes=2,

    tube_length=Length(8, "ft").to("m").value,

    tube_outer_diameter=Length(0.75, "in").to("m").value,

    tube_gauge=16,

    tube_pitch=Length(1.0625, "in").to("m").value,

    tube_layout="triangular",

    shell_dp=Pressure(2, "psi"),

    tube_dp=Pressure(10, "psi"),
    U=HeatTransferCoefficient(568, "W/m2K"),

    mode="design",

    #verbose=True,
)

# ============================================================
# RUN
# ============================================================

results = hx.run()

# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 80)
print("HORIZONTAL n-PROPANOL CONDENSER")
print("=" * 80)

print(results.summary())

print("\n")
print("=" * 80)
print("RAW RESULT DATA")
print("=" * 80)

for k, v in results.data.items():
    print(f"{k:25s} : {v}")