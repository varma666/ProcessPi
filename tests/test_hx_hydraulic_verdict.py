"""The hydraulic verdict and the velocity insights use one set of limits.

The summary judged each side's velocity twice. The hydraulic verdict
(`hydraulic_feasible`, printed as "Hydraulic Performance") compares it with
the band `_get_velocity_limits` returns for that side, phase and service. The
engineering insights in `_finalize_results` used fixed cut-offs whatever the
phase: tube 0.3/1.0/3.0 m/s, shell 0.2/0.5/2.0 m/s. So the docs benzene
condenser (docs/examples/equipment/heatexchanger/benzene_condenser.md), whose
benzene vapour crosses the shell at 29.07 m/s, inside the 10-30 m/s band the
verdict passed, printed "Hydraulic Performance: PASS" next to "Shell-side
velocity very high. Potential shell-side erosion risk.". The docs n-propanol
condenser had the opposite case: its 2.27 m/s cooling water failed the
verdict against the 0.6-2.0 m/s condenser band while the insight said "within
recommended range".

The insights now read the band the verdict used, and the results report it
(`tube_velocity_band`, `shell_velocity_band`). An erosion line is written
exactly when a velocity is above its band, which is exactly when the verdict
fails on that side.

The vapour bands are Sinnott's typical design velocities (Coulson &
Richardson's Chemical Engineering Vol. 6, Sec. 12.4 "Shell and tube fluid
velocities": vapours at atmospheric pressure 10 to 30 m/s; the wording
fetched is a lecture-notes copy of that section). No limit is changed here.
"""

import contextlib
import io
import math

import pytest

from processpi.components import Benzene, OrganicLiquid, Water
from processpi.equipment.heatexchangers import HeatExchangerEngine
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams import MaterialStream
from processpi.units import (
    HeatTransferCoefficient,
    Length,
    MassFlowRate,
    Pressure,
    Temperature,
)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _benzene_condenser():
    """The docs benzene condenser: design, Bell-Delaware, vapour in the shell."""
    hx = HeatExchangerEngine(method="bell_delaware")
    hx.fit(
        hx_type="condenser",
        hot_in=MaterialStream("benzene_vapor_in", component=Benzene(), phase="vapor",
                              temperature=Temperature(95, "C"), pressure=Pressure(1.2, "bar"),
                              mass_flow=MassFlowRate(12000, "kg/h")),
        hot_out=MaterialStream("benzene_liquid_out", component=Benzene(), phase="liquid",
                               temperature=Temperature(95, "C")),
        cold_in=MaterialStream("cw_in", component=Water(), phase="liquid",
                               temperature=Temperature(30, "C"), pressure=Pressure(1, "bar"),
                               mass_flow=MassFlowRate(50000, "kg/h")),
        cold_out=MaterialStream("cw_out", component=Water()),
        latent_heat=394000,
        shell_dp=Pressure(0.5, "bar"),
        tube_dp=Pressure(0.5, "bar"),
        orientation="horizontal",
        mode="design",
    )
    return _quiet(hx.run).data


def _npropanol_condenser():
    """The docs n-propanol condenser: rating of a fixed 766-tube geometry."""
    hx = HeatExchangerEngine(method="bell_delaware")
    hx.fit(
        hx_type="condenser",
        hot_in=MaterialStream("npropanol_vapor_in", component=OrganicLiquid(), phase="vapor",
                              temperature=Temperature(118, "C"), pressure=Pressure(2.03, "bar"),
                              mass_flow=MassFlowRate(60000, "lb/h")),
        hot_out=MaterialStream("npropanol_liquid_out", component=OrganicLiquid(), phase="liquid",
                               temperature=Temperature(118, "C")),
        cold_in=MaterialStream("cooling_water_in", component=Water(), phase="liquid",
                               temperature=Temperature(29.4, "C"), pressure=Pressure(1, "bar")),
        cold_out=MaterialStream("cooling_water_out", component=Water(),
                                temperature=Temperature(40.6, "C")),
        latent_heat=663000,
        orientation="horizontal",
        shell_passes=1,
        tube_passes=4,
        tube_length=Length(8, "ft").to("m").value,
        tube_od=Length(0.75, "in").to("m").value,
        tube_id=Length(0.70, "in").to("m").value,
        tube_count=766,
        shell_diameter=Length(31, "in").to("m").value,
        tube_pitch=Length(1.0625, "in").to("m").value,
        tube_layout="triangular",
        shell_dp=Pressure(2, "psi"),
        tube_dp=Pressure(10, "psi"),
        assumed_U=HeatTransferCoefficient(568, "W/m2K"),
        mode="rate",
    )
    return _quiet(hx.run).data


def _benzene_cooler():
    """The docs benzene cooler: liquid on both sides."""
    hx = HeatExchangerEngine()
    hx.fit(
        hot_in=MaterialStream("hot_in", component=Benzene(), temperature=Temperature(90, "C"),
                              mass_flow=MassFlowRate(21000, "kg/h")),
        hot_out=MaterialStream("hot_out", component=Benzene(), temperature=Temperature(30, "C")),
        cold_in=MaterialStream("cold_in", component=Water(), temperature=Temperature(15, "C"),
                               mass_flow=MassFlowRate(60500, "kg/h")),
        cold_out=MaterialStream("cold_out", component=Water()),
        assumed_U=HeatTransferCoefficient(575, "W/m2K"),
        shell_dp=Pressure(1, "bar"),
        tube_dp=Pressure(1, "bar"),
        mode="design",
    )
    return _quiet(hx.run).data


