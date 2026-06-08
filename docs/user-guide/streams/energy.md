# EnergyStream

The **EnergyStream** class represents heat and work transfer within a process system.

## Features

- Track heat duties
- Track shaft work
- Aggregate energy balances
- Associate duties with equipment

## Example

```python
from processpi.streams import EnergyStream

energy = EnergyStream("Utilities")
energy.record(
    duty=50000,
    tag="Q_in",
    equipment="Heater-101"
)
```
