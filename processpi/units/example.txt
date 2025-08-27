"""
Example usage of the ProcessPI `units` module.

Covers conversions for:
1. Velocity
2. Diameter
3. Density
4. Heat Flux
5. Heat of Vaporization
6. Heat Transfer Coefficient
7. Length
8. Mass Flow Rate
9. Mass
10. Power
11. Pressure
12. Specific Heat
13. Temperature
14. Thermal Conductivity
15. Viscosity
16. Volume
17. Volumetric Flow Rate
"""

from processpi.units import *

# ------------------------------------------------------------------------------
# 1. Velocity conversion
# ------------------------------------------------------------------------------
v = Velocity(1.55, "m/s")
v_converted = v.to("ft/s")
print("\n--- Velocity ---")
print(f"Converted: {v_converted}, Original: {v}")

# ------------------------------------------------------------------------------
# 2. Diameter conversion
# ------------------------------------------------------------------------------
d = Diameter(10, "in")
d_converted = d.to("cm")
print("\n--- Diameter ---")
print(f"Converted: {d_converted}, Original: {d}")

# ------------------------------------------------------------------------------
# 3. Density conversion
# ------------------------------------------------------------------------------
den = Density(1000, "kg/m3")
den_converted = den.to("g/cm3")
print("\n--- Density ---")
print(f"Converted: {den_converted}, Original: {den}")

# ------------------------------------------------------------------------------
# 4. Heat Flux conversion
# ------------------------------------------------------------------------------
heatflux = HeatFlux(5000, "W/m2")
heatflux_converted = heatflux.to("BTU/hft2")
print("\n--- Heat Flux ---")
print(f"Converted: {heatflux_converted}, Original: {heatflux}")

# ------------------------------------------------------------------------------
# 5. Heat of Vaporization conversion
# ------------------------------------------------------------------------------
heat_of_vaporization = HeatOfVaporization(2260, "J/kg")
heat_of_vaporization_converted = heat_of_vaporization.to("BTU/lb")
print("\n--- Heat of Vaporization ---")
print(f"Converted: {heat_of_vaporization_converted}, Original: {heat_of_vaporization}")

# ------------------------------------------------------------------------------
# 6. Heat Transfer Coefficient conversion
# ------------------------------------------------------------------------------
heat_transfer = HeatTransferCoefficient(1000, "W/m2K")
heat_transfer_converted = heat_transfer.to("BTU/hft2F")
print("\n--- Heat Transfer Coefficient ---")
print(f"Converted: {heat_transfer_converted}, Original: {heat_transfer}")

# ------------------------------------------------------------------------------
# 7. Length conversion
# ------------------------------------------------------------------------------
length = Length(5, "m")
length_converted = length.to("ft")
print("\n--- Length ---")
print(f"Converted: {length_converted}, Original: {length}")

# ------------------------------------------------------------------------------
# 8. Mass Flow Rate conversion
# ------------------------------------------------------------------------------
mass_flow = MassFlowRate(100, "kg/s")
mass_flow_converted = mass_flow.to("lb/min")
print("\n--- Mass Flow Rate ---")
print(f"Converted: {mass_flow_converted}, Original: {mass_flow}")

# ------------------------------------------------------------------------------
# 9. Mass conversion
# ------------------------------------------------------------------------------
mass = Mass(10, "kg")
mass_converted = mass.to("lb")
print("\n--- Mass ---")
print(f"Converted: {mass_converted}, Original: {mass}")

# ------------------------------------------------------------------------------
# 10. Power conversion
# ------------------------------------------------------------------------------
power = Power(1000, "W")
power_converted = power.to("BTU/h")
print("\n--- Power ---")
print(f"Converted: {power_converted}, Original: {power}")

# ------------------------------------------------------------------------------
# 11. Pressure conversion
# ------------------------------------------------------------------------------
pressure = Pressure(101325, "Pa")
pressure_converted = pressure.to("psi")
print("\n--- Pressure ---")
print(f"Converted: {pressure_converted}, Original: {pressure}")

# ------------------------------------------------------------------------------
# 12. Specific Heat conversion
# ------------------------------------------------------------------------------
specific_heat = SpecificHeat(4184, "J/kgK")
specific_heat_converted = specific_heat.to("BTU/lbF")
print("\n--- Specific Heat ---")
print(f"Converted: {specific_heat_converted}, Original: {specific_heat}")

# ------------------------------------------------------------------------------
# 13. Temperature conversion
# ------------------------------------------------------------------------------
temp = Temperature(100, "C")
temp_converted = temp.to("F")
print("\n--- Temperature ---")
print(f"Converted: {temp_converted}, Original: {temp}")

# ------------------------------------------------------------------------------
# 14. Thermal Conductivity conversion
# ------------------------------------------------------------------------------
thermal_conductivity = ThermalConductivity(200, "W/mK")
thermal_conductivity_converted = thermal_conductivity.to("BTU/hftF")
print("\n--- Thermal Conductivity ---")
print(f"Converted: {thermal_conductivity_converted}, Original: {thermal_conductivity}")

# ------------------------------------------------------------------------------
# 15. Viscosity conversion
# ------------------------------------------------------------------------------
viscosity = Viscosity(1.55, "Pa·s")
viscosity_converted = viscosity.to("cP")
print("\n--- Viscosity ---")
print(f"Converted: {viscosity_converted}, Original: {viscosity}")

# ------------------------------------------------------------------------------
# 16. Volume conversion
# ------------------------------------------------------------------------------
volume = Volume(1, "L")
volume_converted = volume.to("m3")
print("\n--- Volume ---")
print(f"Converted: {volume_converted}, Original: {volume}")

# ------------------------------------------------------------------------------
# 17. Volumetric Flow Rate conversion
# ------------------------------------------------------------------------------
flow = VolumetricFlowRate(3000, "gal/min")
flow_converted = flow.to("m3/s")
print("\n--- Volumetric Flow Rate ---")
print(f"Converted: {flow_converted}, Original: {flow}")
