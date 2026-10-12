The **Pipeline Network** module provides a flexible framework for modeling process piping systems.  
It supports both **graph-based networks** (nodes & edges) and **hierarchical block construction** (series/parallel), making it compatible with the `PipelineEngine`.

---

## Classes and Types

`Node`
Represents a junction or endpoint in the network.

- **Attributes:**
  - `name` (str): Unique identifier.
  - `elevation` (float): Node elevation (m).
  - `demand` (VolumetricFlowRate, optional): Flow that leaves the network at this node (an outlet or an offtake). See [Solving a graph network](#solving-a-graph-network).
  - `pressure` (Pressure, optional).
  - `flow_rate` (VolumetricFlowRate, optional).
  - `connected_components` (List[Any]): Components linked to this node.

---

`Branch`

A branch in a parallel block can be one of:
- `PipelineNetwork`
- `Pipe`
- `Fitting`
- `Pump`
- `Vessel`
- `Equipment`

---

`PipelineNetwork`
Defines the structure of a pipeline network.

- **Attributes:**
  - `name` (str): Identifier for the network.
  - `nodes` (Dict[str, Node]): Dictionary of nodes.
  - `elements` (List[Branch]): Contained components.
  - `connection_type` (str): `"series"` or `"parallel"`.

---

## Key Methods

| Method | Purpose |
|--------|---------|
| `series(name, *elements)` | Create a series block with elements. |
| `parallel(name, *branches)` | Create a parallel block with branches. |
| `add(*elements)` | Add elements directly. |
| `add_series(*elements)` | Add elements as a series group. |
| `add_parallel(*branches)` | Add elements as a parallel group. |
| `add_node(name, elevation=0.0, demand=None)` | Add a new node, optionally with the flow that leaves the network there. |
| `get_node(name)` | Fetch an existing node. |
| `add_edge(component, start_node, end_node)` | Connect two nodes via a component; the direction is the direction of positive flow. |
| `add_fitting(fitting, at_node)` | Add a fitting at a node. |
| `add_subnetwork(subnetwork)` | Add a nested PipelineNetwork. |
| `validate()` | Perform error checks (unconnected nodes, missing data). |
| `describe(level=0)` | Hierarchical description of the network. |
| `schematic()` | ASCII schematic diagram. |
| `get_all_pipes()` | Returns all `Pipe` objects recursively. |
| `visualize_network(compact=False)` | Interactive visualization (Plotly). |

---

## Validation
The `validate()` method checks for:
- Unconnected nodes.
- Missing diameter/K/L data in fittings.
- Pumps with missing head/pressures.
- Equipment with missing pressure drop.

---

## ASCII Schematic Example
```text
MainNet [series]
  └─1. Pipe-1
  └─2. Pump-A
  └─SubNet [parallel]
      ┌─(branch 1)
      │   └─ Pipe-2
      ┌─(branch 2)
      │   └─ Pipe-3
```

---


## Example Usage
```python
from processpi.pipelines.network import PipelineNetwork, Node
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length

# Create nodes
net = PipelineNetwork("MainNet")
net.add_node("A", elevation=0.0)
net.add_node("B", elevation=5.0)

# Add a pipe between nodes
pipe = Pipe("P1", nominal_diameter=Diameter(4, "in"), length=Length(20, "m"))
net.add_edge(pipe, "A", "B")

# Validate
net.validate()

# Describe structure
print(net.describe())

# Show ASCII schematic
print(net.schematic())
```

---

## Solving a graph network

A network built with `add_node` and `add_edge` is solved by `PipelineEngine` as a graph. (Until now it ran as one series chain, every edge carrying the full network flow.)

- **Inlet:** the one node that no edge enters. The flow given to `fit()` enters there.
- **Direction:** an edge's direction (start to end) is the direction of positive flow. A flow that runs the other way is reported as negative.
- **Outlets and demands:** the flow leaves at the nodes that no edge leaves (outlets) and at nodes with a `demand`. A node with a demand and outgoing edges is an offtake. Outlets without a demand take what the demands leave, at one common pressure. If every outlet has a demand, the demands must add up to the inlet flow; demands above the inlet flow raise `ValueError`.
- **Flows:** in a tree network the flows follow from the mass balance at the nodes. In a looped network (parallel lines, rings, several outlets without a demand) the flow around each loop is found so that the pressure drops around every loop add up to zero: Newton's method on all loops at once, with the Hardy Cross terms (the loop imbalance, and the slope 2 dp/q of each pipe), until every loop's imbalance is below 1e-6 of the losses around it. A loop that has no pipe in it raises `ValueError`, since nothing then sets its split.
- **Drops:** a pipe's friction and fitting losses are those of a single-pipe run at its flow. The static head rho g (z_end - z_start) is counted on every edge with its sign, so a downhill edge gains pressure. A pump adds its fixed gain and equipment its fixed drop, as in block networks.
- **Results:** each component carries `start_node`, `end_node`, its signed `flow_m3s`, `pressure_drop_Pa` (start pressure minus end pressure) and `elevation_dp_Pa`. The summary has `inlet_node`, `number_of_loops`, `outlet_flows_m3s`, `node_pressure_drop_Pa` (the drop from the inlet to each node), `node_pressures_Pa` (when `fit()` is given an `inlet_pressure`), `governing_outlet` (the outlet with the lowest pressure), `governing_path`, and `total_pressure_drop_Pa`, the drop from the inlet to the governing outlet.
- **Sizing:** a pipe without a diameter is sized for the flow of its own edge. In a looped network the split depends on the sizes, so the engine sizes, solves and sizes again until no size changes. Pipes with a diameter keep it.
- **Networks that cannot be solved as a graph** (more than one inlet, no outlet, unconnected parts, or edges mixed with series/parallel blocks) run as a series chain, as before, with a `UserWarning`. A closed circuit has no outlet: open it at its tank, with the tank outlet as the inlet node and the tank return as the outlet node (see the [chilled water loop](../../examples/pipelines/chilled_water_loop.md)).

```python
from processpi.components import Water
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import Diameter, Length, VolumetricFlowRate

net = PipelineNetwork("Cooling Water")
net.add_node("Pump", elevation=0)
net.add_node("Header", elevation=2)
net.add_node("HX1", elevation=2, demand=VolumetricFlowRate(30, "m3/h"))
net.add_node("HX2", elevation=5, demand=VolumetricFlowRate(20, "m3/h"))
net.add_node("Drain", elevation=0)  # no demand: takes the rest

net.add_edge(Pipe("Supply", nominal_diameter=Diameter(6, "in"), length=Length(40, "m")), "Pump", "Header")
net.add_edge(Pipe("ToHX1", nominal_diameter=Diameter(3, "in"), length=Length(25, "m")), "Header", "HX1")
# Two lines to HX2 in parallel: a loop
net.add_edge(Pipe("ToHX2_A", nominal_diameter=Diameter(3, "in"), length=Length(30, "m")), "Header", "HX2")
net.add_edge(Pipe("ToHX2_B", nominal_diameter=Diameter(2, "in"), length=Length(20, "m")), "Header", "HX2")
# No diameter: sized for its own flow
net.add_edge(Pipe("Overflow", length=Length(15, "m")), "Header", "Drain")

model = PipelineEngine().fit(fluid=Water(), flowrate=VolumetricFlowRate(80, "m3/h"), network=net)
results = model.run()
results.summary()
results.detailed_summary()
```

**Output**

```text
🔄 Auto-sizing network pipe diameters...
🔍 Pipe Overflow: No available DP provided. Showing candidates:
  2.5 in -> 2.70 m/s, 17345.18 Pa
  3.0 in -> 1.75 m/s, 5772.78 Pa
  3.5 in -> 1.31 m/s, 2784.17 Pa

=== Pipeline Result 1 (N/A) ===
Mode: Network
Nominal Pipe Size: 6 in
Internal Diameter: 154.08 mm
Inlet Flow: 0.022 m3/s 
Outlet Flow: 0.022 m3/s 
Total Pressure Drop: 54.76 kPa
Total Head Loss: 5.61 m
Total Power Required: 1.74 kW
Velocity: 0.000 m/s
Reynolds Number: 0 (dimensionless)
Friction Factor: 0.0000 (dimensionless)
Flow Solver: graph, 1 loop(s), converged in 8 iteration(s)
Governing Outlet: HX2 (drop from inlet Pump: 54.76 kPa)
Outlet Flows: HX1 30.00 m3/h, HX2 20.00 m3/h, Drain 30.00 m3/h

=== Detailed Components for Result 1 (N/A) ===
+----------+--------+----------------+---------------+-----------------+------------+------------+-------------------+----------------+---------------------+
| Name     | Type   | Edge           |   Flow (m3/h) |   Pressure Drop |   Velocity |   Reynolds |   Friction Factor | Nominal Size   | Internal Diameter   |
+==========+========+================+===============+=================+============+============+===================+================+=====================+
| Supply   | pipe   | Pump > Header  |         80    |         22749.7 |       1.19 |   200164   |            0.0177 | 6 in           | 154.08 mm           |
+----------+--------+----------------+---------------+-----------------+------------+------------+-------------------+----------------+---------------------+
| ToHX1    | pipe   | Header > HX1   |         30    |          9621.3 |       1.75 |   148428   |            0.0197 | 3 in           | 77.92 mm            |
+----------+--------+----------------+---------------+-----------------+------------+------------+-------------------+----------------+---------------------+
| ToHX2_A  | pipe   | Header > HX2   |         13.96 |         32008.6 |       0.81 |    69049   |            0.0217 | 3 in           | 77.92 mm            |
+----------+--------+----------------+---------------+-----------------+------------+------------+-------------------+----------------+---------------------+
| ToHX2_B  | pipe   | Header > HX2   |          6.04 |         32008.6 |       0.78 |    44398.5 |            0.024  | 2 in           | 52.48 mm            |
+----------+--------+----------------+---------------+-----------------+------------+------------+-------------------+----------------+---------------------+
| Overflow | pipe   | Header > Drain |         30    |        -13736.2 |       1.75 |   148428   |            0.0197 | 3 in           | 77.92 mm            |
+----------+--------+----------------+---------------+-----------------+------------+------------+-------------------+----------------+---------------------+
+----------+---------------+-------------------------+
| Outlet   |   Flow (m3/h) |   Drop from Inlet (kPa) |
+==========+===============+=========================+
| HX1      |            30 |                   32.37 |
+----------+---------------+-------------------------+
| HX2      |            20 |                   54.76 |
+----------+---------------+-------------------------+
| Drain    |            30 |                    9.01 |
+----------+---------------+-------------------------+
```

The two lines to HX2 form a loop and end with the same drop (32.01 kPa), the 3 in line carrying 13.96 m3/h and the 2 in line 6.04 m3/h. Drain, with no demand, takes the 30 m3/h the demands leave; its line runs 2 m downhill, so its drop is negative. HX2, 5 m up, has the lowest pressure and governs: the network drop is the 54.76 kPa from Pump to HX2.

---
