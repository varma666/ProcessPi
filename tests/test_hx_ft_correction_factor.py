"""Regression tests for the LMTD correction factor F of ShellAndTubeHX.

Reference for both closed forms: Bowman, Mueller and Nagle, "Mean Temperature
Difference in Design", Trans. ASME 62 (1940) 283, as tabulated in Perry's
Chemical Engineers' Handbook, 8th ed., Table 11-3 (also Kern, "Process Heat
Transfer", and Kakac and Liu, "Heat Exchangers: Selection, Rating and Thermal
Design").

The expected values below are not a restatement of the implementation. They are
hardcoded numbers that were each cross-checked against one of two independent
routes, both of which are also exercised directly as tests:

* ``_ft_reference_via_ntu`` inverts the 1-2 shell-and-tube P-NTU relation
  numerically and forms F = NTU_counterflow / NTU_actual. It shares no algebra
  with ``_ft_1shell`` and needs no special case at R = 1.
* ``_ft2_reference_via_equivalence`` uses the fact that an N-shell exchanger has
  the same F as a single shell evaluated at the per-shell effectiveness P1, so
  the 2-shell result is checked against ``_ft_1shell`` at P1.
"""

import math

import pytest

from processpi.components import Water
from processpi.equipment.heatexchangers.shell_and_tube import ShellAndTubeHX
from processpi.streams.material import MaterialStream
from processpi.units import MassFlowRate, Pressure, SpecificHeat, Temperature


def _stream(name: str, temp_k: float, m_dot: float) -> MaterialStream:
    return MaterialStream(
        name=name,
        component=Water(),
        temperature=Temperature(temp_k, "K"),
        pressure=Pressure(2, "bar"),
        mass_flow=MassFlowRate(m_dot, "kg/s"),
        specific_heat=SpecificHeat(4200, "J/kgK"),
    )


@pytest.fixture
def hx() -> ShellAndTubeHX:
    """A minimally configured exchanger.

    The correction-factor methods are pure functions of (R, S); construction is
    only needed for the logger that _debug uses, and it costs well under a
    millisecond, so a real instance is used rather than object.__new__.
    """
    return ShellAndTubeHX(_stream("hot", 373.15, 5.0), _stream("cold", 303.15, 5.0))


# Independent reference 1: invert the 1-2 P-NTU relation
#   P = 2 / [1 + R + sqrt(1+R^2) coth(NTU sqrt(1+R^2) / 2)]
# then F = NTU_counterflow / NTU.
def _p_of_ntu(ntu: float, r: float) -> float:
    root = math.sqrt(1.0 + r * r)
    decay = math.exp(-ntu * root)
    return 2.0 / (1.0 + r + root * (1.0 + decay) / (1.0 - decay))


def _ft_reference_via_ntu(r: float, s: float) -> float:
    lo, hi = 1e-12, 1.0
    while _p_of_ntu(hi, r) < s:
        hi *= 2.0
        if hi > 1e6:
            raise ValueError(f"(R={r}, S={s}) is not reachable with one shell pass")
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if _p_of_ntu(mid, r) < s:
            lo = mid
        else:
            hi = mid
    ntu = 0.5 * (lo + hi)
    if abs(r - 1.0) < 1e-12:
        ntu_counterflow = s / (1.0 - s)
    else:
        ntu_counterflow = math.log((1.0 - r * s) / (1.0 - s)) / (1.0 - r)
    return ntu_counterflow / ntu


# Independent reference 2: F for N shells equals F for one shell at the
# per-shell effectiveness P1.
def _ft2_reference_via_equivalence(hx: ShellAndTubeHX, r: float, s: float) -> float:
    if abs(r - 1.0) < 1e-12:
        p1 = s / (2.0 - s)
    else:
        x = math.sqrt((1.0 - r * s) / (1.0 - s))
        p1 = (x - 1.0) / (x - r)
    return hx._ft_1shell(r, p1)


# --- 1 shell pass -----------------------------------------------------------

ONE_SHELL_POINTS = [
    (0.5, 0.30, 0.987281200),
    (0.8, 0.50, 0.876925851),
    (2.0, 0.30, 0.882889213),
    (3.0, 0.20, 0.935046846),
    (0.2, 0.90, 0.398041932),
]


@pytest.mark.parametrize("r, s, expected", ONE_SHELL_POINTS)
def test_ft_1shell_matches_reference_values(hx, r, s, expected):
    assert hx._ft_1shell(r, s) == pytest.approx(expected, abs=1e-6)


@pytest.mark.parametrize("r, s", [(r, s) for r, s, _ in ONE_SHELL_POINTS] + [(1.0, 0.3), (1.0, 0.5)])
def test_ft_1shell_matches_independent_ntu_inversion(hx, r, s):
    assert hx._ft_1shell(r, s) == pytest.approx(_ft_reference_via_ntu(r, s), abs=1e-6)


# --- 2 shell passes ---------------------------------------------------------

TWO_SHELL_POINTS = [
    (0.5, 0.30, 0.996849195),
    (0.5, 0.70, 0.947600843),
    (0.5, 0.90, 0.649184039),
    (2.0, 0.30, 0.973225185),
    (2.0, 0.45, 0.649184039),
    (3.0, 0.30, 0.859629871),
    (0.2, 0.90, 0.935609303),
]


