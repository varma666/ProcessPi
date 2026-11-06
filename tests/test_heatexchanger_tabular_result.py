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
    # Stream pressures are absolute by default; datasheet pressure is gauge.
    assert pressure["tube_side"] == 0.0
    assert pressure["shell_side"] == 101325.0 / 9.80665

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



def test_datasheet_converts_processpi_pressure_and_length_objects():
    from processpi.equipment.heatexchangers.datasheet import build_datasheet
    from processpi.units.length import Length
    from processpi.units.pressure import Pressure

    data = {
        "shell_dp_limit": Pressure(1, "bar"),
        "shell_dp": Pressure(0.2, "bar"),
        "tube_dp_limit": Pressure(0.5, "bar"),
        "tube_dp": Pressure(0.1, "bar"),
        "shell_diameter": Length(0.4115, "m"),
        "tube_od": Length(19.05, "mm"),
        "tube_id": Length(14.28, "mm"),
        "tube_length": Length(5, "m"),
        "tube_pitch": Length(23.81, "mm"),
        "tube_count": 176,
    }
    rows = {row["label"]: row for row in build_datasheet(data)}

    dp = rows["Pressure drop, allow./calc."]
    assert dp["shell_side"] == (100000 / 9.80665, 20000 / 9.80665)
    assert dp["tube_side"] == (50000 / 9.80665, 10000 / 9.80665)

    shell = rows["Shell ID / OD / thickness"]
    assert shell["shell_side"] == 411.5

    tube = rows["Tube No. / OD / average thickness / length / pitch"]
    assert tube["shell_side"] == 176
    assert "OD 19.05" in tube["tube_side"]
    assert "length 5000" in tube["tube_side"]


def test_datasheet_pressure_can_be_explicitly_declared_gauge():
    from processpi.equipment.heatexchangers.datasheet import build_datasheet

    data = {
        "pressure_basis": "gauge",
        "stream_properties": {
            "hot": {"name": "Hot", "pressure": 200000},
            "cold": {"name": "Cold", "pressure": 100000},
        },
    }
    rows = {row["label"]: row for row in build_datasheet(data)}
    pressure = rows["Pressure"]
    assert pressure["tube_side"] == 200000 / 9.80665
    assert pressure["shell_side"] == 100000 / 9.80665


def test_datasheet_uses_specs_fallbacks_for_limits_and_geometry():
    from processpi.equipment.heatexchangers.datasheet import build_datasheet

    data = {
        "specs": {
            "shell_dp": 100000,
            "tube_dp": 50000,
            "shell_passes": 1,
            "tube_passes": 2,
            "tube_count": 88,
        },
    }
    rows = {row["label"]: row for row in build_datasheet(data)}
    assert rows["Pressure drop, allow./calc."]["shell_side"][0] == 100000 / 9.80665
    assert rows["Number passes per shell"]["shell_side"] == 1
    assert rows["Number passes per shell"]["tube_side"] == 2
    assert rows["Tube No. / OD / average thickness / length / pitch"]["shell_side"] == 88
