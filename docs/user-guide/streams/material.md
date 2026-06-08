# MaterialStream

The **MaterialStream** class represents a process fluid stream and stores thermodynamic state, flow information, and composition data.

## Features

- Single-component and multi-component streams
- Automatic composition normalization
- Supports volumetric, mass, and molar flow rates
- Component-based initialization
- Manual property-based initialization

## Example

```python
from processpi.streams import MaterialStream
from processpi.components import Water
from processpi.units import Temperature, MassFlowRate

stream = MaterialStream(
    "Hot Water",
    component=Water(),
    temperature=Temperature(350, "K"),
    mass_flow=MassFlowRate(2, "kg/s")
)
```
