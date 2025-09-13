# Complex Network with Pumps, Vessels & Equipment

**Problem**

Build and validate a network with multiple branches, fittings, pumps, vessels, and equipment.  
This example demonstrates network creation, validation, and visualization of a process pipeline system.

## Code

```python
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.pumps import Pump
from processpi.pipelines.vessel import Vessel
from processpi.pipelines.equipment import Equipment
from processpi.units import Diameter

# Create main network
net = PipelineNetwork("MainPlantLoop")

# Define nodes
for node in ["A","B","C","D","E","F","G","H"]:
    net.add_node(node)

# Define elements
pipe1 = Pipe("Pipe1", nominal_diameter=100, length=10)
pipe2 = Pipe("Pipe2", nominal_diameter=150, length=15)
pump1 = Pump("Pump1", pump_type="Centrifugal", head=20)
vessel1 = Vessel("Separator1")
equipment1 = Equipment("HeatExchanger", pressure_drop=0.5)

# Connect series and branches
net.add_edge(pipe1, "A", "B")
net.add_edge(pipe2, "B", "C")
net.add_edge(pump1, "C", "D")
net.add_edge(Pipe("PipeBranch1", nominal_diameter=80, length=5), "D", "E")
net.add_edge(Pipe("PipeBranch2", nominal_diameter=120, length=8), "D", "F")
net.add_edge(Pipe("PipeEG", nominal_diameter=100, length=12), "E", "G")
net.add_edge(Pipe("PipeFH", nominal_diameter=100, length=12), "F", "H")

# Validation, description, schematic
net.validate()
print(net.describe())
print(net.schematic())
net.visualize_network(compact=True)
```

## Output

```py

Network: MainPlantLoop (connection: series)
  Nodes:
    Node(name='A', elevation=0.0 m)
    Node(name='B', elevation=0.0 m)
    Node(name='C', elevation=0.0 m)
    Node(name='D', elevation=0.0 m)
    Node(name='E', elevation=0.0 m)
    Node(name='F', elevation=0.0 m)
    Node(name='G', elevation=0.0 m)
    Node(name='H', elevation=0.0 m)
  Elements:
    Pipe: 100 mm, L=10 m, from A → B
    Pipe: 150 mm, L=15 m, from B → C
    Pump: Centrifugal, from C → D
    Pipe: 80 mm, L=5 m, from D → E
    Pipe: 120 mm, L=8 m, from D → F
    Pipe: 100 mm, L=12 m, from E → G
    Pipe: 100 mm, L=12 m, from F → H

MainPlantLoop [series]
  │ └─1. Pipe1
  │ └─2. Pipe2
  │ └─3. Pump1
  │ └─4. PipeBranch1
  │ └─5. PipeBranch2
  │ └─6. PipeEG
    └─7. PipeFH

```    