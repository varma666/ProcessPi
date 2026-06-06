# `processpi.components` API

## Overview

Chemical component/property model with DIPPR-style constants or category defaults.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.components.__init__`

**Source:** `processpi/components/__init__.py`

**Purpose:** ProcessPI Components Module =========================== Automatically discovers all chemical component classes in this package and exposes them for direct import. Example: from processpi.components import Water, Ethanol, Acetone

No public classes or functions discovered in this module.

### `processpi.components.aceticacid`

**Source:** `processpi/components/aceticacid.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `AceticAcid` | `AceticAcid(...)` | Represents the properties and constants for Acetic Acid ($CH_3COOH$). This class provides a comprehensive set of physical and thermodynamic properties for Acetic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature. | — |

##### `AceticAcid`

Represents the properties and constants for Acetic Acid ($CH_3COOH$). This class provides a comprehensive set of physical and thermodynamic properties for Acetic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.acetone`

**Source:** `processpi/components/acetone.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Acetone` | `Acetone(...)` | Represents the properties and constants for Acetone ($C_3H_6O$). This class provides a comprehensive set of physical and thermodynamic properties for Acetone, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature. | — |

##### `Acetone`

Represents the properties and constants for Acetone ($C_3H_6O$). This class provides a comprehensive set of physical and thermodynamic properties for Acetone, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.acrylicacid`

**Source:** `processpi/components/acrylicacid.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `AcrylicAcid` | `AcrylicAcid(...)` | Represents the properties and constants for Acrylic Acid ($C_3H_4O_2$). This class provides a comprehensive set of physical and thermodynamic properties for Acrylic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature. | — |

##### `AcrylicAcid`

Represents the properties and constants for Acrylic Acid ($C_3H_4O_2$). This class provides a comprehensive set of physical and thermodynamic properties for Acrylic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.air`

**Source:** `processpi/components/air.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Air` | `Air(...)` | Represents the properties and constants for Air (a molecular mixture). This class provides a comprehensive set of physical and thermodynamic properties for Air, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature. | — |

##### `Air`

