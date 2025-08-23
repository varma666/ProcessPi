from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.pipes import Pipe
from processpi.units import *

pipe = Pipe(length=Length(100, "m"), nominal_diameter=Diameter(3,"in"))

net = PipelineNetwork(name="Single Straight Pipeline")
net.add_pipe(pipe)

from processpi.pipelines.engine import PipelineEngine

engine = PipelineEngine(network=net)
from processpi.components import Water
fluid = Water()
flow_rate = VolumetricFlowRate(10, "m3/h")
engine.fit(
        fluid=fluid,
        flow_rate=flow_rate,
        inlet_pressure=Pressure(600_000, "Pa"),
        outlet_pressure=Pressure(101_325, "Pa"),
        temperature=Temperature(50, "C")
    )
engine.run()
engine.summary()


net = PipelineNetwork("Main")
pipe = Pipe(length=Length(800, "m"))
net.add_pipe(pipe, diameter=None, roughness=0.000045)
net.add_fitting("elbow_90", count=8, k_value=0.75)
net.add_fitting("butterfly_valve", count=1, k_value=2.0)
net.add_fitting("flow_nozzle", count=1, k_value=1.5)

engine = PipelineEngine(network=net)
engine.fit(
        fluid={"density": 1.87, "viscosity": 0.016e-3},
        flow_rate=(1000*1000)/86400,  # 1000 t/day -> ~11.57 kg/s
        inlet_pressure=24000,
        outlet_pressure=101325,
        temperature=60
    )
engine.run()
engine.summary()