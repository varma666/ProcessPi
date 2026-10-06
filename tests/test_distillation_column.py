"""DistillationColumn: design, sizing, error handling and flowsheet use."""

import math

import pytest

from processpi.components import Benzene, ChloroBenzene, Hexane, Toluene, Water
from processpi.equipment import DistillationColumn
from processpi.equipment.distillation import IdealVLE
from processpi.integration.flowsheet import Flowsheet
from processpi.streams import MaterialStream
from processpi.units import MassFlowRate, MolarFlowRate, Pressure, Temperature

ATM = Pressure(1.01325, "bar")


def bt_feed(temperature=Temperature(95, "C"), **kwargs):
    kwargs.setdefault("composition", {"Benzene": 0.4, "Toluene": 0.6})
    kwargs.setdefault("molar_flow", MolarFlowRate(100, "kmol/h"))
    return MaterialStream("Feed", temperature=temperature, pressure=ATM, **kwargs)


def bt_column(feed=None, **specs):
    specs.setdefault("distillate_lk_fraction", 0.97)
    specs.setdefault("bottoms_lk_fraction", 0.02)
    return DistillationColumn(
        feed=feed if feed is not None else bt_feed(),
        components=[Benzene(), Toluene()],
        light_key="Benzene",
        heavy_key="Toluene",
        **specs,
    )


# ----------------------------------------------------------------------
# VLE
# ----------------------------------------------------------------------
def test_ideal_vle_pure_component_boiling_points():
    vle = IdealVLE([Benzene, Toluene])
    # Normal boiling points: benzene 353.24 K, toluene 383.78 K.
    assert vle.saturation_temperature("Benzene", 101325.0) == pytest.approx(353.24, abs=0.3)
    assert vle.saturation_temperature("Toluene", 101325.0) == pytest.approx(383.78, abs=0.3)


def test_ideal_vle_bubble_and_dew_points_are_consistent():
    vle = IdealVLE([Benzene(), Toluene()])
    x = {"Benzene": 0.5, "Toluene": 0.5}
    t_bub, y = vle.equilibrium_vapor(x, 101325.0)
    t_dew = vle.dew_temperature(x, 101325.0)
    assert t_bub < t_dew
    # The vapour in equilibrium with x has its dew point at x's bubble point.
    assert vle.dew_temperature(y, 101325.0) == pytest.approx(t_bub, abs=1e-4)
    assert vle.flash_vapor_fraction(x, t_bub - 1, 101325.0) == 0.0
    assert vle.flash_vapor_fraction(x, t_dew + 1, 101325.0) == 1.0
    assert 0.0 < vle.flash_vapor_fraction(x, 0.5 * (t_bub + t_dew), 101325.0) < 1.0


def test_ideal_vle_rejects_broken_vapour_pressure_constants():
    # Hexane's DIPPR-101 B coefficient is stored as 0.0, which puts Psat out
    # by orders of magnitude; refuse it instead of returning nonsense.
    with pytest.raises(ValueError, match="Hexane"):
        IdealVLE([Hexane, Toluene])


# ----------------------------------------------------------------------
# Binary design
# ----------------------------------------------------------------------
def test_binary_material_balance_and_specs():
    data = bt_column().design().data
    d = data["distillate"]["D"].to("kmol/h").original_value
    b = data["bottoms"]["B"].to("kmol/h").original_value
    # D = F (z - xB) / (xD - xB)
    assert d == pytest.approx(100 * (0.4 - 0.02) / (0.97 - 0.02))
    assert d + b == pytest.approx(100.0)
    assert data["distillate"]["x"]["Benzene"] == pytest.approx(0.97)
    assert data["bottoms"]["x"]["Benzene"] == pytest.approx(0.02)


def test_binary_gilliland_agrees_with_mccabe_thiele():
    data = bt_column().design().data
    mt = data["mccabe_thiele"]
    assert "error" not in mt
    # Shortcut and stage-by-stage counts of the same column, within a stage.
    assert abs(data["N_theoretical"] - mt["N_fractional"]) < 1.0
    assert data["R_over_R_min"] == pytest.approx(1.3)
    assert data["N_theoretical"] > data["N_min"]


