from processpi.units import *
from processpi.components import *
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.network import PipelineNetwork

fluid = CarbonMonoxide(temperature=Temperature(50, "C"))

mass_flow = MassFlowRate(1500, "kg/h")
pipe = Pipe(
    name="main_line",
    length=Length(4000, "m")
)

# Add fittings
gate_valves = [Fitting("gate_valve") for _ in range(2)]
elbows_45 = [Fitting("elbow_45") for _ in range(3)]
elbows_90 = [Fitting("elbow_90") for _ in range(6)]

net = PipelineNetwork.series("CO_line", pipe, *gate_valves, *elbows_45, *elbows_90)

# ----------------------
# Engine setup
# ----------------------
engine = PipelineEngine(
    network=net,
    fluid=fluid,
    mass_flow=MassFlowRate(1500, "kg/h"),  # mass flow input
    inlet_pressure=Pressure(50, "kPa"),  # gauge pressure at inlet
    outlet_pressure=Pressure(0, "kPa"),  # atmospheric
    available_dp=Pressure(50, "kPa"),    # available pressure drop for sizing
)

# ----------------------
# Run calculation
# ----------------------
result = engine.run()

# ----------------------
# Show results
# ----------------------
result.summary()