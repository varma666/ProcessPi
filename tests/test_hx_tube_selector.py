"""Tube selection in shell-and-tube design.

With no geometry fixed the selector keeps the preferred 19 mm x 3 m tube, so
the U iteration sees the same tube size on every pass. A tube OD, ID or length
the user gives is kept as given (97865b1), and `search_standard_tube_sizes`
opts in to trying every standard OD and length.
"""
import contextlib
import io
import logging
import warnings

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.standards import (
    PREFERRED_TUBE_LENGTH,
    PREFERRED_TUBE_OD,
    select_tube_configuration,
)
from processpi.streams import MaterialStream
from processpi.units import Length, MassFlowRate, Pressure, Temperature


def _benzene_cooler(**extra):
    """The benzene cooler from docs/examples/equipment/heatexchanger, sized
    from the assumed-U table and iterated (no specified_U)."""
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
               shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"),
               mode="design", **extra)
    return engine


def _run(engine):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logging.disable(logging.CRITICAL)
        try:
            return engine.run().data
        finally:
            logging.disable(logging.NOTSET)


def _m(value):
    return value.to("m").value if hasattr(value, "to") else float(value)


def _hot_cold():
    hot = {"m_dot": 60500 / 3600, "density": 998.0, "component": Water()}
    cold = {"m_dot": 21000 / 3600, "density": 850.0, "component": Benzene()}
    return hot, cold


# ----------------------------------------------------------------------------
# Design results
# ----------------------------------------------------------------------------

def test_design_prints_nothing_to_stdout():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        _run(_benzene_cooler(u_tolerance_percent=1.0))
    assert "fixed_geometry" not in out.getvalue()
    assert "Tube OD:" not in out.getvalue()


def test_free_geometry_keeps_the_preferred_tube_and_converges():
    data = _run(_benzene_cooler(u_tolerance_percent=1.0))
    assert _m(data["tube_od"]) == pytest.approx(PREFERRED_TUBE_OD)
    assert _m(data["tube_length"]) == pytest.approx(PREFERRED_TUBE_LENGTH)
    assert data["converged"] is True
    assert data["convergence_history"][-1] < 1.0
    assert not any("cycles between tube counts" in w for w in data["warnings"])


def test_a_given_tube_length_is_kept():
    data = _run(_benzene_cooler(tube_length=Length(4.88, "m")))
    assert _m(data["tube_length"]) == pytest.approx(4.88)
    assert _m(data["tube_od"]) == pytest.approx(PREFERRED_TUBE_OD)


def test_a_given_tube_od_is_kept():
    data = _run(_benzene_cooler(tube_od=Length(25.4, "mm")))
    assert _m(data["tube_od"]) == pytest.approx(0.0254)
    assert _m(data["tube_length"]) == pytest.approx(PREFERRED_TUBE_LENGTH)


def test_a_given_tube_id_is_kept():
    data = _run(_benzene_cooler(tube_id=Length(15.0, "mm")))
    assert _m(data["tube_id"]) == pytest.approx(0.015)
    assert _m(data["tube_od"]) == pytest.approx(PREFERRED_TUBE_OD)


# ----------------------------------------------------------------------------
# select_tube_configuration
# ----------------------------------------------------------------------------

def test_selector_with_nothing_fixed_uses_the_preferred_tube():
    hot, cold = _hot_cold()
    for area in (20.0, 30.0, 45.0):
        config = select_tube_configuration(area, hot, cold)
        assert config["tube_od"] == pytest.approx(PREFERRED_TUBE_OD)
        assert config["tube_length"] == pytest.approx(PREFERRED_TUBE_LENGTH)


def test_selector_with_a_fixed_length_keeps_it_and_the_preferred_od():
    hot, cold = _hot_cold()
    config = select_tube_configuration(30.0, hot, cold, tube_length=4.88)
    assert config["tube_length"] == pytest.approx(4.88)
    assert config["tube_od"] == pytest.approx(PREFERRED_TUBE_OD)
    assert config["area"] >= 30.0


def test_selector_falls_back_to_a_larger_od_for_a_large_fixed_id():
    hot, cold = _hot_cold()
    config = select_tube_configuration(30.0, hot, cold, tube_id=0.020)
    assert config["tube_id"] == pytest.approx(0.020)
    assert config["tube_od"] > 0.020


def test_search_standard_sizes_tries_other_tubes():
    hot, cold = _hot_cold()
    chosen = {
        (round(c["tube_od"], 4), c["tube_length"])
        for c in (select_tube_configuration(a, hot, cold, search_standard_sizes=True)
                  for a in (20.0, 30.0, 45.0))
    }
    assert chosen != {(PREFERRED_TUBE_OD, PREFERRED_TUBE_LENGTH)}


def test_search_standard_tube_sizes_spec_reaches_the_selector():
    preferred = _run(_benzene_cooler(u_tolerance_percent=15.0))
    searched = _run(_benzene_cooler(u_tolerance_percent=15.0, search_standard_tube_sizes=True))
    assert (_m(searched["tube_od"]), _m(searched["tube_length"])) != (
        _m(preferred["tube_od"]), _m(preferred["tube_length"]))