def test_binary_r_min_from_underwood_matches_the_pinch_with_ideal_vle():
    column = bt_column(q=1.0)
    data = column.design().data
    vle = column._vle
    p = data["pressure"].value
    # Saturated liquid feed: the pinch sits on the equilibrium curve at x = zF.
    _, y = vle.equilibrium_vapor({"Benzene": 0.4, "Toluene": 0.6}, p)
    r_pinch = (0.97 - y["Benzene"]) / (y["Benzene"] - 0.4)
    # Underwood uses the mean (top/bottom) volatility, so only close, not equal.
    assert data["R_min"] == pytest.approx(r_pinch, rel=0.05)


def test_binary_temperatures_and_duties():
    data = bt_column().design().data
    t = data["temperatures"]
    assert t["condenser"].value < t["top_stage"].value < t["reboiler"].value
    # Nearly pure products boil close to the pure-component points.
    assert t["condenser"].value == pytest.approx(353.24, abs=2.0)
    assert t["reboiler"].value == pytest.approx(383.78, abs=2.0)
    # Hand check of the condenser: V = (R + 1) D, times the latent heat.
    v = data["internal_flows"]["V_rectifying"].value
    vle = IdealVLE([Benzene, Toluene])
    lam = vle.mixture_latent_heat(data["distillate"]["x"], t["condenser"].value)
    assert data["condenser_duty"].value == pytest.approx(v * lam)
    assert data["condenser_duty"].to("kW").original_value == pytest.approx(1040, rel=0.03)
    assert data["reboiler_duty"].value > 0


def test_feed_condition_from_temperature():
    sat = bt_column(feed=bt_feed(temperature=None)).design().data["feed"]
    assert sat["q"] == 1.0
    cold = bt_column(feed=bt_feed(temperature=Temperature(40, "C"))).design().data["feed"]
    assert cold["q"] > 1.0
    assert cold["q_source"] == "subcooled liquid feed"
    bub = cold["bubble_point"].value
    dew = cold["dew_point"].value
    two = bt_column(feed=bt_feed(temperature=Temperature(0.5 * (bub + dew), "K"))).design().data["feed"]
    assert 0.0 < two["q"] < 1.0
    # A colder feed needs less reflux.
    r_cold = bt_column(feed=bt_feed(temperature=Temperature(40, "C"))).design().data["R_min"]
    r_two = bt_column(feed=bt_feed(temperature=Temperature(0.5 * (bub + dew), "K"))).design().data["R_min"]
    assert r_cold < r_two


def test_superheated_feed_needs_q():
    with pytest.raises(ValueError, match="superheated"):
        bt_column(feed=bt_feed(temperature=Temperature(150, "C"))).design()
    data = bt_column(feed=bt_feed(temperature=Temperature(150, "C")), q=-0.1).design().data
    assert data["feed"]["q"] == -0.1


def test_tray_efficiency_and_trays():
    data = bt_column().design().data
    assert data["tray_efficiency_source"] == "O'Connell"
    mu_mpa_s = data["liquid_viscosity"].value * 1000
    alpha = data["relative_volatility"]["Benzene"]
    assert data["tray_efficiency"] == pytest.approx(0.503 * (mu_mpa_s * alpha) ** -0.226)
    # The reboiler is a theoretical stage, not a tray.
    assert data["actual_trays"] == math.ceil((data["N_theoretical"] - 1) / data["tray_efficiency"])
    assert 1 <= data["feed_tray"] <= data["actual_trays"]
    fixed = bt_column(tray_efficiency=0.7).design().data
    assert fixed["tray_efficiency_source"] == "specified"
    assert fixed["actual_trays"] == math.ceil((fixed["N_theoretical"] - 1) / 0.7)


