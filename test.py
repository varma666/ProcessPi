from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.equipment import Equipment
from processpi.pipelines.network import PipelineNetwork
from processpi.units import *
from processpi.components import Water
from processpi.components.carbonmonoxide import CarbonMonoxide
from processpi.components.vapor import Vapor
from processpi.components.organic_liquid import OrganicLiquid

print("\n=== A) Quick single-pipe demos ===")

# --- A1) Velocity and pressure drop calculation ---
pipe_diameter_a1 = Diameter(15.5, "in")
PipelineEngine().fit(
    flowrate=VolumetricFlowRate(3000, "gal/min"),
    diameter=pipe_diameter_a1,
    length=Length(1000, "ft"),
    density=Density(998, "kg/m3"),
    viscosity=Viscosity(1.0, "cP"),
    fittings=[Fitting(fitting_type="long_radius_90_deg", quantity=6, diameter=pipe_diameter_a1)]
).run().summary()

# --- A2) Pipe sizing with available ΔP ---
fluid = Water()
PipelineEngine().fit(
    flowrate=VolumetricFlowRate(75, "L/s"),
    length=Length(180, "m"),
    density=Density(998, "kg/m3"),
    viscosity=Viscosity(1.0, "cP"),
    available_dp=Pressure(1.2, "bar"),
    fluid=fluid
).run().summary()

print("\n=== B) Textbook-style problems ===")

# --- B1) CO2 line sizing ---
m_dot = MassFlowRate(1000_000, "kg/day")
mu_CO2 = Viscosity(0.016, "cP")
rho_CO2 = Density(1.61, "kg/m3")
placeholder_diameter = Diameter(2, "in")
fluid = Water()

co2_fittings = [
    Fitting(fitting_type="long_radius_90_deg", quantity=8, diameter=placeholder_diameter),
    Fitting(fitting_type="swing_check_valve", quantity=1, diameter=placeholder_diameter),
    Fitting(fitting_type="entrance_sharp", quantity=1, diameter=placeholder_diameter),
]

print("\n--- B1) CO2 line sizing ---")
co2_size_results = PipelineEngine().fit(
    mass_flowrate=m_dot,
    length=Length(800, "m"),
    available_dp=Pressure(24, "kPa"),
    density=rho_CO2,
    viscosity=mu_CO2,
    fittings=co2_fittings,
    material="CS",
    fluid=fluid
).run()
co2_size_results.summary()

# --- B2) CO line sizing ---
co_mdot = MassFlowRate(1500, "kg/h")
fluid = Vapor()
mu_CO = Viscosity(0.018, "cP")
rho_CO = Density(1.06, "kg/m3")


co_fittings = [
    Fitting(fitting_type="gate_valve", quantity=2, diameter=placeholder_diameter),
    Fitting(fitting_type="standard_elbow_45_deg", quantity=3, diameter=placeholder_diameter),
    Fitting(fitting_type="standard_elbow_90_deg", quantity=6, diameter=placeholder_diameter),
]

print("\n--- B2) CO line sizing ---")
co_size_results = PipelineEngine().fit(
    mass_flowrate=co_mdot,
    length=Length(4, "km"),
    available_dp=Pressure(50, "kPa"),
    density=rho_CO,
    viscosity=mu_CO,
    fittings=co_fittings,
    material="CS",
    fluid = fluid
).run()
co_size_results.summary()

# --- B3) Water by gravity: CS vs Concrete ---
fluid = Water()
m_dot_water = MassFlowRate(100_000, "kg/h")
rho_water40 = Density(993, "kg/m3")
mu_water40 = Viscosity(0.67, "cP")
dp_available_water = Pressure(rho_water40.to("kg/m3").value * 9.81 * 6.0, "Pa")

placeholder_diameter_b3 = Diameter(10, "in")
eq_len_fit = Fitting(fitting_type="long_radius_90_deg", quantity=12, diameter=placeholder_diameter_b3)

print("\n--- B3) Water by gravity: size comparison ---")
print("Assumption: Available head for friction = 6 m (8 m static diff − 2 m submergence).")
print("\n[Carbon Steel]")
water_cs_results = PipelineEngine().fit(
    mass_flowrate=m_dot_water,
    length=Length(3000, "m"),
    available_dp=dp_available_water,
    density=rho_water40,
    viscosity=mu_water40,
    fittings=[eq_len_fit],
    material="CS",
    fluid = fluid
).run()
water_cs_results.summary()

print("\n[Concrete]")
water_concrete_results = PipelineEngine().fit(
    mass_flowrate=m_dot_water,
    length=Length(3000, "m"),
    available_dp=dp_available_water,
    density=rho_water40,
    viscosity=mu_water40,
    fittings=[eq_len_fit],
    material="Concrete",
    fluid = fluid
).run()
water_concrete_results.summary()

# --- B4) Organic liquid: uniform pipe size + residual ΔP ---
m_dot_org = MassFlowRate(5000, "kg/h")
rho_org = Density(930, "kg/m3")
mu_org = Viscosity(0.91, "cP")
fluid = OrganicLiquid()

org_fittings = [
    Fitting(fitting_type="standard_elbow_90_deg", quantity=6, diameter=placeholder_diameter),
    Fitting(fitting_type="standard_tee_through_flow", quantity=2, diameter=placeholder_diameter),
    Fitting(fitting_type="gate_valve", quantity=4, diameter=placeholder_diameter),
    Fitting(fitting_type="globe_valve", quantity=1, diameter=placeholder_diameter),
]

orifice_dp = Equipment(name="orifice meter", pressure_drop=Pressure(40, "kPa"))

print("\n--- B4) Organic liquid sizing & residual ΔP ---")
results_b4 = PipelineEngine().fit(
    mass_flowrate=m_dot_org,
    length=Length(50, "m"),
    density=rho_org,
    viscosity=mu_org,
    fittings=org_fittings,
    equipment=[orifice_dp],
    available_dp=Pressure(600, "kPa"),
    material="CS",
    fluid = fluid
).run()
summary_b4 = results_b4.summary()
residual_pa = Pressure(600, "kPa").to("Pa").value - results_b4.total_pressure_drop

print(f"Residual ΔP available for control valve: {residual_pa}")