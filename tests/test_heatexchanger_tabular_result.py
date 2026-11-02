from unittest.mock import patch

from processpi.equipment.heatexchangers.engine import HeatExchangerResults


def _sample_rows():
    return [
        {
            "row": 10,
            "label": "Fluid allocation",
            "unit": "",
            "shell_side": "Cold",
            "tube_side": "Hot",
        },
        {
            "row": 17,
            "label": "Temperature (In/Out)",
            "unit": "°C",
            "shell_side": "25 / 35",
            "tube_side": "120 / 80",
        },
    ]


def test_result_returns_reference_style_table():
    result = HeatExchangerResults({})

    with patch(
        "processpi.equipment.heatexchangers.engine.build_datasheet",
        return_value=_sample_rows(),
    ):
        table = result.result()

    assert "Ref. No." in table
    assert "Description" in table
    assert "Shell Side" in table
    assert "Tube Side" in table
    assert "Temperature (In/Out)" in table
    assert "120 / 80" in table


def test_result_supports_github_table_format():
    result = HeatExchangerResults({})

    with patch(
        "processpi.equipment.heatexchangers.engine.build_datasheet",
        return_value=_sample_rows(),
    ):
        table = result.result(tablefmt="github")

    assert "| Ref. No. |" in table
    assert "|---" in table


def test_result_rows_preserves_structured_output():
    rows = _sample_rows()
    result = HeatExchangerResults({})

    with patch(
        "processpi.equipment.heatexchangers.engine.build_datasheet",
        return_value=rows,
    ):
        assert result.result_rows() == rows
