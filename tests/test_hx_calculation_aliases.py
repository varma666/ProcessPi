"""The duplicated heat exchanger calculations are one implementation.

`calculations/heat_transfer/heat_exchanger.py` used to be a second copy of
six calculations in `hx_kern.py`, under other names and keywords. The
`hx_kern` classes are kept; the old names now map their keywords onto them
and raise a DeprecationWarning:

    SensibleHeatDuty       -> SensibleDuty
    LatentHeatDuty         -> LatentDuty
    ReynoldsFromProperties -> Reynolds
    KernNusselt            -> DittusBoelter (same 0.023 Re^0.8 Pr^n formula)
    ConvectiveCoefficient  -> ConvectiveH
    DarcyPressureDrop      -> DarcyDrop

The parity and hand-calculation tests also pass on master, where the two
copies were separate code with the same formulas; they guard that the
consolidation changed no number. The deprecation tests are new behaviour.
"""

import warnings

import pytest

from processpi.calculations.heat_transfer import (
    ConvectiveCoefficient,
    ConvectiveH,
    DarcyDrop,
    DarcyPressureDrop,
    DittusBoelter,
    KernNusselt,
    LatentDuty,
    LatentHeatDuty,
    Reynolds,
    ReynoldsFromProperties,
    SensibleDuty,
    SensibleHeatDuty,
)
from processpi.units import (
    Density,
    Diameter,
    HeatTransferCoefficient,
    Length,
    MassFlowRate,
    SpecificHeat,
    Temperature,
    Velocity,
    Viscosity,
)

# (old class, old keywords, canonical class, canonical keywords)
PAIRS = [
    pytest.param(
        SensibleHeatDuty,
        {"mass_flow_rate": 2.0, "specific_heat": 4200.0, "t_in": 360.0, "t_out": 330.0},
        SensibleDuty,
        {"m_dot": 2.0, "cp": 4200.0, "t_in": 360.0, "t_out": 330.0},
        id="sensible-floats",
    ),
    pytest.param(
        SensibleHeatDuty,
        {
            "mass_flow_rate": MassFlowRate(10, "kg/s"),
            "specific_heat": SpecificHeat(4180, "J/kgK"),
            "t_in": Temperature(80, "C"),
            "t_out": Temperature(60, "C"),
        },
        SensibleDuty,
        {
            "m_dot": MassFlowRate(10, "kg/s"),
            "cp": SpecificHeat(4180, "J/kgK"),
            "t_in": Temperature(80, "C"),
            "t_out": Temperature(60, "C"),
        },
        id="sensible-units",
    ),
    pytest.param(
        LatentHeatDuty,
        {"mass_flow_rate": 0.5, "latent_heat": 2.257e6},
        LatentDuty,
        {"m_dot": 0.5, "latent_heat": 2.257e6},
        id="latent",
    ),
    pytest.param(
        ReynoldsFromProperties,
        {"density": 1000.0, "velocity": 1.5, "diameter": 0.02, "viscosity": 1e-3},
        Reynolds,
        {"density": 1000.0, "velocity": 1.5, "diameter": 0.02, "viscosity": 1e-3},
        id="reynolds-floats",
    ),
    pytest.param(
        ReynoldsFromProperties,
        {
            "density": Density(998, "kg/m3"),
            "velocity": Velocity(1.2, "m/s"),
            "diameter": Diameter(25, "mm"),
            "viscosity": Viscosity(0.89, "cP"),
        },
        Reynolds,
        {
            "density": Density(998, "kg/m3"),
            "velocity": Velocity(1.2, "m/s"),
            "diameter": Diameter(25, "mm"),
            "viscosity": Viscosity(0.89, "cP"),
        },
        id="reynolds-units",
    ),
    pytest.param(
        KernNusselt,
        {"reynolds": 1e4, "prandtl": 2.0},
        DittusBoelter,
        {"reynolds": 1e4, "prandtl": 2.0},
        id="nusselt-default-n",
    ),
    pytest.param(
        KernNusselt,
        {"reynolds": 1e4, "prandtl": 2.0, "n": 0.3},
        DittusBoelter,
        {"reynolds": 1e4, "prandtl": 2.0, "n": 0.3},
        id="nusselt-n-0.3",
    ),
    pytest.param(
        ConvectiveCoefficient,
        {"nusselt": 100.0, "thermal_conductivity": 0.6, "characteristic_diameter": 0.02},
        ConvectiveH,
        {"nusselt": 100.0, "k": 0.6, "diameter": 0.02},
        id="convective",
    ),
    pytest.param(
        DarcyPressureDrop,
        {"friction_factor": 0.02, "length": 10.0, "diameter": 0.05, "density": 1000.0, "velocity": 2.0},
        DarcyDrop,
        {"f": 0.02, "length": 10.0, "diameter": 0.05, "density": 1000.0, "velocity": 2.0},
        id="darcy-floats",
    ),
    pytest.param(
        DarcyPressureDrop,
        {
            "friction_factor": 0.02,
            "length": Length(10, "m"),
            "diameter": Diameter(50, "mm"),
            "density": Density(1000, "kg/m3"),
            "velocity": Velocity(2, "m/s"),
        },
        DarcyDrop,
        {
            "f": 0.02,
            "length": Length(10, "m"),
            "diameter": Diameter(50, "mm"),
            "density": Density(1000, "kg/m3"),
            "velocity": Velocity(2, "m/s"),
        },
        id="darcy-units",
    ),
]


