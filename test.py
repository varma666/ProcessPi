from processpi.pipelines.engine import PipelineEngine
from processpi.components import Water
from processpi.units import *

fluid = Water()
flowrate = VolumetricFlowRate(10,"m3/h")
length = Length(100, "m")
print(flowrate.to("m3/s"))
print(fluid.viscosity())

engine = PipelineEngine(flowrate=flowrate, fluid=fluid, length=length)
results = engine.run()
print(results)
#{'optimum_diameter_in': 1.5 in, 'velocity_m_s': 2.4366458313695016 m/s, 'reynolds_number': 124325.41639808552 (dimensionless), 'pressure_drop_Pa': 307808.4443772021 Pa}