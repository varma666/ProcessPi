# Flowsheet + HeatExchanger (Named Port) Example

```python
from processpi.integration.flowsheet import Flowsheet
from processpi.equipment.heatexchangers.base import HeatExchanger
from processpi.streams.material import MaterialStream
from processpi.units import Temperature, Pressure, MassFlowRate

fs = Flowsheet("HX Demo")
hx = HeatExchanger(name="E-101")

hot_in = MaterialStream(
    name="hot_in",
    temperature=Temperature(380, "K"),
    pressure=Pressure(2, "bar"),
    mass_flow=MassFlowRate(1.2, "kg/s"),
)
hot_out = MaterialStream(name="hot_out")
cold_in = MaterialStream(
    name="cold_in",
    temperature=Temperature(300, "K"),
    pressure=Pressure(2, "bar"),
    mass_flow=MassFlowRate(1.0, "kg/s"),
)
cold_out = MaterialStream(name="cold_out")

fs.add_equipment(hx)

# Legacy 3-arg mode (stream -> unit inlet)
fs.connect(hot_in, hx, "hot_in")
fs.connect(cold_in, hx, "cold_in")

# New explicit 5-arg mode (stream from unit:port to unit:port)
source = HeatExchanger(name="Source")
fs.add_equipment(source)
fs.connect(hot_out, source, "hot_out", hx, "hot_in")

# Sequential solve
fs.solve_sequential()
```
