"""Every component carries the heat exchanger data the exchanger reads.

Only Benzene, Toluene, Water, Chlorine, Oil and OrganicLiquid had hx_data(),
and shell_and_tube raises "<Component> does not implement hx_data()" for any
other fluid, so an ethanol or acetic acid cooler could not be designed:

    ValueError: Ethanol does not implement hx_data().

Component now has hx_data() and httype(), driven by a few class attributes
that each component file sets (_hx_family, _hx_liquid_type, _hx_fouling_key,
_hx_corrosion_key, and _hx_velocity_key where standards.py has a row for the
fluid). The six files with their own methods keep them.

httype() is the U-table category at the component's phase: the liquid type for
a liquid; "vapor" for a vapour below its critical temperature (it can condense);
a gas above it, gas_low_pressure up to 3 bar and gas_high_pressure above, the
split the exchanger's assumed-U lookup uses. Water and Steam give "steam".
"""

import contextlib
import io

import pytest

import processpi.components as components
from processpi.components import AceticAcid, Argon, Benzene, Ethanol, Ethylbenzene, Steam, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.standards import (
    CORROSION_SEVERITY_DATABASE,
    FOULING_FACTOR_DATABASE,
    HX_U_STANDARDS,
    RECOMMENDED_VELOCITIES,
)
from processpi.streams import MaterialStream
from processpi.units import HeatTransferCoefficient, MassFlowRate, Pressure, Temperature

U_TYPES = {fluid for service in HX_U_STANDARDS["shell_and_tube"].values() for pair in service for fluid in pair}
STATES = [(25, 1), (150, 1), (25, 20)]  # (C, bar)
ALL_COMPONENTS = [name for name in components.__all__ if name != "Component"]


@pytest.mark.parametrize("name", ALL_COMPONENTS)
def test_every_component_gives_keys_that_are_rows_of_the_tables(name):
    for t_c, p_bar in STATES:
        comp = getattr(components, name)(temperature=Temperature(t_c, "C"), pressure=Pressure(p_bar, "bar"))
        data = comp.hx_data()
        assert data["phase"] in {"liquid", "vapor"}
        assert data["fouling_key"] in FOULING_FACTOR_DATABASE
        assert data["corrosion_key"] in CORROSION_SEVERITY_DATABASE
        assert data["velocity_key"] in RECOMMENDED_VELOCITIES
        assert comp.httype() in U_TYPES


def test_a_liquid_is_its_liquid_type_and_a_vapour_below_tc_is_vapor():
    # Ethanol: Tb 78 C, Tc 514 K.
    assert Ethanol(temperature=Temperature(25, "C")).httype() == "organic"
    hot = Ethanol(temperature=Temperature(150, "C"), pressure=Pressure(1, "bar"))
    assert hot.httype() == "vapor"
    assert hot.hx_data()["phase"] == "vapor"


def test_a_gas_above_tc_splits_at_3_bar():
    # Argon: Tc 150.7 K, so a gas at 25 C.
    assert Argon(temperature=Temperature(25, "C"), pressure=Pressure(1, "bar")).httype() == "gas_low_pressure"
    assert Argon(temperature=Temperature(25, "C"), pressure=Pressure(3, "bar")).httype() == "gas_low_pressure"
    assert Argon(temperature=Temperature(25, "C"), pressure=Pressure(20, "bar")).httype() == "gas_high_pressure"


def test_steam_is_steam_and_its_service_keys_are_the_steam_rows():
    data = Steam(temperature=Temperature(160, "C"), pressure=Pressure(3, "bar")).hx_data()
    assert data["u_key"] == "steam"
    assert data["fouling_key"] == "steam"
    assert data["corrosion_key"] == "steam_condensate"


def test_acids_and_amines_get_their_corrosion_rows():
    assert AceticAcid().hx_data()["corrosion_key"] == "acid"
    assert components.DiethylAmine().hx_data()["corrosion_key"] == "amine"
    assert components.Ammonia().hx_data()["corrosion_key"] == "amine"
    assert Argon().hx_data()["corrosion_key"] == "inert_gas"
    assert CORROSION_SEVERITY_DATABASE["inert_gas"] == "low"
    assert Ethylbenzene().hx_data()["corrosion_key"] == "hydrocarbon"


def test_the_sample_components_keep_their_own_methods():
    assert Benzene().hx_data() == {
        "family": "organic", "phase": "liquid", "velocity_key": "benzene",
        "u_key": "organic", "fouling_key": "hydrocarbons", "corrosion_key": "hydrocarbon",
    }
    assert Water().httype() == "water"


def _cooler(component):
    hx = HeatExchangerEngine().fit(
        hot_in=MaterialStream("hot_in", component=component(), temperature=Temperature(70, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=component(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
        assumed_U=HeatTransferCoefficient(575, "W/m2K"),
        shell_dp=Pressure(1, "bar"),
        tube_dp=Pressure(1, "bar"),
        mode="design",
    )
    with contextlib.redirect_stdout(io.StringIO()):
        return hx.run().data


def test_a_component_without_its_own_methods_can_be_designed():
    results = _cooler(Ethylbenzene)
    assert results["tube_count"] > 0


def test_a_corrosive_fluid_goes_in_the_tubes():
    # Acetic acid scores "high" corrosion, so the assignment puts it in the
    # tubes, where a corrosion-resistant alloy costs least (Sinnott, Sec. 12.4).
    assert _cooler(AceticAcid)["tube_side_fluid"] == "Acetic Acid"
