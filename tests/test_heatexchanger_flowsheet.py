"""Heat exchangers as Flowsheet units with named ports.

The exchangers moved to a stream-based ABC in fe32d5a and stopped being
`Equipment`, so none of them could be connected into a `Flowsheet` (the
abstract `HeatExchanger(name=...)` could not even be built). These tests
cover the port wiring, the flowsheet energy balance written to the outlet
ports, and the errors for an unknown port or an incomplete specification.

Reference case (hand calculation):
    hot  2 kg/s, cp 4200 J/kg.K, 360 K -> C_hot  = 8400 W/K
    cold 3 kg/s, cp 4000 J/kg.K, 300 K -> C_cold = 12000 W/K
    hot outlet specified at 330 K:
        Q      = 8400 * (360 - 330)       = 252000 W
        Tc_out = 300 + 252000 / 12000     = 321 K
        Q_max  = min(8400, 12000) * 60    = 504000 W, effectiveness 0.5
"""

import contextlib
import io

import pytest

from processpi.components import Water
from processpi.equipment.base import Equipment
from processpi.equipment.heatexchangers import HeatExchanger, ShellAndTubeHX
from processpi.integration.flowsheet import Flowsheet
from processpi.streams.material import MaterialStream
from processpi.units import MassFlowRate, Pressure, SpecificHeat, Temperature
from processpi.units.heat_flow import HeatFlow


def _feed(name, temp_k, m_dot, cp, p_bar=2.0):
    return MaterialStream(
        name=name,
        temperature=Temperature(temp_k, "K"),
        pressure=Pressure(p_bar, "bar"),
        mass_flow=MassFlowRate(m_dot, "kg/s"),
        specific_heat=SpecificHeat(cp, "J/kgK"),
    )


def _placeholder(name):
    return MaterialStream(name=name)


class Sink(Equipment):
    """Downstream unit that records the temperature it receives."""

    def __init__(self, name):
        super().__init__(name=name, inlet_ports=1, outlet_ports=0)

    def simulate(self):
        return {"t_in_K": self.inlets["in"].temperature.to("K").value}


def _wired_hx(**specs):
    hx = HeatExchanger(name="E-101", **specs)
    hx.connect_inlet("hot_in", _feed("hot_in", 360, 2.0, 4200, p_bar=3.0))
    hx.connect_inlet("cold_in", _feed("cold_in", 300, 3.0, 4000))
    hx.connect_outlet("hot_out", _placeholder("hot_out"))
    hx.connect_outlet("cold_out", _placeholder("cold_out"))
    return hx


def _k(temperature):
    return temperature.to("K").value


def _w(heat_flow):
    return heat_flow.to("W").value


# ----------------------------------------------------------------------
# Named ports
# ----------------------------------------------------------------------
def test_heat_exchanger_is_equipment_with_named_ports():
    hx = HeatExchanger(name="E-101")

    assert isinstance(hx, Equipment)
    assert list(hx.inlets.keys()) == ["hot_in", "cold_in"]
    assert list(hx.outlets.keys()) == ["hot_out", "cold_out"]


def test_constructor_streams_land_on_the_ports():
    hot_in, cold_in = _feed("h", 360, 2.0, 4200), _feed("c", 300, 3.0, 4000)
    hx = ShellAndTubeHX(hot_in=hot_in, cold_in=cold_in, name="E-102")

    assert hx.inlets["hot_in"] is hot_in
    assert hx.inlets["cold_in"] is cold_in
    assert hx.outlets["hot_out"] is None


def test_flowsheet_runs_exchanger_and_feeds_downstream_unit():
    fs = Flowsheet("hx demo")
    hx = HeatExchanger(name="E-101", hot_out_temperature=Temperature(330, "K"))
    cooler_sink, heater_sink = Sink("hot product"), Sink("cold product")
    hot_in, cold_in = _feed("hot_in", 360, 2.0, 4200, p_bar=3.0), _feed("cold_in", 300, 3.0, 4000)
    hot_out, cold_out = _placeholder("hot_out"), _placeholder("cold_out")

    fs.connect(hot_in, hx, "hot_in")
    fs.connect(cold_in, hx, "cold_in")
    fs.connect(hot_out, hx, "hot_out", cooler_sink, "in")
    fs.connect(cold_out, hx, "cold_out", heater_sink, "in")
    # Registration order puts the sinks first; run() must still solve the exchanger first.
    fs.equipment.sort(key=lambda unit: unit is hx)

    with contextlib.redirect_stdout(io.StringIO()):
        fs.run()

    assert hx.hot_out is hot_out and hx.cold_out is cold_out
    assert _w(hx.data["Q"]) == pytest.approx(252000.0)
    assert cooler_sink.data["t_in_K"] == pytest.approx(330.0)
    assert heater_sink.data["t_in_K"] == pytest.approx(321.0)


# ----------------------------------------------------------------------
# Outlet streams and energy balance
# ----------------------------------------------------------------------
def test_outlet_streams_conserve_mass_and_carry_pressure():
    hx = _wired_hx(hot_out_temperature=Temperature(330, "K"))
    hx.simulate()

    assert hx.hot_out.mass_flow().to("kg/s").value == pytest.approx(2.0)
    assert hx.cold_out.mass_flow().to("kg/s").value == pytest.approx(3.0)
    # No pressure-drop model in simulate(): each outlet leaves at its inlet pressure (.value is Pa).
    assert hx.hot_out.pressure.value == pytest.approx(3.0e5)
    assert hx.cold_out.pressure.value == pytest.approx(2.0e5)
    assert hx.hot_out.specific_heat.to("J/kgK").value == pytest.approx(4200.0)
    assert hx.cold_out.specific_heat.to("J/kgK").value == pytest.approx(4000.0)


