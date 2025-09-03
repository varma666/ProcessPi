from processpi.components import *
from processpi.units import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
fluid = Water(temperature=Temperature(40, "C"))
length = Length(3200, "m")
pipe = Pipe(name="Main Water Pipe", length=length, material="Concrete")
pipe2 = Pipe(name="Main Water Pipe", length=length, material="CS")
allowable_dp = Pressure(0.58, "atm")
flow_rate = MassFlowRate(100000, "kg/h")
model = PipelineEngine()
model.fit(fluid=fluid, pipe=pipe, mass_flow=flow_rate, available_dp=allowable_dp)
model2 = PipelineEngine()
model2.fit(fluid=fluid, pipe=pipe2, mass_flow=flow_rate, available_dp=allowable_dp)

model.run()
model2.run()

model.summary()
model2.summary()