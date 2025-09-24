from processpi.integration.flowsheet import Flowsheet
from processpi.equipment.pumps import Pump
from processpi.equipment.mixer import Mixer
from processpi.streams import MaterialStream
from processpi.components import *
from processpi.units import *

fluid = Water()

# Create flowsheet
fs = Flowsheet("Demo FS")

# Units
pump = Pump("Pump1", pump_type="cp")
s1 = MaterialStream("S1", component=fluid, flow_rate=VolumetricFlowRate(20,"m3/h"), pressure=Pressure(3,"atm"))
s2 = MaterialStream("S2",component=fluid, flow_rate=VolumetricFlowRate(20,"m3/h"), pressure=Pressure(6,"atm"))

fs.add_equipment(pump)
fs.add_material_stream(s1)
fs.add_material_stream(s2)

fs.connect(s1,pump,port="inlet")
fs.connect(pump,s2,port="outlet")

fs.run()

fs.summary()