"""Every component file is exported by processpi.components, by its real name.

c4398e9 replaced the dynamic discovery in processpi/components/__init__.py
with an explicit list of imports. The list did not match the files, so
`import processpi` raised ImportError and every test module failed to collect:

    from ._14dioxane import _14Dioxanefrom      (stray "from ")
    from .ethyleneoxide import Ethylenoexide    (class is EthyleneOxide)
    from .methane import Methane                (there is no methane.py)

57 imports named a class with the wrong spelling or capitals, 16 named a file
that does not exist, and the list left out Component (imported by the
pipeline engine), Steam, Gas, Vapor, Oil, OrganicLiquid, InorganicLiquid and
the EthlylAcetate / Ethlylene aliases. `__all__` held 87 names that were never
imported, so `from processpi.components import *` failed as well.

The explicit list is kept; these tests check it against the files, so a
component added, renamed or removed later fails here first.
"""

import importlib
import inspect
from pathlib import Path

import processpi.components as components
from processpi.components.base import Component

COMPONENTS_DIR = Path(components.__file__).parent
NOT_COMPONENT_FILES = {"__init__.py", "base.py", "constants.py"}


def _component_classes_by_module():
    found = {}
    for path in sorted(COMPONENTS_DIR.glob("*.py")):
        if path.name in NOT_COMPONENT_FILES:
            continue
        module = importlib.import_module(f"processpi.components.{path.stem}")
        found[path.stem] = [
            name
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if cls.__module__ == module.__name__ and issubclass(cls, Component)
        ]
    return found


def test_every_component_class_in_the_folder_is_exported():
    missing = [
        f"{module}.{name}"
        for module, names in _component_classes_by_module().items()
        for name in names
        if getattr(components, name, None) is None or name not in components.__all__
    ]
    assert missing == []


def test_every_component_file_defines_a_component_class():
    empty = [module for module, names in _component_classes_by_module().items() if not names]
    assert empty == []


def test_every_name_in_all_resolves_and_appears_once():
    assert [name for name in components.__all__ if not hasattr(components, name)] == []
    assert len(components.__all__) == len(set(components.__all__))


def test_star_import_works():
    namespace = {}
    exec("from processpi.components import *", namespace)
    for name in ("Component", "Water", "Steam", "_14Dioxane", "EthyleneOxide", "OrganicLiquid"):
        assert name in namespace


def test_the_base_class_and_the_old_alias_spellings_are_still_exported():
    assert components.Component is Component
    assert components.Ethlylene is not None
    assert components.EthlylAcetate is not None
