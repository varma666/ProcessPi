from processpi.pipelines.engine import PipelineEngine
from processpi.components import Water
from processpi.units import *

fluid = Water()
flowrate = VolumetricFlowRate(10,"m3/h")
length = Length(100, "m")
#print(type(fluid.density()))

engine = PipelineEngine(flowrate=flowrate, fluid=fluid, length=length)
results = engine.run()
print(results)
