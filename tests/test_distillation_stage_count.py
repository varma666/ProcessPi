"""DistillationStageCount McCabe-Thiele mode: the stepping must stop at xB."""

import pytest

from processpi.calculations.mass_transfer import DistillationStageCount
from processpi.equipment.distillation import mccabe_thiele


def _alpha_curve(alpha):
    return lambda x: alpha * x / (1 + (alpha - 1) * x)


def test_textbook_case_terminates_with_the_stepped_count():
    # xD 0.95, xB 0.05, zF 0.5, R 2, saturated liquid, alpha 2.5: used to
    # stall at x = 0.0637 and return the 300-stage safety cap plus one.
    out = DistillationStageCount(mode="mccabe_thiele", xD=0.95, xB=0.05, zF=0.5, R=2, q=1,
                                 eq_curve=_alpha_curve(2.5)).calculate()
    y_eq, x_eq = mccabe_thiele.constant_alpha_curves(2.5)
    reference = mccabe_thiele.step_stages(0.95, 0.05, 0.5, 1.0, 2.0, y_eq, x_eq)
    assert out["N_theoretical"] == reference["N"] == 11
    assert out["rectifying_stages"] == reference["feed_stage"] - 1
    assert out["rectifying_stages"] + out["stripping_stages"] == out["N_theoretical"]


@pytest.mark.parametrize("alpha,r", [(2.0, 3.0), (3.0, 1.5), (4.0, 1.0)])
def test_matches_the_equipment_stepper(alpha, r):
    out = DistillationStageCount(mode="mccabe_thiele", xD=0.9, xB=0.1, zF=0.45, R=r, q=1,
                                 eq_curve=_alpha_curve(alpha)).calculate()
    y_eq, x_eq = mccabe_thiele.constant_alpha_curves(alpha)
    assert out["N_theoretical"] == mccabe_thiele.step_stages(0.9, 0.1, 0.45, 1.0, r, y_eq, x_eq)["N"]


def test_tabulated_equilibrium_curve():
    xs = [i / 20 for i in range(21)]
    data = [(x, _alpha_curve(2.5)(x)) for x in xs]
    out = DistillationStageCount(mode="mccabe_thiele", xD=0.95, xB=0.05, zF=0.5, R=2, q=1,
                                 eq_curve=data).calculate()
    assert 10 <= out["N_theoretical"] <= 12


def test_below_minimum_reflux_raises_instead_of_returning_the_cap():
    with pytest.raises(ValueError, match="pinch"):
        DistillationStageCount(mode="mccabe_thiele", xD=0.95, xB=0.05, zF=0.5, R=1.0, q=1,
                               eq_curve=_alpha_curve(2.5)).calculate()
