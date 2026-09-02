# Pressure Vessels

`PressureVessel` is a first-class ProcessPI equipment module for **preliminary
ASME Section VIII, Division 1 internal-pressure sizing**. It uses ProcessPI's
existing units and shared material-property database. It is not a certified
code-design or fabrication package.

```python
from processpi.equipment import PressureVessel
from processpi.units import Diameter, Length, Pressure, Temperature, Volume

vessel = PressureVessel(
    volume=Volume(25, "m3"),
    design_pressure=Pressure(10, "bar"),
    design_temperature=Temperature(150, "C"),
    vessel_type="horizontal",
    head_type="2:1_ellipsoidal",
    material="SA-240-304",
    corrosion_allowance=Length(3, "mm"),
    joint_efficiency=0.85,
)
vessel.add_nozzle("N1", Diameter(100, "mm"), service="Feed")
vessel.add_manhole("MH1", Diameter(450, "mm"))
result = vessel.design()
print(result)
```

`PressureVessels` remains an alias of `PressureVessel` for compatibility.

## Inputs and materials

Use ProcessPI `Pressure`, `Temperature`, `Length`, `Diameter`, and `Volume`
objects (plain numbers use SI units). `design_pressure` and
`design_temperature` are required. `operating_pressure` and
`operating_temperature` can be recorded separately; they are **not** silently
substituted for design conditions. Corrosion allowance must be non-negative and
joint efficiency must be in `(0, 1]`.

The model queries `processpi.pipelines.materials.MATERIAL_PROPERTIES` through
its shared helpers. Existing keys such as `CS`, `SS304`, and `SS316` work;
`SA-516-70`, `SA-240-304`, and `SA-240-316` are normalized to their respective
ProcessPI keys. The material table's temperature limit is validated and its
allowable stress/density are reported without pressure-vessel-specific
temperature derating.

Supported vessel types are `horizontal`, `vertical`, and `spherical`.
Supported heads are `flat`, `2:1_ellipsoidal`, `torispherical`,
`hemispherical`, and `conical`.

## Geometry sizing and volume verification

Geometry is always retained or selected transparently:

| Inputs supplied | Geometry mode | Behaviour |
| --- | --- | --- |
| Diameter and length/height | `USER_SPECIFIED` | Retains both user dimensions and checks actual volume. |
| Diameter only | `DIAMETER_SPECIFIED` | Retains diameter and selects the smallest configured straight length/height meeting volume. |
| Length/height only | `LENGTH_SPECIFIED` | Retains the axial dimension and selects the smallest configured diameter meeting volume. |
| Neither | `AUTO_SIZED` | Selects configured diameter/length candidates meeting volume and aspect-ratio constraints with minimum excess volume. |

`volume` is only mandatory when sizing must fill missing geometry. The default
candidate diameters are 1000–6000 mm and candidate straight lengths/heights are
2000–12000 mm; they are **preliminary fabrication candidates**, not ASME
requirements. Override them with `standard_diameters` and `standard_lengths`.
The default length/diameter or height/diameter range is 1.0–6.0 and can be
configured with `min_length_to_diameter`, `max_length_to_diameter`,
`min_height_to_diameter`, and `max_height_to_diameter`.

Every result reports required volume, shell volume, head volume, total internal
volume, excess volume, volume margin, selected dimensions, aspect ratio, sizing
mode, and selection basis. Final volume is always recalculated from the final
geometry.

## Sizing, accessories, and checks

Shell pressure thickness is reported separately from corrosion allowance and
nominal selected thickness. The preliminary design basis references
UG-27(c)(1), UG-32, UG-34, and UG-99(b). Standard nominal thickness candidates
are configurable through `standard_thicknesses`.

`add_nozzle()` and `add_manhole()` store records per vessel instance. Results
include shell/head/nozzle/manhole/reinforcement/total empty weights and
preliminary hydrotest pressure, liquid volume, liquid weight, and estimated
test-condition weight. `vessel.design_check()` supplies traceable statuses and
actual/required/margin values for material, conditions, geometry, volume,
thicknesses, hydrotest, and openings.

Nozzle/manhole reinforcement is deliberately `INCOMPLETE`: the result exposes
required opening area and placeholders for available area, neck, shell, and pad
contributions. It never reports that incomplete reinforcement as a pass.

## Limitations

This module is preliminary internal-pressure sizing only. External
pressure/vacuum, complete nozzle reinforcement, supports, wind, seismic,
fatigue, MDMT, PWHT, flanges, and other load cases remain **INCOMPLETE** and
must be completed by the responsible engineer using the applicable code and
project requirements.
