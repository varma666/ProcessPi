# `processpi.units` API

## Overview

Engineering unit wrapper that stores a value and converts among supported units.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.units.__init__`

**Source:** `processpi/units/__init__.py`

**Purpose:** ProcessPI Units Module ====================== Automatically discovers and exposes all unit variable classes in this package. The base class `Variable` is always included. Example: from processpi.units import Length, Pressure, Temperature

No public classes or functions discovered in this module.

### `processpi.units.area`

**Source:** `processpi/units/area.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Area` | `Area(self, value, units='m2')` | Represents an Area quantity. Default SI unit: Square Meter (m2). Example: a1 = Area(100, "cm2") a2 = Area(0.5, "m2") | `to()` |

##### `Area`

Represents an Area quantity. Default SI unit: Square Meter (m2). Example: a1 = Area(100, "cm2") a2 = Area(0.5, "m2")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.base`

**Source:** `processpi/units/base.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Variable` | `Variable(self, value: float, units: str)` | A generic physical variable with value and units. Should be subclassed for specific physical types. | `to()`, `to_base()`, `from_base()` |

##### `Variable`

A generic physical variable with value and units. Should be subclassed for specific physical types.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_units: str)` | No source docstring provided. |
| `to_base` | `to_base(self)` | No source docstring provided. |
| `from_base` | `from_base(self, base_value: float, target_units: str)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.density`

**Source:** `processpi/units/density.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Density` | `Density(self, value, units='kg/m3')` | Represents a Density quantity. Default SI unit: kilograms per cubic meter (kg/m³). Example: d1 = Density(1000) # 1000 kg/m³ d2 = Density(1, "g/cm³") # 1 gram per cubic centimeter | `to()` |

##### `Density`

Represents a Density quantity. Default SI unit: kilograms per cubic meter (kg/m³). Example: d1 = Density(1000) # 1000 kg/m³ d2 = Density(1, "g/cm³") # 1 gram per cubic centimeter

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.diameter`

**Source:** `processpi/units/diameter.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Diameter` | `Diameter(self, value, units='m')` | Represents a Diameter quantity. Default SI unit: meters (m). | `to_base()`, `to()` |

##### `Diameter`

Represents a Diameter quantity. Default SI unit: meters (m).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to_base` | `to_base(self)` | Return the base (SI) value in meters. |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.dimensionless`

**Source:** `processpi/units/dimensionless.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Dimensionless` | `Dimensionless(self, value)` | Represents a dimensionless quantity (e.g., Reynolds number, friction factor). Default SI unit: none (unitless). Example: Re = Dimensionless(5000) # Reynolds number f = Dimensionless(0.02) # Friction factor | `to()` |

##### `Dimensionless`

Represents a dimensionless quantity (e.g., Reynolds number, friction factor). Default SI unit: none (unitless). Example: Re = Dimensionless(5000) # Reynolds number f = Dimensionless(0.02) # Friction factor

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit=None)` | Conversion is not applicable, but provided for interface consistency. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.heat_flow`

**Source:** `processpi/units/heat_flow.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatFlow` | `HeatFlow(self, value, units='W')` | Represents Heat Flow (total heat transfer rate). Default SI unit: W (Watts) Example: Q = HeatFlow(5000, "W") Q.to("kW") # -> 5.0 kW | `to()` |

##### `HeatFlow`

Represents Heat Flow (total heat transfer rate). Default SI unit: W (Watts) Example: Q = HeatFlow(5000, "W") Q.to("kW") # -> 5.0 kW

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.heat_flux`

**Source:** `processpi/units/heat_flux.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatFlux` | `HeatFlux(self, value, units='W/m2')` | Represents Heat Flux (heat transfer rate per unit area). Default SI unit: W/m2 (Watts per square meter) Example: q = HeatFlux(300, "W/m²") | `to()` |

##### `HeatFlux`

Represents Heat Flux (heat transfer rate per unit area). Default SI unit: W/m2 (Watts per square meter) Example: q = HeatFlux(300, "W/m²")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.heat_of_vaporization`

**Source:** `processpi/units/heat_of_vaporization.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatOfVaporization` | `HeatOfVaporization(self, value, units='J/kg')` | Represents Heat of Vaporization. Default SI unit: J/kg (Joules per kilogram) Example: hv1 = HeatOfVaporization(2257000) # 2.257 MJ/kg hv2 = HeatOfVaporization(540, "cal/g") # 540 cal/g = ~2.259 MJ/kg | `to()` |

##### `HeatOfVaporization`