@pytest.mark.parametrize("r, s, expected", TWO_SHELL_POINTS)
def test_ft_2shell_matches_reference_values(hx, r, s, expected):
    # Before the fix this returned 0.0 for every input.
    assert hx._ft_2shell(r, s) == pytest.approx(expected, abs=1e-6)


@pytest.mark.parametrize("r, s", [(r, s) for r, s, _ in TWO_SHELL_POINTS] + [(1.0, 0.5), (1.5, 0.5)])
def test_ft_2shell_matches_shell_equivalence(hx, r, s):
    assert hx._ft_2shell(r, s) == pytest.approx(_ft2_reference_via_equivalence(hx, r, s), abs=1e-6)


# --- R = 1 (balanced duty) --------------------------------------------------

def test_ft_1shell_balanced_duty(hx):
    # Review case: hot 100 to 60 C against cold 30 to 70 C, so R = 1 and
    # S = 40/70. The correct F is 0.5349, not the 0.0 the singularity produced.
    s = 40.0 / 70.0
    assert hx._ft_1shell(1.0, s) == pytest.approx(0.534852, abs=1e-6)
    assert hx._ft_1shell(1.0, s) == pytest.approx(_ft_reference_via_ntu(1.0, s), abs=1e-6)


def test_ft_2shell_balanced_duty(hx):
    s = 40.0 / 70.0
    assert hx._ft_2shell(1.0, s) == pytest.approx(0.920937, abs=1e-6)
    assert hx._ft_2shell(1.0, s) == pytest.approx(_ft2_reference_via_equivalence(hx, 1.0, s), abs=1e-6)


@pytest.mark.parametrize("s", [0.2, 0.3, 0.4, 0.5])
def test_ft_1shell_continuous_across_r_unity(hx, s):
    at_unity = hx._ft_1shell(1.0, s)
    assert at_unity == pytest.approx(hx._ft_1shell(1.0 - 1e-4, s), abs=1e-4)
    assert at_unity == pytest.approx(hx._ft_1shell(1.0 + 1e-4, s), abs=1e-4)


@pytest.mark.parametrize("s", [0.2, 0.3, 0.5, 40.0 / 70.0])
def test_ft_2shell_continuous_across_r_unity(hx, s):
    at_unity = hx._ft_2shell(1.0, s)
    assert at_unity == pytest.approx(hx._ft_2shell(1.0 - 1e-4, s), abs=1e-4)
    assert at_unity == pytest.approx(hx._ft_2shell(1.0 + 1e-4, s), abs=1e-4)


def test_calculate_ft_dispatches_balanced_duty_case(hx):
    # Hot 100 to 60 C, cold 30 to 70 C, expressed in kelvin.
    hot = {"t_k": 373.15}
    cold = {"t_k": 303.15}
    th_out, tc_out = 333.15, 343.15
    assert hx._calculate_ft(hot, cold, th_out, tc_out, 1, 2) == pytest.approx(0.534852, abs=1e-6)
    assert hx._calculate_ft(hot, cold, th_out, tc_out, 2, 4) == pytest.approx(0.920937, abs=1e-6)


# --- general properties -----------------------------------------------------

@pytest.mark.parametrize("r, s", [(r, s) for r, s, _ in ONE_SHELL_POINTS + TWO_SHELL_POINTS]
                         + [(1.0, 0.3), (1.0, 0.5), (1.0, 40.0 / 70.0)])
def test_ft_stays_within_unit_interval(hx, r, s):
    for ft in (hx._ft_1shell(r, s), hx._ft_2shell(r, s)):
        assert 0.0 <= ft <= 1.0
    assert hx._ft_2shell(r, s) > 0.0


@pytest.mark.parametrize("r, s", [(r, s) for r, s, _ in ONE_SHELL_POINTS + TWO_SHELL_POINTS]
                         + [(1.0, 0.3), (1.0, 0.5), (1.0, 40.0 / 70.0)])
def test_ft_2shell_never_below_ft_1shell(hx, r, s):
    # Splitting the same duty over two shell passes always moves the unit closer
    # to true counterflow.
    assert hx._ft_2shell(r, s) >= hx._ft_1shell(r, s) - 1e-12


@pytest.mark.parametrize("r, s", [(1.0, 0.90), (2.0, 0.60), (0.5, 0.99), (3.0, 0.50), (1.0, 0.75)])
def test_infeasible_configurations_return_zero(hx, r, s):
    # A temperature cross makes F genuinely undefined. _adjust_passes relies on
    # 0.0 here to move on to the next candidate, so it must not raise.
    assert hx._ft_1shell(r, s) == 0.0
    assert hx._ft_2shell(r, s) == 0.0


@pytest.mark.parametrize("method", ["_ft_1shell", "_ft_2shell"])
def test_programming_errors_are_not_swallowed(hx, method):
    # The handler is narrowed to math errors, so a genuine bug inside the
    # expression must surface instead of being reported as F = 0.0.
    def boom(*args, **kwargs):
        raise TypeError("injected defect")

    hx._safe_log_ratio = boom
    with pytest.raises(TypeError):
        getattr(hx, method)(2.0, 0.3)
