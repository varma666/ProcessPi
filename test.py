from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.pumps import Pump
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork

fluid = OrganicLiquid(density=Density(930, "kg/m3"),viscosity=Viscosity(0.91, "cP"))

print(fluid.density(),fluid.viscosity(),fluid.specific_heat(),fluid.thermal_conductivity())
mass_flow = MassFlowRate(5000, "kg/h")
pipe = Pipe(name="Main Organic Liquid Pipe", length=Length(50, "m"))
elbow = Fitting(fitting_type="standard_elbow_90_deg", quantity=6)
tees = Fitting(fitting_type="standard_tee", quantity=2)
gate_valves = Fitting(fitting_type="gate_valve", quantity=2)
globe_valves = Fitting(fitting_type="globe_valve", quantity=2)
orifice = Fitting(fitting_type="orifice", quantity=1)

model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbow, tees, gate_valves, globe_valves, orifice],
    
)

model.run()
model.summary()
