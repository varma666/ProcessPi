"""Smaller pipeline bugs.

- Hazen-Williams with any fitting raised "Could not interpret
  friction_factor value: None" (N1).
- Fitting.calculate() raised AttributeError (P17).
- get_k_factor was defined twice; the surviving one's equivalent-length
  fallback named ColebrookWhite without importing it (P21).
- get_roughness silently used the "Other" 0.05 mm for every natural spelling
  of carbon steel (P22).
"""

import contextlib
import io
import math
import warnings

import pytest

from processpi.components import Water
from processpi.pipelines import standards
from processpi.pipelines.engine import PipelineEngine
from processpi.pipelines.fittings import Fitting
from processpi.pipelines.standards import EQUIVALENT_LENGTHS, K_FACTORS, get_k_factor, get_roughness
from processpi.units import Diameter, Length, VolumetricFlowRate

Q = VolumetricFlowRate(50, "m3/h")


def _summary(**specs):
    engine = PipelineEngine().fit(fluid=Water(), flowrate=Q, length=Length(100, "m"),
                                  diameter=Diameter(0.10226, "m"), **specs)
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.run().results["summary"]


# ----------------------------------------------------------------------------
# N1
# ----------------------------------------------------------------------------

def test_hazen_williams_with_fittings_runs_and_counts_them():
    bare = _summary(method="hazen_williams")
    fitted = _summary(method="hazen_williams", fittings=[Fitting("standard_elbow_90_deg", quantity=2)])
    darcy = _summary(fittings=[Fitting("standard_elbow_90_deg", quantity=2)])
    darcy_bare = _summary()
    minor_hw = fitted["total_pressure_drop_Pa"] - bare["total_pressure_drop_Pa"]
    minor_dw = darcy["total_pressure_drop_Pa"] - darcy_bare["total_pressure_drop_Pa"]
    # The fittings cost the same on both paths: Darcy-Weisbach on Le with the
    # Colebrook-White f of the same pipe.
    assert minor_hw > 0
    assert minor_hw == pytest.approx(minor_dw, rel=1e-9)


# ----------------------------------------------------------------------------
# P17
# ----------------------------------------------------------------------------

def test_fitting_calculate_reports_le_over_d_and_the_length():
    out = Fitting("standard_elbow_90_deg", diameter=Diameter(4, "in")).calculate()
    le_d = EQUIVALENT_LENGTHS["standard_elbow_90_deg"]
    assert out["le_over_d"] == le_d
    assert out["equivalent_length_m"] == pytest.approx(le_d * 0.1016)
    assert out["k_factor"] == K_FACTORS["standard_elbow_90_deg"]


def test_fitting_calculate_without_a_diameter():
    out = Fitting("standard_elbow_90_deg").calculate()
    assert out["equivalent_length_m"] is None
    assert out["le_over_d"] == EQUIVALENT_LENGTHS["standard_elbow_90_deg"]


# ----------------------------------------------------------------------------
# P21
# ----------------------------------------------------------------------------

def test_one_get_k_factor():
    import inspect
    source = inspect.getsource(standards)
    assert source.count("def get_k_factor(") == 1


def test_k_from_equivalent_length_uses_colebrook(monkeypatch):
    """K = f Le/D when the fitting has no tabulated K; the fallback used to
    raise NameError."""
    monkeypatch.delitem(K_FACTORS, "globe_valve")
    re, rel, d = 1.0e5, 4.5e-4, 0.1
    k = get_k_factor("globe_valve", re, rel, d)
    # Colebrook-White solved independently by fixed-point iteration.
    f = 0.02
    for _ in range(100):
        f = (-2.0 * math.log10(rel / 3.7 + 2.51 / (re * math.sqrt(f)))) ** -2
    assert k == pytest.approx(f * EQUIVALENT_LENGTHS["globe_valve"], rel=1e-3)


def test_tabulated_k_is_returned_as_is():
    assert get_k_factor("globe_valve") == K_FACTORS["globe_valve"]


# ----------------------------------------------------------------------------
# P22
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("name, key", [
    ("CS", "CS"), ("cs", "CS"), ("Carbon Steel", "CS"), ("carbon-steel", "CS"),
    ("Steel", "CS"), ("stainless steel", "SS"), ("SS", "SS"), ("pvc", "PVC"),
])
def test_roughness_spellings(name, key):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert get_roughness(name).value == standards.ROUGHNESS[key]


@pytest.mark.parametrize("name", ["unobtainium", None])
def test_unknown_material_warns_and_uses_other(name):
    with pytest.warns(UserWarning, match="No roughness for pipe material"):
        assert get_roughness(name).value == standards.ROUGHNESS["Other"]
