# `processpi.pipelines` API

## Overview

Pipeline, fittings, material, network, hydraulic engine, or standards helper.

### Design assumptions and limitations

- Calculations generally expect engineering quantities in the units documented by the corresponding class constructor or module examples.
- Unit wrapper objects expose `.to("unit")`; many higher-level models accept either ProcessPI unit objects or numeric SI values depending on context.
- Validation is implemented in each class through `validate_inputs()` or constructor checks where available; invalid or missing inputs generally raise `ValueError`, `TypeError`, or `NotImplementedError`.
- The API reference below is generated from source signatures and public names. If a class has limited source docstrings, consult its examples and calculation result keys for engineering interpretation.

## Public modules

### `processpi.pipelines.__init__`

**Source:** `processpi/pipelines/__init__.py`

**Purpose:** ProcessPI Pipelines Module ========================== Provides core components for the fluid flow simulation engine, including: - Pipeline elements: Pipe, Pump, Vessel, Junction - Main engine: PipelineEngine for simulations and analysis Example: from processpi.pipelines import PipelineEngine, Pipe, Pump

No public classes or functions discovered in this module.

### `processpi.pipelines.base`

**Source:** `processpi/pipelines/base.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PipelineBase` | `PipelineBase(self, name: Optional[str]=None, **kwargs: Any)` | Abstract base class for all pipeline-related components and calculations in the ProcessPI simulation suite. Provides: - A unified way to store metadata like `name` - A flexible params dictionary for input configuration - Utility methods for safe parameter access and validation | `calculate()`, `get_param()`, `validate_required()` |

##### `PipelineBase`

Abstract base class for all pipeline-related components and calculations in the ProcessPI simulation suite. Provides: - A unified way to store metadata like `name` - A flexible params dictionary for input configuration - Utility methods for safe parameter access and validation

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `calculate` | `calculate(self)` | Perform the core calculation for the pipeline object. Must be implemented by subclasses. Returns: dict: A dictionary containing calculation results. |
| `get_param` | `get_param(self, key: str, default: Any=None)` | Retrieve a parameter safely with a default fallback. Args: key (str): Parameter name. default (Any, optional): Value to return if key not found. Returns: Any: The parameter value or default. |
| `validate_required` | `validate_required(self, required_keys: list[str])` | Validate that required parameters are present in `self.params`. Args: required_keys (list[str]): Required parameter names. Raises: ValueError: If any required parameters are missing. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.design_rules`

**Source:** `processpi/pipelines/design_rules.py`

**Purpose:** Design rules module for ProcessPi pipelines. This module defines reusable validation rules for pipeline steps, ensuring that each step is well-formed, inputs/outputs are consistent, and parameters meet expected requirements.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `DesignRuleError` | `DesignRuleError(...)` | Custom exception for design rule violations. | — |
| `DesignRules` | `DesignRules(...)` | Provides static design rule checks for pipeline steps and configurations. | `validate_step_name()`, `validate_inputs_outputs()`, `validate_parameters()`, `validate_callable()`, `validate_pipeline_consistency()`, `summary()` |

##### `DesignRuleError`

Custom exception for design rule violations.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `DesignRules`

Provides static design rule checks for pipeline steps and configurations.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `validate_step_name` | `validate_step_name(name: str)` | Ensures that the step name is valid (non-empty and alphanumeric with underscores). |
| `validate_inputs_outputs` | `validate_inputs_outputs(inputs: List[str], outputs: List[str])` | Ensures that inputs and outputs are lists of non-empty strings and do not overlap. |
| `validate_parameters` | `validate_parameters(params: Dict[str, Any], required: List[str]=None)` | Ensures that required parameters are present. |
| `validate_callable` | `validate_callable(func: Callable, name: str='')` | Ensures that a provided function or callable is valid. |
| `validate_pipeline_consistency` | `validate_pipeline_consistency(steps: List[Dict[str, Any]])` | Checks that pipeline steps are connected properly, with consistent data flow. |
| `summary` | `summary()` | Returns a summary of available design rules. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.engine`

