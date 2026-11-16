"""
A mixture of ProcessPI components, usable wherever a single component is.

A stream made from a composition (a column's distillate, a mixer outlet) has no
single component, so an exchanger or a pipe had no density, heat capacity,
viscosity or conductivity to work with. ``Mixture`` takes the pure-component
properties at the mixture's temperature, pressure and phase and combines them,
with the same interface as ``Component``:

    from processpi.components import Benzene, Toluene, Mixture
    from processpi.units import Temperature, Pressure

    mix = Mixture({Benzene: 0.4, Toluene: 0.6},
                  temperature=Temperature(80, "C"), pressure=Pressure(1, "atm"),
                  phase="liquid")
    mix.density()        # Density, kg/m3
    mix.specific_heat()  # SpecificHeat, J/kgK

The phase, when none is given, comes from Raoult's law: liquid at or above the
bubble-point pressure, gas at or below the dew-point pressure, and "two-phase"
in between, where no single-phase property exists and the methods raise.
"""

from functools import lru_cache
from math import exp, isfinite, log, sqrt
from typing import Dict, Iterable, Mapping, Optional, Union

from processpi.constants import R_UNIVERSAL  # 8.314 J/mol-K
from processpi.units import (
    Density, HeatOfVaporization, Pressure, SpecificHeat, Temperature,
    ThermalConductivity, Viscosity,
)

from .base import Component, PropertyMethod

_GAS_PHASES = {"gas", "vapor", "vapour", "steam"}


def _component_class(component) -> type:
    return component if isinstance(component, type) else type(component)


