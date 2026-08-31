# Pressure Vessels

`PressureVessel` is a native ProcessPI equipment module for preliminary ASME
Section VIII, Division 1 internal-pressure sizing.

```python
from processpi.equipment import PressureVessel
from processpi.units import Diameter, Length, Pressure, Temperature

vessel = PressureVessel(
    vessel_type="horizontal",
    head_type="ellipsoidal",
    design_pressure=Pressure(10, "bar"),
    design_temperature=Temperature(150, "C"),
    diameter=Diameter(1.2),
    length=Length(4),
    corrosion_allowance=Length(3, "mm"),
    material="sa-516-70",
    joint_efficiency=0.85,
)
result = vessel.design()
```

The result includes shell/head thicknesses, a selected standard thickness,
volume, estimated shell weight, hydrotest pressure, nozzle/manhole records,
and design warnings. `PressureVessels` remains an alias for backwards
compatibility.

## Scope

The implementation is preliminary internal-pressure sizing based on UG-27(c)(1),
UG-34, UG-32, and UG-99(b). It does **not** complete external-pressure/vacuum,
nozzle reinforcement, support, wind, seismic, fatigue, MDMT, PWHT, or flange
design. Those limitations are also returned in the result warnings.