**Source:** `processpi/pipelines/engine.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `ElementReport` | `ElementReport(...)` | A data class to store the results of a single pipeline element calculation. | `as_dict()` |
| `PipelineEngine` | `PipelineEngine(self, **kwargs: Any)` | Pipeline simulation and sizing engine. This class provides a comprehensive set of tools for modeling fluid flow in pipelines. It can handle single pipes, series networks, and parallel networks, calculating pressure drop, velocity, Reynolds number, and other key fluid properties. Usage: 1. Instantiate the engine: `engine = PipelineEngine()` 2. Configure inputs with `.fit()`: `engine.fit(fluid=water, flowrate=1.0)` 3. Run the simulation: `results = engine.run()` 4. Access results: `results.summary()` The object stores the last results in `self._results` (PipelineResults). | `fit()`, `run()`, `summary()` |

##### `ElementReport`

A data class to store the results of a single pipeline element calculation.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `as_dict` | `as_dict(self)` | Convert the dataclass to a dictionary. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `PipelineEngine`

Pipeline simulation and sizing engine. This class provides a comprehensive set of tools for modeling fluid flow in pipelines. It can handle single pipes, series networks, and parallel networks, calculating pressure drop, velocity, Reynolds number, and other key fluid properties. Usage: 1. Instantiate the engine: `engine = PipelineEngine()` 2. Configure inputs with `.fit()`: `engine.fit(fluid=water, flowrate=1.0)` 3. Run the simulation: `results = engine.run()` 4. Access results: `results.summary()` The object stores the last results in `self._results` (PipelineResults).

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `fit` | `fit(self, **kwargs: Any)` | Configures engine inputs with unit-aware conversions and normalized keys. Args: **kwargs: Input parameters (e.g., flowrate, diameter, network). Returns: PipelineEngine: The configured engine instance. Raises: TypeError: If the provided network is not a PipelineNetwork. |
| `run` | `run(self)` | Execute pipeline simulation and return PipelineResults with all losses included. |
| `summary` | `summary(self)` | Returns the summary of the last run. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.equipment`

**Source:** `processpi/pipelines/equipment.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Equipment` | `Equipment(self, name: str, pressure_drop: float=0.0, description: str='')` | Represents a generic piece of inline process equipment within a fluid flow network, such as a heat exchanger, filter, or control valve. This class models the equipment as a component that causes a fixed pressure drop. It also includes attributes to define its connections within a network. | `add_inlet()`, `add_outlet()` |

##### `Equipment`

Represents a generic piece of inline process equipment within a fluid flow network, such as a heat exchanger, filter, or control valve. This class models the equipment as a component that causes a fixed pressure drop. It also includes attributes to define its connections within a network.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `add_inlet` | `add_inlet(self, node: Any)` | Adds a node to the list of inlet connections. Args: node (Any): The node object to connect as an inlet. |
| `add_outlet` | `add_outlet(self, node: Any)` | Adds a node to the list of outlet connections. Args: node (Any): The node object to connect as an outlet. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.fittings`

**Source:** `processpi/pipelines/fittings.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Fitting` | `Fitting(self, fitting_type: str, diameter: Optional[Diameter]=None, quantity: int=1)` | Represents a pipe fitting for head loss and equivalent length calculations. | `equivalent_length()`, `k_factor()`, `calculate()` |

##### `Fitting`

Represents a pipe fitting for head loss and equivalent length calculations.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `equivalent_length` | `equivalent_length(self)` | Returns the equivalent length (Le) for the fitting type. If Le depends on diameter and diameter is missing, raises a ValueError. |
| `k_factor` | `k_factor(self)` | Returns the K-factor for the fitting type. If K depends on diameter and diameter is missing, raises a ValueError. |
| `calculate` | `calculate(self)` | Returns a summary dictionary with fitting data and calculated values. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.insulation`

