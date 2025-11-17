"""
Example 1 
Double Pipe Benzene-Toluene Exchanger. It is desired to heat 9820 lb/hr of cold benzene from 80 to 120°F using hot toluene which is cooled from 160 to 100°F. 
The specific gravities at 68°F are 0.88 and 0.87, respectively. The other fluid properties will be found in the Appendix. 
A fouling factor of 0.001 should be provided for each stream, and the allowable pressure drop on each stream is 10.0 psi.
A number of 20-ft hairpins of 2- by lJ4-in. IPS pipe are available. How many hairpins are required?


from processpi.units import *
from processpi.components import *
from processpi.streams import MaterialStream
cold_fluid = Benzene()
hot_fluid = Toluene()
cold_in = MaterialStream("cold_in", component=cold_fluid, temperature=Temperature(80, "F"), mass_flow=MassFlowRate(9820, "lb/h"))
hot_in = MaterialStream("hot_in", component=hot_fluid, temperature=Temperature(160, "F"), mass_flow=MassFlowRate(12000, "lb/h"))
cold_out = MaterialStream("cold_out", component=cold_fluid, temperature=Temperature(120, "F"))
hot_out = MaterialStream("hot_out", component=hot_fluid, temperature=Temperature(100, "F"))
from processpi.equipment.heatexchangers import HeatExchanger
hx = HeatExchanger("HX1")
hx.cold_in = cold_in
hx.cold_out = cold_out
hx.hot_in = hot_in
hx.hot_out = hot_out
hx.simulate()
design_results = hx.design()
print(design_results)


{'innerpipe_dia': Diameter(0.0127, 'm'), 'outerpipe_dia': Diameter(0.0213, 'm'), 
'assignment': ('hot_tube', 'cold_annulus'), 'inner_mode': 'series', 'passes': 1, 
'annulus_parallel': 1, 'total_length': 1.440697834907453 m, 
'length_per_pass': 1.440711611449158 m, 
'U_ref': 74.60045437444104 W/m2K, 
'U_max': 74.60045437444104 W/m2K, 
'Ft': 0.9886284291662744, 
'required_area': 0.05748092238446456 m2, 
'effective_area': 0.05748183848377138 m2, 
'Q': 67.95632604948932 W, 'Re_tube': 151582.9774938471 (dimensionless), 
'Re_annulus': 46334.61006534493 (dimensionless), 'Nu_tube': 16.05783607563219 (dimensionless), 
'Nu_annulus': 6.68765375496242 (dimensionless), 'dp_tube': 356390.8712710743 Pa, 
'dp_annulus': 85294.95728892722 Pa, 'total_dp': 441685.8285600015 Pa, 'converged': True, 'iterations': 39, 'hairpin_info': {}}

"""
"""
Example 2
Double Kpe Dube Oil-Crude Oil Exchanger. 6,900 lb /hr of a 26°API lube oil must be cooled from 450 to. 350°F by 72,500 lb/hr of 34°API mid-conti¬ nent crude oil. 
The crude oil .will be heated from 300 to 310°F.
A fouling factor of 0.003 should be provided for each stream, and the allowable pressure drop on each stream will be 10 psi.
A number of 20-ft hairpins of 3- by 2-in. IPS pipe are available. How many must be used, and how shall they be arranged? 
The viscosity of the crude oil may be obtained from Kg. 14. For the lube oil, viscosities are 1.4 centipoises at 500°F, 3.0 at 400°F, 
and 7.7 at 300°F. These viscosities are great enough to introduce an error if = 1 is assumed.

from processpi.units import *
from processpi.components import *
from processpi.streams import MaterialStream
cold_fluid = Oil()
hot_fluid = Oil()
cold_in = MaterialStream("cold_in", component=cold_fluid, temperature=Temperature(300, "F"), mass_flow=MassFlowRate(72500, "lb/h"))
hot_in = MaterialStream("hot_in", component=hot_fluid, temperature=Temperature(450, "F"), mass_flow=MassFlowRate(6900, "lb/h"))
cold_out = MaterialStream("cold_out", component=cold_fluid, temperature=Temperature(310, "F"))
hot_out = MaterialStream("hot_out", component=hot_fluid, temperature=Temperature(350, "F"))
from processpi.equipment.heatexchangers import HeatExchanger
hx = HeatExchanger("HX1")
hx.cold_in = cold_in
hx.cold_out = cold_out
hx.hot_in = hot_in
hx.hot_out = hot_out
hx.simulate()
design_results = hx.design()
print(design_results)

{'innerpipe_dia': Diameter(0.0254, 'm'), 'outerpipe_dia': Diameter(0.0334, 'm'), 
'assignment': ('cold_tube', 'hot_annulus'), 
'inner_mode': 'series', 'passes': 1, 
'annulus_parallel': 1, 
'total_length': 0.3635763694543851 m, 
'length_per_pass': 0.36357917852517496 m, 
'U_ref': 41.863760211315736 W/m2K, 
'U_max': 41.863760211315736 W/m2K, 
'Ft': 0.9796834742725529, 'required_area': 0.02901195538701306 m2, 
'effective_area': 0.0290123289768237 m2, 'Q': 57.78225871666726 W, 
'Re_tube': 457907.0177003547 (dimensionless), 'Re_annulus': 18825.431319720734 (dimensionless), 
'Nu_tube': 24.12519047851141 (dimensionless), 'Nu_annulus': 3.462097005988024 (dimensionless), 
'dp_tube': 448762.5194831092 Pa, 'dp_annulus': 7910.788721676213 Pa, 
'total_dp': 456673.3082047854 Pa, 'converged': True, 'iterations': 35, 'hairpin_info': {}}


"""

