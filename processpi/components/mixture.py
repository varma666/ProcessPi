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

from math import exp, isfinite, log
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

    @PropertyMethod
    def viscosity(self) -> Viscosity:
        """
        Liquid: ln mu = sum x_i ln mu_i (ideal logarithmic mixing).
        Gas: mole-fraction average of the pure-component viscosities.
        """
        if self._viscosity is not None:
            return self._viscosity
        phase = self._single_phase()
        mu_i = self._pure_values("viscosity", phase, "Pa·s")
        if phase == "liquid":
            mu = exp(sum(x * log(mu_i[n]) for n, x in self._mole_fractions.items()))
        else:
            mu = sum(x * mu_i[n] for n, x in self._mole_fractions.items())
        return Viscosity(mu, "Pa·s")

    @PropertyMethod
    def thermal_conductivity(self) -> ThermalConductivity:
        """Mass-fraction average (liquid) or mole-fraction average (gas)."""
        if self._thermal_conductivity is not None:
            return self._thermal_conductivity
        phase = self._single_phase()
        k_i = self._pure_values("thermal_conductivity", phase, "W/mK")
        fractions = self._mass_fractions if phase == "liquid" else self._mole_fractions
        return ThermalConductivity(sum(f * k_i[n] for n, f in fractions.items()), "W/mK")

    def __repr__(self) -> str:
        comp = ", ".join(f"{n}: {x:.4g}" for n, x in self._mole_fractions.items())
        return f"<Mixture {{{comp}}} (mole), T={self.temperature}, P={self.pressure}>"
