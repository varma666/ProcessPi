"""The fluid assignment decides which stream the shell-and-tube model puts in the tubes.

`_assign_fluids_to_sides` scores which fluid belongs in the tubes (fouling,
corrosion, hazard, phase), but the Kern and Bell routines used to model the hot
stream in the tubes whatever it decided. They now take the resolved
(tube, shell) pair, so the tube-side Re, h, velocity, pressure drop and fouling
factor all belong to the stream that is actually in the tubes. An explicit
force_hot_in_tubes / force_cold_in_tubes still overrides the scoring.

The master reference values below were produced by 3e8a241 (upstream master
before this change) with the same inputs.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, Water
from processpi.equipment.heatexchangers import CondenserHX, HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.equipment.heatexchangers.standards import get_fouling_factor
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


def _value(x):
    return float(getattr(x, "value", x))


def _streams(hot_component, cold_component, hot_t, hot_out_t, cold_t, hot_kg_h, cold_kg_h,
             cold_out_t=None):
    hot_in = MaterialStream("hot_in", component=hot_component(),
                            temperature=Temperature(hot_t, "C"),
                            mass_flow=MassFlowRate(hot_kg_h, "kg/h"))
    hot_out = MaterialStream("hot_out", component=hot_component(),
                             temperature=Temperature(hot_out_t, "C"))
    cold_in = MaterialStream("cold_in", component=cold_component(),
                             temperature=Temperature(cold_t, "C"),
                             mass_flow=MassFlowRate(cold_kg_h, "kg/h"))
    cold_out_kwargs = {"component": cold_component()}
    if cold_out_t is not None:
        cold_out_kwargs["temperature"] = Temperature(cold_out_t, "C")
    cold_out = MaterialStream("cold_out", **cold_out_kwargs)
    return dict(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out)


def _benzene_cooler(cold_out_t=None):
    """docs/examples benzene cooler: the scoring puts the water (cold) in the tubes."""
    return _streams(Benzene, Water, 90, 30, 15, 21000.0, 60500.0, cold_out_t)


def _water_heats_benzene():
    """Hot water heating benzene: the scoring puts the water (hot) in the tubes."""
    return _streams(Water, Benzene, 90, 60, 15, 40000.0, 60000.0)


_DESIGN_SPECS = dict(U=HeatTransferCoefficient(575, "W/m2K"),
                     shell_dp=Pressure(1, "bar"), tube_dp=Pressure(1, "bar"))


def _run(streams, method="kern", mode="design", **specs):
    engine = HeatExchangerEngine(method=method).fit(
        **streams, **dict(_DESIGN_SPECS, mode=mode, **specs)
    )
    return _quiet(engine.run).data


def _hx(streams, **specs):
    return ShellAndTubeHX(method="kern", **streams, **dict(_DESIGN_SPECS, **specs))


# ----------------------------------------------------------------------------
# When the hot stream ends up in the tubes, nothing moves.
# ----------------------------------------------------------------------------

# 3e8a241, Kern design of `_water_heats_benzene()`.
_MASTER_WATER_HEATS_BENZENE_KERN = {
    "Q": 1394826.7825549562, "LMTD": 35.29904091545207, "tube_count": 312,
    "Area": 55.87008375144088, "U_calculated": 767.5589877633034,
    "h_tube": 4968.716479964737, "h_shell": 1629.1775462954492,
    "tube_velocity": 1.4245578021049645, "shell_velocity": 0.9342485961940565,
    "tube_dp": 35201.061099024926, "shell_dp": 20232.05347274748,
    "re_shell": 18679.152166691878,
}

# 3e8a241, Kern design of `_benzene_cooler()` (which always modelled benzene in
# the tubes there).
_MASTER_BENZENE_COOLER_KERN = {
    "Q": 611559.6187674904, "LMTD": 34.520091803901416, "tube_count": 174,
    "Area": 31.158315938303566, "U_calculated": 662.0909250527172,
    "h_tube": 1300.5797132688929, "h_shell": 6967.053746031809,
    "tube_velocity": 1.1459582271189999, "shell_velocity": 1.3925400262032763,
    "tube_dp": 9900.280984232031, "shell_dp": 56918.24516105351,
    "re_shell": 20848.5869653056,
}


# Values that have moved since 3e8a241 because the physics under them was
# corrected in a later change, not because of the side assignment. Each entry
# names the change. The hot-in-tubes runs must match master in everything else.
_SINCE_MASTER_WATER_HEATS_BENZENE_KERN = {
    # Settled tube passes in the final pressure drop: 35201.061 Pa on master
    # at 4 passes counted as 2.
    # Bundle diameter from Sinnott Table 12.4 for the settled passes (8 here)
    # instead of the 2-pass constants: a larger bundle and shell, a lower shell velocity,
    # and so a new geometry. Master: 312 tubes, 55.870 m2, U 767.56,
    # h_tube 4968.7, h_shell 1629.2, v_tube 1.4246, v_shell 0.93425,
    # shell_dp 20232, Re_s 18679.
    "tube_count": 344, "Area": 61.60034875158866, "U_calculated": 683.0794571965115,
    "h_tube": 4595.376905482573, "h_shell": 1323.5966895421316,
    "tube_velocity": 1.292040797257991, "shell_velocity": 0.6403822470290648,
    "tube_dp": 58687.81131173749,
    # Textbook Kern shell-side pressure drop in place of the Kern/Bell hybrid.
    "shell_dp": 28159.587927023906,
    "re_shell": 12803.655778380571,
}
_SINCE_MASTER_BENZENE_COOLER_KERN = {
    # As above, 6 settled passes. Master: 174 tubes, 31.158 m2, U 662.09,
    # h_tube 1300.6, h_shell 6967.1, v_tube 1.1460, v_shell 1.3925,
    # tube_dp 9900.3 (6 passes counted as 2), shell_dp 56918, Re_s 20849.
    "tube_count": 168, "Area": 30.083891250775856, "U_calculated": 664.3626466565012,
    "h_tube": 1337.608280910971, "h_shell": 6110.828556840333,
    "tube_velocity": 1.186885306658964, "shell_velocity": 1.0971447749938399,
    "tube_dp": 31710.83428017723,
    # Textbook Kern shell-side pressure drop in place of the Kern/Bell hybrid.
    "shell_dp": 91454.82574918722,
    "re_shell": 16426.04005958439,
}


def _assert_matches(data, reference, since_master=None):
    for key, expected in {**reference, **(since_master or {})}.items():
        assert _value(data[key]) == pytest.approx(expected, rel=1e-12), key


def test_scoring_hot_in_tubes_gives_the_master_numbers():
    data = _run(_water_heats_benzene())
    assert data["assignment"]["tube_side"] == "hot"
    assert data["tube_side_fluid"] == "Water"
    assert data["shell_side_fluid"] == "Benzene"
    _assert_matches(data, _MASTER_WATER_HEATS_BENZENE_KERN,
                    _SINCE_MASTER_WATER_HEATS_BENZENE_KERN)
    assert not any("ASSIGNMENT_WARNING" in w for w in data["warnings"])


def test_scoring_hot_in_tubes_gives_the_master_numbers_on_the_bell_path():
    data = _run(_water_heats_benzene(), method="bell_delaware")
    assert data["assignment"]["tube_side"] == "hot"
    # Bell-Delaware design of the same case. 3e8a241 gave U 460.1777828989243,
    # h_shell 673.8324876931076 and shell_dp 23266.861493659602; these moved with
    # the Kern geometry under them (see _SINCE_MASTER_WATER_HEATS_BENZENE_KERN),
    # and the shell dP is now the Kern one with no 1.15 uplift.
    assert _value(data["U_calculated"]) == pytest.approx(416.87097088356177, rel=1e-12)
    assert _value(data["h_shell"]) == pytest.approx(591.5821168422973, rel=1e-12)
    assert _value(data["shell_dp"]) == pytest.approx(28159.587927023906, rel=1e-12)


def test_force_hot_in_tubes_overrides_the_scoring_and_gives_the_master_numbers():
    data = _run(_benzene_cooler(), force_hot_in_tubes=True)
    assert data["assignment"]["tube_side"] == "hot"
    assert data["tube_side_fluid"] == "Benzene"
    # The scoring's own pick is still reported, and the reason says who decided.
    assert data["assignment"]["recommended_tube_side_fluid"] == "Water"
    assert data["assignment_reason"][0] == "Forced by user: hot in tubes"
    _assert_matches(data, _MASTER_BENZENE_COOLER_KERN, _SINCE_MASTER_BENZENE_COOLER_KERN)


# ----------------------------------------------------------------------------
# When the scoring picks the cold stream, the tube side is the cold stream.
# ----------------------------------------------------------------------------

def test_scoring_cold_in_tubes_is_modelled_and_reported():
    data = _run(_benzene_cooler())
    assert data["assignment"]["tube_side"] == "cold"
    assert data["tube_side_fluid"] == "Water"
    assert data["shell_side_fluid"] == "Benzene"
    assert data["assignment"]["recommended_tube_side_fluid"] == "Water"
    # The report and the model agree, so there is nothing to warn about.
    assert not any("ASSIGNMENT_WARNING" in w for w in data["warnings"])
    # Water in the tubes gives a far higher tube-side coefficient than the
    # benzene did on master (1300.6 W/m2K), and benzene on the shell side a far
    # lower shell-side one (6967.1 W/m2K on master, with water there).
    assert _value(data["h_tube"]) > 2.0 * _MASTER_BENZENE_COOLER_KERN["h_tube"]
    assert _value(data["h_shell"]) < 0.5 * _MASTER_BENZENE_COOLER_KERN["h_shell"]


def test_duty_and_lmtd_do_not_depend_on_the_side_assignment():
    cold_in_tubes = _run(_benzene_cooler())
    hot_in_tubes = _run(_benzene_cooler(), force_hot_in_tubes=True)
    assert cold_in_tubes["assignment"]["tube_side"] == "cold"
    assert hot_in_tubes["assignment"]["tube_side"] == "hot"
    for key in ("Q", "LMTD"):
        assert _value(cold_in_tubes[key]) == _value(hot_in_tubes[key])
        assert _value(cold_in_tubes[key]) == pytest.approx(
            _MASTER_BENZENE_COOLER_KERN[key], rel=1e-12
        )


def test_cold_in_tubes_tube_side_uses_the_cold_fluid_properties():
    """Rating with fixed geometry, checked against the correlations by hand.

    Water (the cold stream) in the tubes, 200 tubes 19.05/16.0 mm x 4.88 m,
    2 passes; benzene in a 0.45 m shell with 0.18 m baffle spacing.

    Water at 15 C from the component: rho = 994.679 kg/m3,
    mu = 9.1253e-4 Pa.s, cp = 4184.48 J/kg.K, k = 0.60630 W/m.K,
    m = 60500 kg/h = 16.8056 kg/s.

      tube flow area = (200/2) pi 0.016^2 / 4    = 0.0201062 m2
      v_tube         = 16.8056 / 994.679 / A      = 0.84031 m/s
      Re_t           = 994.679 * 0.84031 * 0.016 / 9.1253e-4 = 14655
      Pr_t           = 4184.48 * 9.1253e-4 / 0.60630        = 6.2980
      Nu_t           = 0.023 Re^0.8 Pr^0.4 (water is heated) = 103.32
      h_tube         = 103.32 * 0.60630 / 0.016              = 3915.4 W/m2K

    With benzene in the tubes instead (master), Re_t came out 7740 and
    h_tube 483.1 W/m2K, so the two cannot be confused.
    """
    streams = _benzene_cooler(cold_out_t=25)
    geometry = dict(tube_od=0.01905, tube_id=0.016, tube_length=4.88, tube_count=200,
                    tube_passes=2, shell_diameter=0.45, baffle_spacing=0.18)
    data = _run(streams, mode="rate", **geometry)
    assert data["assignment"]["tube_side"] == "cold"

    hx = _hx(streams)
    water = hx._stream_props(streams["cold_in"])
    benzene = hx._stream_props(streams["hot_in"])

    # Independent recomputation from the raw water properties.
    flow_area = (200 / 2) * math.pi * 0.016 ** 2 / 4.0
    v_tube = water["m_dot"] / water["density"] / flow_area
    re_t = water["density"] * v_tube * 0.016 / water["viscosity"]
    pr_t = water["cp"] * water["viscosity"] / water["k"]
    h_tube = 0.023 * re_t ** 0.8 * pr_t ** 0.4 * water["k"] / 0.016

    assert v_tube == pytest.approx(0.84031, rel=1e-4)
    assert re_t == pytest.approx(14655, rel=1e-4)
    assert h_tube == pytest.approx(3915.4, rel=1e-4)
    assert _value(data["tube_velocity"]) == pytest.approx(v_tube, rel=1e-9)
    assert _value(data["h_tube"]) == pytest.approx(h_tube, rel=1e-9)

    # Tube-side pressure drop from the water density and Re, Kern's
    # 4 f (L Np / di) rho v^2/2 + 4 Np rho v^2/2 with f = 0.079 Re^-0.25.
    velocity_head = water["density"] * v_tube ** 2 / 2.0
    f = 0.079 / re_t ** 0.25
    tube_dp = 4.0 * f * (4.88 * 2 / 0.016) * velocity_head + 4.0 * 2 * velocity_head
    assert _value(data["tube_dp"]) == pytest.approx(tube_dp, rel=1e-9)

    # Shell side is the benzene: Kern cross-flow area, triangular-pitch De,
    # Nu = 0.36 Re^0.55 Pr^(1/3).
    pitch, od = 1.25 * 0.01905, 0.01905
    area_s = (pitch - od) * 0.45 * 0.18 / pitch
    v_shell = benzene["m_dot"] / benzene["density"] / area_s
    de = 4.0 * (math.sqrt(3.0) / 4.0 * pitch ** 2 - math.pi * od ** 2 / 8.0) / (math.pi * od / 2.0)
    re_s = benzene["density"] * v_shell * de / benzene["viscosity"]
    pr_s = benzene["cp"] * benzene["viscosity"] / benzene["k"]
    h_shell = 0.36 * re_s ** 0.55 * pr_s ** (1.0 / 3.0) * benzene["k"] / de
    assert _value(data["shell_velocity"]) == pytest.approx(v_shell, rel=1e-9)
    assert data["re_shell"] == pytest.approx(re_s, rel=1e-9)
    assert _value(data["h_shell"]) == pytest.approx(h_shell, rel=1e-9)


def test_dittus_boelter_uses_the_heating_exponent_for_the_cold_stream():
    from processpi.calculations.heat_transfer import DittusBoelter

    streams = _benzene_cooler()
    hx = _hx(streams)
    hot = hx._stream_props(streams["hot_in"])
    cold = hx._stream_props(streams["cold_in"])
    _quiet(hx._assign_fluids_to_sides, hot, cold)
    tube, shell = hx._side_props(hot, cold)
    assert tube is cold and shell is hot

    geometry = dict(tube_od=0.019, tube_id=0.015, tube_pitch=1.25 * 0.019,
                    tube_count=138, tube_length=3.0, shell_diameter=0.5)
    dimless = _quiet(hx._calculate_dimensionless, geometry, tube, shell, 1.5, 1.0)
    assert dimless["re_t"] == pytest.approx(cold["density"] * 1.5 * 0.015 / cold["viscosity"])
    expected = DittusBoelter(reynolds=dimless["re_t"], prandtl=dimless["pr_t"], n=0.4).calculate()
    assert dimless["nu_t"] == pytest.approx(expected)


def test_fouling_factors_follow_the_streams_to_their_sides():
    streams = _benzene_cooler()
    hx = _hx(streams)
    _quiet(hx._assign_fluids_to_sides, hx._stream_props(streams["hot_in"]),
           hx._stream_props(streams["cold_in"]))
    result = _quiet(hx._calculate_overall_U, h_t=2000.0, h_s=3000.0,
                    geometry={"tube_od": 0.019, "tube_id": 0.015})

    water_fouling = get_fouling_factor(
        fluid_key=streams["cold_in"].component.hx_data()["fouling_key"],
        velocity=None, temperature=_value(streams["cold_in"].temperature.to("C")),
    )
    benzene_fouling = get_fouling_factor(
        fluid_key=streams["hot_in"].component.hx_data()["fouling_key"],
        velocity=None, temperature=_value(streams["hot_in"].temperature.to("C")),
    )
    assert result["Rf_tube"] == pytest.approx(water_fouling * 0.019 / 0.015)
    assert result["Rf_shell"] == pytest.approx(benzene_fouling)


def test_velocity_limits_are_those_of_the_fluid_on_each_side():
    streams = _benzene_cooler()
    hx = _hx(streams)
    _quiet(hx._assign_fluids_to_sides, hx._stream_props(streams["hot_in"]),
           hx._stream_props(streams["cold_in"]))
    tube_stream, shell_stream = hx._side_streams()
    assert tube_stream is streams["cold_in"]
    assert shell_stream is streams["hot_in"]

    vmin, _ = hx._get_velocity_limits("tube", streams["cold_in"].component)
    warnings = hx._velocity_warnings(0.99 * vmin, 1.0, {}, {})
    assert f"Tube velocity low ({0.99 * vmin:.2f} m/s)" in warnings


def test_force_cold_in_tubes_overrides_a_hot_scoring():
    data = _run(_water_heats_benzene(), force_cold_in_tubes=True)
    assert data["assignment"]["tube_side"] == "cold"
    assert data["tube_side_fluid"] == "Benzene"
    assert data["assignment"]["recommended_tube_side_fluid"] == "Water"
    assert data["assignment_reason"][0] == "Forced by user: cold in tubes"
    assert _value(data["h_tube"]) != pytest.approx(_MASTER_WATER_HEATS_BENZENE_KERN["h_tube"])


def test_both_force_flags_are_refused():
    with pytest.raises(ValueError, match="force_hot_in_tubes and force_cold_in_tubes"):
        _run(_benzene_cooler(), force_hot_in_tubes=True, force_cold_in_tubes=True)


def test_bell_path_uses_the_resolved_sides():
    kern = _run(_benzene_cooler())
    bell = _run(_benzene_cooler(), method="bell_delaware")
    assert bell["assignment"]["tube_side"] == "cold"
    assert bell["tube_side_fluid"] == "Water"
    # Bell corrects only the shell side of the Kern result.
    assert _value(bell["h_tube"]) == pytest.approx(_value(kern["h_tube"]))


# ----------------------------------------------------------------------------
# Phase-change exchangers keep the hot stream in the tubes.
# ----------------------------------------------------------------------------

def _benzene_condenser_streams():
    hot_in = MaterialStream("benzene_vapor_in", component=Benzene(), phase="vapor",
                            temperature=Temperature(95, "C"), pressure=Pressure(1.2, "bar"),
                            mass_flow=MassFlowRate(12000, "kg/h"))
    hot_out = MaterialStream("benzene_liquid_out", component=Benzene(), phase="liquid",
                             temperature=Temperature(95, "C"))
    cold_in = MaterialStream("cw_in", component=Water(), phase="liquid",
                             temperature=Temperature(30, "C"), pressure=Pressure(1, "bar"),
                             mass_flow=MassFlowRate(50000, "kg/h"))
    cold_out = MaterialStream("cw_out", component=Water())
    return dict(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out)


def test_condenser_keeps_the_hot_stream_in_the_tubes_and_says_so():
    streams = _benzene_condenser_streams()
    engine = HeatExchangerEngine(method="kern").fit(
        hx_type="condenser", latent_heat=394000, orientation="horizontal",
        mode="design", **streams,
    )
    data = _quiet(engine.run).data
    assert data["assignment"]["tube_side"] == "hot"
    assert data["tube_side_fluid"] == "Benzene"
    assert data["assignment"]["recommended_tube_side_fluid"] == "Water"
    assert any(
        "ASSIGNMENT_WARNING" in w and "CondenserHX models the hot stream" in w
        for w in data["warnings"]
    )


def test_condenser_refuses_a_forced_cold_tube_side():
    streams = _benzene_condenser_streams()
    hx = CondenserHX(latent_heat=394000, force_cold_in_tubes=True, **streams)
    with pytest.raises(ValueError, match="CondenserHX models the hot stream in the tubes"):
        _quiet(hx.design)
