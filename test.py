from processpi.components.base import Component
from processpi.units import Temperature, Density, SpecificHeat
from processpi.components.water import Water

water = Water()
print(f"Name: {water.name}")
water_density = water.density(Temperature(353.15))  # Example temperature in °C
print(f"Density of water at 353.15 K : {water_density.value} {water_density.units}")
water_density = water.density(Temperature(273.16))  # Example temperature in °C
print(f"Density of water at 273.16 K : {water_density.value} {water_density.units}")
water_specific_heat = water.specific_heat(Temperature(533.15))  # Example temperature in °C
print(f"Specific heat of water at 533.15 K : {water_specific_heat.value} {water_specific_heat.units}")
water_specific_heat = water.specific_heat(Temperature(273.16))  # Example temperature in °C
print(f"Specific heat of water at 273.16 K : {water_specific_heat.value} {water_specific_heat.units}")
water_viscosity = water.viscosity(Temperature(646.15))  # Example temperature in °C
print(f"Viscosity of water at 646.15 K : {water_viscosity.value} {water_viscosity.units}")
water_viscosity = water.viscosity(Temperature(273.16))  # Example temperature in °C
print(f"Viscosity of water at 273.16 K : {water_viscosity.value} {water_viscosity.units}")
water_thermal_conductivity = water.thermal_conductivity(Temperature(633.15))  # Example temperature in °C
print(f"Thermal conductivity of water at 633.15 K : {water_thermal_conductivity.value} {water_thermal_conductivity.units}")
water_thermal_conductivity = water.thermal_conductivity(Temperature(273.16))  # Example temperature in °C
print(f"Thermal conductivity of water at 273.16 K : {water_thermal_conductivity.value} {water_thermal_conductivity.units}")
water_vapor_pressure = water.vapor_pressure(Temperature(647.096))  # Example temperature in °C
print(f"Vapor pressure of water at 647.096 K : {water_vapor_pressure.value} {water_vapor_pressure.units}")
water_vapor_pressure = water.vapor_pressure(Temperature(273.16))  # Example temperature in °C
print(f"Vapor pressure of water at 273.16 K : {water_vapor_pressure.value} {water_vapor_pressure.units}")
water_enthalpy = water.enthalpy(Temperature(647.096))  # Example temperature in °C
print(f"Enthalpy of water at 647.096 K : {water_enthalpy.value} {water_enthalpy.units}")
water_enthalpy = water.enthalpy(Temperature(273.16))  # Example temperature in °C
print(f"Enthalpy of water at 273.16 K : {water_enthalpy.value} {water_enthalpy.units}")