Represents Heat of Vaporization. Default SI unit: J/kg (Joules per kilogram) Example: hv1 = HeatOfVaporization(2257000) # 2.257 MJ/kg hv2 = HeatOfVaporization(540, "cal/g") # 540 cal/g = ~2.259 MJ/kg

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.heat_transfer_coefficient`

**Source:** `processpi/units/heat_transfer_coefficient.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatTransferCoefficient` | `HeatTransferCoefficient(self, value, units='W/m2K')` | Represents Heat Transfer Coefficient. Default SI unit: W/m2K (Watts per square meter-Kelvin) Example: h = HeatTransferCoefficient(200, "W/m2K") | `to()` |

##### `HeatTransferCoefficient`

Represents Heat Transfer Coefficient. Default SI unit: W/m2K (Watts per square meter-Kelvin) Example: h = HeatTransferCoefficient(200, "W/m2K")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.length`

**Source:** `processpi/units/length.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Length` | `Length(self, value, units='m')` | Represents a Length quantity Variable. Default SI unit: Meters (m). Example: length = Length(30) # 30 meters length = Length(30, "in") # 30 inches | `to()` |

##### `Length`

Represents a Length quantity Variable. Default SI unit: Meters (m). Example: length = Length(30) # 30 meters length = Length(30, "in") # 30 inches

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.mass`

**Source:** `processpi/units/mass.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Mass` | `Mass(self, value, units='kg')` | Represents a Mass quantity. Default SI unit: Kilogram (kg). Example: m1 = Mass(500, "g") m2 = Mass(2, "kg") | `to()` |

##### `Mass`

Represents a Mass quantity. Default SI unit: Kilogram (kg). Example: m1 = Mass(500, "g") m2 = Mass(2, "kg")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.mass_flowrate`

**Source:** `processpi/units/mass_flowrate.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `MassFlowRate` | `MassFlowRate(self, value, units='kg/s')` | Represents a Mass Flow Rate quantity. Default SI unit: kilograms per second (kg/s). Example: m1 = MassFlowRate(100, "kg/h") m2 = MassFlowRate(0.5, "lb/s") | `to()` |

##### `MassFlowRate`

Represents a Mass Flow Rate quantity. Default SI unit: kilograms per second (kg/s). Example: m1 = MassFlowRate(100, "kg/h") m2 = MassFlowRate(0.5, "lb/s")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.molar_flowrate`

**Source:** `processpi/units/molar_flowrate.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `MolarFlowRate` | `MolarFlowRate(self, value, units='mol/s')` | Represents a Molar Flow Rate quantity. Default SI unit: mol/s. Example: n1 = MolarFlowRate(100, "mol/h") n2 = MolarFlowRate(0.5, "kmol/s") | `to()` |

##### `MolarFlowRate`

Represents a Molar Flow Rate quantity. Default SI unit: mol/s. Example: n1 = MolarFlowRate(100, "mol/h") n2 = MolarFlowRate(0.5, "kmol/s")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.power`

**Source:** `processpi/units/power.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Power` | `Power(self, value, units='W')` | Represents a Power quantity. Default SI unit: watt (W). Example: p1 = Power(1000) # 1000 W p2 = Power(1, "kW") # 1 kilowatt p3 = Power(0.5, "MW") # 0.5 megawatt p4 = Power(1.34, "hp") # 1.34 horsepower | `to()` |

##### `Power`

Represents a Power quantity. Default SI unit: watt (W). Example: p1 = Power(1000) # 1000 W p2 = Power(1, "kW") # 1 kilowatt p3 = Power(0.5, "MW") # 0.5 megawatt p4 = Power(1.34, "hp") # 1.34 horsepower

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.pressure`

**Source:** `processpi/units/pressure.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Pressure` | `Pressure(self, value, units='Pa')` | Represents a Pressure quantity. Default SI unit: Pascal (Pa). Example: p1 = Pressure(1, "atm") p2 = Pressure(101325, "Pa") | `to_base()`, `from_base()`, `to()` |

##### `Pressure`

Represents a Pressure quantity. Default SI unit: Pascal (Pa). Example: p1 = Pressure(1, "atm") p2 = Pressure(101325, "Pa")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to_base` | `to_base(self)` | Convert to base SI unit (Pa). |
| `from_base` | `from_base(self, base_value: float, target_units: str)` | Convert from Pa to target units and return a Pressure object. |
| `to` | `to(self, target_unit)` | Return new Pressure in target units. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.specific_heat`

**Source:** `processpi/units/specific_heat.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `SpecificHeat` | `SpecificHeat(self, value, units='kJ/kgK')` | Represents Specific Heat Capacity. Default SI unit: kJ/kgK Example: cp1 = SpecificHeat(4.186, "kJ/kgK") cp2 = SpecificHeat(1.0, "cal/gK") | `to()` |

##### `SpecificHeat`

Represents Specific Heat Capacity. Default SI unit: kJ/kgK Example: cp1 = SpecificHeat(4.186, "kJ/kgK") cp2 = SpecificHeat(1.0, "cal/gK")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.strings`

**Source:** `processpi/units/strings.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `StringUnit` | `StringUnit(self, value: str, category: str='string')` | Represents a string-based categorical quantity (e.g., flow type, phase, material category). Default unit: none (string). Example: flow = StringUnit("Laminar", "flow_type") phase = StringUnit("Gas", "phase_state") | `to()` |