def _old(cls, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return cls(**kwargs)


def _as_tuple(result):
    """(type, number, units) so a result compares exactly, units and all."""
    if hasattr(result, "value") and hasattr(result, "units"):
        return type(result), result.value, result.units
    return type(result), result, None


@pytest.mark.parametrize("old_cls, old_kwargs, new_cls, new_kwargs", PAIRS)
def test_old_name_gives_exactly_the_canonical_result(old_cls, old_kwargs, new_cls, new_kwargs):
    old = _old(old_cls, **old_kwargs).calculate()
    new = new_cls(**new_kwargs).calculate()
    assert _as_tuple(old) == _as_tuple(new)


@pytest.mark.parametrize("old_cls, old_kwargs, new_cls, new_kwargs", PAIRS)
def test_old_name_keeps_its_inputs_and_to_dict(old_cls, old_kwargs, new_cls, new_kwargs):
    calc = _old(old_cls, **old_kwargs)
    assert calc.get_inputs() == old_kwargs
    out = calc.to_dict()
    assert out["inputs"] == old_kwargs
    assert _as_tuple(out["results"]) == _as_tuple(new_cls(**new_kwargs).calculate())


@pytest.mark.parametrize("old_cls, old_kwargs, new_cls, new_kwargs", PAIRS)
def test_old_name_warns_and_names_its_replacement(old_cls, old_kwargs, new_cls, new_kwargs):
    with pytest.warns(DeprecationWarning, match=rf"{old_cls.__name__} is deprecated; use .*\.{new_cls.__name__}\b") as record:
        old_cls(**old_kwargs)
    # The warning points at the caller, not at the alias module.
    assert record[0].filename == __file__


@pytest.mark.parametrize("old_cls, old_kwargs, new_cls, new_kwargs", PAIRS)
def test_canonical_name_does_not_warn(old_cls, old_kwargs, new_cls, new_kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        new_cls(**new_kwargs).calculate()


@pytest.mark.parametrize(
    "old_cls, kwargs, missing",
    [
        (SensibleHeatDuty, {"specific_heat": 4200.0, "t_in": 360.0, "t_out": 330.0}, "mass_flow_rate"),
        (LatentHeatDuty, {"mass_flow_rate": 1.0}, "latent_heat"),
        (ReynoldsFromProperties, {"density": 1000.0, "velocity": 1.0, "diameter": 0.02}, "viscosity"),
        (KernNusselt, {"reynolds": 1e4}, "prandtl"),
        (ConvectiveCoefficient, {"nusselt": 100.0, "thermal_conductivity": 0.6}, "characteristic_diameter"),
        (DarcyPressureDrop, {"length": 1.0, "diameter": 0.05, "density": 1000.0, "velocity": 2.0}, "friction_factor"),
    ],
)
def test_old_name_still_reports_missing_inputs_by_old_keyword(old_cls, kwargs, missing):
    with pytest.raises(ValueError, match=rf"^Missing required input: {missing}$"):
        _old(old_cls, **kwargs)


def test_old_name_reports_bad_values_by_old_keyword():
    calc = _old(SensibleHeatDuty, mass_flow_rate="two", specific_heat=4200.0, t_in=360.0, t_out=330.0)
    with pytest.raises(TypeError, match="Could not interpret mass_flow_rate value"):
        calc.calculate()


# Hand calculations. Each is checked through both names.

def test_sensible_duty_by_hand():
    # Q = m cp |Tin - Tout| = 2 kg/s * 4200 J/kg.K * (360 - 330) K = 252 000 W
    q = SensibleDuty(m_dot=2.0, cp=4200.0, t_in=360.0, t_out=330.0).calculate()
    q_old = _old(SensibleHeatDuty, mass_flow_rate=2.0, specific_heat=4200.0, t_in=360.0, t_out=330.0).calculate()
    for value in (q, q_old):
        assert value.to("W").value == pytest.approx(252_000.0)


def test_latent_duty_by_hand():
    # Q = m lambda = 0.5 kg/s * 2.257e6 J/kg = 1 128 500 W
    q = LatentDuty(m_dot=0.5, latent_heat=2.257e6).calculate()
    q_old = _old(LatentHeatDuty, mass_flow_rate=0.5, latent_heat=2.257e6).calculate()
    for value in (q, q_old):
        assert value.to("W").value == pytest.approx(1_128_500.0)


def test_reynolds_by_hand():
    # Re = rho v D / mu = 1000 * 1.5 * 0.02 / 1e-3 = 30 000
    re = Reynolds(density=1000.0, velocity=1.5, diameter=0.02, viscosity=1e-3).calculate()
    re_old = _old(ReynoldsFromProperties, density=1000.0, velocity=1.5, diameter=0.02, viscosity=1e-3).calculate()
    for value in (re, re_old):
        assert value == pytest.approx(30_000.0)


def test_dittus_boelter_by_hand():
    # Nu = 0.023 Re^0.8 Pr^n with Re = 1e4, Pr = 2:
    #   Re^0.8 = 10^3.2 = 1584.893
    #   n = 0.4 (default): 2^0.4 = 1.319508, Nu = 0.023 * 1584.893 * 1.319508 = 48.0994
    #   n = 0.3:           2^0.3 = 1.231144, Nu = 0.023 * 1584.893 * 1.231144 = 44.8783
    for n, expected in ((None, 48.0994), (0.3, 44.8783)):
        extra = {} if n is None else {"n": n}
        nu = DittusBoelter(reynolds=1e4, prandtl=2.0, **extra).calculate()
        nu_old = _old(KernNusselt, reynolds=1e4, prandtl=2.0, **extra).calculate()
        for value in (nu, nu_old):
            assert value == pytest.approx(expected, rel=1e-5)


def test_convective_coefficient_by_hand():
    # h = Nu k / D = 100 * 0.6 W/m.K / 0.02 m = 3000 W/m2.K
    h = ConvectiveH(nusselt=100.0, k=0.6, diameter=0.02).calculate()
    h_old = _old(ConvectiveCoefficient, nusselt=100.0, thermal_conductivity=0.6, characteristic_diameter=0.02).calculate()
    for value in (h, h_old):
        assert isinstance(value, HeatTransferCoefficient)
        assert value.to("W/m2K").value == pytest.approx(3000.0)


def test_darcy_pressure_drop_by_hand():
    # Darcy-Weisbach, f the Darcy factor:
    # dP = f (L/D) rho v^2 / 2 = 0.02 * (10 / 0.05) * 1000 * 2^2 / 2 = 0.02 * 200 * 2000 = 8000 Pa
    dp = DarcyDrop(f=0.02, length=10.0, diameter=0.05, density=1000.0, velocity=2.0).calculate()
    dp_old = _old(DarcyPressureDrop, friction_factor=0.02, length=10.0, diameter=0.05, density=1000.0, velocity=2.0).calculate()
    for value in (dp, dp_old):
        assert value.to("Pa").value == pytest.approx(8000.0)
