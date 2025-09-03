from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork
fluid = Carbondioxide(temperature=Temperature(60, "C"))
print(fluid.density(),fluid.viscosity().to("cP"))

mass_flow = MassFlowRate(1000, "t/day")
pipe = Pipe(name="Main Pipe", length=Length(800, "m"), material="CS")
elbow = Fitting(fitting_type="standard_elbow_90_deg", quantity=8)
valve = Fitting(fitting_type="gate_valve", quantity=1)
nozzle = Fitting(fitting_type="exit", quantity=1)
model = PipelineEngine()
model.fit(
    fluid=fluid,
    mass_flow=mass_flow,
    pipe=pipe,
    fittings=[elbow, valve, nozzle],
    available_dp=Pressure(24, "kPa")
    
)
model.run()
model.summary()