def test_diameter_sizing():
    data = bt_column().design().data
    top, bottom = data["hydraulics"]["top"], data["hydraulics"]["bottom"]
    assert data["diameter"].value == pytest.approx(max(top["diameter"].value, bottom["diameter"].value))
    # A 100 kmol/h benzene/toluene column at 1 atm is about a metre across.
    assert 0.7 < data["diameter"].value < 1.6
    assert data["tray_section_height"].value == pytest.approx(data["actual_trays"] * 0.6)
    # Higher surface tension raises the flooding velocity and shrinks the column.
    wide = bt_column(surface_tension=0.010).design().data["diameter"].value
    narrow = bt_column(surface_tension=0.030).design().data["diameter"].value
    assert narrow < data["diameter"].value < wide
    # Designing closer to flood gives a smaller column, and a warning past 85 %.
    tight = bt_column(flood_fraction=0.9).design().data
    assert tight["diameter"].value < data["diameter"].value
    assert any("flood_fraction" in w for w in tight["warnings"])


def test_doubling_the_feed_doubles_the_column_area():
    one = bt_column().design().data
    two = bt_column(feed=bt_feed(molar_flow=MolarFlowRate(200, "kmol/h"))).design().data
    assert two["diameter"].value == pytest.approx(one["diameter"].value * math.sqrt(2), rel=1e-6)
    assert two["N_theoretical"] == pytest.approx(one["N_theoretical"])


def test_reflux_ratio_specified():
    data = bt_column(reflux_ratio=3.0).design().data
    assert data["reflux_ratio"] == 3.0
    assert data["reflux_ratio_source"] == "specified"
    with pytest.raises(ValueError, match="R_min"):
        bt_column(reflux_ratio=1.0).design()


def test_recovery_specs_and_mass_basis_feed():
    by_recovery = bt_column(distillate_lk_fraction=None, bottoms_lk_fraction=None,
                            light_key_recovery=0.95, heavy_key_recovery=0.97).design().data
    assert by_recovery["key_recoveries"]["light_key_to_distillate"] == pytest.approx(0.95)
    assert by_recovery["key_recoveries"]["heavy_key_to_bottoms"] == pytest.approx(0.97)
    # 40/60 mol % benzene/toluene as a mass-basis feed.
    w_b, w_t = 0.4 * 78.114, 0.6 * 92.141
    mass_feed = MaterialStream(
        "Feed", composition={"Benzene": w_b, "Toluene": w_t}, basis="mass",
        mass_flow=MassFlowRate(100 * (w_b + w_t) / 3600, "kg/s"),
        temperature=Temperature(95, "C"), pressure=ATM,
    )
    mass = bt_column(feed=mass_feed).design().data
    molar = bt_column().design().data
    assert mass["feed"]["z"]["Benzene"] == pytest.approx(0.4, rel=1e-3)
    assert mass["feed"]["F"].value == pytest.approx(molar["feed"]["F"].value, rel=1e-3)


def test_summary_mentions_the_main_results():
    text = bt_column().design().summary()
    for fragment in ("Fenske", "Underwood", "Gilliland", "Kirkbride", "McCabe-Thiele", "O'Connell",
                     "Condenser duty", "Column diameter", "Assumptions"):
        assert fragment in text


# ----------------------------------------------------------------------
# Multicomponent, constant relative volatility
# ----------------------------------------------------------------------
def oep_column(**specs):
    # OpenExamPrep PE Chemical 11.4 worked example (see test_distillation_shortcut.py).
    feed = MaterialStream(
        "Feed", composition={"Ethane": 0.1, "Propane": 0.4, "nButane": 0.35, "nPentane": 0.15},
        molar_flow=MolarFlowRate(100, "kmol/h"), pressure=Pressure(10, "bar"),
    )
    specs.setdefault("q", 1.0)
    specs.setdefault("light_key_recovery", 0.98)
    specs.setdefault("heavy_key_recovery", 0.98)
    return DistillationColumn(
        feed=feed, relative_volatility={"Ethane": 5.0, "Propane": 2.2, "nButane": 1.0, "nPentane": 0.4},
        light_key="Propane", heavy_key="nButane", **specs,
    )


