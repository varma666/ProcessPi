from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.pipes import Pipe
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.equipment import Equipment
from processpi.pipelines.network import PipelineNetwork
from processpi.pipelines.nozzle import Nozzle
from processpi.units import *
from processpi.components.organic_liquid import OrganicLiquid
placeholder_diameter = Diameter(10, "in")
m_dot_org = MassFlowRate(5000, "kg/h")
rho_org = Density(930, "kg/m3")
mu_org = Viscosity(0.91, "cP")
fluid = OrganicLiquid(density=rho_org, viscosity=mu_org)

org_fittings = [
    Fitting(fitting_type="standard_elbow_90_deg", quantity=6, diameter=placeholder_diameter),
    Fitting(fitting_type="standard_tee_through_flow", quantity=2, diameter=placeholder_diameter),
    Fitting(fitting_type="gate_valve", quantity=4, diameter=placeholder_diameter),
    Fitting(fitting_type="globe_valve", quantity=1, diameter=placeholder_diameter),
]

orifice_dp = Equipment(name="orifice meter", pressure_drop=Pressure(40, "kPa"))

print("\n--- B4) Organic liquid sizing & residual ΔP ---")
results_b4 = PipelineEngine().fit(
    mass_flowrate=m_dot_org,
    length=Length(50, "m"),
    fluid=fluid,
    fittings=org_fittings,
    equipment=[orifice_dp],
    #available_dp=Pressure(600, "kPa"),
    material="CS",
).run()
summary_b4 = results_b4.summary()