CASES = {
    "benzene_condenser": _benzene_condenser,
    "npropanol_condenser": _npropanol_condenser,
    "benzene_cooler": _benzene_cooler,
}


def _velocity_line(results, side):
    lines = [
        line for line in results["engineering_insights"]
        if line.startswith(f"{side}-side velocity")
    ]
    assert len(lines) == 1, results["engineering_insights"]
    return lines[0]


def test_vapour_shell_inside_its_band_is_not_an_erosion_risk():
    results = _benzene_condenser()
    v_shell = results["shell_velocity"].to("m/s").value

    # Benzene vapour at 1.2 bar: Sinnott's atmospheric-pressure vapour band.
    assert results["shell_velocity_band"] == (10.0, 30.0)
    # The docs page prints Shell Velocity 25.587 m/s. It was 29.066 m/s
    # (approx(29.07, abs=0.01)) while design() sized this condenser as a
    # heater, on the 1.0-2.5 m/s liquid band for its cooling-water tubes in
    # place of the 0.6-2.0 m/s condenser band
    # (tests/test_hx_design_phase_change_service.py).
    assert 10.0 <= v_shell <= 30.0
    assert v_shell == pytest.approx(25.59, abs=0.01)
    assert results["feasibility_summary"]["hydraulic_ok"] is True

    # Before: "Shell-side velocity very high. Potential shell-side erosion risk."
    line = _velocity_line(results, "Shell")
    assert "erosion" not in line
    assert "within the 10-30 m/s range" in line
    assert not any("erosion" in s for s in results["engineering_insights"])


def test_coolant_above_its_band_is_reported_with_the_failed_verdict():
    results = _npropanol_condenser()
    v_tube = results["tube_velocity"].to("m/s").value

    # Hand calc of the tube velocity. Cooling water flow from the latent
    # duty: Q = 7.55987 kg/s x 663 kJ/kg = 5012.19 kW, so
    # m_cw = Q / (cp dT) = 5012.19 / (4.181 x 11.2) = 107.04 kg/s
    # (the page's FLOW_BALANCE_INFO line prints 107.035 kg/s).
    # Flow area: 766 tubes / 4 passes = 191.5 tubes of 0.70 in (0.01778 m)
    # bore, 191.5 x pi/4 x 0.01778^2 = 0.047547 m2.
    # Water near its 35 C mean, rho ~ 994 kg/m3:
    # v = 107.04 / 994 / 0.047547 = 2.265 m/s.
    m_cw = 7.55987 * 663.0 / (4.181 * 11.2)
    flow_area = 766 / 4 * math.pi / 4 * 0.01778**2
    assert v_tube == pytest.approx(m_cw / 994.0 / flow_area, rel=0.01)

    # Condenser service, coolant side: the 0.6-2.0 m/s band of
    # `_get_velocity_limits`, so 2.27 m/s fails the verdict.
    assert results["tube_velocity_band"] == (0.6, 2.0)
    assert v_tube > 2.0
    assert results["feasibility_summary"]["hydraulic_ok"] is False

    # Before: "Tube-side velocity within recommended range." (old cut-off 3.0)
    line = _velocity_line(results, "Tube")
    assert "above the 0.6-2 m/s range" in line
    assert "erosion" in line

    # n-propanol vapour at 2.03 bar (16.60 m/s): inside 10-30 m/s. Before:
    # "Shell-side velocity very high. Potential shell-side erosion risk."
    line = _velocity_line(results, "Shell")
    assert results["shell_velocity_band"] == (10.0, 30.0)
    assert "within the 10-30 m/s range" in line
    assert "erosion" not in line


@pytest.mark.parametrize("case", sorted(CASES))
def test_erosion_line_if_and_only_if_the_verdict_fails_that_side(case):
    results = CASES[case]()
    above_any = False
    for side, key in (("Tube", "tube"), ("Shell", "shell")):
        vmin, vmax = results[f"{key}_velocity_band"]
        velocity = results[f"{key}_velocity"].to("m/s").value
        line = _velocity_line(results, side)
        assert ("erosion" in line) == (velocity > vmax)
        assert ("below" in line) == (velocity < vmin)
        above_any |= not (vmin <= velocity <= vmax)
    assert results["feasibility_summary"]["hydraulic_ok"] is (not above_any)


def test_velocity_insight_boundaries_match_the_verdict():
    # The verdict passes vmin <= v <= vmax, so the band edges are "within".
    band = (10.0, 30.0)
    assert "within" in ShellAndTubeHX._velocity_insight("Shell", 30.0, band)
    assert "within" in ShellAndTubeHX._velocity_insight("Shell", 10.0, band)
    above = ShellAndTubeHX._velocity_insight("Shell", 30.01, band)
    assert "above the 10-30 m/s range" in above and "shell-side erosion" in above
    below = ShellAndTubeHX._velocity_insight("Tube", 0.5, (0.6, 2.0))
    assert "below the 0.6-2 m/s range" in below and "erosion" not in below
