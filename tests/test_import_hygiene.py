"""`import processpi` loads only what it needs, and the console script exists.

CoolProp (about 4.6 s to import), matplotlib.pyplot and networkx were imported
at `import processpi` even when nothing used them; the import took 5-9 s.
The `processpi` console script pointed at `processpi.cli`, which did not
exist (cli.py sat at the repository root), and setup.py's entry_points are
ignored once pyproject.toml has a [project] table.
"""

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _modules_after(statement):
    code = (
        "import sys\n"
        f"{statement}\n"
        "print(','.join(m for m in ('CoolProp', 'matplotlib', 'networkx') if m in sys.modules))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         cwd=ROOT, env={"PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"},
                         check=True)
    lines = out.stdout.splitlines()
    return lines[-1].strip() if lines else ""


def test_import_processpi_loads_no_heavy_optional_modules():
    assert _modules_after("import processpi") == ""


def test_steam_loads_coolprop_when_used():
    loaded = _modules_after(
        "from processpi.components import Steam\n"
        "from processpi.units import Temperature, Pressure\n"
        "Steam(temperature=Temperature(200, 'C'), pressure=Pressure(5, 'bar')).density()"
    )
    assert "CoolProp" in loaded.split(",")


def test_steam_properties_still_come_from_coolprop():
    from processpi.components import Steam
    from processpi.units import Pressure, Temperature
    import CoolProp.CoolProp as CP

    steam = Steam(temperature=Temperature(200, "C"), pressure=Pressure(5, "bar"))
    assert steam.density().value == pytest.approx(CP.PropsSI("D", "T", 473.15, "P", 5e5, "Water"))


def test_console_script_target_exists_and_is_declared():
    from processpi import cli

    assert callable(cli.main)
    text = (ROOT / "pyproject.toml").read_text()
    assert '[project.scripts]' in text
    assert 'processpi = "processpi.cli:main"' in text