def test_multicomponent_oep_worked_example():
    data = oep_column(gilliland_correlation="eduljee").design().data
    assert data["N_min"] == pytest.approx(9.872, abs=1e-3)
    assert data["underwood_theta"][0] == pytest.approx(1.3250, abs=1e-4)
    assert data["R_min"] == pytest.approx(1.2046, abs=1e-4)
    assert data["N_theoretical"] == pytest.approx(20.86, abs=0.05)
    assert data["N_rectifying"] / data["N_stripping"] == pytest.approx(1.0271, abs=1e-3)
    # "The feed should enter at Stage 11 or 12 from the top."
    assert data["feed_stage"] in (11, 12)
    assert data["distillate"]["D"].to("kmol/h").original_value == pytest.approx(49.90, abs=0.01)
    assert "mccabe_thiele" not in data
    assert "diameter" not in data


def test_relative_volatility_is_normalised_to_the_heavy_key():
    a = oep_column().design().data
    b = DistillationColumn(
        feed=oep_column().feed,
        relative_volatility={"Ethane": 10.0, "Propane": 4.4, "nButane": 2.0, "nPentane": 0.8},
        light_key="Propane", heavy_key="nButane", light_key_recovery=0.98, heavy_key_recovery=0.98, q=1.0,
    ).design().data
    assert b["R_min"] == pytest.approx(a["R_min"])
    assert b["N_min"] == pytest.approx(a["N_min"])


def test_relative_volatility_mode_with_a_given_efficiency():
    data = oep_column(tray_efficiency=0.8).design().data
    assert data["actual_trays"] == math.ceil((data["N_theoretical"] - 1) / 0.8)


# ----------------------------------------------------------------------
# Multicomponent, component data
# ----------------------------------------------------------------------
def btc_column(lk, hk):
    feed = MaterialStream(
        "Feed", composition={"benzene": 0.3, "Toluene": 0.4, "Chlorobenzene": 0.3},
        molar_flow=MolarFlowRate(150, "kmol/h"), temperature=Temperature(90, "C"), pressure=Pressure(1.2, "bar"),
    )
    return DistillationColumn(feed=feed, components=[Benzene(), Toluene(), ChloroBenzene()], light_key=lk,
                              heavy_key=hk, light_key_recovery=0.99, heavy_key_recovery=0.99)


def test_component_names_match_loosely():
    # The feed says "Chlorobenzene" and "benzene"; the components are named
    # "Chloro Benzene" and "Benzene".
    data = btc_column("Benzene", "Toluene").design().data
    assert set(data["feed"]["z"]) == {"Benzene", "Toluene", "Chloro Benzene"}
    assert data["heavy_key"] == "Toluene"


def test_multicomponent_with_component_data():
    data = btc_column("Benzene", "Toluene").design().data
    # Chlorobenzene is the heavy non-key: it leaves in the bottoms.
    assert data["distillate"]["x"]["Chloro Benzene"] < 1e-3
    assert data["relative_volatility"]["Chloro Benzene"] < 1.0 < data["relative_volatility"]["Benzene"]
    f = data["feed"]["F"].value
    for n, z in data["feed"]["z"].items():
        d = data["distillate"]["flows"][n].value
        b = data["bottoms"]["flows"][n].value
        assert d + b == pytest.approx(f * z)
    assert "underwood_distillate_at_R_min" not in data


def test_component_between_the_keys_distributes():
    data = btc_column("Benzene", "ChloroBenzene").design().data
    assert len(data["underwood_theta"]) == 2
    flows = data["underwood_distillate_at_R_min"]
    assert set(flows) == {"Toluene"}
    toluene_feed = data["feed"]["F"].value * 0.4
    assert 0.0 < flows["Toluene"].value < toluene_feed
    assert 0.05 < data["distillate"]["x"]["Toluene"] and 0.05 < data["bottoms"]["x"]["Toluene"]
    assert "Toluene distributes" in btc_column("Benzene", "ChloroBenzene").design().summary()


