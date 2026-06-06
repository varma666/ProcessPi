# `processpi.calculations` API

## Overview

Calculation framework module.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.calculations.__init__`

**Source:** `processpi/calculations/__init__.py`

**Purpose:** ProcessPI Calculations Module ============================= This module provides core calculation classes and dynamically loads all available calculation submodules under `processpi.calculations`. Example: import processpi.calculations as calc engine = calc.CalculationEngine() water_dp = calc.fluids.PressureDropDarcy(...)

No public classes or functions discovered in this module.

### `processpi.calculations.base`

**Source:** `processpi/calculations/base.py`

**Purpose:** Calculation framework module.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CalculationBase` | `CalculationBase(self, **kwargs)` | Abstract base class for all calculation modules in the processpi library. This class defines a standard interface and common utility methods for all calculation classes, ensuring they have a consistent structure for input validation, calculation execution, and result handling. All specific calculation classes (e.g., `PressureDropDarcy`, `ReynoldsNumber`) must inherit from this class. | `validate_inputs()`, `calculate()`, `get_inputs()`, `to_dict()` |

##### `CalculationBase`

Abstract base class for all calculation modules in the processpi library. This class defines a standard interface and common utility methods for all calculation classes, ensuring they have a consistent structure for input validation, calculation execution, and result handling. All specific calculation classes (e.g., `PressureDropDarcy`, `ReynoldsNumber`) must inherit from this class.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Abstract method to validate the inputs. Subclasses must implement this method to check for the presence and validity of required inputs. It should raise a `ValueError` if any input is missing or invalid. |
| `calculate` | `calculate(self)` | Abstract method to perform the calculation. Subclasses must implement this method to execute the core calculation logic. The method should return the results, typically as a dictionary or a specific unit object. |
| `get_inputs` | `get_inputs(self)` | Returns the original inputs provided during initialization. Returns: dict: A dictionary of the input parameters. |
| `to_dict` | `to_dict(self)` | Performs the calculation and returns a dictionary with both inputs and results. This method combines the inputs and the output of the `calculate()` method into a single, comprehensive dictionary. Returns: dict: A dictionary containing two keys: "inputs" and "results". |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.engine`

**Source:** `processpi/calculations/engine.py`

**Purpose:** This module acts as the central engine for performing calculations in the ProcessPI library. The `CalculationEngine` class serves as a central hub, providing a registry for all available calculation classes. This design allows users to execute calculations by name without needing to directly import or instantiate each class.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CalculationEngine` | `CalculationEngine(self)` | The central hub for all ProcessPI calculations. The engine maintains a registry of calculation classes and provides a single, consistent method to execute any registered calculation by its name. This decouples the calling code from the specific implementation details of each calculation. | `register_calculation()`, `calculate()` |

##### `CalculationEngine`

The central hub for all ProcessPI calculations. The engine maintains a registry of calculation classes and provides a single, consistent method to execute any registered calculation by its name. This decouples the calling code from the specific implementation details of each calculation.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `register_calculation` | `register_calculation(self, name: str, calc_class: Type)` | Dynamically registers a new calculation class with the engine. This method allows for extending the engine's capabilities at runtime without modifying the source code. Args: name (str): The string name to be used for the calculation. calc_class (Type): The calculation class to register. |
| `calculate` | `calculate(self, name: str, **kwargs)` | Executes a calculation by its registered name. The method looks up the calculation class in the registry, instantiates it with the provided keyword arguments, and then runs its `calculate` method. Args: name (str): The name of the calculation to execute. **kwargs: Arbitrary keyword arguments to be passed as inputs to the calculation class. Returns: Any: The result of the calculation, as returned by the `calculate` method of the specific class. Raises: ValueError: If the specified calculation name is not found in the registry. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.__init__`

**Source:** `processpi/calculations/fluids/__init__.py`

**Purpose:** ProcessPI Fluid Mechanics Calculations ====================================== This module loads all calculation classes for fluid mechanics automatically. Available calculations: - PressureDropDarcy - PressureDropFanning - PumpPower - ReynoldsNumber - OptimumPipeDiameter - FluidVelocity - ColebrookWhite - PressureDropHazenWilliams - TypeOfFlow

No public classes or functions discovered in this module.

### `processpi.calculations.fluids.flow_type`

**Source:** `processpi/calculations/fluids/flow_type.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `TypeOfFlow` | `TypeOfFlow(...)` | A class to determine the type of fluid flow based on the Reynolds number. This class serves as a calculation engine for classifying flow regimes as Laminar, Transitional, or Turbulent according to standard engineering criteria. It inherits from `CalculationBase` to ensure a standardized input/output structure. **Flow Regime Criteria:** * Laminar Flow: Occurs when the fluid moves in smooth, parallel layers, with little to no mixing. This regime is defined by a Reynolds number (Re) less than 2000. * Transitional Flow: An unstable regime where the flow can fluctuate between laminar and turbulent characteristics. It is defined by a Reynolds number between 2000 and 4000 (inclusive). * Turbulent Flow: Characterized by chaotic, unpredictable fluid motion with significant mixing. This regime is defined by a Reynolds number greater than 4000. **Inputs:** * `reynolds_number` (Re): A dimensionless quantity representing the ratio of inertial forces to viscous forces. **Output:** * A `StringUnit` containing the determined flow type ("Laminar", "Transitional", or "Turbulent"). | `validate_inputs()`, `calculate()` |

##### `TypeOfFlow`

A class to determine the type of fluid flow based on the Reynolds number. This class serves as a calculation engine for classifying flow regimes as Laminar, Transitional, or Turbulent according to standard engineering criteria. It inherits from `CalculationBase` to ensure a standardized input/output structure. **Flow Regime Criteria:** * Laminar Flow: Occurs when the fluid moves in smooth, parallel layers, with little to no mixing. This regime is defined by a Reynolds number (Re) less than 2000. * Transitional Flow: An unstable regime where the flow can fluctuate between laminar and turbulent characteristics. It is defined by a Reynolds number between 2000 and 4000 (inclusive). * Turbulent Flow: Characterized by chaotic, unpredictable fluid motion with significant mixing. This regime is defined by a Reynolds number greater than 4000. **Inputs:** * `reynolds_number` (Re): A dimensionless quantity representing the ratio of inertial forces to viscous forces. **Output:** * A `StringUnit` containing the determined flow type ("Laminar", "Transitional", or "Turbulent").

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. Ensures that the 'reynolds_number' key is present in the inputs dictionary. Raises a ValueError if the key is missing. |
| `calculate` | `calculate(self)` | Performs the calculation to determine the flow type. Retrieves the Reynolds number from the inputs and applies the flow regime criteria to classify the flow. Returns: StringUnit: An object containing the flow type as a string. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.friction_factor_colebrookwhite`

**Source:** `processpi/calculations/fluids/friction_factor_colebrookwhite.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ColebrookWhite` | `ColebrookWhite(...)` | A class to calculate the Darcy friction factor using the Colebrook–White equation. The Colebrook-White equation is an empirical formula used to determine the Darcy friction factor (f) for fluid flow in pipes, particularly for turbulent flow. Because the equation is implicit, the friction factor must be solved for iteratively. **Formula (Implicit):** $ rac{1}{\sqrt{f}} = -2.0 \cdot \log_{10} \left( rac{\epsilon/D}{3.7} + rac{2.51}{Re \cdot \sqrt{f}} ight) $ **Inputs:** * `reynolds_number` (Re): A dimensionless quantity. * `diameter` (D): The internal diameter of the pipe. * `roughness` (ε): The absolute roughness of the pipe surface. **Output:** * A `Dimensionless` object containing the calculated friction factor (f). | `validate_inputs()`, `calculate()` |

##### `ColebrookWhite`

A class to calculate the Darcy friction factor using the Colebrook–White equation. The Colebrook-White equation is an empirical formula used to determine the Darcy friction factor (f) for fluid flow in pipes, particularly for turbulent flow. Because the equation is implicit, the friction factor must be solved for iteratively. **Formula (Implicit):** $ rac{1}{\sqrt{f}} = -2.0 \cdot \log_{10} \left( rac{\epsilon/D}{3.7} + rac{2.51}{Re \cdot \sqrt{f}} ight) $ **Inputs:** * `reynolds_number` (Re): A dimensionless quantity. * `diameter` (D): The internal diameter of the pipe. * `roughness` (ε): The absolute roughness of the pipe surface. **Output:** * A `Dimensionless` object containing the calculated friction factor (f).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. Ensures that 'reynolds_number', 'diameter', and 'roughness' are present in the inputs dictionary. Raises a ValueError if any key is missing. |
| `calculate` | `calculate(self)` | Calculates the Darcy friction factor. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.optimium_pipe_dia`

