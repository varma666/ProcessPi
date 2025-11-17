'''
Example 2
Double Kpe Dube Oil-Crude Oil Exchanger. 6,900 lb /hr of a 26°API lube oil must be cooled from 450 to. 350°F by 72,500 lb/hr of 34°API mid-conti¬ nent crude oil. 
The crude oil .will be heated from 300 to 310°F.
A fouling factor of 0.003 should be provided for each stream, and the allowable pressure drop on each stream will be 10 psi.
A number of 20-ft hairpins of 3- by 2-in. IPS pipe are available. How many must be used, and how shall they be arranged? 
The viscosity of the crude oil may be obtained from Kg. 14. For the lube oil, viscosities are 1.4 centipoises at 500°F, 
3.0 at 400°F, and 7.7 at 300°F. These viscosities are great enough to introduce an error if = 1 is assumed.
'''
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