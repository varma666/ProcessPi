# Getting Started Tutorial

## Install

```bash
pip install processpi
```

For local development from the repository:

```bash
pip install -e .
```

## First calculation

```python
from processpi.calculations.fluids.velocity import FluidVelocity

velocity = FluidVelocity(volumetric_flow_rate=0.01, diameter=0.1).calculate()
print(velocity)
```

## Project structure

- `processpi.components` — component/property classes.
- `processpi.units` — engineering unit wrappers and conversions.
- `processpi.calculations` — reusable calculation primitives.
- `processpi.pipelines` — pipe, pump, fitting, network, standards, and hydraulic engine models.
- `processpi.equipment.heatexchangers` — exchanger sizing/rating models.
- `processpi.streams` — material and energy streams.
- `processpi.integration` — flowsheet connection layer.

## Next steps

- Use the heat-exchanger engineering guide for thermal equipment.
- Use the pipeline examples for hydraulic-network calculations.
- Use the generated API reference when you need exact class and method names.