**Source:** `processpi/calculations/fluids/optimium_pipe_dia.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `OptimumPipeDiameter` | `OptimumPipeDiameter(...)` | A class to calculate the optimum pipe diameter using an empirical formula. This class provides a method for calculating the most efficient pipe diameter for a given set of fluid properties and flow rate, based on an empirical correlation. The calculated optimum diameter is then mapped to the nearest available standard pipe size. **Empirical Formula:** $D_{opt} = 293 \cdot Q_{mass}^{0.53} \cdot ho^{-0.37}$ Where: * $D_{opt}$ = Optimum diameter [mm] * $Q_{mass}$ = Mass flow rate [kg/s] * $ ho$ = Fluid density [kg/m³] **Inputs:** * `flow_rate` (Q): The volumetric flow rate of the fluid. * `density` ($ ho$): The density of the fluid. **Output:** * The nearest standard pipe diameter as a `Diameter` object in millimeters. | `validate_inputs()`, `calculate()` |

##### `OptimumPipeDiameter`

A class to calculate the optimum pipe diameter using an empirical formula. This class provides a method for calculating the most efficient pipe diameter for a given set of fluid properties and flow rate, based on an empirical correlation. The calculated optimum diameter is then mapped to the nearest available standard pipe size. **Empirical Formula:** $D_{opt} = 293 \cdot Q_{mass}^{0.53} \cdot ho^{-0.37}$ Where: * $D_{opt}$ = Optimum diameter [mm] * $Q_{mass}$ = Mass flow rate [kg/s] * $ ho$ = Fluid density [kg/m³] **Inputs:** * `flow_rate` (Q): The volumetric flow rate of the fluid. * `density` ($ ho$): The density of the fluid. **Output:** * The nearest standard pipe diameter as a `Diameter` object in millimeters.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method ensures that the 'flow_rate' and 'density' keys are present in the inputs dictionary, raising a ValueError if any required input is missing. |
| `calculate` | `calculate(self)` | Performs the calculation to find the optimum and nearest standard pipe diameter. The method first calculates the mass flow rate from the volumetric flow rate and density. It then applies the empirical formula to find the optimum diameter. Finally, it uses an external utility function to find the closest standard pipe size and returns it. Returns: Diameter: The nearest standard pipe diameter. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.pressure_drop_darcy`

**Source:** `processpi/calculations/fluids/pressure_drop_darcy.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PressureDropDarcy` | `PressureDropDarcy(...)` | A class to calculate the pressure drop in a pipe using the Darcy–Weisbach equation. This formula is a widely used tool in fluid dynamics to calculate the loss of pressure due to friction along a given length of pipe. It is applicable for both laminar and turbulent flow regimes. **Formula:** $ \Delta P = f \cdot rac{L}{D} \cdot rac{ ho \cdot v^2}{2} $ Where: * $ \Delta P $ = Pressure drop [Pa] * $ f $ = Darcy friction factor [dimensionless] * $ L $ = Pipe length [m] * $ D $ = Pipe diameter [m] * $ ho $ = Fluid density [kg/m³] * $ v $ = Fluid velocity [m/s] **Inputs:** * `friction_factor`: The friction factor of the pipe. * `length`: The length of the pipe. * `diameter`: The internal diameter of the pipe. * `density`: The density of the fluid. * `velocity`: The velocity of the fluid. **Output:** * A `Pressure` object containing the calculated pressure drop in Pascals (Pa). | `validate_inputs()`, `calculate()` |

##### `PressureDropDarcy`

A class to calculate the pressure drop in a pipe using the Darcy–Weisbach equation. This formula is a widely used tool in fluid dynamics to calculate the loss of pressure due to friction along a given length of pipe. It is applicable for both laminar and turbulent flow regimes. **Formula:** $ \Delta P = f \cdot rac{L}{D} \cdot rac{ ho \cdot v^2}{2} $ Where: * $ \Delta P $ = Pressure drop [Pa] * $ f $ = Darcy friction factor [dimensionless] * $ L $ = Pipe length [m] * $ D $ = Pipe diameter [m] * $ ho $ = Fluid density [kg/m³] * $ v $ = Fluid velocity [m/s] **Inputs:** * `friction_factor`: The friction factor of the pipe. * `length`: The length of the pipe. * `diameter`: The internal diameter of the pipe. * `density`: The density of the fluid. * `velocity`: The velocity of the fluid. **Output:** * A `Pressure` object containing the calculated pressure drop in Pascals (Pa).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method checks for the presence of all necessary keys in the inputs dictionary and raises a ValueError if any are missing. |
| `calculate` | `calculate(self)` | Performs the pressure drop calculation using the Darcy–Weisbach equation. Retrieves all required input values and applies the formula to compute the pressure drop. The result is returned as a `Pressure` object. Returns: Pressure: The calculated pressure drop in Pascals. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.pressure_drop_fanning`

**Source:** `processpi/calculations/fluids/pressure_drop_fanning.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PressureDropFanning` | `PressureDropFanning(...)` | A class to calculate the pressure drop in a pipe using the Fanning equation. The Fanning friction factor is a dimensionless number that relates the shear stress at the pipe wall to the kinetic energy of the fluid. The Fanning equation is widely used in chemical and process engineering for pressure drop calculations. **Formula:** $ \Delta P = 4 \cdot f_F \cdot rac{L}{D} \cdot rac{ ho \cdot v^2}{2} $ Where: * $ \Delta P $ = Pressure drop [Pa] * $ f_F $ = Fanning friction factor [dimensionless] * $ L $ = Pipe length [m] * $ D $ = Pipe diameter [m] * $ ho $ = Fluid density [kg/m³] * $ v $ = Fluid velocity [m/s] **Inputs:** * `friction_factor`: The Fanning friction factor of the pipe. * `length`: The length of the pipe. * `diameter`: The internal diameter of the pipe. * `density`: The density of the fluid. * `velocity`: The velocity of the fluid. **Output:** * A `Pressure` object containing the calculated pressure drop in Pascals (Pa). | `validate_inputs()`, `calculate()` |

##### `PressureDropFanning`

A class to calculate the pressure drop in a pipe using the Fanning equation. The Fanning friction factor is a dimensionless number that relates the shear stress at the pipe wall to the kinetic energy of the fluid. The Fanning equation is widely used in chemical and process engineering for pressure drop calculations. **Formula:** $ \Delta P = 4 \cdot f_F \cdot rac{L}{D} \cdot rac{ ho \cdot v^2}{2} $ Where: * $ \Delta P $ = Pressure drop [Pa] * $ f_F $ = Fanning friction factor [dimensionless] * $ L $ = Pipe length [m] * $ D $ = Pipe diameter [m] * $ ho $ = Fluid density [kg/m³] * $ v $ = Fluid velocity [m/s] **Inputs:** * `friction_factor`: The Fanning friction factor of the pipe. * `length`: The length of the pipe. * `diameter`: The internal diameter of the pipe. * `density`: The density of the fluid. * `velocity`: The velocity of the fluid. **Output:** * A `Pressure` object containing the calculated pressure drop in Pascals (Pa).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method ensures all necessary keys are present in the inputs dictionary, raising a ValueError if any are missing. |
| `calculate` | `calculate(self)` | Performs the pressure drop calculation using the Fanning equation. Retrieves all required input values and applies the formula to compute the pressure drop. The result is returned as a `Pressure` object. Returns: Pressure: The calculated pressure drop in Pascals. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.pressure_drop_hazen_williams`

**Source:** `processpi/calculations/fluids/pressure_drop_hazen_williams.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PressureDropHazenWilliams` | `PressureDropHazenWilliams(...)` | A class to calculate the pressure drop in a pipe using the Hazen–Williams equation. The Hazen–Williams equation is an empirical formula for calculating head loss in a pipe due to friction. It is primarily used for water systems and is simpler than the Darcy-Weisbach equation as it does not require an iterative solution for the friction factor. **Formula (SI units):** $ h_f = 10.67 \cdot L \cdot Q^{1.852} / (C^{1.852} \cdot D^{4.87}) $ **Where:** * $ h_f $ = head loss [m] * $ L $ = pipe length [m] * $ Q $ = volumetric flow rate [m³/s] * $ C $ = Hazen-Williams roughness coefficient [dimensionless] * $ D $ = pipe diameter [m] The pressure drop ($\Delta P$) is then calculated from the head loss ($h_f$) using the following relationship: $ \Delta P = \rho \cdot g \cdot h_f $ **Inputs:** * `length`: The length of the pipe. * `flow_rate`: The volumetric flow rate of the fluid. * `coefficient`: The Hazen-Williams roughness coefficient. * `diameter`: The internal diameter of the pipe. * `density`: The density of the fluid. **Output:** * A `Pressure` object containing the calculated pressure drop in Pascals (Pa). | `validate_inputs()`, `calculate()` |

##### `PressureDropHazenWilliams`