"""
Example 3
Calculation of a Kerosene-Crude Oil Exchanger. 43,800 lb/hr of a 42°API kerosene leaves the bottom of a distilling column at 390°F and will be cooled to 200°F by 149,000 lb/hr of 34°API
Mid-continent crude coming from storage at 100°F and heated to 170°F. A 10 psi pressure drop is permissible on both streams, and in accordance with Table 12, a combined dirt factor of 0.003 should be provided.
Available for this service is a 21 3<t in. ID exchanger having 158 1 in. OD, 13 BWG tubes 16'0" long and laid out on 134-in. square pitch. The bundle is arranged for four passes, and baffles are spaced 5 in. apart.
Will the exchanger be suitable; i.e., what is the dirt factor?
"""

"""
Example 4
Calculation of a Distilled-water-Raw-water Exchanger. 175,000 lb/hr of distilled water enters an exchanger at 93°F and leaves at 85°F. 
The heat will be transferred to 280,000 lb/hr of raw water coming from supply at 75°F and leaving the exchanger at 80°F. 
A 10 psi pressure drop may be expended on both streams while providing a fouling factor of 0.0005 for distilled water and 0.0015 for raw water when the tube velocity exceeds 6 fps.
Available for this service is a 15)4 in. ID exchanger having-160 % in. OD, 18 BWG tubes 16'0" long and laid out on ij-fg-in. triangular pitch. 
The bundle is arranged for two passes, and baffles are spaced 12 in. apart.
Will the exchanger be suitable
"""

"""
Example 5

Calculation of a Phosphate Solution Cooler. 20,160 lb /hr of a 30% KjPO, solution, specific gravity at 120°F = 1.30, is to be cooled from 150 to 90°F using well water from 68 to 90°F. 
Pressure drops of 10 psi are allowable on both streams, and a total dirt factor of 0.002 is required.
Available for this service is a 10.02 in. ID 1-2 exchanger having 52 % in. OD, 16 BWG tubes 16'0" long laid out on 1-in. square pitch. 
The bundle is arranged for two passes, and the baffles are spaced 2 in. apart.
■Will the exchanger be suitable?
"""
