"""Regression tests for code paths that used to raise before producing a result.

Each test exercises one public entry point with plausible inputs and checks the
result against a hand calculation where one is cheap to state.
"""
import math

import pytest

from processpi.units import (
    Area, Diameter, HeatFlow, Length, Pressure, Temperature, VolumetricFlowRate,
)
from processpi.components import Ammonia, Ethane, Steam, Water
from processpi.calculations.heat_transfer.conduction_heat_loss import ConductionHeatLoss
from processpi.calculations.heat_transfer.convection_heat_loss import ConvectionHeatLoss
from processpi.calculations.heat_transfer.crossflow_tube import CrossFlowSingleTube
from processpi.pipelines.engine import PipelineEngine
from processpi.streams import MaterialStream


def _single_pipe_engine(**extra):
    return PipelineEngine().fit(
        fluid=Water(),
        flowrate=VolumetricFlowRate(50, "m3/h"),
        diameter=Diameter(102.3, "mm"),
        length=Length(100, "m"),
        **extra,
    )


def test_single_pipe_run_with_explicit_diameter():
    # Used to raise UnboundLocalError: pump_eff was only bound in the network branch.
    results = _single_pipe_engine().run()
    assert results is not None


def test_single_pipe_run_hazen_williams():
    # Used to raise TypeError: the calculation was built from a positional dict.
    results = _single_pipe_engine(method="hazen_williams").run()
    assert results is not None


def test_crossflow_single_tube():
    # Used to raise NameError: math was never imported.
    q = CrossFlowSingleTube(
        h=50.0, diameter=0.05, length=2.0, T_surface=400.0, T_fluid=300.0
    ).calculate()
    expected = 50.0 * math.pi * 0.05 * 2.0 * 100.0
    assert q.value == pytest.approx(expected, rel=1e-4)


@pytest.mark.parametrize("component", [Ammonia, Ethane])
def test_specific_heat_attribute_name(component):
    # Used to raise AttributeError on the misspelt _sepcific_heat_constants.
    # Only checks the call completes; the correlation itself is a separate issue.
    assert component().specific_heat() is not None


def test_steam_properties():
    # Used to raise NameError: CP was referenced but only PropsSI was imported.
    steam = Steam(temperature=Temperature(150, "C"), pressure=Pressure(101325, "Pa"))
    # Superheated steam at 1 atm and 150 C is about 0.52 kg/m3.
    assert steam.density().value == pytest.approx(0.52, rel=0.05)


def test_conduction_heat_loss_returns_heat_flow():
    # Used to raise TypeError: "W" is not a HeatFlux unit.
    q = ConductionHeatLoss(
        thermal_conductivity=0.5, area=2.0, temp_difference=20.0, thickness=0.1
    ).calculate()
    assert isinstance(q, HeatFlow)
    assert q.value == pytest.approx(200.0)


def test_convection_heat_loss_returns_heat_flow():
    q = ConvectionHeatLoss(
        heat_transfer_coeff=25.0, area=2.0, temp_difference=20.0
    ).calculate()
    assert isinstance(q, HeatFlow)
    assert q.value == pytest.approx(1000.0)


def test_material_stream_copy():
    # Used to raise AttributeError/TypeError: copy() passed cp=self.cp.
    stream = MaterialStream(
        name="S1",
        component=Water(),
        temperature=Temperature(25, "C"),
        pressure=Pressure(101325, "Pa"),
        flow_rate=VolumetricFlowRate(10, "m3/h"),
    )
    clone = stream.copy("S2")
    assert clone.name == "S2"
    assert clone.specific_heat == stream.specific_heat


def test_reaction_rate_with_supplied_rate_constant():
    # Used to raise ValueError: dict.get() evaluated the Arrhenius default eagerly.
    from processpi.calculations.reaction_engineering.reaction_rate import ReactionRate

    result = ReactionRate(
        model="power_law", k=0.1, C={"A": 2.0, "B": 1.0}, exponents={"A": 1, "B": 1}
    ).calculate()
    assert 0.2 in [pytest.approx(v) for v in result.values() if isinstance(v, float)]


def test_catalyst_activity_with_supplied_decay_constant():
    # Same eager-default bug: used to raise KeyError: 'A_d'.
    from processpi.calculations.reaction_engineering.catalyst_activity import CatalystActivity

    result = CatalystActivity(model="first_order", k_d=0.01, t=100.0).calculate()
    assert math.exp(-1.0) in [pytest.approx(v) for v in result.values() if isinstance(v, float)]


def test_string_unit_supports_format():
    # Used to raise AttributeError: StringUnit has no original_unit.
    from processpi.units import StringUnit

    assert f"{StringUnit('Laminar', 'flow_type')}" == "Laminar"