A class to calculate the pressure drop in a pipe using the Hazen–Williams equation. The Hazen–Williams equation is an empirical formula for calculating head loss in a pipe due to friction. It is primarily used for water systems and is simpler than the Darcy-Weisbach equation as it does not require an iterative solution for the friction factor. **Formula (SI units):** $ h_f = 10.67 \cdot L \cdot Q^{1.852} / (C^{1.852} \cdot D^{4.87}) $ **Where:** * $ h_f $ = head loss [m] * $ L $ = pipe length [m] * $ Q $ = volumetric flow rate [m³/s] * $ C $ = Hazen-Williams roughness coefficient [dimensionless] * $ D $ = pipe diameter [m] The pressure drop ($\Delta P$) is then calculated from the head loss ($h_f$) using the following relationship: $ \Delta P = \rho \cdot g \cdot h_f $ **Inputs:** * `length`: The length of the pipe. * `flow_rate`: The volumetric flow rate of the fluid. * `coefficient`: The Hazen-Williams roughness coefficient. * `diameter`: The internal diameter of the pipe. * `density`: The density of the fluid. **Output:** * A `Pressure` object containing the calculated pressure drop in Pascals (Pa).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method checks for the presence of all necessary keys in the inputs dictionary and raises a ValueError if any are missing. |
| `calculate` | `calculate(self)` | Performs the pressure drop calculation using the Hazen-Williams equation. The method first computes the head loss using the Hazen-Williams formula and then converts the head loss to pressure drop. The result is returned as a `Pressure` object. Returns: Pressure: The calculated pressure drop in Pascals. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.pump_power`

**Source:** `processpi/calculations/fluids/pump_power.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PumpPower` | `PumpPower(...)` | A class to calculate the required pump power for a fluid system. This class computes both the hydraulic power (the power imparted to the fluid) and the shaft power (the power required at the pump's shaft, accounting for efficiency). The calculation is based on the fluid's flow rate, head, density, and the pump's mechanical efficiency. **Formulas:** * Hydraulic Power ($P_{hydraulic}$) = $ ho \cdot g \cdot Q \cdot H $ * Shaft Power ($P_{shaft}$) = $ P_{hydraulic} / \eta $ Where: * $P_{hydraulic}$ = Hydraulic (water) power [W] * $P_{shaft}$ = Shaft power [W] * $ ho $ = Fluid density [kg/m³] * $ g $ = Acceleration due to gravity (9.81 m/s²) * $ Q $ = Volumetric flow rate [m³/s] * $ H $ = Total dynamic head [m] * $ \eta $ = Pump efficiency [decimal] **Inputs:** * `flow_rate` (Q): The volumetric flow rate. * `head` (H): The total dynamic head. * `density` ($ ho$): The fluid's density. * `efficiency` ($\eta$): The pump's efficiency as a decimal (0 to 1). **Outputs:** * A dictionary containing two power values: * "hydraulic_power_W": The calculated hydraulic power in Watts. * "shaft_power_W": The calculated shaft power in Watts. | `validate_inputs()`, `calculate()` |

##### `PumpPower`

A class to calculate the required pump power for a fluid system. This class computes both the hydraulic power (the power imparted to the fluid) and the shaft power (the power required at the pump's shaft, accounting for efficiency). The calculation is based on the fluid's flow rate, head, density, and the pump's mechanical efficiency. **Formulas:** * Hydraulic Power ($P_{hydraulic}$) = $ ho \cdot g \cdot Q \cdot H $ * Shaft Power ($P_{shaft}$) = $ P_{hydraulic} / \eta $ Where: * $P_{hydraulic}$ = Hydraulic (water) power [W] * $P_{shaft}$ = Shaft power [W] * $ ho $ = Fluid density [kg/m³] * $ g $ = Acceleration due to gravity (9.81 m/s²) * $ Q $ = Volumetric flow rate [m³/s] * $ H $ = Total dynamic head [m] * $ \eta $ = Pump efficiency [decimal] **Inputs:** * `flow_rate` (Q): The volumetric flow rate. * `head` (H): The total dynamic head. * `density` ($ ho$): The fluid's density. * `efficiency` ($\eta$): The pump's efficiency as a decimal (0 to 1). **Outputs:** * A dictionary containing two power values: * "hydraulic_power_W": The calculated hydraulic power in Watts. * "shaft_power_W": The calculated shaft power in Watts.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method checks for the presence of all necessary keys in the inputs dictionary and ensures that the efficiency is a valid value between 0 and 1. |
| `calculate` | `calculate(self)` | Performs the pump power calculation. The method first calculates the hydraulic power and then the shaft power, accounting for the pump's efficiency. Returns: dict: A dictionary with the calculated hydraulic and shaft power. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.reynolds_number`

**Source:** `processpi/calculations/fluids/reynolds_number.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ReynoldsNumber` | `ReynoldsNumber(...)` | A class to calculate the Reynolds number for fluid flow in a pipe. The Reynolds number (Re) is a dimensionless quantity that helps predict the flow patterns in a fluid. It represents the ratio of inertial forces to viscous forces. A low Reynolds number indicates laminar flow, while a high Reynolds number indicates turbulent flow. **Formulas:** * Using dynamic viscosity ($\mu$): $ Re = rac{ ho \cdot v \cdot D}{\mu} $ * Using kinematic viscosity ($ u$): $ Re = rac{v \cdot D}{ u} $ **Where:** * $ ho $ = Fluid density [kg/m³] * $ v $ = Fluid velocity [m/s] * $ D $ = Pipe diameter [m] * $ \mu $ = Dynamic viscosity [Pa·s] * $ u $ = Kinematic viscosity [m²/s] **Inputs:** * `density`: The fluid's density. * `velocity`: The fluid's velocity. * `diameter`: The internal diameter of the pipe. * `viscosity`: The fluid's viscosity (can be dynamic or kinematic). **Output:** * A `Dimensionless` object containing the calculated Reynolds number. | `validate_inputs()`, `calculate()` |

##### `ReynoldsNumber`

A class to calculate the Reynolds number for fluid flow in a pipe. The Reynolds number (Re) is a dimensionless quantity that helps predict the flow patterns in a fluid. It represents the ratio of inertial forces to viscous forces. A low Reynolds number indicates laminar flow, while a high Reynolds number indicates turbulent flow. **Formulas:** * Using dynamic viscosity ($\mu$): $ Re = rac{ ho \cdot v \cdot D}{\mu} $ * Using kinematic viscosity ($ u$): $ Re = rac{v \cdot D}{ u} $ **Where:** * $ ho $ = Fluid density [kg/m³] * $ v $ = Fluid velocity [m/s] * $ D $ = Pipe diameter [m] * $ \mu $ = Dynamic viscosity [Pa·s] * $ u $ = Kinematic viscosity [m²/s] **Inputs:** * `density`: The fluid's density. * `velocity`: The fluid's velocity. * `diameter`: The internal diameter of the pipe. * `viscosity`: The fluid's viscosity (can be dynamic or kinematic). **Output:** * A `Dimensionless` object containing the calculated Reynolds number.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method checks for the presence of all necessary keys in the inputs dictionary, raising a ValueError if any are missing. |
| `calculate` | `calculate(self)` | Performs the Reynolds number calculation based on the type of viscosity provided. The method first retrieves all required input values. It then determines whether the input viscosity is dynamic or kinematic and applies the appropriate formula to calculate the Reynolds number. Returns: Dimensionless: The calculated Reynolds number. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.fluids.velocity`

**Source:** `processpi/calculations/fluids/velocity.py`

**Purpose:** Fluid-mechanics calculation primitive for velocity, Reynolds number, friction, pressure drop, pump power, or flow classification.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `FluidVelocity` | `FluidVelocity(...)` | A class to calculate the average fluid velocity in a circular pipe. This calculation is fundamental in fluid dynamics and is used to determine how quickly a fluid is moving through a pipe based on its volumetric flow rate and the pipe's cross-sectional area. **Formula:** $ v = rac{Q}{A} = rac{4 \cdot Q}{\pi \cdot D^2} $ Where: * $ v $ = Fluid velocity [m/s] * $ Q $ = Volumetric flow rate [m³/s] * $ A $ = Cross-sectional area [m²] * $ D $ = Pipe diameter [m] **Inputs:** * `volumetric_flow_rate` (Q): The rate at which the fluid is flowing. * `diameter` (D): The internal diameter of the pipe. **Output:** * A `Velocity` object containing the calculated fluid velocity in meters per second (m/s). | `validate_inputs()`, `calculate()` |

##### `FluidVelocity`

A class to calculate the average fluid velocity in a circular pipe. This calculation is fundamental in fluid dynamics and is used to determine how quickly a fluid is moving through a pipe based on its volumetric flow rate and the pipe's cross-sectional area. **Formula:** $ v = rac{Q}{A} = rac{4 \cdot Q}{\pi \cdot D^2} $ Where: * $ v $ = Fluid velocity [m/s] * $ Q $ = Volumetric flow rate [m³/s] * $ A $ = Cross-sectional area [m²] * $ D $ = Pipe diameter [m] **Inputs:** * `volumetric_flow_rate` (Q): The rate at which the fluid is flowing. * `diameter` (D): The internal diameter of the pipe. **Output:** * A `Velocity` object containing the calculated fluid velocity in meters per second (m/s).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | Validates the required inputs for the calculation. This method checks for the presence of all necessary keys in the inputs dictionary, raising a ValueError if any are missing. |
| `calculate` | `calculate(self)` | Performs the fluid velocity calculation. The method retrieves the volumetric flow rate and pipe diameter, calculates the cross-sectional area of the pipe, and then applies the formula to determine the fluid velocity. Returns: Velocity: The calculated fluid velocity in m/s. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.__init__`

**Source:** `processpi/calculations/heat_transfer/__init__.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

No public classes or functions discovered in this module.

### `processpi.calculations.heat_transfer.biot`

**Source:** `processpi/calculations/heat_transfer/biot.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `BiotNumber` | `BiotNumber(...)` | Biot number. **Formula:** Bi = h * Lc / k | `validate_inputs()`, `calculate()` |

##### `BiotNumber`