**Source:** `processpi/pipelines/insulation.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

No public classes or functions discovered in this module.

### `processpi.pipelines.materials`

**Source:** `processpi/pipelines/materials.py`

**Purpose:** Pipeline Materials Specifications and Properties This module contains physical and mechanical properties of pipeline materials commonly used in process industries. All values are representative and may vary depending on standards (ASME, ASTM, ISO) and manufacturer data.

#### Functions

| Function | Signature | Description |
| --- | --- | --- |
| `get_material_property` | `get_material_property(material: str, prop: str)` | Get a specific property of a pipeline material. Args: material (str): Material code (e.g., 'CS', 'SS316', 'PVC'). prop (str): Property name (e.g., 'density', 'roughness'). Returns: Any: Property value if found, else None. |
| `get_material_data` | `get_material_data(material: str)` | Get all properties for a given pipeline material. Args: material (str): Material code. Returns: dict: Dictionary of material properties. |

### `processpi.pipelines.network`

**Source:** `processpi/pipelines/network.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Node` | `Node(self, name: str, elevation: float=0.0)` | Represents a connection point, junction, or endpoint in a pipeline network. Nodes have a name for identification and an elevation for calculating static head differences in the system. | — |
| `PipelineNetwork` | `PipelineNetwork(self, name: str, connection_type: Optional[str]='series')` | A framework for defining a process pipeline network. This class provides a dual-purpose structure: 1. A **node-and-edge graph** for general network problems. 2. A **composable series/parallel block model** for easier, hierarchical construction and calculation, compatible with a `PipelineEngine`. | `series()`, `parallel()`, `add()`, `add_series()`, `add_parallel()`, `add_node()`, `get_node()`, `add_edge()`, `add_fitting()`, `add_subnetwork()`, `validate()`, `describe()`, `schematic()`, `get_all_pipes()`, `visualize_network()` |

##### `Node`

Represents a connection point, junction, or endpoint in a pipeline network. Nodes have a name for identification and an elevation for calculating static head differences in the system.

**Methods**

No public methods beyond constructor/properties were discovered.

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

##### `PipelineNetwork`

A framework for defining a process pipeline network. This class provides a dual-purpose structure: 1. A **node-and-edge graph** for general network problems. 2. A **composable series/parallel block model** for easier, hierarchical construction and calculation, compatible with a `PipelineEngine`.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `series` | `series(name: str, *elements: Branch)` | Class method to create a series block pre-populated with elements. Args: name (str): The name for the series network. *elements (Branch): A variable number of elements (Pipes, Fittings, or other networks) to be added in series. Returns: PipelineNetwork: A new PipelineNetwork instance configured for series flow. |
| `parallel` | `parallel(name: str, *branches: Branch)` | Class method to create a parallel block with pre-defined branches. Args: name (str): The name for the parallel network. *branches (Branch): A variable number of branches (elements or child networks) that exist in parallel. Returns: PipelineNetwork: A new PipelineNetwork instance configured for parallel flow. |
| `add` | `add(self, *elements: Branch)` | A unified method to append one or more elements to the current network block. This provides a more fluent and readable interface for building. Args: *elements (Branch): One or more elements to add. Returns: PipelineNetwork: The current network instance, allowing for method chaining. |
| `add_series` | `add_series(self, *elements: Branch)` | Adds a series group to the network. If the current network is a series block, it appends the new elements directly. If it is a parallel block, it wraps the new elements in a child series network, which is then added as a branch. This preserves the correct hierarchical structure. Args: *elements (Branch): The elements to add to the series group. Returns: PipelineNetwork: The current network instance for chaining. |
| `add_parallel` | `add_parallel(self, *branches: Branch)` | Adds a parallel group to the network. If the current network is a parallel block, it appends the new branches directly. If it is a series block, it wraps the new branches in a child parallel network, which is then added as a single element. Args: *branches (Branch): The branches (elements or networks) to add to the parallel group. Returns: PipelineNetwork: The current network instance for chaining. |
| `add_node` | `add_node(self, name: str, elevation: float=0.0)` | Adds a new node (junction) to the network's internal node dictionary. Args: name (str): The unique name of the node. elevation (float, optional): The elevation in meters. Defaults to 0.0. Returns: Node: The newly created Node object. Raises: ValueError: If a node with the given name already exists. |
| `get_node` | `get_node(self, name: str)` | Fetches an existing node by name from the network's node dictionary. Args: name (str): The name of the node to retrieve. Returns: Node: The found Node object. Raises: KeyError: If the node does not exist in the network. |
| `add_edge` | `add_edge(self, component: Union[Pipe, Pump, Vessel, Equipment], start_node: str, end_node: str)` | Adds a connection (an edge) between two existing nodes using a component. This method strictly links components that have a defined inlet and outlet to the network's nodes. It also automatically adds the component to the network's `elements` list. Args: component (Union[Pipe, Pump, Vessel, Equipment]): The component to connect. start_node (str): The name of the inlet node. end_node (str): The name of the outlet node. Raises: ValueError: If either the start or end node is not found, or if a self-loop (start=end) is attempted. TypeError: If the component type is not supported for edge creation. |
| `add_fitting` | `add_fitting(self, fitting: Fitting, at_node: str)` | Adds a fitting to a specific node within the network. Fittings are considered zero-length elements, so they are associated with a single node rather than an edge. Args: fitting (Fitting): The fitting object to add. at_node (str): The name of the node where the fitting is located. Raises: ValueError: If the specified node does not exist. |
| `add_subnetwork` | `add_subnetwork(self, subnetwork: 'PipelineNetwork')` | Adds an existing PipelineNetwork instance as a child element. This provides compatibility with code that constructs subnetworks separately. Args: subnetwork (PipelineNetwork): The pre-built subnetwork to add. Raises: ValueError: If the subnetwork is the same as the parent network. |
| `validate` | `validate(self)` | Performs a comprehensive check for common network errors. This includes checking for unconnected nodes and ensuring all elements have required properties. Raises: ValueError: If any validation errors are found. The exception message will list all detected issues. |
| `describe` | `describe(self, level: int=0)` | Returns a detailed, hierarchical string representation of the network. Args: level (int): The current indentation level for nested networks. Returns: str: A multi-line string describing the network's structure. |
| `schematic` | `schematic(self)` | Generates an ASCII schematic representation of the network's hierarchical structure. Returns: str: A multi-line string visual representation of the network. |
| `get_all_pipes` | `get_all_pipes(self)` | Returns a flat list of all Pipe objects in this network, including nested subnetworks. Returns: list[Pipe]: List of Pipe objects found in the network. |
| `visualize_network` | `visualize_network(self, compact=False, width=1200, height=800)` | Interactive P&ID-style visualization using Plotly. Supports series, parallel, and circular loops. compact=True shortens node/edge labels for compact diagrams. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.nozzle`

