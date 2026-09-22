"""Regression tests for the ASME B36.10M / B36.19M pipe schedule table.

The wall thicknesses had slipped one place along the schedule sequence for
NPS 8 and larger, so a named schedule returned the thickness of the next
heavier one and the bore was too small. Pressure drop goes as D^-5, so the
error did not stay small.

Reference values are Table 1 of ASME B36.10M-2015 (carbon and alloy steel) and
Table 1 of ASME B36.19M-2004 (R2015) (stainless), both read in millimetres.
"""

import pytest

from processpi.pipelines.standards import (
    PIPE_SCHEDULES,
    STANDARD_SIZES,
    get_internal_diameter,
    get_thickness,
)
from processpi.units import Diameter


def _thickness_mm(nps_in, schedule):
    return get_thickness(Diameter(nps_in, "in"), schedule).value * 1000


def _bore_mm(nps_in, schedule):
    return get_internal_diameter(Diameter(nps_in, "in"), schedule).value * 1000


# ASME B36.10M-2015 Table 1, NPS 8, outside diameter 219.1 mm.
NPS_8_B3610M = {
    "S5": 2.77, "S10": 3.76, "S20": 6.35, "S30": 7.04, "S40": 8.18,
    "S60": 10.31, "S80": 12.70, "S100": 15.09, "S120": 18.26, "S140": 20.62,
    "S160": 23.01, "STD": 8.18, "XS": 12.70, "XXS": 22.23,
}

# ASME B36.10M-2015 Table 1, NPS 12, outside diameter 323.8 mm.
NPS_12_B3610M = {
    "S5": 3.96, "S10": 4.57, "S20": 6.35, "S30": 8.38, "S40": 10.31,
    "S60": 14.27, "S80": 17.48, "S100": 21.44, "S120": 25.40, "S140": 28.58,
    "S160": 33.32, "STD": 9.53, "XS": 12.70, "XXS": 25.40,
}


@pytest.mark.parametrize("schedule,thickness", sorted(NPS_8_B3610M.items()))
def test_nps_8_matches_b3610m(schedule, thickness):
    assert _thickness_mm(8, schedule) == pytest.approx(thickness)


@pytest.mark.parametrize("schedule,thickness", sorted(NPS_12_B3610M.items()))
def test_nps_12_matches_b3610m(schedule, thickness):
    assert _thickness_mm(12, schedule) == pytest.approx(thickness)


def test_extra_strong_is_half_an_inch_from_nps_8_up():
    """XS stops tracking schedule 80 at NPS 8; above it XS is 12.70 mm flat."""
    for nps in (8, 10, 12, 14, 16, 18, 20, 24, 30, 36):
        assert _thickness_mm(nps, "XS") == pytest.approx(12.70)


def test_standard_wall_is_three_eighths_of_an_inch_from_nps_12_up():
    """STD stops tracking schedule 40 at NPS 12; above it STD is 9.53 mm flat."""
    for nps in (12, 14, 16, 18, 20, 24, 30, 36):
        assert _thickness_mm(nps, "STD") == pytest.approx(9.53)


def test_nps_12_extra_strong_bore():
    """The bore the hydraulics actually use, for the size that was worst hit."""
    assert _bore_mm(12, "XS") == pytest.approx(323.8 - 2 * 12.70)


@pytest.mark.parametrize(
    "nps,schedule,thickness",
    [
        # B36.19M Table 1 departs from B36.10M in exactly these places.
        (10, "80S", 12.70),   # B36.10M schedule 80 is 15.09 mm
        (12, "80S", 12.70),   # B36.10M schedule 80 is 17.48 mm
        (12, "40S", 9.53),    # B36.10M schedule 40 is 10.31 mm
        (14, "10S", 4.78),    # B36.10M schedule 10 is 6.35 mm
        (16, "10S", 4.78),
        (18, "10S", 4.78),
        (20, "10S", 5.54),
        (22, "10S", 5.54),
    ],
)
def test_stainless_schedules_follow_b3619m(nps, schedule, thickness):
    assert _thickness_mm(nps, schedule) == pytest.approx(thickness)


def test_wall_thickness_increases_with_schedule_number():
    """The defect that started this: a column holding its neighbour's value."""
    sequence = ("S5", "S10", "S20", "S30", "S40", "S60", "S80",
                "S100", "S120", "S140", "S160")
    for nps, schedules in PIPE_SCHEDULES.items():
        listed = [
            (name, schedules[name][0].value)
            for name in sequence
            if name in schedules
        ]
        for (lower, t_lower), (upper, t_upper) in zip(listed, listed[1:]):
            assert t_upper > t_lower, f"{nps}: {lower} {t_lower} -> {upper} {t_upper}"


def test_table_guard_runs_clean():
    """The import-time guard that keeps a shifted column from landing again."""
    from processpi.pipelines.standards import _check_pipe_schedule_table

    _check_pipe_schedule_table()


def test_every_bore_is_positive():
    for nps, schedules in PIPE_SCHEDULES.items():
        for schedule, (thickness, od, bore) in schedules.items():
            assert bore.value > 0, f"NPS {nps} {schedule}"
            assert bore.value == pytest.approx(od.value - 2 * thickness.value)


def test_standard_sizes_are_all_in_the_schedule_table():
    """NPS 50 is not an ASME B36.10M size; every listed size must be lookupable."""
    assert all(size in PIPE_SCHEDULES for size in STANDARD_SIZES)
    assert Diameter(50, "in") not in PIPE_SCHEDULES
    assert Diameter(1.25, "in") in STANDARD_SIZES