def _normalise(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


# ----------------------------------------------------------------------
# Transport-property mixing rules
# ----------------------------------------------------------------------
# Each takes {name: value} dicts over the same names; the units only need to
# be consistent (the rules use ratios).

def wilke_viscosity(x: Mapping[str, float], mu: Mapping[str, float], mw: Mapping[str, float]) -> float:
    """
    Low-pressure gas mixture viscosity, Wilke's rule as given in the API
    Technical Data Book, Procedure 11B2.1 (Bromley and Wilke, Ind. Eng. Chem.
    43, 1641 (1951)), about 3 percent average deviation:

        mu_m   = sum_i mu_i / (1 + sum_{j != i} phi_ij x_j / x_i)
        phi_ij = [1 + (mu_i/mu_j)^(1/2) (M_j/M_i)^(1/4)]^2 / (8 (1 + M_i/M_j))^(1/2)

    The printed Eq. (11B2.1-2) reads (M_i/M_j)^(1/4); the procedure's own
    hydrogen/propane example (phi_12 = 3.59, phi_21 = 0.15) only follows from
    (M_j/M_i)^(1/4), which is Wilke's original form.
    """
    total = 0.0
    for i, xi in x.items():
        # phi_ii = 1, so 1 + sum_{j != i} phi_ij x_j / x_i = sum_j phi_ij x_j / x_i.
        denominator = sum(
            xj * (1.0 + sqrt(mu[i] / mu[j]) * (mw[j] / mw[i]) ** 0.25) ** 2 / sqrt(8.0 * (1.0 + mw[i] / mw[j]))
            for j, xj in x.items()
        )
        total += xi * mu[i] / denominator
    return total


def lindsay_bromley_conductivity(
    y: Mapping[str, float],
    k: Mapping[str, float],
    mu: Mapping[str, float],
    mw: Mapping[str, float],
    sutherland: Mapping[str, float],
    t_k: float,
) -> float:
    """
    Gas mixture thermal conductivity, API Technical Data Book Procedure 12B2.1
    (the Wassiljewa form with Lindsay-Bromley coefficients):

        k_m  = sum_i y_i k_i / sum_j y_j A_ij
        A_ij = 1/4 {1 + [(mu_i/mu_j) (M_j/M_i)^(3/4) (1 + S_i/T)/(1 + S_j/T)]^(1/2)}^2
               * (1 + S_ij/T) / (1 + S_i/T),        S_ij = (S_i S_j)^(1/2)

    with S the Sutherland constants, in the same unit as T.
    """
    total = 0.0
    for i, yi in y.items():
        si = sutherland[i]
        denominator = 0.0
        for j, yj in y.items():
            sj = sutherland[j]
            ratio = (mu[i] / mu[j]) * (mw[j] / mw[i]) ** 0.75 * (1.0 + si / t_k) / (1.0 + sj / t_k)
            a_ij = 0.25 * (1.0 + sqrt(ratio)) ** 2 * (1.0 + sqrt(si * sj) / t_k) / (1.0 + si / t_k)
            denominator += yj * a_ij
        total += yi * k[i] / denominator
    return total


def li_conductivity(x: Mapping[str, float], k: Mapping[str, float], molar_volume: Mapping[str, float]) -> float:
    """
    Liquid mixture thermal conductivity, Li correlation (Li, AIChE J. 22, 927
    (1976)), Perry's 8th ed. Eq. (2-113), 4 to 8 percent:

        k = sum_i sum_j phi_i phi_j 2 k_i k_j / (k_i + k_j),   phi_i = x_i V_i / sum_j x_j V_j

    with V_i the pure-liquid molar volume (1 / molar density).
    """
    volume = sum(x[n] * molar_volume[n] for n in x)
    phi = {n: x[n] * molar_volume[n] / volume for n in x}
    return sum(
        phi[i] * phi[j] * 2.0 * k[i] * k[j] / (k[i] + k[j])
        for i in x for j in x
    )


# API TDB Eq. (12B2.1-4): S = 142 R (78.9 K) for hydrogen, deuterium and helium.
_SUTHERLAND_LIGHT_GASES_K = {"Hydrogen": 142.0 / 1.8, "Deuterium": 142.0 / 1.8, "Helium": 142.0 / 1.8}


@lru_cache(maxsize=None)
def _normal_boiling_point(cls: type) -> float:
    """Temperature, K, at which the component's vapour pressure is 1 atm (bisection)."""
    one_atm = 101325.0
    t_c = cls._critical_temperature.to("K").value

    def excess(t_k: float) -> float:
        return cls(temperature=Temperature(t_k, "K"), pressure=Pressure(one_atm, "Pa")).vapor_pressure().to("Pa").value - one_atm

    lo, hi = 0.2 * t_c, 0.999 * t_c
    f_lo, f_hi = excess(lo), excess(hi)
    if not (f_lo < 0.0 < f_hi):
        raise ValueError(f"{cls.name}: vapour pressure does not cross 1 atm below Tc, so no normal boiling point.")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if excess(mid) < 0.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-6:
            break
    return 0.5 * (lo + hi)


def _sutherland_constant(cls: type) -> float:
    """Sutherland constant, K, per API TDB Eqs. (12B2.1-3, -4): 1.5 Tb, or 78.9 K for H2, D2 and He."""
    return _SUTHERLAND_LIGHT_GASES_K.get(cls.__name__) or 1.5 * _normal_boiling_point(cls)


class Mixture(Component):
    """
    A mixture of components at one temperature, pressure and phase.

    Args:
        composition: {component: fraction}, the component as a class or an
            instance (``{Benzene: 0.4, Toluene: 0.6}``). Fractions are
            normalised.
        basis: "mole" (default) or "mass", the basis of the fractions.
        temperature, pressure: the state; defaults 25 C and 1 atm.
        phase: "liquid" or "gas"/"vapor" to fix the phase; None takes it from
            Raoult's law.
    """

    def __init__(
        self,
        composition: Mapping[Union[type, Component], float],
        basis: str = "mole",
        temperature: Temperature = None,
        pressure: Pressure = None,
        phase: str = None,
    ):
        if basis not in {"mole", "mass"}:
            raise ValueError(f"basis must be 'mole' or 'mass', not {basis!r}.")
        classes: Dict[str, type] = {}
        fractions: Dict[str, float] = {}
        for comp, fraction in composition.items():
            cls = _component_class(comp)
            if isinstance(cls, type) and issubclass(cls, Mixture):
                raise TypeError("A Mixture cannot contain another Mixture.")
            name = getattr(cls, "name", None)
            if not isinstance(name, str):
                raise TypeError(f"{comp!r} is not a ProcessPI component (no name).")
            fraction = float(fraction)
            if not isfinite(fraction) or fraction < 0:
                raise ValueError(f"{name}: fraction must be a non-negative number, not {fraction!r}.")
            if fraction == 0:
                continue
            classes[name] = cls
            fractions[name] = fractions.get(name, 0.0) + fraction
        total = sum(fractions.values())
        if not classes or total <= 0:
            raise ValueError("A Mixture needs at least one component with a positive fraction.")
        fractions = {name: f / total for name, f in fractions.items()}

        self._classes = classes
        if basis == "mole":
            self._mole_fractions = fractions
        else:
            moles = {n: w / float(classes[n].molecular_weight) for n, w in fractions.items()}
            n_total = sum(moles.values())
            self._mole_fractions = {n: v / n_total for n, v in moles.items()}
        mw = sum(x * float(classes[n].molecular_weight) for n, x in self._mole_fractions.items())
        self._mw = mw
        self._mass_fractions = {
            n: x * float(classes[n].molecular_weight) / mw for n, x in self._mole_fractions.items()
        }
        # Kay's rule: pseudo-critical constants as mole-fraction averages.
        self._critical_temperature = Temperature(
            sum(x * classes[n]._critical_temperature.to("K").value for n, x in self._mole_fractions.items()), "K"
        )
        self._critical_pressure = Pressure(
            sum(x * classes[n]._critical_pressure.to("Pa").value for n, x in self._mole_fractions.items()), "Pa"
        )
        super().__init__(temperature=temperature, pressure=pressure, phase=phase)

    # ------------------------------------------------------------------
    # Identity and composition
    # ------------------------------------------------------------------
    @property
    def name(self) -> str:
        return " / ".join(self._classes)

    @property
    def formula(self) -> str:
        return " + ".join(str(getattr(cls, "formula", name)) for name, cls in self._classes.items())

    @property
    def molecular_weight(self) -> float:
        """Mean molecular weight, g/mol: sum x_i M_i."""
        return self._mw

    @property
    def component_names(self):
        return list(self._classes)

    def mole_fractions(self) -> Dict[str, float]:
        return dict(self._mole_fractions)

    def mass_fractions(self) -> Dict[str, float]:
        return dict(self._mass_fractions)

    def component_class(self, name: str) -> type:
        """The component class for `name`, ignoring case, spaces and punctuation."""
        if name in self._classes:
            return self._classes[name]
        key = _normalise(name)
        for canonical, cls in self._classes.items():
            if key in (_normalise(canonical), _normalise(cls.__name__)):
                return cls
        raise KeyError(name)

    def _infer_hx_type(self) -> str:
        return getattr(self._dominant(), "hx_type", Component._hx_liquid_type)

    @classmethod
    def from_names(
        cls,
        composition: Mapping[str, float],
        components: Iterable[Union[type, Component]],
        **kwargs,
    ) -> "Mixture":
        """
        Build a mixture from {name: fraction}, as a MaterialStream holds it,
        with the component classes looked up in `components` by name
        (ignoring case, spaces and punctuation, or by class name).
        """
        lookup: Dict[str, type] = {}
        for comp in components:
            c = _component_class(comp)
            lookup[_normalise(c.name)] = c
            lookup[_normalise(c.__name__)] = c
        resolved = {}
        for name, fraction in composition.items():
            c = lookup.get(_normalise(name))
            if c is None:
                raise KeyError(f"No component data for {name!r} in the components given.")
            resolved[c] = resolved.get(c, 0.0) + float(fraction)
        return cls(resolved, **kwargs)

    # ------------------------------------------------------------------
    # Pure components at the mixture state
    # ------------------------------------------------------------------
    def _t_k(self) -> float:
        return self.temperature.to("K").value

    def _pure(self, name: str, phase: Optional[str] = None):
        return self._classes[name](
            temperature=Temperature(self._t_k(), "K"),
            pressure=self.pressure,
            phase=phase,
        )

    def _psat(self, name: str) -> float:
        """Pure-component vapour pressure, Pa; infinite above the component's Tc."""
        cls = self._classes[name]
        if self._t_k() >= cls._critical_temperature.to("K").value:
            return float("inf")
        return self._pure(name).vapor_pressure().to("Pa").value

    def _dominant(self) -> type:
        """The component with the largest mass fraction."""
        name = max(self._mass_fractions, key=self._mass_fractions.get)
        return self._classes[name]

    def _single_phase(self) -> str:
        phase = self.phase()
        if phase == "two-phase":
            raise ValueError(
                f"{self.name} at {self._t_k():.2f} K and {self.pressure.to('Pa').value:.6g} Pa is between "
                "its bubble and dew points (two-phase); give the phase, or flash it."
            )
        return phase

    def _pure_values(self, method: str, phase: str, unit: str) -> Dict[str, float]:
        if phase == "liquid":
            t_k = self._t_k()
            supercritical = [
                n for n, cls in self._classes.items() if t_k >= cls._critical_temperature.to("K").value
            ]
            if supercritical:
                raise ValueError(
                    f"{', '.join(supercritical)} is above its critical temperature at {t_k:.2f} K, "
                    "so it has no liquid properties to mix."
                )
        values = {}
        for name in self._classes:
            value = getattr(self._pure(name, phase), method)().to(unit).value
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name}: {method} is {value!r} {unit} at {self._t_k():.2f} K ({phase}).")
            values[name] = value
        return values

    # ------------------------------------------------------------------
    # Phase equilibrium (Raoult's law)
    # ------------------------------------------------------------------
    def bubble_pressure(self) -> Pressure:
        """Pressure at which the liquid starts to boil: P = sum x_i Psat_i."""
        return Pressure(sum(x * self._psat(n) for n, x in self._mole_fractions.items()), "Pa")

    def dew_pressure(self) -> Pressure:
        """Pressure at which the vapour starts to condense: 1/P = sum y_i / Psat_i."""
        return Pressure(1.0 / sum(y / self._psat(n) for n, y in self._mole_fractions.items()), "Pa")

    @PropertyMethod
    def vapor_pressure(self) -> Pressure:
        """The bubble-point pressure, the mixture's analogue of a vapour pressure."""
        return self.bubble_pressure()

    @PropertyMethod
    def phase(self) -> str:
        """
        "liquid", "gas" or "two-phase". A phase given to the mixture is used
        as is; otherwise the liquid exists at or above the bubble-point
        pressure and the gas at or below the dew-point pressure.
        """
        forced = getattr(self, "_phase", None)
        if forced:
            return "gas" if str(forced).lower() in _GAS_PHASES else "liquid"
        p = self.pressure.to("Pa").value
        if p >= self.bubble_pressure().to("Pa").value:
            return "liquid"
        if p <= self.dew_pressure().to("Pa").value:
            return "gas"
        return "two-phase"

    # ------------------------------------------------------------------
    # Heat exchanger data
    # ------------------------------------------------------------------
    def _dominant_state(self):
        """The component with the largest mass fraction, at the mixture's state and phase."""
        name = max(self._mass_fractions, key=self._mass_fractions.get)
        return self._pure(name, self._single_phase())

    def httype(self) -> str:
        """Fluid category for the U lookup: that of the component with the largest mass fraction."""
        return self._dominant_state().httype()

    def hx_data(self) -> dict:
        """
        Service keys for the exchanger (fouling, corrosion, velocity band, U
        category): those of the component with the largest mass fraction, in
        the mixture's phase.
        """
        return self._dominant_state().hx_data()

    # ------------------------------------------------------------------
    # Mixture properties
    # ------------------------------------------------------------------
    @PropertyMethod
    def density(self) -> Density:
        """
        Gas: ideal gas, rho = P M / (R T).
        Liquid: ideal solution (additive volumes), 1/rho = sum w_i / rho_i.
        """
        if self._density is not None:
            return self._density
        phase = self._single_phase()
        if phase == "gas":
            rho = self.pressure.to("Pa").value * (self._mw / 1000.0) / (R_UNIVERSAL * self._t_k())
            return Density(rho, "kg/m3")
        rho_i = self._pure_values("density", "liquid", "kg/m3")
        return Density(1.0 / sum(w / rho_i[n] for n, w in self._mass_fractions.items()), "kg/m3")

    @PropertyMethod
    def specific_heat(self) -> SpecificHeat:
        """Ideal mixing: cp = sum w_i cp_i, each component in the mixture's phase."""
        if self._specific_heat is not None:
            return self._specific_heat
        phase = self._single_phase()
        cp_i = self._pure_values("specific_heat", phase, "J/kgK")
        return SpecificHeat(sum(w * cp_i[n] for n, w in self._mass_fractions.items()), "J/kgK")

    @PropertyMethod
    def enthalpy(self) -> HeatOfVaporization:
        """
        Heat of vaporisation, J/kg: sum w_i dHv_i, which is the mole-fraction
        average of the molar latent heats divided by the mean molecular weight.
        This is the heat to vaporise the liquid at constant temperature; the
        sensible heat between the bubble and dew points is not included.
        """
        if self._enthalpy is not None:
            return self._enthalpy
        dh_i = self._pure_values("enthalpy", "liquid", "J/kg")
        return HeatOfVaporization(sum(w * dh_i[n] for n, w in self._mass_fractions.items()), "J/kg")

    latent_heat = enthalpy

    def _mw_values(self) -> Dict[str, float]:
        return {n: float(cls.molecular_weight) for n, cls in self._classes.items()}

    @PropertyMethod
    def viscosity(self) -> Viscosity:
        """
        Liquid: ln mu = sum x_i ln mu_i, the Grunberg-Nissan equation (Perry's
        8th ed. Eq. 2-98) with G_ij = 0, which Perry gives for hydrocarbon
        mixtures at about 15 percent; G_ij must otherwise be fitted to mixture
        data.
        Gas: Wilke's rule, API TDB Procedure 11B2.1 (see `wilke_viscosity`),
        for reduced pressures below 0.6.
        """
        if self._viscosity is not None:
            return self._viscosity
        phase = self._single_phase()
        mu_i = self._pure_values("viscosity", phase, "Pa·s")
        if phase == "liquid":
            mu = exp(sum(x * log(mu_i[n]) for n, x in self._mole_fractions.items()))
        else:
            mu = wilke_viscosity(self._mole_fractions, mu_i, self._mw_values())
        return Viscosity(mu, "Pa·s")

    @PropertyMethod
    def thermal_conductivity(self) -> ThermalConductivity:
        """
        Liquid: Li correlation, Perry's 8th ed. Eq. (2-113), with the molar
        volumes from the pure-liquid densities (see `li_conductivity`).
        Gas: API TDB Procedure 12B2.1, Lindsay-Bromley coefficients, with
        Sutherland constants 1.5 Tb (see `lindsay_bromley_conductivity`).
        """
        if self._thermal_conductivity is not None:
            return self._thermal_conductivity
        phase = self._single_phase()
        k_i = self._pure_values("thermal_conductivity", phase, "W/mK")
        mw = self._mw_values()
        if phase == "liquid":
            rho_i = self._pure_values("density", "liquid", "kg/m3")
            k = li_conductivity(self._mole_fractions, k_i, {n: mw[n] / rho_i[n] for n in k_i})
        else:
            mu_i = self._pure_values("viscosity", "gas", "Pa·s")
            sutherland = {n: _sutherland_constant(cls) for n, cls in self._classes.items()}
            k = lindsay_bromley_conductivity(self._mole_fractions, k_i, mu_i, mw, sutherland, self._t_k())
        return ThermalConductivity(k, "W/mK")

    def __repr__(self) -> str:
        comp = ", ".join(f"{n}: {x:.4g}" for n, x in self._mole_fractions.items())
        return f"<Mixture {{{comp}}} (mole), T={self.temperature}, P={self.pressure}>"