**Source:** `processpi/pipelines/nozzle.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Nozzle` | `Nozzle(self, name: str, cv: float)` | No source docstring provided. See module purpose and examples. | `pressure_drop_at_flow()` |

##### `Nozzle`

Public class discovered from source. Constructor parameters are shown in the class table above.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `pressure_drop_at_flow` | `pressure_drop_at_flow(self, q: VolumetricFlowRate)` | No source docstring provided. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.pipelineresults`

**Source:** `processpi/pipelines/pipelineresults.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PipelineResults` | `PipelineResults(self, results: Dict[str, Any])` | Stores pipeline simulation results with full unit safety. Supports formatted summaries, detailed component tables, and raw exports. | `pipe_diameter()`, `summary()`, `detailed_summary()` |

##### `PipelineResults`

Stores pipeline simulation results with full unit safety. Supports formatted summaries, detailed component tables, and raw exports.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `pipe_diameter` | `pipe_diameter(self)` | No source docstring provided. |
| `summary` | `summary(self)` | Print and return a clean summary of results with units. |
| `detailed_summary` | `detailed_summary(self)` | Print a component-level breakdown in table form. Supports both old-style (nested dict) and new-style (flat keys) results. Removes duplicate rows and fills missing types. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.pipes`

**Source:** `processpi/pipelines/pipes.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Pipe` | `Pipe(self, name: str, nominal_diameter: Optional[Diameter]=None, schedule: str='STD', material: str='CS', length: Optional[Length]=None, inlet_pressure: Optional[Pressure]=None, outlet_pressure: Optional[Pressure]=None, internal_diameter: Optional[Diameter]=None, flow_rate: Optional[VolumetricFlowRate]=None, **kwargs: Any)` | Represents a straight section of a process pipeline. Encapsulates geometry (diameter, length), material properties (roughness), and state (inlet/outlet pressure). Useful for flow and pressure drop calculations, and compatible with optimization workflows. | `cross_sectional_area()`, `surface_area()`, `pressure_difference()`, `to_dict()`, `calculate()` |

##### `Pipe`

Represents a straight section of a process pipeline. Encapsulates geometry (diameter, length), material properties (roughness), and state (inlet/outlet pressure). Useful for flow and pressure drop calculations, and compatible with optimization workflows.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `cross_sectional_area` | `cross_sectional_area(self)` | Calculate internal cross-sectional area (m²). |
| `surface_area` | `surface_area(self)` | Calculate external surface area (m²). |
| `pressure_difference` | `pressure_difference(self)` | Calculate ΔP (inlet - outlet). |
| `to_dict` | `to_dict(self)` | Export all key pipe data as a dictionary. |
| `calculate` | `calculate(self)` | Return pipe data (for engine compatibility). |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.piping_costs`

**Source:** `processpi/pipelines/piping_costs.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `PipeCostModel` | `PipeCostModel(self, cost_data: Dict[str, Dict[str, float]])` | A simple model for calculating piping system costs based on diameter, material, and length. Costs are in dollars per meter. | `default_steel_model()`, `get_pipe_cost()`, `calculate_network_cost()` |

