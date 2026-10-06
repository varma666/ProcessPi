"""DistillationEngine: the fit/run interface over DistillationColumn."""

import pytest

from processpi.components import Benzene, Toluene
from processpi.equipment import DistillationColumn, DistillationEngine, DistillationResults
from processpi.streams import MaterialStream
from processpi.units import MolarFlowRate, Pressure, Temperature

SPECS = dict(
    components=[Benzene(), Toluene()],
    light_key="Benzene",
    heavy_key="Toluene",
    distillate_lk_fraction=0.97,
    bottoms_lk_fraction=0.02,
)


def feed():
    return MaterialStream(
        "Feed",
        composition={"Benzene": 0.4, "Toluene": 0.6},
        molar_flow=MolarFlowRate(100, "kmol/h"),
        temperature=Temperature(95, "C"),
        pressure=Pressure(1.01325, "bar"),
    )


def test_fit_returns_the_engine_and_run_returns_results():
    model = DistillationEngine()
    assert model.fit(feed=feed(), **SPECS) is model
    results = model.run()
    assert isinstance(results, DistillationResults)
    assert model.results() is results
    assert model.summary() == results.summary()
    assert isinstance(model.column, DistillationColumn)


def test_engine_matches_the_column():
    via_engine = DistillationEngine().fit(feed=feed(), **SPECS).run().data
    via_column = DistillationColumn(feed=feed(), **SPECS).design().data
    for key in ("N_min", "R_min", "reflux_ratio", "N_theoretical", "feed_stage", "actual_trays"):
        assert via_engine[key] == pytest.approx(via_column[key])
    assert via_engine["diameter"].value == pytest.approx(via_column["diameter"].value)
    assert via_engine["condenser_duty"].value == pytest.approx(via_column["condenser_duty"].value)


def test_constructor_kwargs_go_to_fit_and_name_is_kept():
    model = DistillationEngine(name="T-101", feed=feed(), **SPECS)
    assert model.data["feed"].name == "Feed"
    assert model.run()["name"] == "T-101"
    model.fit(feed=feed(), name="T-102", **SPECS)
    assert model.run()["name"] == "T-102"


def test_refit_clears_the_previous_results():
    model = DistillationEngine().fit(feed=feed(), **SPECS)
    model.run()
    model.fit(feed=feed(), reflux_ratio=3.0, **SPECS)
    assert model.summary() is None
    with pytest.raises(RuntimeError):
        model.results()
    assert model.run()["reflux_ratio"] == 3.0


def test_product_streams_are_written_when_given():
    distillate, bottoms = MaterialStream("D"), MaterialStream("B")
    results = DistillationEngine().fit(feed=feed(), distillate=distillate, bottoms=bottoms, **SPECS).run()
    assert distillate.components["Benzene"] == pytest.approx(0.97)
    assert bottoms.components["Toluene"] == pytest.approx(0.98)
    assert distillate.molar_flow().value == pytest.approx(results["distillate"]["D"].value)


def test_fit_and_run_errors():
    with pytest.raises(TypeError):
        DistillationEngine().fit(feed={"Benzene": 0.4}, **SPECS)
    with pytest.raises(ValueError, match="light_key"):
        DistillationEngine().fit(feed=feed(), components=[Benzene(), Toluene()], heavy_key="Toluene")
    with pytest.raises(ValueError, match="both"):
        DistillationEngine().fit(feed=feed(), distillate=MaterialStream("D"), **SPECS)
    with pytest.raises(RuntimeError, match="fit"):
        DistillationEngine().run()
    model = DistillationEngine()
    assert model.summary() is None
    with pytest.raises(RuntimeError, match="run"):
        model.results()
