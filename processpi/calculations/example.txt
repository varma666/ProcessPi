"""
Example usage of the ProcessPI `CalculationEngine`.

Covers:
1. Basic fluid velocity (US units)
2. Basic fluid velocity (Metric units)
3. Velocity and Reynolds number (US units)
4. Velocity and Reynolds number (Metric units)
5. Friction factor using Colebrook-White (US units)
6. Darcy pressure drop (US units)
7. Long pipeline pressure drop (Metric units)
8. Pressure drop using Hazen-Williams (US units)
"""

from processpi.calculations import CalculationEngine
from processpi.units import VolumetricFlowRate, Diameter, Density, Viscosity, Length

# Initialize the engine (used across all examples)
engine = CalculationEngine()

# ------------------------------------------------------------------------------
# 1. Basic fluid velocity (US Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(3000, 'gal/min')
diameter = Diameter(15.5, 'in')
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)
print("\n--- Example 1: Fluid Velocity (US Units) ---")
print(f"Velocity: {velocity.to('ft/s')}")

# ------------------------------------------------------------------------------
# 2. Basic fluid velocity (Metric Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(75, 'L/s')
diameter = Diameter(180, 'mm')
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)
print("\n--- Example 2: Fluid Velocity (Metric Units) ---")
print(f"Velocity: {velocity}")

# ------------------------------------------------------------------------------
# 3. Velocity and Reynolds number (US Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(6000, 'gal/min')
diameter = Diameter(19.25, 'in')
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)
density = Density(998, 'kg/m3')
viscosity = Viscosity(1.0, 'cSt')
nre = engine.calculate("reynolds_number", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)
print("\n--- Example 3: Velocity and Reynolds Number (US Units) ---")
print(f"Velocity: {velocity.to('ft/s')}")
print(f"Reynolds Number: {nre}")

# ------------------------------------------------------------------------------
# 4. Velocity and Reynolds number (Metric Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(640, 'm3/h')
diameter = Diameter(380, 'mm')
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)
density = Density(998, 'kg/m3')
viscosity = Viscosity(1.0, 'cSt')
nre = engine.calculate("reynolds_number", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)
print("\n--- Example 4: Velocity and Reynolds Number (Metric Units) ---")
print(f"Velocity: {velocity}")
print(f"Reynolds Number: {nre}")

# ------------------------------------------------------------------------------
# 5. Friction factor using Colebrook-White (US Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(3000, "gal/min")
diameter = Diameter(15.25, "in")
roughness = Length(0.002, "in")
density = Density(998, "kg/m3")
viscosity = Viscosity(1.0, "cP")
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)
nre = engine.calculate("nre", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)
friction_factor = engine.calculate("friction_factor_colebrookwhite", diameter=diameter, roughness=roughness, reynolds_number=nre)
print("\n--- Example 5: Friction Factor (Colebrook-White, US Units) ---")
print(f"Velocity: {velocity}")
print(f"Reynolds Number: {nre}")
print(f"Friction Factor: {friction_factor}")

# ------------------------------------------------------------------------------
# 6. Darcy pressure drop (US Units)
# ------------------------------------------------------------------------------
length = Length(1000, "ft")
pressure_drop = engine.calculate("pressure_drop_darcy", friction_factor=friction_factor, length=length, diameter=diameter, density=density, velocity=velocity)
print("\n--- Example 6: Darcy Pressure Drop (US Units) ---")
print(f"Pressure Drop: {pressure_drop.to('psi')}")

# ------------------------------------------------------------------------------
# 7. Long pipeline pressure drop (Metric Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(34000, "m3/h")
diameter = Diameter(2, "m")
roughness = Length(0.05, "mm")
density = Density(998, "kg/m3")
viscosity = Viscosity(1.0, "cP")
velocity = engine.calculate("fluid_velocity", volumetric_flow_rate=volumetric_flow_rate, diameter=diameter)
nre = engine.calculate("nre", density=density, velocity=velocity, diameter=diameter, viscosity=viscosity)
friction_factor = engine.calculate("friction_factor_colebrookwhite", diameter=diameter, roughness=roughness, reynolds_number=nre)
length = Length(5, "km")
pressure_drop = engine.calculate("pressure_drop_darcy", friction_factor=friction_factor, length=length, diameter=diameter, density=density, velocity=velocity)
print("\n--- Example 7: Long Pipeline Pressure Drop (Metric Units) ---")
print(f"Velocity: {velocity}")
print(f"Reynolds Number: {nre}")
print(f"Friction Factor: {friction_factor}")
print(f"Pressure Drop: {pressure_drop.to('kPa')}")

# ------------------------------------------------------------------------------
# 8. Pressure drop using Hazen-Williams (US Units)
# ------------------------------------------------------------------------------
volumetric_flow_rate = VolumetricFlowRate(3000, "gal/min")
diameter = Diameter(15.25, "in")
density = Density(998, "kg/m3")
length = Length(1000, "ft")
pressure_drop = engine.calculate("pressure_drop_hazen_williams", length=length, flow_rate=volumetric_flow_rate, diameter=diameter, density=density, coefficient=120)
print("\n--- Example 8: Pressure Drop (Hazen-Williams, US Units) ---")
print(f"Pressure Drop: {pressure_drop.to('psi')}")
