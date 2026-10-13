# Class: `PipelineEngine`

The **`PipelineEngine`** is the main interface for pipeline network analysis in ProcessPI.  
It performs **component-wise and network-wide calculations**, including **pressure drops, velocities, Reynolds numbers, friction factors**, and **optimum pipe sizing**.

---

## Methods

**`fit()`**
Configures the `PipelineEngine` instance by processing input parameters, converting units, normalizing keys, and setting default values.

**Parameters**  
- `**kwargs`: Keyword arguments representing pipeline properties (`flowrate`, `nominal_diameter`, `internal_diameter`, `schedule`, `velocity`, `length`) and solver configuration (`method`, `solver`).

**Functionality**
- **Data Initialization:** Stores inputs in `data` dictionary.  
- **Alias Mapping:** Normalizes input keys using a predefined `alias_map`.

| Key              | Aliases                                         |
|------------------|-------------------------------------------------|
| `flowrate`       | `flow_rate`, `q`, `Q`, `flowrate`               |
| `mass_flowrate`  | `mass_flow`, `m_dot`, `mdot`                    |
| `velocity`       | `v`                                             |
| `internal_diameter` | `diameter`, `dia`, `D` (deprecated, see below) |
| `length`         | `len`, `L`                                      |
| `inlet_pressure` | `in_pressure`, `pin`, `p_in`                    |
| `outlet_pressure`| `out_pressure`, `pout`, `p_out`                 |

- **Pipe size:** `nominal_diameter` and `internal_diameter` are separate inputs:
  - `nominal_diameter` is the pipe size, an NPS (`Diameter(4, "in")`) or a DN in millimetres (`Diameter(100, "mm")`, which is NPS 4). The internal diameter is looked up for `schedule` (default `"STD"`) in the ASME B36.10M / B36.19M table: NPS 4 STD is 102.26 mm.
  - `internal_diameter` is the bore, used as given.
  - Given both, the internal diameter is used (a lined pipe, a wall the table does not list) and must be smaller than the nominal size's outside diameter, otherwise `ValueError`.
  - A `nominal_diameter` that is not a standard size cannot be looked up; it is used as the internal diameter, with a `UserWarning`.
  - `diameter` (and `dia`, `D`) is the internal diameter, as before, with a `DeprecationWarning`. Until this change `nominal_diameter` was an alias of it, so a nominal 4 in was used as a 101.6 mm bore.
  - With none of these, a `pipe` passed to `fit()` that has a nominal or internal diameter is calculated on its own size. It used to be ignored and the pipe sized. A diameter given to `fit()` is used over the pipe's, as before, with a `UserWarning` when the two differ.
- **Bare numbers:** a diameter given as a plain number is read in millimetres (metres with `assume_mm_for_numbers=False`), a length in metres, as before, each with a `UserWarning` naming the unit. Pass `Diameter` and `Length` objects to avoid both.
- **Default Values:** Applies defaults for `assume_mm_for_numbers`, `flow_split`, `tolerance_m3s`, `pump_efficiency`, `method`, `hw_coefficient`, and `solver`.  
- **Network Validation:** Validates that `network` is a `PipelineNetwork` instance.  
- **Attribute Binding:** Binds normalized parameters (`flowrate`, `mass_flowrate`, `velocity`, `nominal_diameter`, `internal_diameter`, and `diameter`, the same bore) as instance attributes.

**Returns**  
- `PipelineEngine`: Configured instance for method chaining.

**Raises**  
- `TypeError`: If `network` is not a `PipelineNetwork`.
- `ValueError`: If the diameter inputs contradict each other, or `schedule` is not tabulated for the nominal size.

```python
model.fit(fluid=Water(), flowrate=VolumetricFlowRate(50, "m3/h"), length=Length(100, "m"),
          nominal_diameter=Diameter(4, "in"), schedule="40")   # bore 102.26 mm
model.fit(fluid=Water(), flowrate=VolumetricFlowRate(50, "m3/h"), length=Length(100, "m"),
          internal_diameter=Diameter(102.26, "mm"))             # the same bore, given directly
```

