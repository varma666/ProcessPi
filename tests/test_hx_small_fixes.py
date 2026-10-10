"""Smaller heat exchanger fixes.

- HeatExchangerEngine(hx_type="bell_delaware") with the default method ran
  Kern and reported method "kern".
- The side scoring looked fluids up by name with a test that also matched a
  name contained in a key, so plain "Water" scored as seawater (fouling
  3.5e-4, corrosion "high"); a tie then went to the hot stream regardless.
- The design loop judged pressure drop against the built-in defaults while the
  final verdict used the user's tube_dp/shell_dp.
- CondenserHX held the condensing stream in the tubes whatever condensing_side
  said, and gave the vapour the liquid velocity band of the service.
"""

import contextlib
import io

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import CondenserHX, HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import MassFlowRate, Pressure, Temperature


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _benzene_cooler():
    """docs/examples benzene cooler: benzene 21 000 kg/h 90 to 30 C, water 60 500 kg/h from 15 C."""
    return dict(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
    )


def _engine(method=None, **specs):
    kwargs = {} if method is None else {"method": method}
    return HeatExchangerEngine(**kwargs).fit(
        **_benzene_cooler(), shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
        mode="design", **specs,
    )


# ----------------------------------------------------------------------------
# hx_type="bell_delaware"
# ----------------------------------------------------------------------------

def test_hx_type_bell_delaware_runs_the_bell_method():
    data = _quiet(_engine(hx_type="bell_delaware").run).data
    assert data["method"] == "bell_delaware"
    assert "bell_factors" in data
    same = _quiet(_engine(method="bell_delaware").run).data
    assert data["h_shell"] == same["h_shell"]


def test_hx_type_bell_delaware_with_kern_chosen_is_refused():
    with pytest.raises(ValueError, match="conflicts with method='kern'"):
        _quiet(_engine(method="kern", hx_type="bell_delaware").run)


# ----------------------------------------------------------------------------
# Side scoring
# ----------------------------------------------------------------------------

def _hx():
    return ShellAndTubeHX(**_benzene_cooler())


def test_plain_water_is_not_looked_up_as_seawater():
    hx = _hx()
    assert hx._get_fouling_factor("water") != hx._fouling_db["seawater"]["base"]
    assert hx._get_corrosion_severity("water") == "medium"
    # A name that does contain a table key still finds it.
    assert hx._get_fouling_factor("sea water") == hx._fouling_db["seawater"]["base"]
    assert hx._get_corrosion_severity("Seawater") == "high"
    assert hx._get_fouling_factor("cooling tower water") == hx._fouling_db["cooling_tower_water"]["base"]


def test_scoring_uses_the_keys_the_component_declares():
    hx = _hx()
    assert hx._service_key(hx.cold_in, "fouling_key") == "treated_water"
    assert hx._service_key(hx.hot_in, "fouling_key") == "hydrocarbons"
    assert hx._service_key(hx.hot_in, "corrosion_key") == "hydrocarbon"


def test_a_tie_puts_the_larger_flow_in_the_tubes():
    """Treated water and benzene tie on the scoring. Sinnott (C&R Vol. 6,
    Sec. 12.4): the lowest flow rate to the shell side, so the water
    (about 61 m3/h against 25 m3/h of benzene) goes in the tubes."""
    data = _quiet(_engine().run).data
    assert data["assignment"]["tube_side"] == "cold"
    assert data["tube_side_fluid"] == "Water"
    assert data["assignment_reason"][0].startswith("Tube-side scores tie")


def test_a_declared_corrosive_stream_still_wins_the_tubes():
    data = _quiet(_engine(hot_corrosion_level="high").run).data
    assert data["assignment"]["tube_side"] == "hot"
    assert data["assignment_reason"][0].startswith("Hot fluid tube-side score")


# ----------------------------------------------------------------------------
# Pressure drop limits inside the design loop
# ----------------------------------------------------------------------------

def test_the_design_loop_uses_the_users_pressure_drop_limits():
    hx = ShellAndTubeHX(**_benzene_cooler(), tube_dp=Pressure(0.2, "bar"), shell_dp=5000.0)
    props = {"viscosity": 5e-4, "phase": "liquid", "p_bar": 1.0}
    assert hx._design_dp_limits(props, props) == pytest.approx((20000.0, 5000.0))
    # Without them, the built-in limit (35 kPa below 1 cP).
    plain = ShellAndTubeHX(**_benzene_cooler())
    assert plain._design_dp_limits(props, props) == pytest.approx((35000.0, 35000.0))


# ----------------------------------------------------------------------------
# Condenser
# ----------------------------------------------------------------------------

def _condenser_streams():
    return dict(
        hot_in=MaterialStream("benzene_vapor_in", component=Benzene(), phase="vapor",
                              temperature=Temperature(95, "C"), pressure=Pressure(1.2, "bar"),
                              mass_flow=MassFlowRate(12000, "kg/h")),
        hot_out=MaterialStream("benzene_liquid_out", component=Benzene(), phase="liquid",
                               temperature=Temperature(95, "C")),
        cold_in=MaterialStream("cw_in", component=Water(), phase="liquid",
                               temperature=Temperature(30, "C"), pressure=Pressure(1, "bar"),
                               mass_flow=MassFlowRate(50000, "kg/h")),
        cold_out=MaterialStream("cw_out", component=Water()),
    )


def test_condensing_coefficient_sits_on_the_condensing_stream():
    """Shell-side condensation: the water in the tubes keeps its own film
    coefficient and the condensing coefficient is the shell one. Before, the
    vapour was in the tubes with a single-phase coefficient and the
    condensing coefficient replaced the water's."""
    hx = CondenserHX(latent_heat=394000, orientation="horizontal", **_condenser_streams())
    data = _quiet(hx.design)
    assert data["tube_side_fluid"] == "Water"
    assert data["condensing_side"] == "shell"
    # The condensing coefficient is bounded to 1200-20000 W/m2K by the model.
    assert 1200.0 <= float(getattr(data["h_shell"], "value", data["h_shell"])) <= 20000.0


def test_the_condensing_side_takes_the_vapour_velocity_band():
    hx = CondenserHX(latent_heat=394000, **_condenser_streams())
    vapour = hx.hot_in.component
    vapour._phase = "gas"
    assert hx._get_velocity_limits("shell", vapour) == (10.0, 30.0)
    # The coolant side keeps the condenser service band.
    assert hx._get_velocity_limits("tube", hx.cold_in.component) == (0.6, 2.0)
