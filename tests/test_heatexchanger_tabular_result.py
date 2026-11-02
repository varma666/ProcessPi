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

    assert "Ref. No." not in table
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

    assert "| Ref. No. |" not in table
    assert "|---" in table


def test_result_rows_preserves_structured_output():
    rows = _sample_rows()
    result = HeatExchangerResults({})

    with patch(
        "processpi.equipment.heatexchangers.engine.build_datasheet",
        return_value=rows,
    ):
        assert result.result_rows() == rows



def test_datasheet_uses_calculated_energy_balance_outlet_temperatures():
    from processpi.equipment.heatexchangers.datasheet import build_datasheet

    data = {
        "tube_side": "hot",
        "hot_in": None,
        "cold_in": None,
        "hot_out_temperature": 303.15,
        "cold_out_temperature": 318.15,
        "stream_properties": {
            "hot": {"name": "Hot fluid", "temperature": (363.15, None), "pressure": 101325.0},
            "cold": {"name": "Cooling water", "temperature": (288.15, None), "pressure": 202650.0},
        },
        "shell_dp_limit": 98066.5,
        "tube_dp_limit": 49033.25,
        "shell_dp": 19613.3,
        "tube_dp": 9806.65,
    }

    rows = {row["label"]: row for row in build_datasheet(data)}
    temperature = rows["Temperature (In/Out)"]
    assert temperature["tube_side"] == (363.15, 303.15)
    assert temperature["shell_side"] == (288.15, 318.15)

    pressure = rows["Pressure"]
    assert pressure["tube_side"] == 101325.0 / 9.80665
    assert pressure["shell_side"] == 202650.0 / 9.80665

    pressure_drop = rows["Pressure drop, allow./calc."]
    assert pressure_drop["shell_side"] == (98066.5 / 9.80665, 19613.3 / 9.80665)
    assert pressure_drop["tube_side"] == (49033.25 / 9.80665, 9806.65 / 9.80665)



def test_datasheet_reports_tube_geometry_and_converts_shell_and_baffle_lengths():
    from processpi.equipment.heatexchangers.datasheet import build_datasheet

    data = {
        "tube_count": 176,
        "tube_od": 0.01905,
        "tube_id": 0.01428,
        "tube_length": 5.0,
        "tube_pitch": 0.02381,
        "shell_diameter": 0.4115,
        "baffle_spacing": 0.1646,
        "baffle_cut": 0.25,
        "geometry": {
            "tube_od": 0.01905,
            "tube_id": 0.01428,
            "tube_length": 5.0,
            "tube_pitch": 0.02381,
            "shell_diameter": 0.4115,
            "baffle_spacing": 0.1646,
        },
    }
    rows = {row["label"]: row for row in build_datasheet(data)}

    tube = rows["Tube No. / OD / average thickness / length / pitch"]
    assert tube["shell_side"] == 176
    assert "OD 19.05" in tube["tube_side"]
    assert "wall 2.39" in tube["tube_side"]
    assert "length 5000" in tube["tube_side"]
    assert "pitch 23.81" in tube["tube_side"]

    shell = rows["Shell ID / OD / thickness"]
    assert shell["shell_side"] == 411.5

    baffle = rows["Baffle crossing / type / cut / spacing"]
    assert "cut 25%" in baffle["shell_side"]
    assert "spacing 164.6 mm" in baffle["shell_side"]
    assert baffle["tube_side"] is None

    longitudinal = rows["Baffle-long / seal type / inlet"]
    assert longitudinal["shell_side"] is None
    assert longitudinal["tube_side"] is None