The results report both: `summary["nominal_diameter"]` and the component `nominal_diameter` (None when only a bore was given), `summary["calculated_diameter_m"]` and the component `diameter` (the bore used).

---

**`run()`**
Executes the pipeline simulation based on inputs from `fit()`.  
Chooses between **Network Mode** or **Single Pipe Mode**.

**Parameters**  
- None (relies on `data` populated by `fit()`).

**Returns**  
- `PipelineResults`: Encapsulates simulation results.

**Core Logic**
- **Network Mode** (with `network` object):  
  - Diameter Check → Auto-sizing if missing: only pipes without a diameter are sized, each for the flow it carries in the network (a parallel block's flow split by `flow_split` when given, evenly otherwise; in a graph network the flow of its own edge); a pipe with a nominal or internal diameter keeps it  
  - Flowrate Assignment → Distributes flow  
  - Network Solving → Pressure drop, head, pump power  
  - A network built with `add_node` / `add_edge` is solved as a graph: the flow in each edge from the mass balance at the nodes (node demands, outlets), the loops balanced so that the drops around each loop add up to zero, and the network drop taken from the inlet to the outlet with the lowest pressure. See [Solving a graph network](network.md#solving-a-graph-network).  

- **Single Pipe Mode** (without `network`):  
  - If no diameter (in `fit()` or on the `pipe`) → Solves for optimum diameter  
  - If diameter present → Standard hydraulic calculation  

- **Sizing:** without `available_dp`, the size is the standard bore at or above the one for the middle of the fluid's recommended velocity range; when that size is below the range and the next smaller size is within the maximum, the smaller size is used. With `available_dp`, it is the smallest size whose drop fits in it and whose velocity is at or below the maximum. When the velocity is still outside the range, the warning says which limit governs.

**Results Output**  
- Consolidates into `results_out` → returned as `PipelineResults`.

---

**`summary()`**
Retrieves a summary of the most recent simulation.

**Parameters**  
- None  

**Functionality**
- Checks if `_results` exists  
- Returns summary from `PipelineResults` or `None`

**Returns**  
- `PipelineResults` (summary) or `None`

---

## Engine Helper Functions

These private helper methods are used internally by the `PipelineEngine` class to retrieve properties and perform the core hydraulic calculations for both single pipes and entire networks.

---

### Property Resolvers

**`_get_density`**
- Retrieves or infers fluid density.  
- **Returns:** `Density`  
- **Raises:** `ValueError` if not available.

**`_get_viscosity`**
- Retrieves or infers viscosity.  
- **Returns:** `Viscosity`  
- **Raises:** `ValueError` if not available.

**`_infer_flowrate`**
- Infers volumetric flow rate from:
  - Direct `flowrate`
  - `mass_flowrate` + density
  - `velocity` + `diameter`  
- **Returns:** `VolumetricFlowRate`  
- **Raises:** `ValueError` if inference fails.

**`_maybe_velocity`**
- Ensures velocity is available.  
- Calculates from `flowrate` and `diameter` if missing.  
- **Returns:** `Velocity`  
- **Raises:** `ValueError` if data is insufficient.

**`_resolve_internal_diameter`**
Determines the internal diameter of a pipe using a priority order:
1. `pipe.internal_diameter` (explicitly defined)  
2. `pipe.nominal_diameter`, looked up with `pipe.schedule` in the schedule table (a size that is not tabulated is used as the bore, with a `UserWarning`)  
3. `engine.diameter` (default from `fit`)  
4. **Fallback:** Calculates hydraulically optimum diameter  

- **Parameters:** `pipe (Optional[Pipe])`  
- **Returns:** `Diameter`  

---

### Primitive Calculators

**`_velocity`**
- **Purpose:** Calculates fluid velocity.  
- **Parameters:** `q (VolumetricFlowRate)`, `d (Diameter)`  
- **Returns:** `Velocity`  

**`_reynolds`**
- **Purpose:** Computes Reynolds number to determine flow regime.  
- **Parameters:** `v (Velocity)`, `d (Diameter)`  
- **Returns:** `float`  

**`_friction_factor`**
- **Purpose:** Friction factor using Colebrook-White correlation.  
- **Parameters:** `Re (float)`, `d (Diameter)`, `material (Optional[str])`  
- **Returns:** `float`  

**`_major_dp_pa`**
- **Purpose:** Major pressure drop due to friction.  
- **Parameters:** `f (float)`, `L (Length)`, `d (Diameter)`, `v (Velocity)`  
- **Returns:** `Pressure (Pa)`  

**`_minor_dp_pa`**
- **Purpose:** Minor losses due to fittings (elbows, valves, etc.).  
- **Rule (per fitting):** both methods are worked out and the higher loss is used:  
  1. **K-Factor:** `K * rho v^2 / 2` (`K_FACTORS`)  
  2. **Equivalent Length:** `f * (Le/D) * rho v^2 / 2` with the pipe's Darcy `f` (`EQUIVALENT_LENGTHS`)  
  A fitting found in only one table uses that one; one found in neither adds nothing and warns.
  A `K`, `K_factor`, `Le` (per unit) or `total_K`, `total_Le` (whole quantity) set on the fitting replaces the tables.  
- **Details:** `_fitting_loss` returns both losses and `fitting_method` (`"K"` or `"Le/D"`);
  `_pipe_calculation` lists them under `fitting_losses`, and the component reports carry that list.  

- **Parameters:** `fitting (Fitting)`, `v (Velocity)`, `f (Optional[float])`, `d (Diameter)`  
- **Returns:** `Pressure (Pa)`  

---

### Composite Calculator

**`_pipe_calculation`**
Orchestrates all primitives to perform full pipe analysis.

**Functionality**
1. Resolves diameter & flow (via `_resolve_internal_diameter`, `_infer_flowrate`).  
2. Computes Reynolds number & friction factor.  
3. Calculates **major losses**, **minor losses**, and **elevation effects**.  
4. Aggregates results into a structured output.  

**Parameters:** `pipe (Pipe)`, `flow_rate (Optional[VolumetricFlowRate])`  
**Returns:** `Dict[str, Any]` → Includes:
- Diameter  
- Velocity  
- Reynolds number  
- Major losses  
- Minor losses  
- Elevation losses  
- Total pressure drop  

---
### **Series and Network Evaluation**

**`_compute_series`**
- **Purpose:** Calculates the total pressure drop for a series of pipes. In a series, the flow rate is constant, and the total pressure drop is the sum of the pressure drops of each individual pipe and its fittings.  
- **Normalization:** It intelligently handles various inputs (a single Pipe, a list of Pipes, or a list of branches) by flattening them into a single series of pipes before calculation.  
- **Returns:** A tuple containing the total pressure drop, a list of detailed reports for each pipe, and a summary of the series.  

**`_compute_network`**
- **Purpose:** Serves as a high-level function for calculating the total pressure drop of a more complex network. It normalizes the network structure into a list of branches before performing calculations.  
- **Logic:** It iterates through each branch and calls `_pipe_calculation` to get the pressure drop for each pipe within that branch. It then aggregates these results to provide a comprehensive report for the entire network.  
- **Returns:** A tuple containing the total network pressure drop, a list of all element reports, and a network summary.  

---

### **Network Solvers**

**`_balance_parallel_flows`** and **`_solve_network_dual`** (series/parallel block networks)
- **Purpose:** Balance the flow between the branches of a parallel block until every branch has the same pressure drop (or apply `flow_split` when given), and add the drops of series elements.  
- **Logic:** It starts with an equal split and updates each branch flow as q * sqrt(dp_mean / dp), rescaled to the total, until the spread of the branch drops is below 1e-4 of their mean.  

**`_solve_graph_network`** (networks built with `add_node` / `add_edge`)
- **Purpose:** Finds the flow in every edge from the mass balance at the nodes, then the drop along each edge, the node pressures and the governing drop (inlet to the outlet with the lowest pressure).  
- **Logic:** `_graph_topology` finds the inlet, the flow leaving each node (demands, outlets) and a spanning tree; each edge outside the tree closes one loop. The tree edges carry what the mass balance gives them. The loop flows are solved by Newton's method on all loops at once (`_graph_balance_loops`; Hardy Cross applies the same correction one loop at a time): r is the pressure imbalance of each loop, J sums the slopes 2 dp/q of the edges two loops share, and J dq = -r is solved by Gaussian elimination, until every loop's imbalance is below 1e-6 of the losses around it. `_size_graph_network` sizes the pipes without a diameter on their edge flows, solving again until the sizes settle in a looped network.  

---

### **Utility Helpers**

- **`_select_standard_diameter`**: Maps an ideal calculated diameter to the nearest available standard pipe size.  
- **`_as_pressure`**: Ensures that a given input is correctly converted to a Pressure object with a specified unit.  
- **`_pump_gain_pa`**: Calculates the pressure gain provided by a pump, converting from either head or inlet/outlet pressure values.  
- **`_equipment_dp_pa`**: Handles the pressure drop of non-pipe equipment, such as filters or heat exchangers, converting units as needed.  
- **`_fitting_dp_pa`**: A specialized helper for calculating the pressure drop of a single fitting using K-factors or equivalent lengths.  
- **`_normalize_branches`**: A crucial function for preparing network data. It takes various network inputs and flattens them into a consistent, nested list structure (`list[list[Pipe]]`), making them ready for the solvers.  

---

## ✅ Key Features

**Single Pipeline Analysis**
- Pressure drop & flow rate via:
  - **Darcy–Weisbach** (precise)  
  - **Hazen–Williams** (quick for water)  
- Accounts for elevation, roughness, fittings, valves.

**Network Analysis**
- Series/parallel block networks (balanced parallel branches)  
- Branched/looped networks built from nodes and edges, with node demands (Newton loop solver with the Hardy Cross terms)  
- Supports plant utility networks, firewater loops, cooling systems.

**Component Loss Modeling**
- Inline equipment & fittings (valves, bends, tees, orifices).  
- Uses **K-factor data** for accurate modeling.

**Elevation & Static Head**
- Includes elevation effects.  
- Suitable for tanks, hilly terrains, sump transfers.

**Multiple Solver Options**

| Solver            | Best For                       | Notes                            |
|-------------------|--------------------------------|----------------------------------|
| Darcy–Weisbach    | Precise engineering calcs       | Custom fluid properties supported |
| Hazen–Williams    | Quick water line checks         | Assumes low viscosity             |
| Graph loop solver | `add_edge` networks with loops  | Newton on all loops at once       |

**Typical Use Cases**
- Utility water networks  
- Chemical transfer lines  
- Cooling water loops  
- Firewater ring mains  
- Static head studies  

**Current Limitations**
- Steady-state only  
- Single-phase only  
- Constant density/viscosity  
- No pump curves  
- Limited to ~50 pipes  

**Planned Roadmap**

| Stage        | Feature                                      |
|--------------|----------------------------------------------|
| Short-term   | Newton–Raphson solver for larger networks    |
| Mid-term     | Pump curve integration + auto pump point     |
| Mid-term     | Compressible (gas) network support           |
| Long-term    | Dynamic/transient (surge, water hammer)      |
| Long-term    | Two-phase and slurry flow models             |

---

## 💻 Example Usage

**Dry Chlorine Gas Pipeline**

```python
from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine

# Define fluid and mass flow
fluid = Chlorine(temperature=Temperature(20, "C"), pressure=Pressure(6, "atm"))
mass_flow = MassFlowRate(10000, "kg/h")

print(fluid.density())

# Create engine without an explicit network
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow
    # realistic pipe length can be added
)
results = model.run()  # auto diameter sizing
results.summary()
results.detailed_summary()
```

---

