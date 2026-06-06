# Components, Properties, and Streams

## Overview

ProcessPI stores chemical-component behavior under `processpi.components`, unit wrappers under `processpi.units`, and stream state under `processpi.streams`. The current component model combines fixed component constants, DIPPR-style correlations, ideal-gas density behavior, and user overrides passed into the component constructor.

## Component database structure

Each concrete component class subclasses `processpi.components.base.Component` and provides at minimum:

- `name`
- `formula`
- `molecular_weight` in g/mol
- correlation constants such as density, heat capacity, viscosity, thermal conductivity, vapor pressure, or heat of vaporization when available

Implemented component modules include water, steam, air, ammonia, benzene, toluene, ethanol, methanol, acetone, acetic acid, carbon dioxide, carbon monoxide, chlorine, chloroform, bromine, butane, ethane, and additional organic/inorganic categories. See the generated components API inventory for the exact import paths and public classes.

## Property access pattern

Component properties use a descriptor that supports both property-style and method-style access:

```python
from processpi.components.water import Water
from processpi.units import Temperature, Pressure

water = Water(temperature=Temperature(25, "C"), pressure=Pressure(1, "atm"))

rho = water.density()       # method-style
rho_value = water.density.value  # property-style wrapper value
cp = water.specific_heat()
phase = water.phase()
```

## Units used

| Property | Typical wrapper | Common base unit |
| --- | --- | --- |
| Temperature | `Temperature` | K |
| Pressure | `Pressure` | Pa |
| Density | `Density` | kg/m3 |
| Specific heat | `SpecificHeat` | J/kgK |
| Viscosity | `Viscosity` | Pa.s |
| Thermal conductivity | `ThermalConductivity` | W/mK |
| Heat of vaporization | `HeatOfVaporization` | J/kg |
| Mass flow | `MassFlowRate` | kg/s |
| Volumetric flow | `VolumetricFlowRate` | m3/s |

## Data validation methods

- Component property methods raise `ValueError` when a calculated value is unphysical, for example negative or excessively high heat capacity.
- Unit wrappers raise conversion errors for unsupported units.
- `MaterialStream` normalizes composition fractions and derives mass or molar flow when enough density, volumetric flow, composition, and molecular-weight data are available.

## Property retrieval example

```python
from processpi.components.benzene import Benzene
from processpi.units import Temperature, Pressure

benzene = Benzene(temperature=Temperature(60, "C"), pressure=Pressure(1, "atm"))
print(benzene.density().to("kg/m3"))
print(benzene.viscosity().to("Pa.s"))
print(benzene.vapor_pressure().to("bar"))
```

## Thermodynamic calculation example

```python
from processpi.calculations.heat_transfer.hx_kern import SensibleDuty

# m_dot [kg/s], cp [J/kgK], temperatures [K or C differences]
result = SensibleDuty(m_dot=1.0, cp=4180, t_in=80, t_out=40).calculate()
print(result.to("kW"))
```

## Mixture and stream example

`MaterialStream` supports composition dictionaries and average molecular weight calculation when molecular weights are supplied.

```python
from processpi.streams.material import MaterialStream
from processpi.units import MassFlowRate, Temperature, Pressure

stream = MaterialStream(
    name="binary_feed",
    mass_flow=MassFlowRate(1.0, "kg/s"),
    temperature=Temperature(30, "C"),
    pressure=Pressure(1, "bar"),
    composition={"ethanol": 0.4, "water": 0.6},
    basis="mole",
    molecular_weights={"ethanol": 46.07, "water": 18.015},
)

print(stream.avg_mw())
print(stream.molar_flow())
```

## Limitations

- The component system is not a full equation-of-state package.
- Mixture property blending is limited; users should provide validated mixture properties for design-critical calculations.
- Correlation ranges are not universally enforced for every component.
