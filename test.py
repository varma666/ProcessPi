# ============================================
# EXAMPLE 1 — BENZENE COOLING
# ============================================

# Problem:
# 21000 kg/h of liquid benzene at 90°C is to be cooled to 30°C
# using a heat exchanger.
# Cooling water available: 60500 kg/h at 15°C
# Maximum allowable pressure drop: 1 bar on both sides


# ============================================
# IMPORTS
# ============================================

from processpi.units import *
from processpi.components import *
from processpi.streams import MaterialStream
from processpi.equipment.heatexchangers import HeatExchangerEngine


# ============================================
# DEFINE FLUIDS
# ============================================

benzene = Benzene(
    density=Density(876, "kg/m3"),
    viscosity=Viscosity(0.6, "cP"),
    specific_heat=SpecificHeat(1.74, "kJ/kgK"),
)

water = Water(
    density=Density(1000, "kg/m3"),
    viscosity=Viscosity(1.0, "cP"),
    specific_heat=SpecificHeat(4.18, "kJ/kgK"),
)


# ============================================
# DEFINE STREAMS
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

# Outlet temperature unknown → to be calculated
cold_out = MaterialStream(
    "cold_out",
    component=water
)


# ============================================
# RUN HEAT EXCHANGER MODEL
# ============================================

hx = HeatExchangerEngine()

hx.fit(
    hot_in=hot_in,
    hot_out=hot_out,
    cold_in=cold_in,
    cold_out=cold_out,
    U=HeatTransferCoefficient(300, "W/m2K"),
    shell_dp=Pressure(1, "bar"),
    tube_dp=Pressure(1, "bar"),
)

hx.run()

results = hx.results()


# ============================================
# DISPLAY RESULTS
# ============================================

print("\n=== DESIGN RESULTS ===")
print(results)