##### `PipeCostModel`

A simple model for calculating piping system costs based on diameter, material, and length. Costs are in dollars per meter.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `default_steel_model` | `default_steel_model(cls)` | Returns a predefined cost model for carbon steel pipes. |
| `get_pipe_cost` | `get_pipe_cost(self, nominal_diameter: Union[str, float, int], material: str)` | Retrieves the cost per meter for a given pipe size and material. |
| `calculate_network_cost` | `calculate_network_cost(self, network: PipelineNetwork)` | Calculates the total cost of all pipes in a given network. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.pumps`

**Source:** `processpi/pipelines/pumps.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Pump` | `Pump(self, name: str, pump_type: str, flow_rate: Optional[VolumetricFlowRate]=None, head: Optional[Length]=None, density: Optional[Density]=None, efficiency: Optional[float]=None, inlet_pressure: Optional[Pressure]=None, outlet_pressure: Optional[Pressure]=None)` | Represents a pump in a pipeline system. Attributes: name (str): The name of the pump. pump_type (str): Type of pump (e.g., 'centrifugal', 'positive_displacement'). flow_rate (Optional[FlowRate]): Volumetric flow rate. head (Optional[Length]): Pump head, representing the energy added per unit weight of fluid. density (Density): Fluid density. efficiency (float): Pump efficiency (0 < η <= 1). inlet_pressure (Optional[Pressure]): Inlet pressure to the pump. outlet_pressure (Optional[Pressure]): Outlet pressure from the pump. start_node (Optional[Any]): The node object at the pump's inlet. end_node (Optional[Any]): The node object at the pump's outlet. | `hydraulic_power()`, `brake_power()`, `to_dict()`, `calculate()` |

##### `Pump`

Represents a pump in a pipeline system. Attributes: name (str): The name of the pump. pump_type (str): Type of pump (e.g., 'centrifugal', 'positive_displacement'). flow_rate (Optional[FlowRate]): Volumetric flow rate. head (Optional[Length]): Pump head, representing the energy added per unit weight of fluid. density (Density): Fluid density. efficiency (float): Pump efficiency (0 < η <= 1). inlet_pressure (Optional[Pressure]): Inlet pressure to the pump. outlet_pressure (Optional[Pressure]): Outlet pressure from the pump. start_node (Optional[Any]): The node object at the pump's inlet. end_node (Optional[Any]): The node object at the pump's outlet.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `hydraulic_power` | `hydraulic_power(self)` | Calculates the hydraulic power (fluid power) delivered by the pump. Formula: P_h = ρ * g * Q * H Returns: Optional[Power]: The hydraulic power as a Power object (W), or None if flow rate or head is not defined. |
| `brake_power` | `brake_power(self)` | Calculates the brake power (shaft power) required to drive the pump, considering its efficiency. Formula: P_b = P_h / η Returns: Optional[Power]: The brake power as a Power object (W), or None if hydraulic power cannot be calculated. |
| `to_dict` | `to_dict(self)` | Exports pump properties and calculations as a dictionary for reporting. |
| `calculate` | `calculate(self)` | This method serves as a wrapper to perform calculations and return the results as a dictionary. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.selection`

**Source:** `processpi/pipelines/selection.py`

**Purpose:** Pipeline Material Selection Module This module provides logic for selecting appropriate pipeline materials based on design conditions such as temperature, pressure, and corrosion requirements. Uses data from materials.py

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `MaterialSelector` | `MaterialSelector(self, design_temp: float, design_pressure: float, corrosive: bool=False)` | Class for selecting suitable pipeline materials. | `filter_materials()`, `recommend_material()` |

##### `MaterialSelector`

Class for selecting suitable pipeline materials.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `filter_materials` | `filter_materials(self)` | Filter materials that can withstand design conditions. Returns: list: Suitable material codes. |
| `recommend_material` | `recommend_material(self)` | Recommend the most suitable material based on design conditions. Returns: dict: Recommended material data. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.

### `processpi.pipelines.standards`

