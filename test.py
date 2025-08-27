from processpi.pipelines.engine import PipelineEngine
from processpi.units import *
from processpi.components import Water
fluid = Water()
flow_rate = VolumetricFlowRate(3000, "gal/min")
internal_diameter = Diameter(15.5, "in")
model = PipelineEngine()
model.fit(
    fluid=fluid,
    flow_rate=flow_rate,
    internal_diameter=internal_diameter
)
result = model.run()
result.summary()