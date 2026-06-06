# Advanced Workflows

## Programmatic calculations

ProcessPI classes are regular Python objects. A common pattern is to wrap calculation inputs in dictionaries or dataclasses, loop through design cases, and collect `.calculate()` or `.detailed_summary()` outputs.

```python
from processpi.calculations.fluids.reynolds_number import ReynoldsNumber

cases = [
    {"density": 1000, "velocity": 1.0, "diameter": 0.05, "viscosity": 0.001},
    {"density": 1000, "velocity": 2.0, "diameter": 0.05, "viscosity": 0.001},
]

for case in cases:
    print(ReynoldsNumber(**case).calculate())
```

## Batch heat-exchanger screening

```python
results = []
for tube_length in [3.0, 4.5, 6.0]:
    result = HeatExchangerEngine().fit(
        hot_in=hot,
        cold_in=cold,
        hot_out=hot_out,
        hx_type="shell_and_tube",
        tube_length=tube_length,
    ).run()
    results.append(result.detailed_summary())
```

## Integration into larger projects

Use ProcessPI as a calculation kernel:

- Keep stream creation at project boundaries.
- Convert external units into ProcessPI units before calculation.
- Store raw result dictionaries for auditability.
- Treat warning lists as required engineering review items.

## Automation guidance

- Validate inputs before batch runs.
- Record package version, source assumptions, and units with every calculation set.
- Avoid using preliminary exchanger outputs as final mechanical design.
