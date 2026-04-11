from processpi.components import Water
from processpi.equipment.heatexchangers import ShellAndTube
from processpi.equipment.heatexchangers.base import HeatExchanger
from processpi.equipment.heatexchangers.mechanical.shell_tube import design_shelltube
from processpi.streams.material import MaterialStream
from processpi.units import MassFlowRate, Pressure, SpecificHeat, Temperature


def _stream(name: str, temp_k: float, m_dot: float):
    return MaterialStream(
        name=name,
        component=Water(),
        temperature=Temperature(temp_k, "K"),
        pressure=Pressure(2, "bar"),
        mass_flow=MassFlowRate(m_dot, "kg/s"),
        specific_heat=SpecificHeat(4200, "J/kgK"),
    )


def test_shell_tube_design_returns_structured_kern_bell_results():
    hx = HeatExchanger("HX-ST")
    hx.hot_in = _stream("hot", 360, 2.0)
    hx.cold_in = _stream("cold", 300, 2.0)
    hx.simulated_params = {
        "Hot in Temp": Temperature(360, "K"),
        "Hot out Temp": Temperature(330, "K"),
        "Cold in Temp": Temperature(300, "K"),
        "Cold out Temp": Temperature(325, "K"),
        "m_hot": MassFlowRate(2, "kg/s"),
        "m_cold": MassFlowRate(2, "kg/s"),
        "cP_hot": SpecificHeat(4200, "J/kgK"),
        "cP_cold": SpecificHeat(4200, "J/kgK"),
    }

    out = design_shelltube(hx)

    assert "Q_W" in out
    assert "U_W_m2K" in out
    assert "A_required_m2" in out
    assert "dp_tube" in out
    assert "dp_shell" in out
    assert "bell_delaware" in out
    assert "J_c" in out["bell_delaware"]
    assert isinstance(out["converged"], bool)


def test_shell_and_tube_class_import_and_design_wrapper():
    hx = ShellAndTube("HX-ST-CLASS")
    hx.hot_in = _stream("hot", 360, 2.0)
    hx.cold_in = _stream("cold", 300, 2.0)
    hx.simulated_params = {
        "Hot in Temp": Temperature(360, "K"),
        "Hot out Temp": Temperature(330, "K"),
        "Cold in Temp": Temperature(300, "K"),
        "Cold out Temp": Temperature(325, "K"),
        "m_hot": MassFlowRate(2, "kg/s"),
        "m_cold": MassFlowRate(2, "kg/s"),
        "cP_hot": SpecificHeat(4200, "J/kgK"),
        "cP_cold": SpecificHeat(4200, "J/kgK"),
    }
    out = hx.design()
    assert "U_W_m2K" in out
