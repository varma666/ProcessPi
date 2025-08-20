from processpi.pipelines.engine import PipelineEngine
from processpi.components import Water
from processpi.units import *
from processpi.pipelines.pipes import Pipe
pipe = Pipe(nominal_diameter=Diameter(4, "in"), length=50, material="Steel", schedule="40")
engine = PipelineEngine(
        flowrate=VolumetricFlowRate(0.01, "m3/s"),
        fluid=Water(),
        pipe=pipe,
    )


results = engine.run()
print("Reynolds Number:", results["reynolds_number"])