Represents the properties and constants for Air (a molecular mixture). This class provides a comprehensive set of physical and thermodynamic properties for Air, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.ammonia`

**Source:** `processpi/components/ammonia.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Ammonia` | `Ammonia(...)` | Represents the properties and constants for Ammonia ($NH_3$). This class provides a comprehensive set of physical and thermodynamic properties for Ammonia, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature. | `specific_heat()` |

##### `Ammonia`

Represents the properties and constants for Ammonia ($NH_3$). This class provides a comprehensive set of physical and thermodynamic properties for Ammonia, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library. **Properties:** - `name`: The common name of the compound. - `formula`: The chemical formula. - `molecular_weight`: The molar mass in g/mol. - `_critical_temperature`: The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. - `_critical_pressure`: The critical pressure, the vapor pressure at the critical temperature. - `_critical_volume`: The critical volume per kmole. - `_critical_zc`: The critical compressibility factor. - `_critical_acentric_factor`: The acentric factor, a measure of the non-sphericity of the molecule. - `_density_constants`: Constants for calculating density as a function of temperature. - `_specific_heat_constants`: Constants for calculating specific heat capacity as a function of temperature. - `_viscosity_constants`: Constants for calculating viscosity as a function of temperature. - `_thermal_conductivity_constants`: Constants for calculating thermal conductivity as a function of temperature. - `_vapor_pressure_constants`: Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models. - `_enthalpy_constants`: Constants for calculating enthalpy as a function of temperature.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `specific_heat` | `specific_heat(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.base`

**Source:** `processpi/components/base.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PropertyMethod` | `PropertyMethod(self, func)` | Descriptor that allows both property-style and method-style access. Example: @PropertyMethod def density(self): return 100 # obj.density -> 100 # obj.density() -> 100 | — |
| `Component` | `Component(self, temperature: Temperature=None, pressure: Pressure=None, density: Density=None, specific_heat: SpecificHeat=None, viscosity: Viscosity=None, thermal_conductivity: ThermalConductivity=None, vapor_pressure: Pressure=None, enthalpy: HeatOfVaporization=None)` | Abstract base class for a chemical component with DIPPR-style property methods. | `name()`, `formula()`, `molecular_weight()`, `phase()`, `density()`, `specific_heat()`, `viscosity()`, `thermal_conductivity()`, `vapor_pressure()`, `enthalpy()` |

##### `PropertyMethod`

Descriptor that allows both property-style and method-style access. Example: @PropertyMethod def density(self): return 100 # obj.density -> 100 # obj.density() -> 100

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `Component`

Abstract base class for a chemical component with DIPPR-style property methods.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `name` | `name(self)` | No source docstring provided. |
| `formula` | `formula(self)` | No source docstring provided. |
| `molecular_weight` | `molecular_weight(self)` | No source docstring provided. |
| `phase` | `phase(self)` | Detects phase based on system pressure and vapor pressure. Returns: "gas" or "liquid" |
| `density` | `density(self)` | Returns density (kg/m³): - Gas: Ideal Gas Law (PV = nRT) - Liquid: DIPPR correlation |
| `specific_heat` | `specific_heat(self)` | No source docstring provided. |
| `viscosity` | `viscosity(self)` | Returns viscosity (Pa·s): - Liquid: DIPPR correlation - Gas: Sutherland approximation |
| `thermal_conductivity` | `thermal_conductivity(self)` | No source docstring provided. |
| `vapor_pressure` | `vapor_pressure(self)` | No source docstring provided. |
| `enthalpy` | `enthalpy(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.benzene`

**Source:** `processpi/components/benzene.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Benzene` | `Benzene(...)` | Represents the chemical component Benzene ($C_6H_6$). This class provides a comprehensive set of physical and thermodynamic properties for Benzene, including its molecular weight, critical properties, and constants for various property calculations. | `specific_heat()`, `hx_data()`, `httype()` |

##### `Benzene`

Represents the chemical component Benzene ($C_6H_6$). This class provides a comprehensive set of physical and thermodynamic properties for Benzene, including its molecular weight, critical properties, and constants for various property calculations.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `specific_heat` | `specific_heat(self)` | Calculates the specific heat of Benzene at a given temperature. The calculation uses a polynomial fit for specific heat ($C_p$) as a function of temperature. The function selects a set of constants based on the provided temperature value to ensure accuracy. Args: temperature (Temperature): The temperature at which to calculate the specific heat, in Kelvin. Returns: SpecificHeat: The calculated specific heat in units of J/kgK. |
| `hx_data` | `hx_data(self)` | No source docstring provided. |
| `httype` | `httype(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.benzoicacid`

**Source:** `processpi/components/benzoicacid.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `BenzoicAcid` | `BenzoicAcid(...)` | No source docstring provided. See module purpose and examples. | — |

##### `BenzoicAcid`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.bromine`

**Source:** `processpi/components/bromine.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Bromine` | `Bromine(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Bromine`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.butane`

**Source:** `processpi/components/butane.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Butane` | `Butane(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Butane`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.carbondioxide`

**Source:** `processpi/components/carbondioxide.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Carbondioxide` | `Carbondioxide(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Carbondioxide`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.carbonmonoxide`

**Source:** `processpi/components/carbonmonoxide.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CarbonMonoxide` | `CarbonMonoxide(...)` | No source docstring provided. See module purpose and examples. | `specific_heat()` |

##### `CarbonMonoxide`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `specific_heat` | `specific_heat(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.carbontetrachloride`

**Source:** `processpi/components/carbontetrachloride.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CarbonTetrachloride` | `CarbonTetrachloride(...)` | No source docstring provided. See module purpose and examples. | — |

##### `CarbonTetrachloride`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.chlorine`

**Source:** `processpi/components/chlorine.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Chlorine` | `Chlorine(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Chlorine`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.chlorobenzene`

**Source:** `processpi/components/chlorobenzene.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ChloroBenzene` | `ChloroBenzene(...)` | No source docstring provided. See module purpose and examples. | — |

##### `ChloroBenzene`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.chloroform`

**Source:** `processpi/components/chloroform.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Chloroform` | `Chloroform(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Chloroform`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.chloromethane`

**Source:** `processpi/components/chloromethane.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ChloroMethane` | `ChloroMethane(...)` | No source docstring provided. See module purpose and examples. | — |

##### `ChloroMethane`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.constants`

**Source:** `processpi/components/constants.py`

**Purpose:** Physical constants used across Components.

No public classes or functions discovered in this module.

### `processpi.components.cyanogen`

**Source:** `processpi/components/cyanogen.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Cyanogen` | `Cyanogen(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Cyanogen`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.cyclohexene`

**Source:** `processpi/components/cyclohexene.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Cyclohexane` | `Cyclohexane(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Cyclohexane`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.ethane`

**Source:** `processpi/components/ethane.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Ethane` | `Ethane(...)` | No source docstring provided. See module purpose and examples. | `specific_heat()` |

##### `Ethane`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `specific_heat` | `specific_heat(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.ethanol`

**Source:** `processpi/components/ethanol.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Ethanol` | `Ethanol(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Ethanol`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.ethylacetate`

**Source:** `processpi/components/ethylacetate.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `EthlylAcetate` | `EthlylAcetate(...)` | No source docstring provided. See module purpose and examples. | — |

##### `EthlylAcetate`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.ethylene`

**Source:** `processpi/components/ethylene.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Ethlylene` | `Ethlylene(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Ethlylene`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.fluorine`

**Source:** `processpi/components/fluorine.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Fluorine` | `Fluorine(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Fluorine`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.fluorobenzene`

**Source:** `processpi/components/fluorobenzene.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `FluoroBenzene` | `FluoroBenzene(...)` | No source docstring provided. See module purpose and examples. | — |

##### `FluoroBenzene`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.formicacid`

**Source:** `processpi/components/formicacid.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `FormicAcid` | `FormicAcid(...)` | No source docstring provided. See module purpose and examples. | — |

##### `FormicAcid`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.gas`

**Source:** `processpi/components/gas.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Gas` | `Gas(...)` | No source docstring provided. See module purpose and examples. | `density()` |

##### `Gas`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `density` | `density(self)` | Density for a generic gas using the ideal gas equation: rho = (P * M) / (R * T) |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.inorganic_liquid`

**Source:** `processpi/components/inorganic_liquid.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `InorganicLiquid` | `InorganicLiquid(...)` | No source docstring provided. See module purpose and examples. | — |

##### `InorganicLiquid`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.methanol`

**Source:** `processpi/components/methanol.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Methanol` | `Methanol(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Methanol`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.oil`

**Source:** `processpi/components/oil.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Oil` | `Oil(...)` | No source docstring provided. See module purpose and examples. | `hx_data()`, `httype()` |

##### `Oil`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `hx_data` | `hx_data(self)` | No source docstring provided. |
| `httype` | `httype(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.organic_liquid`

**Source:** `processpi/components/organic_liquid.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `OrganicLiquid` | `OrganicLiquid(...)` | No source docstring provided. See module purpose and examples. | `hx_data()`, `httype()` |

##### `OrganicLiquid`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `hx_data` | `hx_data(self)` | No source docstring provided. |
| `httype` | `httype(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.steam`

**Source:** `processpi/components/steam.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Steam` | `Steam(self, temperature: Temperature=None, pressure: Pressure=None, phase: Literal['liquid', 'vapor']='vapor')` | No source docstring provided. See module purpose and examples. | `density()`, `specific_heat()`, `viscosity()`, `thermal_conductivity()`, `vapor_pressure()`, `enthalpy()` |

##### `Steam`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `density` | `density(self)` | No source docstring provided. |
| `specific_heat` | `specific_heat(self)` | No source docstring provided. |
| `viscosity` | `viscosity(self)` | No source docstring provided. |
| `thermal_conductivity` | `thermal_conductivity(self)` | No source docstring provided. |
| `vapor_pressure` | `vapor_pressure(self)` | No source docstring provided. |
| `enthalpy` | `enthalpy(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.toluene`

**Source:** `processpi/components/toluene.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Toluene` | `Toluene(...)` | No source docstring provided. See module purpose and examples. | `hx_data()`, `httype()` |

##### `Toluene`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `hx_data` | `hx_data(self)` | No source docstring provided. |
| `httype` | `httype(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.vapor`

**Source:** `processpi/components/vapor.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Vapor` | `Vapor(...)` | No source docstring provided. See module purpose and examples. | — |

##### `Vapor`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.components.water`

**Source:** `processpi/components/water.py`

**Purpose:** Chemical component/property model with DIPPR-style constants or category defaults.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Water` | `Water(...)` | No source docstring provided. See module purpose and examples. | `density()`, `hx_data()`, `httype()` |

##### `Water`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `density` | `density(self, temperature: Temperature=None)` | No source docstring provided. |
| `hx_data` | `hx_data(self)` | No source docstring provided. |
| `httype` | `httype(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.
