from processpi.equipment.base import Equipment
from processpi.integration.flowsheet import Flowsheet
from processpi.streams.material import MaterialStream
from processpi.units import Temperature, Pressure
from processpi.equipment.heatexchangers.base import HeatExchanger


class PassthroughUnit(Equipment):
    def __init__(self, name: str):
        super().__init__(name=name, inlet_ports=1, outlet_ports=1)

    def simulate(self):
        return {"ok": True, "in": self.inlets["in"], "out": self.outlets["out"]}


def make_stream(name: str) -> MaterialStream:
    return MaterialStream(name=name, temperature=Temperature(300, "K"), pressure=Pressure(1, "bar"))


def test_equipment_ports_are_dict_with_legacy_index_support():
    u = PassthroughUnit("U1")
    s_in = make_stream("s_in")
    s_out = make_stream("s_out")

    u.connect_inlet("in", s_in)
    u.connect_outlet("out", s_out)

    assert isinstance(u.inlets, dict)
    assert isinstance(u.outlets, dict)
    assert u.inlets["in"] is s_in
    assert u.inlets[0] is s_in
    assert u.outlets["out"] is s_out
    assert u.outlets[0] is s_out


def test_flowsheet_named_port_connect_and_sequential_solve():
    fs = Flowsheet("demo")
    u1 = PassthroughUnit("U1")
    u2 = PassthroughUnit("U2")
    stream = make_stream("S1")

    fs.add_equipment(u1)
    fs.add_equipment(u2)

    fs.connect(stream, u1, "out", u2, "in")

    assert u1.outlets["out"] is stream
    assert u2.inlets["in"] is stream

    fs.solve_sequential()
    assert u1.data["ok"] is True
    assert u2.data["ok"] is True


def test_heatexchanger_uses_named_ports():
    hx = HeatExchanger(name="HX1")
    hot_in = make_stream("hot_in")
    hot_out = make_stream("hot_out")
    cold_in = make_stream("cold_in")
    cold_out = make_stream("cold_out")

    hx.connect_inlet("hot_in", hot_in)
    hx.connect_outlet("hot_out", hot_out)
    hx.connect_inlet("cold_in", cold_in)
    hx.connect_outlet("cold_out", cold_out)

    assert hx.hot_in is hot_in
    assert hx.hot_out is hot_out
    assert hx.cold_in is cold_in
    assert hx.cold_out is cold_out
