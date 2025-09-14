from processpi.components import Water
from processpi.units import *
fluid = Water(temperature=Temperature(80,"C"))
print(fluid.density())