# ----------------------------------------------------------------------
# Input errors
# ----------------------------------------------------------------------
def test_input_errors():
    with pytest.raises(ValueError, match="light_key"):
        DistillationColumn(feed=bt_feed(), components=[Benzene(), Toluene()]).design()
    with pytest.raises(ValueError, match="exactly one"):
        bt_column(relative_volatility={"Benzene": 2.5, "Toluene": 1.0}).design()
    with pytest.raises(ValueError, match="either"):
        bt_column(light_key_recovery=0.9, heavy_key_recovery=0.9).design()
    with pytest.raises(ValueError, match="binary"):
        oep_column(light_key_recovery=None, heavy_key_recovery=None,
                   distillate_lk_fraction=0.9, bottoms_lk_fraction=0.05).design()
    with pytest.raises(KeyError, match="Water"):
        bt_column(feed=bt_feed(composition={"Benzene": 0.4, "Water": 0.6})).design()
    with pytest.raises(ValueError, match="single component"):
        bt_column(feed=MaterialStream("W", component=Water(), molar_flow=MolarFlowRate(1, "mol/s"))).design()
    with pytest.raises(ValueError, match="not connected"):
        DistillationColumn(components=[Benzene(), Toluene()], light_key="Benzene", heavy_key="Toluene",
                           distillate_lk_fraction=0.97, bottoms_lk_fraction=0.02).design()


def test_reversed_keys_are_rejected():
    with pytest.raises(ValueError):
        DistillationColumn(feed=bt_feed(), components=[Benzene(), Toluene()], light_key="Toluene",
                           heavy_key="Benzene", light_key_recovery=0.9, heavy_key_recovery=0.9).design()


def test_results_before_design():
    column = bt_column()
    assert column.summary() is None
    with pytest.raises(RuntimeError):
        column.results()


# ----------------------------------------------------------------------
# Flowsheet
# ----------------------------------------------------------------------
def test_simulate_writes_the_product_streams():
    distillate, bottoms = MaterialStream("D"), MaterialStream("B")
    column = bt_column(distillate=distillate, bottoms=bottoms)
    out = column.simulate()
    data = column.results().data
    assert distillate.components == pytest.approx({"Benzene": 0.97, "Toluene": 0.03})
    assert bottoms.components == pytest.approx({"Benzene": 0.02, "Toluene": 0.98})
    assert distillate.molar_flow().value == pytest.approx(data["distillate"]["D"].value)
    assert bottoms.molar_flow().value + distillate.molar_flow().value == pytest.approx(column.feed.molar_flow().value)
    assert distillate.temperature.value == pytest.approx(data["temperatures"]["condenser"].value)
    assert bottoms.temperature.value == pytest.approx(data["temperatures"]["reboiler"].value)
    assert distillate.pressure.value == pytest.approx(ATM.value)
    # The written stream has what MaterialStream needs for its own mass flow.
    assert distillate.mass_flow() is not None
    assert out["condenser_duty"] is data["condenser_duty"]


def test_simulate_needs_both_outlets():
    with pytest.raises(ValueError, match="distillate"):
        bt_column().simulate()


def test_column_runs_inside_a_flowsheet():
    feed, distillate, bottoms = bt_feed(), MaterialStream("D"), MaterialStream("B")
    column = DistillationColumn(
        name="T-101", components=[Benzene(), Toluene()], light_key="Benzene", heavy_key="Toluene",
        distillate_lk_fraction=0.97, bottoms_lk_fraction=0.02,
    )
    fs = Flowsheet("BTX")
    fs.connect(feed, column, "feed")
    column.connect_outlet("distillate", distillate)
    column.connect_outlet("bottoms", bottoms)
    fs.run()
    assert column.data["N_theoretical"] > 0
    assert distillate.components["Benzene"] == pytest.approx(0.97)