##### `StringUnit`

Represents a string-based categorical quantity (e.g., flow type, phase, material category). Default unit: none (string). Example: flow = StringUnit("Laminar", "flow_type") phase = StringUnit("Gas", "phase_state")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit=None)` | Conversion is not applicable for string-based units. Provided only for interface consistency. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.temperature`

**Source:** `processpi/units/temperature.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Temperature` | `Temperature(self, value, units='K')` | Represents a Temperature quantity. Default SI unit: Kelvin (K). Example: t1 = Temperature(100, "C") # 100°C t2 = Temperature(373.15) # 373.15 K | `to()` |

##### `Temperature`

Represents a Temperature quantity. Default SI unit: Kelvin (K). Example: t1 = Temperature(100, "C") # 100°C t2 = Temperature(373.15) # 373.15 K

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.thermal_conductivity`

**Source:** `processpi/units/thermal_conductivity.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ThermalConductivity` | `ThermalConductivity(self, value, units='W/mK')` | Represents Thermal Conductivity of a material. Default SI unit: W/mK (Watts per meter-Kelvin) Example: k = ThermalConductivity(0.5, "W/mK") | `to()` |

##### `ThermalConductivity`

Represents Thermal Conductivity of a material. Default SI unit: W/mK (Watts per meter-Kelvin) Example: k = ThermalConductivity(0.5, "W/mK")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.thermal_resistance`

**Source:** `processpi/units/thermal_resistance.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ThermalResistance` | `ThermalResistance(self, value, units='K/W')` | Represents Thermal Resistance. Default SI unit: K/W (Kelvin per Watt) Example: r1 = ThermalResistance(0.5, "K/W") r2 = ThermalResistance(2, "C/W") | `to()` |

##### `ThermalResistance`

Represents Thermal Resistance. Default SI unit: K/W (Kelvin per Watt) Example: r1 = ThermalResistance(0.5, "K/W") r2 = ThermalResistance(2, "C/W")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.velocity`

**Source:** `processpi/units/velocity.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Velocity` | `Velocity(self, value, units='m/s')` | Represents a Velocity quantity. Default SI unit: meters per second (m/s). | `to_base()`, `from_base()`, `to()` |

##### `Velocity`

Represents a Velocity quantity. Default SI unit: meters per second (m/s).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to_base` | `to_base(self)` | No source docstring provided. |
| `from_base` | `from_base(self, base_value, target_units)` | No source docstring provided. |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.viscosity`

**Source:** `processpi/units/viscosity.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Viscosity` | `Viscosity(self, value, units='Pa·s')` | Represents a viscosity quantity. Supports both dynamic viscosity (Pa·s) and kinematic viscosity (m²/s). Example: v1 = Viscosity(1e-3, units="Pa·s") # Dynamic viscosity v2 = Viscosity(1, units="cSt") # Kinematic viscosity | `to()` |

##### `Viscosity`

Represents a viscosity quantity. Supports both dynamic viscosity (Pa·s) and kinematic viscosity (m²/s). Example: v1 = Viscosity(1e-3, units="Pa·s") # Dynamic viscosity v2 = Viscosity(1, units="cSt") # Kinematic viscosity

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.volume`

**Source:** `processpi/units/volume.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Volume` | `Volume(self, value, units='m3')` | Represents a Volume quantity. Default SI unit: Cubic Meter (m3). Example: v1 = Volume(1, "L") v2 = Volume(0.001, "m3") | `to()` |

##### `Volume`

Represents a Volume quantity. Default SI unit: Cubic Meter (m3). Example: v1 = Volume(1, "L") v2 = Volume(0.001, "m3")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.units.volumetric_flowrate`

**Source:** `processpi/units/volumetric_flowrate.py`

**Purpose:** Engineering unit wrapper that stores a value and converts among supported units.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `VolumetricFlowRate` | `VolumetricFlowRate(self, value, units='m3/s')` | Represents a Volumetric Flow Rate quantity. Default SI unit: Cubic meters per second (m³/s). Example: v1 = VolumetricFlowRate(2, "m3/h") v2 = VolumetricFlowRate(500, "L/min") | `to()`, `from_mass_flow()` |

##### `VolumetricFlowRate`

Represents a Volumetric Flow Rate quantity. Default SI unit: Cubic meters per second (m³/s). Example: v1 = VolumetricFlowRate(2, "m3/h") v2 = VolumetricFlowRate(500, "L/min")

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `to` | `to(self, target_unit)` | No source docstring provided. |
| `from_mass_flow` | `from_mass_flow(cls, mass_flow: 'MassFlowRate', density: 'Density')` | Convert a mass flow rate to volumetric flow rate using density. Q_vol = m_dot / rho |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.
