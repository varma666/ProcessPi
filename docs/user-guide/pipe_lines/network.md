The **Pipeline Network** module provides a flexible framework for modeling process piping systems.  
It supports both **graph-based networks** (nodes & edges) and **hierarchical block construction** (series/parallel), making it compatible with the `PipelineEngine`.

---

## Classes and Types

### `Node`
Represents a junction or endpoint in the network.
- **Attributes:**
  - `name` (str): Unique identifier.
  - `elevation` (float): Node elevation (m).
  - `pressure` (Pressure, optional).
  - `flow_rate` (VolumetricFlowRate, optional).
  - `connected_components` (List[Any]): Components linked to this node.

---

### `Branch`
A branch in a parallel block can be one of:
- `PipelineNetwork`
- `Pipe`
- `Fitting`
- `Pump`
- `Vessel`
- `Equipment`

---

### `PipelineNetwork`
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
| `add_node(name, elevation=0.0)` | Add a new node. |
| `get_node(name)` | Fetch an existing node. |
| `add_edge(component, start_node, end_node)` | Connect two nodes via a component. |
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

# Create nodes
net = PipelineNetwork("MainNet")
net.add_node("A", elevation=0.0)
net.add_node("B", elevation=5.0)

# Add a pipe between nodes
pipe = Pipe(diameter="100 mm", length=20)
net.add_edge(pipe, "A", "B")

# Validate
net.validate()

# Describe structure
print(net.describe())

# Show ASCII schematic
print(net.schematic())
```

---