**Source:** `processpi/pipelines/standards.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Functions

| Function | Signature | Description |
| --- | --- | --- |
| `get_internal_diameter` | `get_internal_diameter(nominal_diameter: Diameter, schedule: str='STD')` | Returns internal diameter for a given nominal diameter and schedule. |
| `get_thickness` | `get_thickness(nominal_diameter: Diameter, schedule: str='STD')` | Returns wall thickness for a given nominal diameter and schedule. |
| `get_roughness` | `get_roughness(material: str)` | Returns roughness for given material. Defaults if not found. |
| `get_recommended_velocity` | `get_recommended_velocity(service: str)` | Returns recommended velocity (m/s) for a given chemical or general service. |
| `get_nearest_diameter` | `get_nearest_diameter(calculated_diameter: Diameter)` | Returns the nearest standard nominal diameter for a given calculated diameter. |
| `get_standard_pipe_data` | `get_standard_pipe_data(nominal_diameter: Diameter, schedule: str='STD')` | Returns a dictionary of standard pipe properties for a given nominal size and schedule. |
| `get_k_factor` | `get_k_factor(fitting_type: str)` | Retrieve the standard K-factor (loss coefficient) for a given fitting type. |
| `list_available_pipe_diameters` | `list_available_pipe_diameters()` | Returns a list of all available standard nominal pipe diameters. |
| `get_next_standard_nominal` | `get_next_standard_nominal(diameter_m: float)` | Finds the next standard nominal size >= given diameter (inner diameter basis). If no larger diameter is found, returns the largest available. |
| `get_previous_standard_nominal` | `get_previous_standard_nominal(nominal_diameter: Diameter)` | Finds the previous standard nominal size in the sorted list. |
| `get_next_next_standard_nominal` | `get_next_next_standard_nominal(nominal_diameter: Diameter)` | Finds the next-next standard nominal size in the sorted list. |
| `get_standard_diameters_list` | `get_standard_diameters_list()` | Returns a sorted list of standard nominal diameters. |
| `get_equivalent_length` | `get_equivalent_length(fitting_type: str)` | Return the equivalent length multiplier (Le/D) for a fitting type. |
| `get_k_factor` | `get_k_factor(fitting_type: str, reynolds_number: Optional[float]=None, relative_roughness: Optional[float]=None, diameter: Optional[float]=None)` | Return the K-factor (resistance coefficient) for a fitting type. Includes logic for Reynolds number-dependent fittings. Args: fitting_type: The type of fitting. reynolds_number: Reynolds number of the flow (for fittings where K depends on Re). relative_roughness: Pipe roughness divided by diameter (not always used). diameter: Pipe internal diameter in meters. Returns: The K-factor as a float, or None if not found. |
| `get_nominal_dia_from_internal_dia` | `get_nominal_dia_from_internal_dia(internal_diameter: Diameter, schedule: str='STD')` | Finds the nominal diameter of a pipe given its internal diameter and schedule. This function performs a reverse lookup in the PIPE_SCHEDULES data. It iterates through all nominal diameters and calculates the corresponding internal diameter for a given schedule. It returns the first nominal diameter that matches the input internal diameter. Args: internal_diameter (Diameter): The internal diameter of the pipe. schedule (str): The pipe schedule (e.g., "STD", "40", "80"). Returns: Optional[Diameter]: The nominal diameter, or None if no match is found. |

### `processpi.pipelines.vessel`

**Source:** `processpi/pipelines/vessel.py`

**Purpose:** Pipeline, fittings, material, network, hydraulic engine, or standards helper.

#### Classes

| Class | Constructor | Description | Public methods |
| --- | --- | --- | --- |
| `Vessel` | `Vessel(self, name: str, volume: float=0.0, pressure: float=0.0, temperature: float=0.0)` | Vessel represents a storage or process vessel in a fluid network. It can have one or more inlet and outlet connections, allowing it to serve as a hub for fluid flow within a pipeline system. | `add_inlet()`, `add_outlet()` |

##### `Vessel`

Vessel represents a storage or process vessel in a fluid network. It can have one or more inlet and outlet connections, allowing it to serve as a hub for fluid flow within a pipeline system.

**Methods**

| Method | Signature | Notes |
| --- | --- | --- |
| `add_inlet` | `add_inlet(self, node)` | Attaches a new inlet node to the vessel. Args: node: The node object (e.g., from a Pipe or Pump) that feeds into the vessel. |
| `add_outlet` | `add_outlet(self, node)` | Attaches a new outlet node to the vessel. Args: node: The node object (e.g., from a Pipe or Valve) that the vessel feeds into. |

**Typical exceptions**: `ValueError` for invalid engineering inputs, `TypeError` for incompatible object types, and `NotImplementedError` where a future method is reserved.
