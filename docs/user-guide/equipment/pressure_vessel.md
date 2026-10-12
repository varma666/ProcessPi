# Pressure Vessels

`PressureVessel` is a native ProcessPI equipment module for preliminary ASME
Section VIII, Division 1 internal-pressure sizing.

## With the engine

`PressureVesselEngine` has the same fit/run interface as the other ProcessPI
engines:

```python
from processpi.equipment import PressureVesselEngine
from processpi.units import Diameter, Length, Pressure, Temperature

model = PressureVesselEngine(name="V-101")
model.fit(
    vessel_type="horizontal",
    head_type="ellipsoidal",
    design_pressure=Pressure(10, "bar"),
    design_temperature=Temperature(150, "C"),
    diameter=Diameter(1.2),
    length=Length(4),
    corrosion_allowance=Length(3, "mm"),
    material="sa-516-70",
    joint_efficiency=0.85,
    nozzles=[{"name": "N1", "diameter": Length(0.1, "m")}],
)
results = model.run()
print(results.summary())
print(results["selected_thickness"])
```

`fit()` takes every `PressureVessel` input, plus optional `nozzles` and
`manholes` lists of keyword dicts for `add_nozzle` / `add_manhole`. `run()`
returns `PressureVesselResults`; `summary()` and `results()` return the last run.

## With the class

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

## Notes

- Design temperatures down to -20°F (-29°C) use the first allowable-stress
  column of ASME Section II, Part D, Table 1A ("-20 to 100°F"; metric
  "-30 to 40°C"). Below that, the MDMT rules (UCS-66) apply and are not
  evaluated.
- `ug27_validity` reports whether the cylindrical shell is inside the range of
  the UG-27(c)(1) formula (t <= R/2 and P <= 0.385 S E); outside it a warning
  says the Appendix 1-2 thick-wall rules apply.
- The weight estimate uses the surface area of the chosen heads (flat,
  ellipsoidal, torispherical, hemispherical or conical).

## Scope

The implementation is preliminary internal-pressure sizing based on UG-27(c)(1),
UG-34, UG-32, and UG-99(b). It does **not** complete external-pressure/vacuum,
nozzle reinforcement, support, wind, seismic, fatigue, MDMT, PWHT, or flange
design. Those limitations are also returned in the result warnings.
