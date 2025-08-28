from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.equipment import Equipment
from processpi.pipelines.network import PipelineNetwork
from processpi.units import *
from processpi.components.carbondioxide import Carbondioxide
fluid = Carbondioxide() # Use default state (15C, 1 atm)

m_dot = MassFlowRate(1000_000, "kg/day")
fluid.viscosity = Viscosity(0.016, "cP")
fluid.density = Density(1.61, "kg/m3")

co2_fittings = [
    Fitting(fitting_type="long_radius_90_deg", quantity=8),
    Fitting(fitting_type="swing_check_valve", quantity=1),
    Fitting(fitting_type="entrance_sharp", quantity=1),
]

print("\n--- B1) CO2 line sizing ---")
co2_size_results = PipelineEngine().fit(
    mass_flowrate=m_dot,
    length=Length(800, "m"),
    available_dp=Pressure(24, "kPa"),
    fittings=co2_fittings,
    fluid=fluid
).run()
co2_size_results.summary()