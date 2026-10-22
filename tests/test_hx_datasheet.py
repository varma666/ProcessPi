"""Tests for the reference-style heat-exchanger datasheet and exports."""
import pytest

from processpi.equipment.heatexchangers.datasheet import build_datasheet


def test_datasheet_includes_reference_rows_and_leaves_unknowns_blank():
    rows = build_datasheet({
        "hx_type": "shell_and_tube",
        "status": "HYDRAULIC_LIMITED",
        "Q": 1000.0,
        "U_calculated": 250.0,
        "tube_count": 50,
        "tube_length": 4.0,
        "shell_passes": 1,
        "tube_passes": 2,
        "specs": {"shell_diameter": 0.5, "baffle_spacing": 0.15},
    })
    by_number = {row["row"]: row for row in rows}
    assert 10 in by_number and 31 in by_number and 34 in by_number and 57 in by_number
    assert by_number[30]["shell_side"] == pytest.approx(859.8452279)
    assert by_number[31]["shell_side"] == 250.0
    assert by_number[36]["shell_side"] == 1
    assert by_number[36]["tube_side"] == 2
    assert by_number[41]["shell_side"] == 50
    assert by_number[41]["tube_side"] == 4.0
    assert by_number[19]["shell_side"] is None


def test_datasheet_contains_side_columns_for_all_rows():
    rows = build_datasheet({"specs": {}})
    assert len(rows) == 21 + 24
    assert all({"row", "label", "unit", "shell_side", "tube_side"} <= set(row) for row in rows)