Biot number. **Formula:** Bi = h * Lc / k

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.boiling_chen`

**Source:** `processpi/calculations/heat_transfer/boiling_chen.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ChenBoiling` | `ChenBoiling(...)` | Chen correlation for **flow boiling heat transfer**. **Formula (simplified):** h_total = S * h_pool + F * h_conv **Where:** * h_total = overall heat transfer coefficient [W/m²·K] * h_pool = pool boiling coefficient (from Rohsenow or others) * h_conv = forced convection coefficient (from Dittus-Boelter or similar) * S = suppression factor (empirical, function of Re, Boiling number, etc.) * F = enhancement factor (empirical, function of flow parameters) **Inputs:** * h_pool * h_conv * S * F **Output:** * HeatTransferCoefficient [W/m²·K] | `validate_inputs()`, `calculate()` |

##### `ChenBoiling`

Chen correlation for **flow boiling heat transfer**. **Formula (simplified):** h_total = S * h_pool + F * h_conv **Where:** * h_total = overall heat transfer coefficient [W/m²·K] * h_pool = pool boiling coefficient (from Rohsenow or others) * h_conv = forced convection coefficient (from Dittus-Boelter or similar) * S = suppression factor (empirical, function of Re, Boiling number, etc.) * F = enhancement factor (empirical, function of flow parameters) **Inputs:** * h_pool * h_conv * S * F **Output:** * HeatTransferCoefficient [W/m²·K]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.combined_modes`

**Source:** `processpi/calculations/heat_transfer/combined_modes.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ConductionConvectionCombined` | `ConductionConvectionCombined(...)` | Heat transfer with conduction resistance + convection resistance. **Formula:** Q = (Ts - T∞) / (R_cond + R_conv) Where: R_cond = dx / (k * A) R_conv = 1 / (h * A) **Inputs:** * `thickness`: Conduction thickness [m] * `k`: Thermal conductivity [W/m·K] * `h`: Convective coefficient [W/m²·K] * `area`: Heat transfer area [m²] * `T_surface`: Surface temperature [K] * `T_fluid`: Bulk fluid temperature [K] **Output:** * HeatFlow [W] | `validate_inputs()`, `calculate()` |

##### `ConductionConvectionCombined`

Heat transfer with conduction resistance + convection resistance. **Formula:** Q = (Ts - T∞) / (R_cond + R_conv) Where: R_cond = dx / (k * A) R_conv = 1 / (h * A) **Inputs:** * `thickness`: Conduction thickness [m] * `k`: Thermal conductivity [W/m·K] * `h`: Convective coefficient [W/m²·K] * `area`: Heat transfer area [m²] * `T_surface`: Surface temperature [K] * `T_fluid`: Bulk fluid temperature [K] **Output:** * HeatFlow [W]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.condensation`

**Source:** `processpi/calculations/heat_transfer/condensation.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CondensingVapourFilm` | `CondensingVapourFilm(...)` | Heat transfer from condensing vapours on a vertical plate (Nusselt’s theory). **Formula:** h = 0.943 * [ (ρ_l * (ρ_l - ρ_v) * g * h_fg * k_l^3) / (μ_l * L * ΔT) ]^(1/4) Then: Q = h * A * ΔT **Inputs:** * `rho_l`: Liquid density [kg/m³] * `rho_v`: Vapour density [kg/m³] * `g`: Gravity [m/s²] * `h_fg`: Latent heat [J/kg] * `k_l`: Liquid thermal conductivity [W/m·K] * `mu_l`: Liquid viscosity [Pa·s] * `L`: Plate length [m] * `A`: Area [m²] * `deltaT`: Temperature difference [K] | `validate_inputs()`, `calculate()` |

##### `CondensingVapourFilm`

Heat transfer from condensing vapours on a vertical plate (Nusselt’s theory). **Formula:** h = 0.943 * [ (ρ_l * (ρ_l - ρ_v) * g * h_fg * k_l^3) / (μ_l * L * ΔT) ]^(1/4) Then: Q = h * A * ΔT **Inputs:** * `rho_l`: Liquid density [kg/m³] * `rho_v`: Vapour density [kg/m³] * `g`: Gravity [m/s²] * `h_fg`: Latent heat [J/kg] * `k_l`: Liquid thermal conductivity [W/m·K] * `mu_l`: Liquid viscosity [Pa·s] * `L`: Plate length [m] * `A`: Area [m²] * `deltaT`: Temperature difference [K]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.condensation_dropwise`

**Source:** `processpi/calculations/heat_transfer/condensation_dropwise.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `DropwiseCondensation` | `DropwiseCondensation(...)` | Empirical correlations for **dropwise condensation**. Dropwise condensation has much higher heat transfer coefficients than filmwise (often 5–10× larger). **Simple empirical model:** h_dw = C * h_fw **Where:** * h_dw = dropwise condensation heat transfer coefficient [W/m²·K] * h_fw = filmwise condensation coefficient [W/m²·K] (from Nusselt theory) * C = enhancement factor (typically 5–10, depending on surface treatment) **Inputs:** * h_fw – filmwise coefficient [W/m²·K] * C – enhancement factor (default: 7) **Output:** * HeatTransferCoefficient [W/m²·K] | `validate_inputs()`, `calculate()` |

##### `DropwiseCondensation`

Empirical correlations for **dropwise condensation**. Dropwise condensation has much higher heat transfer coefficients than filmwise (often 5–10× larger). **Simple empirical model:** h_dw = C * h_fw **Where:** * h_dw = dropwise condensation heat transfer coefficient [W/m²·K] * h_fw = filmwise condensation coefficient [W/m²·K] (from Nusselt theory) * C = enhancement factor (typically 5–10, depending on surface treatment) **Inputs:** * h_fw – filmwise coefficient [W/m²·K] * C – enhancement factor (default: 7) **Output:** * HeatTransferCoefficient [W/m²·K]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.condensation_nusselt`

**Source:** `processpi/calculations/heat_transfer/condensation_nusselt.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `NusseltCondensation` | `NusseltCondensation(...)` | Filmwise condensation heat transfer coefficient based on **Nusselt’s theory** (laminar film condensation on vertical surface). **Formula (vertical plate/tube):** h = 0.943 * [ (k_l^3 * rho_l^2 * g * h_fg) / (mu_l * L * ΔT) ]^(1/4) **Where:** * h = average heat transfer coefficient [W/m²·K] * k_l = liquid thermal conductivity [W/m·K] * rho_l = liquid density [kg/m³] * g = gravity [m/s²] * h_fg = latent heat of vaporization [J/kg] * mu_l = liquid viscosity [Pa·s] * L = characteristic length (plate height or tube length) [m] * ΔT = (T_wall – T_sat) [K] **Inputs:** * k_l * rho_l * g * h_fg * mu_l * L * dT **Output:** * HeatTransferCoefficient [W/m²·K] | `validate_inputs()`, `calculate()` |

##### `NusseltCondensation`

Filmwise condensation heat transfer coefficient based on **Nusselt’s theory** (laminar film condensation on vertical surface). **Formula (vertical plate/tube):** h = 0.943 * [ (k_l^3 * rho_l^2 * g * h_fg) / (mu_l * L * ΔT) ]^(1/4) **Where:** * h = average heat transfer coefficient [W/m²·K] * k_l = liquid thermal conductivity [W/m·K] * rho_l = liquid density [kg/m³] * g = gravity [m/s²] * h_fg = latent heat of vaporization [J/kg] * mu_l = liquid viscosity [Pa·s] * L = characteristic length (plate height or tube length) [m] * ΔT = (T_wall – T_sat) [K] **Inputs:** * k_l * rho_l * g * h_fg * mu_l * L * dT **Output:** * HeatTransferCoefficient [W/m²·K]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.conduction_heat_loss`

**Source:** `processpi/calculations/heat_transfer/conduction_heat_loss.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ConductionHeatLoss` | `ConductionHeatLoss(...)` | Calculate steady-state conduction heat loss through a wall. Formula: Q = k * A * ΔT / L | `validate_inputs()`, `calculate()` |

##### `ConductionHeatLoss`

Calculate steady-state conduction heat loss through a wall. Formula: Q = k * A * ΔT / L

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.convection_heat_loss`

**Source:** `processpi/calculations/heat_transfer/convection_heat_loss.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ConvectionHeatLoss` | `ConvectionHeatLoss(...)` | Calculate convection heat loss. Formula: Q = h * A * ΔT | `validate_inputs()`, `calculate()` |

##### `ConvectionHeatLoss`

Calculate convection heat loss. Formula: Q = h * A * ΔT

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.crossflow_tube`

**Source:** `processpi/calculations/heat_transfer/crossflow_tube.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CrossFlowSingleTube` | `CrossFlowSingleTube(...)` | Heat transfer to/from fluid flowing normal to a single tube. **Formula:** Q = h * A * (T_surface - T_fluid) **Inputs:** * `h`: Convective heat transfer coefficient [W/m²·K] * `diameter`: Tube outer diameter [m] * `length`: Tube length [m] * `T_surface`: Tube surface temperature [K] * `T_fluid`: Bulk fluid temperature [K] | `validate_inputs()`, `calculate()` |

##### `CrossFlowSingleTube`