@pytest.mark.parametrize(
    "spec",
    [
        {"hot_out_temperature": Temperature(330, "K")},
        {"cold_out_temperature": Temperature(321, "K")},
        {"Q": HeatFlow(252, "kW")},
        {"Q": 252000.0},
    ],
    ids=["hot_out_T", "cold_out_T", "Q_heatflow", "Q_watts"],
)
def test_energy_balance_closes_for_every_duty_spec(spec):
    hx = _wired_hx(**spec)
    result = hx.simulate()

    th_out, tc_out = _k(hx.hot_out.temperature), _k(hx.cold_out.temperature)
    q_hot = 2.0 * 4200.0 * (360.0 - th_out)
    q_cold = 3.0 * 4000.0 * (tc_out - 300.0)

    assert th_out == pytest.approx(330.0)
    assert tc_out == pytest.approx(321.0)
    assert q_hot == pytest.approx(q_cold)
    assert _w(result["Q"]) == pytest.approx(252000.0)
    assert result["effectiveness"] == pytest.approx(0.5)
    assert _k(result["hot_out_temperature"]) == pytest.approx(th_out)
    assert _k(result["cold_out_temperature"]) == pytest.approx(tc_out)


def test_ports_feed_the_sizing_methods():
    """A ShellAndTubeHX wired only through its ports designs the 252 kW duty."""
    def water(name, temp_k, m_dot=None):
        kwargs = {"mass_flow": MassFlowRate(m_dot, "kg/s")} if m_dot else {}
        return MaterialStream(name=name, component=Water(), temperature=Temperature(temp_k, "K"),
                              pressure=Pressure(2, "bar"), specific_heat=SpecificHeat(4200, "J/kgK"), **kwargs)

    hx = ShellAndTubeHX(name="E-103")
    hx.connect_inlet("hot_in", water("hot", 360, 2.0))
    hx.connect_inlet("cold_in", water("cold", 300, 2.0))
    hx.connect_outlet("hot_out", water("hot_out", 330))

    with contextlib.redirect_stdout(io.StringIO()):
        out = hx.design()

    # Q = 2 kg/s * 4200 J/kg.K * (360 - 330) K = 252 kW
    assert _w(out["Q"]) == pytest.approx(252000.0)


# ----------------------------------------------------------------------
# Errors
# ----------------------------------------------------------------------
def test_unknown_port_is_refused():
    hx = HeatExchanger(name="E-101")
    with pytest.raises(ValueError, match="inlet port 'shell_in' is not defined"):
        hx.connect_inlet("shell_in", _feed("s", 300, 1.0, 4180))

    fs = Flowsheet("bad port")
    with pytest.raises(ValueError, match="outlet port 'tube_out' does not exist"):
        fs.connect(_placeholder("s"), hx, "tube_out", Sink("sink"), "in")


def test_port_cannot_be_connected_twice():
    hx = _wired_hx(Q=1000.0)
    with pytest.raises(ValueError, match="already connected"):
        hx.connect_inlet("hot_in", _feed("again", 360, 1.0, 4200))


@pytest.mark.parametrize(
    "specs, match",
    [
        ({}, "exactly one of"),
        ({"Q": 1000.0, "hot_out_temperature": Temperature(350, "K")}, "exactly one of"),
        ({"cold_out_temperature": Temperature(370, "K")}, "outside the feasible range"),
        ({"hot_out_temperature": Temperature(370, "K")}, "outside the feasible range"),
    ],
    ids=["no_spec", "two_specs", "cold_above_hot_inlet", "hot_heated"],
)
def test_bad_duty_spec_is_refused(specs, match):
    hx = _wired_hx(**specs)
    with pytest.raises(ValueError, match=match):
        hx.simulate()


def test_missing_outlet_stream_is_refused():
    hx = HeatExchanger(name="E-101", Q=1000.0)
    hx.connect_inlet("hot_in", _feed("h", 360, 2.0, 4200))
    hx.connect_inlet("cold_in", _feed("c", 300, 3.0, 4000))
    with pytest.raises(ValueError, match="outlet port 'hot_out' is not connected"):
        hx.simulate()


def test_inlet_without_mass_flow_is_refused():
    hx = HeatExchanger(name="E-101", Q=1000.0)
    hx.connect_inlet("hot_in", MaterialStream("h", temperature=Temperature(360, "K"),
                                              specific_heat=SpecificHeat(4200, "J/kgK")))
    hx.connect_inlet("cold_in", _feed("c", 300, 3.0, 4000))
    with pytest.raises(ValueError, match="has no mass flow"):
        hx.simulate()


def test_phase_change_is_not_simulated_silently():
    hx = _wired_hx(Q=1000.0, cold_out_phase="vapor")
    with pytest.raises(NotImplementedError, match="sensible heat only"):
        hx.simulate()


def test_generic_exchanger_has_no_sizing_method():
    with pytest.raises(NotImplementedError, match="no sizing method"):
        HeatExchanger(name="E-101").design()


def test_sizing_without_inlets_is_refused():
    with pytest.raises(ValueError, match="connect the hot_in and cold_in streams"):
        ShellAndTubeHX(name="E-104").design()
