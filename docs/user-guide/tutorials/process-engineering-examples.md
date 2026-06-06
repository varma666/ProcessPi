# Process Engineering Examples

## Heat exchanger sizing

See the [Heat Exchanger Engineering Guide](../engineering/heat-exchangers.md) for a full water-cooler example using `HeatExchangerEngine`.

## Heat exchanger rating

Provide fixed geometry such as tube size, tube count, passes, length, and shell diameter to rate an existing shell-and-tube exchanger. Use `result.detailed_summary()` to inspect calculated U, velocities, and pressure drops.

## Fluid property calculation

```python
from processpi.components.water import Water
from processpi.units import Temperature

water = Water(temperature=Temperature(40, "C"))
print(water.density())
print(water.specific_heat())
```

## Pressure-drop calculation

```python
from processpi.calculations.fluids.pressure_drop_darcy import PressureDropDarcy

dp = PressureDropDarcy(
    friction_factor=0.02,
    length=100,
    diameter=0.1,
    density=1000,
    velocity=2,
).calculate()
print(dp)
```

## Equipment calculation pattern

1. Define unit-wrapped inputs.
2. Build streams or equipment objects.
3. Call `.fit()` for engine-style APIs when available.
4. Call `.run()` or `.calculate()`.
5. Inspect warnings and result dictionaries before using values in design decisions.