Heat transfer to/from fluid flowing normal to a single tube. **Formula:** Q = h * A * (T_surface - T_fluid) **Inputs:** * `h`: Convective heat transfer coefficient [W/m²·K] * `diameter`: Tube outer diameter [m] * `length`: Tube length [m] * `T_surface`: Tube surface temperature [K] * `T_fluid`: Bulk fluid temperature [K]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.fourier`

**Source:** `processpi/calculations/heat_transfer/fourier.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `FourierNumber` | `FourierNumber(...)` | Fourier number (transient conduction). **Formula:** Fo = α * t / L² | `validate_inputs()`, `calculate()` |

##### `FourierNumber`

Fourier number (transient conduction). **Formula:** Fo = α * t / L²

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.fourierlaw`

**Source:** `processpi/calculations/heat_transfer/fourierlaw.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `FourierLaw` | `FourierLaw(...)` | Heat transfer rate by conduction (Fourier's Law). **Formula:** q = k * A * (ΔT / dx) **Where:** * k = Thermal conductivity [W/m·K] * A = Cross-sectional area [m²] * ΔT = Temperature difference [K] * dx = Thickness of material [m] **Inputs:** * `conductivity`: Thermal conductivity (k). * `area`: Heat transfer area (A). * `deltaT`: Temperature difference (ΔT). * `thickness`: Material thickness (dx). **Output:** * HeatFlow [W] | `validate_inputs()`, `calculate()` |

##### `FourierLaw`

Heat transfer rate by conduction (Fourier's Law). **Formula:** q = k * A * (ΔT / dx) **Where:** * k = Thermal conductivity [W/m·K] * A = Cross-sectional area [m²] * ΔT = Temperature difference [K] * dx = Thickness of material [m] **Inputs:** * `conductivity`: Thermal conductivity (k). * `area`: Heat transfer area (A). * `deltaT`: Temperature difference (ΔT). * `thickness`: Material thickness (dx). **Output:** * HeatFlow [W]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.grashof`

**Source:** `processpi/calculations/heat_transfer/grashof.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `GrashofNumber` | `GrashofNumber(...)` | Grashof number (buoyancy vs. viscous forces in natural convection). **Formula:** Gr = g * β * ΔT * L³ / ν² | `validate_inputs()`, `calculate()` |

##### `GrashofNumber`

Grashof number (buoyancy vs. viscous forces in natural convection). **Formula:** Gr = g * β * ΔT * L³ / ν²

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.heat_exchanger`

**Source:** `processpi/calculations/heat_transfer/heat_exchanger.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `SensibleHeatDuty` | `SensibleHeatDuty(...)` | Q = m * Cp * (Tin - Tout). | `validate_inputs()`, `calculate()` |
| `LatentHeatDuty` | `LatentHeatDuty(...)` | Q = m * lambda. | `validate_inputs()`, `calculate()` |
| `KernNusselt` | `KernNusselt(...)` | Nu = 0.023 * Re^0.8 * Pr^n. | `validate_inputs()`, `calculate()` |
| `ConvectiveCoefficient` | `ConvectiveCoefficient(...)` | h = Nu * k / D. | `validate_inputs()`, `calculate()` |
| `DarcyPressureDrop` | `DarcyPressureDrop(...)` | dP = f * (L / D) * (rho * v^2 / 2). | `validate_inputs()`, `calculate()` |
| `ReynoldsFromProperties` | `ReynoldsFromProperties(...)` | Re = rho * v * D / mu. | `validate_inputs()`, `calculate()` |

##### `SensibleHeatDuty`

Q = m * Cp * (Tin - Tout).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `LatentHeatDuty`

Q = m * lambda.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `KernNusselt`

Nu = 0.023 * Re^0.8 * Pr^n.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `ConvectiveCoefficient`

h = Nu * k / D.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `DarcyPressureDrop`

dP = f * (L / D) * (rho * v^2 / 2).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `ReynoldsFromProperties`

Re = rho * v * D / mu.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.heat_exchanger_area`

**Source:** `processpi/calculations/heat_transfer/heat_exchanger_area.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatExchangerArea` | `HeatExchangerArea(...)` | Calculate required heat exchanger area. Formula: Q = U * A * ΔTlm => A = Q / (U * ΔTlm) | `validate_inputs()`, `calculate()` |

##### `HeatExchangerArea`

Calculate required heat exchanger area. Formula: Q = U * A * ΔTlm => A = Q / (U * ΔTlm)

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.hx_kern`

**Source:** `processpi/calculations/heat_transfer/hx_kern.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `SensibleDuty` | `SensibleDuty(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `LatentDuty` | `LatentDuty(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `Reynolds` | `Reynolds(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `DittusBoelter` | `DittusBoelter(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `KernShellNu` | `KernShellNu(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `ConvectiveH` | `ConvectiveH(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `TubeCountFromArea` | `TubeCountFromArea(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `ShellDiameterEstimate` | `ShellDiameterEstimate(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `DarcyDrop` | `DarcyDrop(...)` | No source docstring provided. See module purpose and examples. | `validate_inputs()`, `calculate()` |
| `CondensationHTC` | `CondensationHTC(...)` | Nusselt film condensation correlation for vertical tube condensation. Preliminary engineering approximation. | `validate_inputs()`, `calculate()` |
| `BoilingHTC` | `BoilingHTC(...)` | Simplified boiling heat-transfer coefficient. Preliminary engineering approximation. | `validate_inputs()`, `calculate()` |

##### `SensibleDuty`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `LatentDuty`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `Reynolds`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `DittusBoelter`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `KernShellNu`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `ConvectiveH`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `TubeCountFromArea`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `ShellDiameterEstimate`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `DarcyDrop`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `CondensationHTC`

Nusselt film condensation correlation for vertical tube condensation. Preliminary engineering approximation.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `BoilingHTC`

Simplified boiling heat-transfer coefficient. Preliminary engineering approximation.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.lmtd`

**Source:** `processpi/calculations/heat_transfer/lmtd.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `LMTD` | `LMTD(...)` | Heat Exchanger using LMTD method. Q = U * A * ΔTlm | `validate_inputs()`, `calculate()` |

##### `LMTD`

Heat Exchanger using LMTD method. Q = U * A * ΔTlm

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.newton_cooling`

**Source:** `processpi/calculations/heat_transfer/newton_cooling.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `NewtonCooling` | `NewtonCooling(...)` | Convective heat transfer (Newton’s Law of Cooling). **Formula:** q = h * A * (Ts - T∞) **Where:** * h = Heat transfer coefficient [W/m²·K] * A = Surface area [m²] * Ts = Surface temperature [K] * T∞ = Bulk fluid temperature [K] **Inputs:** * `h`: Heat transfer coefficient. * `area`: Surface area. * `T_surface`: Surface temperature. * `T_fluid`: Bulk fluid temperature. **Output:** * HeatFlow [W] | `validate_inputs()`, `calculate()` |

##### `NewtonCooling`

Convective heat transfer (Newton’s Law of Cooling). **Formula:** q = h * A * (Ts - T∞) **Where:** * h = Heat transfer coefficient [W/m²·K] * A = Surface area [m²] * Ts = Surface temperature [K] * T∞ = Bulk fluid temperature [K] **Inputs:** * `h`: Heat transfer coefficient. * `area`: Surface area. * `T_surface`: Surface temperature. * `T_fluid`: Bulk fluid temperature. **Output:** * HeatFlow [W]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.ntu`

**Source:** `processpi/calculations/heat_transfer/ntu.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `NTUHeatExchanger` | `NTUHeatExchanger(...)` | Heat Exchanger using Effectiveness-NTU method. Q = ε * C_min * (T_hot,in - T_cold,in) | `validate_inputs()`, `calculate()` |

##### `NTUHeatExchanger`

Heat Exchanger using Effectiveness-NTU method. Q = ε * C_min * (T_hot,in - T_cold,in)

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.nusselt`

**Source:** `processpi/calculations/heat_transfer/nusselt.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `NusseltNumber` | `NusseltNumber(...)` | Nusselt number (dimensionless heat transfer coefficient). **Formula:** Nu = h * L / k | `validate_inputs()`, `calculate()` |

##### `NusseltNumber`

Nusselt number (dimensionless heat transfer coefficient). **Formula:** Nu = h * L / k

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.overall_u`

**Source:** `processpi/calculations/heat_transfer/overall_u.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `OverallHeatTransferCoefficient` | `OverallHeatTransferCoefficient(...)` | Overall heat transfer coefficient for a composite wall. U = 1 / ΣR | `validate_inputs()`, `calculate()` |

##### `OverallHeatTransferCoefficient`

Overall heat transfer coefficient for a composite wall. U = 1 / ΣR

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.peclet`

**Source:** `processpi/calculations/heat_transfer/peclet.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PecletNumber` | `PecletNumber(...)` | Peclet number (convection vs. conduction in fluid flow). **Formula:** Pe = Re * Pr = (ρ * v * L / μ) * (μ * Cp / k) = ρ * v * L * Cp / k | `validate_inputs()`, `calculate()` |

##### `PecletNumber`

Peclet number (convection vs. conduction in fluid flow). **Formula:** Pe = Re * Pr = (ρ * v * L / μ) * (μ * Cp / k) = ρ * v * L * Cp / k

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.prandtl`

**Source:** `processpi/calculations/heat_transfer/prandtl.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PrandtlNumber` | `PrandtlNumber(...)` | Prandtl number. **Formula:** Pr = μ * Cp / k | `validate_inputs()`, `calculate()` |

##### `PrandtlNumber`

Prandtl number. **Formula:** Pr = μ * Cp / k

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.radial_cylinder`

**Source:** `processpi/calculations/heat_transfer/radial_cylinder.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `RadialHeatFlowCylinder` | `RadialHeatFlowCylinder(...)` | Radial heat conduction through a hollow cylinder. **Formula:** Q = (2 * π * k * L * (T1 - T2)) / ln(r2/r1) **Inputs:** * `k`: Thermal conductivity [W/m·K] * `length`: Cylinder length [m] * `r_inner`: Inner radius [m] * `r_outer`: Outer radius [m] * `T_inner`: Temperature at inner surface [K] * `T_outer`: Temperature at outer surface [K] **Output:** * HeatFlow [W] | `validate_inputs()`, `calculate()` |

##### `RadialHeatFlowCylinder`

Radial heat conduction through a hollow cylinder. **Formula:** Q = (2 * π * k * L * (T1 - T2)) / ln(r2/r1) **Inputs:** * `k`: Thermal conductivity [W/m·K] * `length`: Cylinder length [m] * `r_inner`: Inner radius [m] * `r_outer`: Outer radius [m] * `T_inner`: Temperature at inner surface [K] * `T_outer`: Temperature at outer surface [K] **Output:** * HeatFlow [W]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.radiation_blackbody`

**Source:** `processpi/calculations/heat_transfer/radiation_blackbody.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `BlackbodyRadiation` | `BlackbodyRadiation(...)` | Stefan–Boltzmann law for blackbody radiation. **Formula:** q = σ * T^4 **Where:** * q = radiative flux [W/m²] * σ = Stefan–Boltzmann constant (5.670374419e-8 W/m²·K⁴) * T = absolute temperature [K] **Inputs:** * T – surface temperature [K] **Output:** * HeatFlux [W/m²] | `validate_inputs()`, `calculate()` |

##### `BlackbodyRadiation`

Stefan–Boltzmann law for blackbody radiation. **Formula:** q = σ * T^4 **Where:** * q = radiative flux [W/m²] * σ = Stefan–Boltzmann constant (5.670374419e-8 W/m²·K⁴) * T = absolute temperature [K] **Inputs:** * T – surface temperature [K] **Output:** * HeatFlux [W/m²]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.radiation_exchange`

**Source:** `processpi/calculations/heat_transfer/radiation_exchange.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `RadiationExchange` | `RadiationExchange(...)` | Net radiative heat exchange between two diffuse gray surfaces. **Formula:** q = σ * (T1^4 – T2^4) / ( (1/ε1) + (1/ε2) – 1 ) **Where:** * T1, T2 = absolute temperatures [K] * ε1, ε2 = emissivities * q = net flux [W/m²] **Inputs:** * T1 * T2 * epsilon1 * epsilon2 **Output:** * HeatFlux [W/m²] | `validate_inputs()`, `calculate()` |

##### `RadiationExchange`

Net radiative heat exchange between two diffuse gray surfaces. **Formula:** q = σ * (T1^4 – T2^4) / ( (1/ε1) + (1/ε2) – 1 ) **Where:** * T1, T2 = absolute temperatures [K] * ε1, ε2 = emissivities * q = net flux [W/m²] **Inputs:** * T1 * T2 * epsilon1 * epsilon2 **Output:** * HeatFlux [W/m²]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.radiation_greybody`

**Source:** `processpi/calculations/heat_transfer/radiation_greybody.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `GreybodyRadiation` | `GreybodyRadiation(...)` | Greybody radiation with emissivity factor. **Formula:** q = ε * σ * T^4 **Where:** * ε = emissivity (0 < ε ≤ 1) * q = radiative flux [W/m²] * T = absolute temperature [K] **Inputs:** * T – surface temperature [K] * ε – emissivity (dimensionless) **Output:** * HeatFlux [W/m²] | `validate_inputs()`, `calculate()` |

##### `GreybodyRadiation`

Greybody radiation with emissivity factor. **Formula:** q = ε * σ * T^4 **Where:** * ε = emissivity (0 < ε ≤ 1) * q = radiative flux [W/m²] * T = absolute temperature [K] **Inputs:** * T – surface temperature [K] * ε – emissivity (dimensionless) **Output:** * HeatFlux [W/m²]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.radiation_viewfactor`

**Source:** `processpi/calculations/heat_transfer/radiation_viewfactor.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `RadiationWithViewFactor` | `RadiationWithViewFactor(...)` | Radiation exchange between two surfaces with a given view factor. **Formula:** Q = σ * A1 * F12 * (T1^4 – T2^4) **Where:** * A1 = area of surface 1 [m²] * F12 = view factor from surface 1 to 2 * T1, T2 = temperatures [K] * Q = net heat transfer [W] **Inputs:** * A1 * F12 * T1 * T2 **Output:** * HeatFlow [W] | `validate_inputs()`, `calculate()` |

##### `RadiationWithViewFactor`

Radiation exchange between two surfaces with a given view factor. **Formula:** Q = σ * A1 * F12 * (T1^4 – T2^4) **Where:** * A1 = area of surface 1 [m²] * F12 = view factor from surface 1 to 2 * T1, T2 = temperatures [K] * Q = net heat transfer [W] **Inputs:** * A1 * F12 * T1 * T2 **Output:** * HeatFlow [W]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.resistance`

**Source:** `processpi/calculations/heat_transfer/resistance.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ThermalResistanceSeries` | `ThermalResistanceSeries(...)` | Equivalent thermal resistance for series layers. R_total = Σ Ri | `validate_inputs()`, `calculate()` |
| `ThermalResistanceParallel` | `ThermalResistanceParallel(...)` | Equivalent thermal resistance for parallel layers. 1/R_total = Σ (1/Ri) | `validate_inputs()`, `calculate()` |

##### `ThermalResistanceSeries`

Equivalent thermal resistance for series layers. R_total = Σ Ri

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `ThermalResistanceParallel`

Equivalent thermal resistance for parallel layers. 1/R_total = Σ (1/Ri)

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.reyleigh`

**Source:** `processpi/calculations/heat_transfer/reyleigh.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `RayleighNumber` | `RayleighNumber(...)` | Rayleigh number (convection onset parameter). **Formula:** Ra = Gr * Pr | `validate_inputs()`, `calculate()` |

##### `RayleighNumber`

Rayleigh number (convection onset parameter). **Formula:** Ra = Gr * Pr

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.rohsenow_boiling`

**Source:** `processpi/calculations/heat_transfer/rohsenow_boiling.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `RohsenowBoiling` | `RohsenowBoiling(...)` | Rohsenow correlation for **pool boiling heat transfer**. **Formula:** q'' = μ_l * h_fg * [ (g * (ρ_l - ρ_v) / σ)^(1/2) ] * [ Cp_l * (ΔT / (h_fg * Pr_l^n)) ]^3 **Where:** * q'' = Heat flux [W/m²] * μ_l = Liquid viscosity [Pa·s] * h_fg = Latent heat of vaporization [J/kg] * g = Gravity [m/s²] * ρ_l, ρ_v = Liquid and vapor densities [kg/m³] * σ = Surface tension [N/m] * Cp_l = Specific heat of liquid [J/kg·K] * ΔT = (T_wall – T_sat) [K] * Pr_l = Prandtl number of liquid * n = empirical constant (usually 1.0 for water, 1.7 for other fluids) **Inputs:** * mu_l * h_fg * g * rho_l * rho_v * sigma * Cp_l * dT * Pr_l * n (default: 1.0) **Output:** * HeatFlux [W/m²] | `validate_inputs()`, `calculate()` |

##### `RohsenowBoiling`

Rohsenow correlation for **pool boiling heat transfer**. **Formula:** q'' = μ_l * h_fg * [ (g * (ρ_l - ρ_v) / σ)^(1/2) ] * [ Cp_l * (ΔT / (h_fg * Pr_l^n)) ]^3 **Where:** * q'' = Heat flux [W/m²] * μ_l = Liquid viscosity [Pa·s] * h_fg = Latent heat of vaporization [J/kg] * g = Gravity [m/s²] * ρ_l, ρ_v = Liquid and vapor densities [kg/m³] * σ = Surface tension [N/m] * Cp_l = Specific heat of liquid [J/kg·K] * ΔT = (T_wall – T_sat) [K] * Pr_l = Prandtl number of liquid * n = empirical constant (usually 1.0 for water, 1.7 for other fluids) **Inputs:** * mu_l * h_fg * g * rho_l * rho_v * sigma * Cp_l * dT * Pr_l * n (default: 1.0) **Output:** * HeatFlux [W/m²]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.heat_transfer.stefan_boltzmann`

**Source:** `processpi/calculations/heat_transfer/stefan_boltzmann.py`

**Purpose:** Reusable heat-transfer calculation primitive used by exchanger and engineering workflows.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `StefanBoltzmann` | `StefanBoltzmann(...)` | Radiative heat transfer (Stefan–Boltzmann Law). **Formula:** q = εσA(Ts⁴ - Tsur⁴) **Where:** * ε = Surface emissivity [-] * σ = Stefan–Boltzmann constant [5.67e-8 W/m²·K⁴] * A = Surface area [m²] * Ts = Surface temperature [K] * Tsur = Surrounding temperature [K] **Inputs:** * `emissivity`: Surface emissivity. * `area`: Surface area. * `T_surface`: Surface temperature. * `T_surround`: Surrounding temperature. **Output:** * HeatFlow [W] | `validate_inputs()`, `calculate()` |

##### `StefanBoltzmann`

Radiative heat transfer (Stefan–Boltzmann Law). **Formula:** q = εσA(Ts⁴ - Tsur⁴) **Where:** * ε = Surface emissivity [-] * σ = Stefan–Boltzmann constant [5.67e-8 W/m²·K⁴] * A = Surface area [m²] * Ts = Surface temperature [K] * Tsur = Surrounding temperature [K] **Inputs:** * `emissivity`: Surface emissivity. * `area`: Surface area. * `T_surface`: Surface temperature. * `T_surround`: Surrounding temperature. **Output:** * HeatFlow [W]

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.mass_transfer.__init__`

**Source:** `processpi/calculations/mass_transfer/__init__.py`

**Purpose:** Mass-transfer calculation primitive.

No public classes or functions discovered in this module.

### `processpi.calculations.mass_transfer.distillation_stage_count`

**Source:** `processpi/calculations/mass_transfer/distillation_stage_count.py`

**Purpose:** Mass-transfer calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `DistillationStageCount` | `DistillationStageCount(...)` | Detailed distillation stage calculations. Supports two workflows: 1) Fenske minimum stages (binary): - Inputs: alpha_avg: float # Average relative volatility (LK relative to HK), alpha > 1 xD: float # LK mole fraction in distillate xB: float # LK mole fraction in bottoms - Output: {"Nmin_theoretical": float} 2) McCabe–Thiele graphical stepping (binary): - Inputs: xD: float # LK in distillate xB: float # LK in bottoms zF: float # LK in feed R: float # Reflux ratio (L/D) q: float # Feed thermal condition (q-line slope param) eq_curve: List[Tuple[float,float]] or callable x->y_eq # Equilibrium data: y = f(x). You can pass: # - list of (x,y) pairs (monotonic in x), OR # - a callable y_eq(x) total_condenser: bool = True # If True, add total condenser stage partial_reboiler: bool = True # If True, count reboiler as a stage max_stages: int = 300 # Safety limit for stepping tol: float = 1e-6 # Numeric tolerance - Assumptions: * Binary system (LK/HK). * Constant molar overflow (straight rectifying/stripping lines). * Feed plate determined by q-line intersection. - Output: { "N_theoretical": int, "rectifying_stages": int, "stripping_stages": int, "includes_total_condenser": bool, "includes_partial_reboiler": bool } Notes ----- * The McCabe–Thiele stepper uses piecewise linear interpolation of eq data if provided as (x,y) pairs. * Rectifying operating line: y = (R/(R+1)) x + xD/(R+1) * q-line (feed): y = (q/(q-1)) x - zF/(q-1) (q != 1 case) Special cases: - q = 1 (saturated liquid): vertical line at x = zF - q = 0 (saturated vapor): line slope 0 through y = zF * Stripping line is constructed through feed intersection and (xB, xB) pinch. | `validate_inputs()`, `calculate()` |

##### `DistillationStageCount`

Detailed distillation stage calculations. Supports two workflows: 1) Fenske minimum stages (binary): - Inputs: alpha_avg: float # Average relative volatility (LK relative to HK), alpha > 1 xD: float # LK mole fraction in distillate xB: float # LK mole fraction in bottoms - Output: {"Nmin_theoretical": float} 2) McCabe–Thiele graphical stepping (binary): - Inputs: xD: float # LK in distillate xB: float # LK in bottoms zF: float # LK in feed R: float # Reflux ratio (L/D) q: float # Feed thermal condition (q-line slope param) eq_curve: List[Tuple[float,float]] or callable x->y_eq # Equilibrium data: y = f(x). You can pass: # - list of (x,y) pairs (monotonic in x), OR # - a callable y_eq(x) total_condenser: bool = True # If True, add total condenser stage partial_reboiler: bool = True # If True, count reboiler as a stage max_stages: int = 300 # Safety limit for stepping tol: float = 1e-6 # Numeric tolerance - Assumptions: * Binary system (LK/HK). * Constant molar overflow (straight rectifying/stripping lines). * Feed plate determined by q-line intersection. - Output: { "N_theoretical": int, "rectifying_stages": int, "stripping_stages": int, "includes_total_condenser": bool, "includes_partial_reboiler": bool } Notes ----- * The McCabe–Thiele stepper uses piecewise linear interpolation of eq data if provided as (x,y) pairs. * Rectifying operating line: y = (R/(R+1)) x + xD/(R+1) * q-line (feed): y = (q/(q-1)) x - zF/(q-1) (q != 1 case) Special cases: - q = 1 (saturated liquid): vertical line at x = zF - q = 0 (saturated vapor): line slope 0 through y = zF * Stripping line is constructed through feed intersection and (xB, xB) pinch.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.mass_transfer.drying_rate`

**Source:** `processpi/calculations/mass_transfer/drying_rate.py`

**Purpose:** Mass-transfer calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `DryingRate` | `DryingRate(...)` | Detailed batch drying time and flux calculations across constant-rate and falling-rate periods. Two workflows: (A) Use direct constant-rate flux + falling-rate coefficient Inputs: M_dry: float # Dry solid mass (kg dry basis) A: float # Exposed drying area (m^2) X_i: float # Initial moisture content (kg water/kg dry solid) X_f: float # Final moisture content (kg water/kg dry solid) X_c: float # Critical moisture content (kg/kg dry solid) X_star: float # Equilibrium moisture content (kg/kg dry solid) N_c: float # Constant-rate flux (kg/m^2/s), e.g., measured or from HT/MT analysis k_f: float # Falling-rate coefficient (1/s) with linear-w.r.t-free-moisture assumption Output: { "t_constant_s": float, "t_falling_s": float, "t_total_s": float, "avg_flux_kg_m2_s": float } Model: * Constant-rate period: t_c = (M_dry/A) * (X_i - X_c) / N_c * Falling-rate (linear w.r.t free moisture X - X*): N = k_f * (X - X_star) t_f = (M_dry/A) * ln( (X_c - X_star) / (X_f - X_star) ) / k_f (B) Compute constant-rate flux from a mass-transfer coefficient (Lewis analogy style) Inputs: M_dry, A, X_i, X_f, X_c, X_star (as above) h_m: float # Mass-transfer coefficient (m/s) rho_v: float # Vapor density at interface/film (kg/m^3) Y_s: float # Humidity ratio (kg vapor/kg dry gas) at surface (saturation) Y_inf: float # Humidity ratio in bulk gas (kg/kg_dry_gas) k_f: float # Falling-rate coefficient (1/s) Output: same keys as (A) Model: N_c = h_m * rho_v * (Y_s - Y_inf) | `validate_inputs()`, `calculate()` |

##### `DryingRate`

Detailed batch drying time and flux calculations across constant-rate and falling-rate periods. Two workflows: (A) Use direct constant-rate flux + falling-rate coefficient Inputs: M_dry: float # Dry solid mass (kg dry basis) A: float # Exposed drying area (m^2) X_i: float # Initial moisture content (kg water/kg dry solid) X_f: float # Final moisture content (kg water/kg dry solid) X_c: float # Critical moisture content (kg/kg dry solid) X_star: float # Equilibrium moisture content (kg/kg dry solid) N_c: float # Constant-rate flux (kg/m^2/s), e.g., measured or from HT/MT analysis k_f: float # Falling-rate coefficient (1/s) with linear-w.r.t-free-moisture assumption Output: { "t_constant_s": float, "t_falling_s": float, "t_total_s": float, "avg_flux_kg_m2_s": float } Model: * Constant-rate period: t_c = (M_dry/A) * (X_i - X_c) / N_c * Falling-rate (linear w.r.t free moisture X - X*): N = k_f * (X - X_star) t_f = (M_dry/A) * ln( (X_c - X_star) / (X_f - X_star) ) / k_f (B) Compute constant-rate flux from a mass-transfer coefficient (Lewis analogy style) Inputs: M_dry, A, X_i, X_f, X_c, X_star (as above) h_m: float # Mass-transfer coefficient (m/s) rho_v: float # Vapor density at interface/film (kg/m^3) Y_s: float # Humidity ratio (kg vapor/kg dry gas) at surface (saturation) Y_inf: float # Humidity ratio in bulk gas (kg/kg_dry_gas) k_f: float # Falling-rate coefficient (1/s) Output: same keys as (A) Model: N_c = h_m * rho_v * (Y_s - Y_inf)

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.reaction_engineering.__init__`

**Source:** `processpi/calculations/reaction_engineering/__init__.py`

**Purpose:** Reaction-engineering calculation primitive.

No public classes or functions discovered in this module.

### `processpi.calculations.reaction_engineering.catalyst_activity`

**Source:** `processpi/calculations/reaction_engineering/catalyst_activity.py`

**Purpose:** Reaction-engineering calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `CatalystActivity` | `CatalystActivity(...)` | Catalyst activity decay & temperature correction utilities. Workflows (select with `model`): -------------------------------- 1) First-order deactivation: model = "first_order" Inputs: k_d or (A_d, Ea_d, T[, R]) # deactivation constant (1/time) or Arrhenius params t: float # time on stream a0: float = 1.0 # initial activity Output: {"a": float} Equation: a(t) = a0 * exp(-k_d * t) 2) Power-law deactivation order n: model = "power_order" Inputs: n: float # deactivation order (n >= 0) k_d or (A_d, Ea_d, T[, R]) # deactivation constant or Arrhenius t: float a0: float = 1.0 Output: {"a": float} Equation: da/dt = -k_d * a^n => if n = 1: a = a0 exp(-k_d t) if n != 1: a = a0 * [1 + (n-1) k_d t / a0^{(n-1)}]^(-1/(n-1)) 3) Temperature correction for activity-related constants (Arrhenius): model = "arrhenius_correction" Inputs: A_d, Ea_d, T[, R] Output: {"k_d": float} Equation: k_d = A_d * exp(-Ea_d/(R*T)) Notes ----- * For consistency, default R = 8.314 if not supplied. * a0 typically in [0,1], but any positive value is allowed for generic scaling. | `validate_inputs()`, `calculate()` |

##### `CatalystActivity`

Catalyst activity decay & temperature correction utilities. Workflows (select with `model`): -------------------------------- 1) First-order deactivation: model = "first_order" Inputs: k_d or (A_d, Ea_d, T[, R]) # deactivation constant (1/time) or Arrhenius params t: float # time on stream a0: float = 1.0 # initial activity Output: {"a": float} Equation: a(t) = a0 * exp(-k_d * t) 2) Power-law deactivation order n: model = "power_order" Inputs: n: float # deactivation order (n >= 0) k_d or (A_d, Ea_d, T[, R]) # deactivation constant or Arrhenius t: float a0: float = 1.0 Output: {"a": float} Equation: da/dt = -k_d * a^n => if n = 1: a = a0 exp(-k_d t) if n != 1: a = a0 * [1 + (n-1) k_d t / a0^{(n-1)}]^(-1/(n-1)) 3) Temperature correction for activity-related constants (Arrhenius): model = "arrhenius_correction" Inputs: A_d, Ea_d, T[, R] Output: {"k_d": float} Equation: k_d = A_d * exp(-Ea_d/(R*T)) Notes ----- * For consistency, default R = 8.314 if not supplied. * a0 typically in [0,1], but any positive value is allowed for generic scaling.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.reaction_engineering.reaction_rate`

**Source:** `processpi/calculations/reaction_engineering/reaction_rate.py`

**Purpose:** Reaction-engineering calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ReactionRate` | `ReactionRate(...)` | General reaction-rate calculator supporting several kinetic models. Workflows (select with `model`): -------------------------------- 1) Power law (elementary / empirical): model = "power_law" Inputs: C: Mapping[str, float] # species concentrations, mol/L (or consistent units) exponents: Mapping[str, float] # reaction orders for each species (e.g., {"A":1, "B":1}) k: float # rate constant (units consistent with orders & C) (optional) A, Ea, T, R # If k not given, compute k via Arrhenius: k = A*exp(-Ea/(R*T)) Output: {"rate": float} Equation: r = k * Π_i C_i^{a_i} 2) Langmuir–Hinshelwood (adsorption + surface reaction): model = "langmuir_hinshelwood" Inputs: k or (A, Ea, T, R) # rate constant or Arrhenius params C: Mapping[str, float] # species concentrations (e.g., {"A":..., "B":...}) K: Mapping[str, float] # adsorption constants for species present numerator: Mapping[str, float] # stoich exponents in numerator (default {"A":1}) denom_power: float = 1.0 # overall power on denominator (default 1) Output: {"rate": float} Equation (generic): r = k * Π_j (C_j)^{ν_j} / [ 1 + Σ_i K_i C_i ]^{denom_power} 3) Michaelis–Menten (enzymatic form, optional): model = "michaelis_menten" Inputs: Vmax: float Km: float S: float # substrate concentration Output: {"rate": float} Equation: r = Vmax * S / (Km + S) Notes ----- * Units are your responsibility; keep them consistent. * If both `k` and (A,Ea,T[,R]) are provided, `k` is used and Arrhenius params ignored. * Default R = 8.314 if not supplied and Arrhenius is used. | `validate_inputs()`, `calculate()` |

##### `ReactionRate`

General reaction-rate calculator supporting several kinetic models. Workflows (select with `model`): -------------------------------- 1) Power law (elementary / empirical): model = "power_law" Inputs: C: Mapping[str, float] # species concentrations, mol/L (or consistent units) exponents: Mapping[str, float] # reaction orders for each species (e.g., {"A":1, "B":1}) k: float # rate constant (units consistent with orders & C) (optional) A, Ea, T, R # If k not given, compute k via Arrhenius: k = A*exp(-Ea/(R*T)) Output: {"rate": float} Equation: r = k * Π_i C_i^{a_i} 2) Langmuir–Hinshelwood (adsorption + surface reaction): model = "langmuir_hinshelwood" Inputs: k or (A, Ea, T, R) # rate constant or Arrhenius params C: Mapping[str, float] # species concentrations (e.g., {"A":..., "B":...}) K: Mapping[str, float] # adsorption constants for species present numerator: Mapping[str, float] # stoich exponents in numerator (default {"A":1}) denom_power: float = 1.0 # overall power on denominator (default 1) Output: {"rate": float} Equation (generic): r = k * Π_j (C_j)^{ν_j} / [ 1 + Σ_i K_i C_i ]^{denom_power} 3) Michaelis–Menten (enzymatic form, optional): model = "michaelis_menten" Inputs: Vmax: float Km: float S: float # substrate concentration Output: {"rate": float} Equation: r = Vmax * S / (Km + S) Notes ----- * Units are your responsibility; keep them consistent. * If both `k` and (A,Ea,T[,R]) are provided, `k` is used and Arrhenius params ignored. * Default R = 8.314 if not supplied and Arrhenius is used.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.reaction_engineering.residence_time`

**Source:** `processpi/calculations/reaction_engineering/residence_time.py`

**Purpose:** Reaction-engineering calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ResidenceTime` | `ResidenceTime(...)` | Space time (τ) and conversion relations for ideal reactors. Workflows (select with `mode`): ------------------------------- 1) Space time: mode = "tau" Inputs: V: float # reactor volume Q: float # volumetric flow rate Output: {"tau": float, "space_velocity": float} Equations: τ = V / Q SV = 1 / τ 2) Conversion for first-order kinetics (isothermal, constant density): mode = "conversion" Inputs: reactor: "CSTR" or "PFR" k: float # first-order rate constant (1/time) tau: float # space time (V/Q) Output: {"X": float} Equations: CSTR: X = (k τ) / (1 + k τ) PFR: X = 1 - exp(-k τ) | `validate_inputs()`, `calculate()` |

##### `ResidenceTime`

Space time (τ) and conversion relations for ideal reactors. Workflows (select with `mode`): ------------------------------- 1) Space time: mode = "tau" Inputs: V: float # reactor volume Q: float # volumetric flow rate Output: {"tau": float, "space_velocity": float} Equations: τ = V / Q SV = 1 / τ 2) Conversion for first-order kinetics (isothermal, constant density): mode = "conversion" Inputs: reactor: "CSTR" or "PFR" k: float # first-order rate constant (1/time) tau: float # space time (V/Q) Output: {"X": float} Equations: CSTR: X = (k τ) / (1 + k τ) PFR: X = 1 - exp(-k τ)

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.thermodynamics.__init__`

**Source:** `processpi/calculations/thermodynamics/__init__.py`

**Purpose:** Thermodynamic calculation primitive.

No public classes or functions discovered in this module.

### `processpi.calculations.thermodynamics.enthalpy_change`

**Source:** `processpi/calculations/thermodynamics/enthalpy_change.py`

**Purpose:** Thermodynamic calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `EnthalpyChange` | `EnthalpyChange(...)` | Calculate enthalpy change using: ΔH = m * Cp * ΔT | `validate_inputs()`, `calculate()` |

##### `EnthalpyChange`

Calculate enthalpy change using: ΔH = m * Cp * ΔT

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.thermodynamics.entropy_change`

**Source:** `processpi/calculations/thermodynamics/entropy_change.py`

**Purpose:** Thermodynamic calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `EntropyChange` | `EntropyChange(...)` | Calculate entropy change (ideal reversible process): ΔS = m * Cp * ln(T2/T1) | `validate_inputs()`, `calculate()` |

##### `EntropyChange`

Calculate entropy change (ideal reversible process): ΔS = m * Cp * ln(T2/T1)

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.calculations.thermodynamics.heat_of_vaporization`

**Source:** `processpi/calculations/thermodynamics/heat_of_vaporization.py`

**Purpose:** Thermodynamic calculation primitive.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `HeatOfVaporization` | `HeatOfVaporization(...)` | Calculate heat required for vaporization: Q = m * ΔHvap | `validate_inputs()`, `calculate()` |

##### `HeatOfVaporization`

Calculate heat required for vaporization: Q = m * ΔHvap

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_inputs` | `validate_inputs(self)` | No source docstring provided. |
| `calculate` | `calculate(self)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.
