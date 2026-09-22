"""Regression tests for heat exchanger convergence reporting and crashes.

The U iteration called a 30% step converged, its verdict never reached the
result, warnings raised inside it were thrown away, every design run reported
status "UNKNOWN", and the phase-change exchangers either crashed or reported
zero pressure drop because they read a velocity keyword nobody passes.
"""

import contextlib
import io

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.streams import MaterialStream
from processpi.units import (
    HeatTransferCoefficient,
    MassFlowRate,
    Pressure,
    Temperature,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _benzene_cooler(**extra):
    """The benzene cooler from docs/examples/equipment/heatexchanger."""
    hot_in = MaterialStream("hot_in", component=Benzene(),
                            temperature=Temperature(90, "C"),
                            mass_flow=MassFlowRate(21000, "kg/h"))
    hot_out = MaterialStream("hot_out", component=Benzene(),
                             temperature=Temperature(30, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(15, "C"),
                             mass_flow=MassFlowRate(60500, "kg/h"))
    cold_out = MaterialStream("cold_out", component=Water())
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out,
               U=HeatTransferCoefficient(575, "W/m2K"),
               shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
               mode="design", **extra)
    return engine


def _phase_change_engine(hx_type, **extra):
    hot_in = MaterialStream("hot_in", component=Water(),
                            temperature=Temperature(120, "C"),
                            pressure=Pressure(2, "bar"),
                            mass_flow=MassFlowRate(3, "kg/s"), phase="vapor")
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(25, "C"),
                             pressure=Pressure(2, "bar"),
                             mass_flow=MassFlowRate(10, "kg/s"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, cold_in=cold_in, hx_type=hx_type, mode="design",
               orientation="horizontal", **extra)
    return engine


def test_results_before_run_raises():
    engine = _benzene_cooler()
    with pytest.raises(RuntimeError):
        engine.results()


def test_results_after_run_are_returned():
    engine = _benzene_cooler()
    _quiet(engine.run)
    assert engine.results() is not None


def test_convergence_tolerance_is_honoured():
    """The first U step is 26% out; only a tolerance above it may accept it."""
    loose = _quiet(_benzene_cooler(u_tolerance_percent=30.0).run).data
    assert loose["converged"] is True
    assert len(loose["convergence_history"]) == 1
    assert loose["convergence_history"][0] > 20.0

    tight = _quiet(_benzene_cooler(u_tolerance_percent=1.0).run).data
    assert tight["converged"] is False
    assert len(tight["convergence_history"]) > 1


def test_failed_convergence_reaches_the_status():
    data = _quiet(_benzene_cooler(u_tolerance_percent=1.0).run).data
    assert data["status"] == "FAILED_CONVERGENCE"
    assert any("CONVERGENCE_WARNING" in w for w in data["warnings"])


def test_design_status_is_never_unknown():
    for tolerance in (1.0, 5.0, 30.0):
        data = _quiet(_benzene_cooler(u_tolerance_percent=tolerance).run).data
        assert data["status"] != "UNKNOWN"
        assert data["status"] is not None


def test_warnings_raised_inside_the_iteration_survive():
    """The hydraulic and stagnation warnings are raised during _iterate_U."""
    data = _quiet(_benzene_cooler(u_tolerance_percent=1.0).run).data
    categories = {w.split("]")[0].lstrip("[") for w in data["warnings"] if w.startswith("[")}
    assert "HYDRAULIC_WARNING" in categories
    assert "CONVERGENCE_WARNING" in categories


def test_feasibility_flags_reflect_the_design_that_was_produced():
    """Design mode reported nothing, so every flag defaulted to True."""
    hot_in = MaterialStream("hot_in", component=Water(),
                            temperature=Temperature(95, "C"),
                            mass_flow=MassFlowRate(12, "kg/s"))
    hot_out = MaterialStream("hot_out", component=Water(),
                             temperature=Temperature(65, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(25, "C"),
                             mass_flow=MassFlowRate(18, "kg/s"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, mode="design")

    data = _quiet(engine.run).data
    summary = data.get("feasibility_summary", {})
    for key in ("thermal_ok", "hydraulic_ok", "pressure_drop_ok"):
        assert isinstance(summary.get(key), bool)

    # This duty overruns the shell-side pressure drop limit, and the warning says
    # so, so the flag and the status must say so too.
    assert any("pressure drop" in w.lower() for w in data["warnings"])
    assert summary["pressure_drop_ok"] is False
    assert data["status"] == "PRESSURE_DROP_FAILURE"


@pytest.mark.parametrize(
    "hx_type,extra",
    [
        ("condenser", {"condensation_mode": "total", "condensing_side": "shell",
                       "latent_heat": 2.1e6}),
        ("evaporator", {"boiling_side": "shell", "latent_heat": 2.25e6}),
        ("reboiler", {"boiling_side": "shell", "latent_heat": 2.25e6}),
    ],
)
def test_phase_change_exchangers_run_and_report_pressure_drop(hx_type, extra):
    """They read v_tube/v_shell now, and no longer drop the shell diameter."""
    data = _quiet(_phase_change_engine(hx_type, **extra).run).data

    tube_dp = float(getattr(data["tube_dp"], "value", data["tube_dp"]))
    shell_dp = float(getattr(data["shell_dp"], "value", data["shell_dp"]))
    tube_velocity = float(getattr(data["tube_velocity"], "value", data["tube_velocity"]))

    assert tube_velocity > 0
    assert tube_dp > 0
    assert shell_dp > 0
    # A dropped shell diameter forced a 1e-6 m baffle spacing and so a baffle
    # count in the hundreds of thousands.
    assert shell_dp < 1e7


def test_specified_outlet_that_breaks_the_balance_is_reported():
    """A supplied outlet used to be dropped in silence."""
    hot_in = MaterialStream("hot_in", component=Water(),
                            temperature=Temperature(95, "C"),
                            mass_flow=MassFlowRate(12, "kg/s"))
    hot_out = MaterialStream("hot_out", component=Water(),
                             temperature=Temperature(65, "C"))
    cold_in = MaterialStream("cold_in", component=Water(),
                             temperature=Temperature(25, "C"),
                             mass_flow=MassFlowRate(18, "kg/s"))
    # Far from anything the energy balance can produce.
    cold_out = MaterialStream("cold_out", component=Water(),
                              temperature=Temperature(90, "C"))
    engine = HeatExchangerEngine(method="kern")
    engine.fit(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out,
               mode="design")

    data = _quiet(engine.run).data
    assert any("BALANCE_WARNING" in w for w in data["warnings"])
