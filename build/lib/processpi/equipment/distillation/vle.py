"""
Ideal vapour-liquid equilibrium for the distillation module.

Raoult's law, K_i = Psat_i(T) / P, with the pure-component vapour pressures
taken from each component's DIPPR-101 constants (``Component.vapor_pressure``).
This is the ideal-solution, ideal-gas model: it is good for mixtures of
chemically similar molecules (benzene/toluene, light hydrocarbons) and wrong
for strongly non-ideal ones (ethanol/water, anything that forms an azeotrope).
For those, give the column a ``relative_volatility`` dict instead.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional

from processpi.units import Pressure, Temperature

R_GAS = 8.314462618  # J/mol-K

# A vapour-pressure curve ends at the critical point, so Psat(Tc) must be close
# to Pc. A factor of 3 either way is far wider than any honest DIPPR fit and
# catches the components whose constants were transcribed wrongly (for example a
# missing B term, which puts Psat out by orders of magnitude).
_PSAT_AT_TC_TOLERANCE = 3.0


def _component_class(component):
    return component if isinstance(component, type) else type(component)


def _normalise(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


class IdealVLE:
    """
    Raoult's-law VLE over a set of ProcessPI components.

    Args:
        components: component instances or classes, e.g. ``[Benzene(), Toluene()]``.
            Each is addressed by its ``name`` attribute.
    """

    def __init__(self, components: Iterable):
        self._classes: Dict[str, type] = {}
        for comp in components:
            cls = _component_class(comp)
            name = getattr(cls, "name", None)
            if not isinstance(name, str):
                raise TypeError(f"{comp!r} is not a ProcessPI component (no name).")
            self._classes[name] = cls
        if len(self._classes) < 2:
            raise ValueError("IdealVLE needs at least two components.")
        for name in self._classes:
            self._check_vapor_pressure(name)

    # ------------------------------------------------------------------
    # Pure-component properties
    # ------------------------------------------------------------------
    @property
    def names(self) -> List[str]:
        return list(self._classes)

    def resolve(self, name: str) -> str:
        """
        The component name for `name`, ignoring case, spaces and punctuation
        and accepting the class name too ("chlorobenzene" and "ChloroBenzene"
        both give "Chloro Benzene"). Raises KeyError when nothing matches.
        """
        if name in self._classes:
            return name
        key = _normalise(name)
        for canonical, cls in self._classes.items():
            if key in (_normalise(canonical), _normalise(cls.__name__)):
                return canonical
        raise KeyError(name)

    def component_class(self, name: str) -> type:
        return self._classes[name]

    def molecular_weight(self, name: str) -> float:
        """g/mol."""
        return float(self._classes[name].molecular_weight)

    def critical_temperature(self, name: str) -> float:
        return self._classes[name]._critical_temperature.to("K").value

    def psat(self, name: str, t_k: float) -> float:
        """Pure-component vapour pressure in Pa at t_k (K)."""
        comp = self._classes[name](temperature=Temperature(t_k, "K"))
        return comp.vapor_pressure().to("Pa").value

    def _check_vapor_pressure(self, name: str) -> None:
        cls = self._classes[name]
        tc = self.critical_temperature(name)
        pc = cls._critical_pressure.to("Pa").value
        try:
            p_at_tc = self.psat(name, tc)
        except (OverflowError, ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"{name}: vapour pressure cannot be evaluated at Tc ({exc}).") from exc
        if not (math.isfinite(p_at_tc) and p_at_tc > 0):
            raise ValueError(f"{name}: vapour pressure at Tc is {p_at_tc!r}.")
        ratio = p_at_tc / pc
        if not (1.0 / _PSAT_AT_TC_TOLERANCE <= ratio <= _PSAT_AT_TC_TOLERANCE):
            raise ValueError(
                f"{name}: the vapour-pressure constants {list(cls._vapor_pressure_constants)} give "
                f"Psat(Tc) = {p_at_tc:.4g} Pa against Pc = {pc:.4g} Pa, so they cannot be used for VLE. "
                "Check the component data, or give the column a `relative_volatility` dict."
            )

    def saturation_temperature(self, name: str, p_pa: float) -> float:
        """Temperature (K) at which the pure component boils at p_pa."""
        tc = self.critical_temperature(name)
        lo, hi = 0.25 * tc, tc
        if self.psat(name, lo) > p_pa:
            raise ValueError(f"{name}: boils below {lo:.1f} K at {p_pa:.4g} Pa, outside the correlation.")
        if self.psat(name, hi) < p_pa:
            raise ValueError(f"{name}: {p_pa:.4g} Pa is above its critical pressure; it cannot boil.")
        # ln Psat is close to linear in 1/T, so bisect on that.
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if self.psat(name, mid) > p_pa:
                hi = mid
            else:
                lo = mid
            if hi - lo < 1e-7:
                break
        return 0.5 * (lo + hi)

    def latent_heat(self, name: str, t_k: float) -> float:
        """Molar heat of vaporisation in J/mol at t_k."""
        cls = self._classes[name]
        comp = cls(temperature=Temperature(t_k, "K"))
        h_kg = comp.enthalpy().to("J/kg").value
        if not (math.isfinite(h_kg) and h_kg > 0):
            raise ValueError(f"{name}: heat of vaporisation at {t_k:.2f} K is {h_kg!r} J/kg.")
        return h_kg * self.molecular_weight(name) / 1000.0

    def _liquid(self, name: str, t_k: float):
        # Component.density/viscosity pick the gas branch whenever P < Psat;
        # the column needs the liquid property at the boiling point, so build
        # the component at a pressure above its own vapour pressure.
        p_liquid = max(101325.0, 2.0 * self.psat(name, t_k))
        return self._classes[name](temperature=Temperature(t_k, "K"), pressure=Pressure(p_liquid, "Pa"))

    def liquid_density(self, name: str, t_k: float) -> float:
        """kg/m3."""
        return self._liquid(name, t_k).density().to("kg/m3").value

    def liquid_viscosity(self, name: str, t_k: float) -> float:
        """Pa.s."""
        return self._liquid(name, t_k).viscosity().to("Pa·s").value

    def liquid_cp(self, name: str, t_k: float) -> float:
        """Molar liquid heat capacity in J/mol-K."""
        comp = self._classes[name](temperature=Temperature(t_k, "K"))
        cp_kg = comp.specific_heat().to("J/kgK").value
        return cp_kg * self.molecular_weight(name) / 1000.0

    # ------------------------------------------------------------------
    # Mixture equilibrium
    # ------------------------------------------------------------------
    def _composition(self, x: Dict[str, float]) -> Dict[str, float]:
        unknown = [name for name in x if name not in self._classes]
        if unknown:
            raise KeyError(f"No component data for {unknown}; known: {self.names}.")
        total = sum(x.values())
        if total <= 0:
            raise ValueError("Composition must have a positive total.")
        return {name: value / total for name, value in x.items() if value > 0}

    def k_values(self, t_k: float, p_pa: float, names: Optional[Iterable[str]] = None) -> Dict[str, float]:
        names = list(names) if names is not None else self.names
        return {name: self.psat(name, t_k) / p_pa for name in names}

    def relative_volatilities(self, t_k: float, p_pa: float, reference: str) -> Dict[str, float]:
        """alpha_i = K_i / K_reference = Psat_i / Psat_reference (Raoult)."""
        p_ref = self.psat(reference, t_k)
        return {name: self.psat(name, t_k) / p_ref for name in self.names}

    def _bracket(self, names: Iterable[str], p_pa: float):
        t_sat = [self.saturation_temperature(name, p_pa) for name in names]
        return min(t_sat), max(t_sat)

    def bubble_temperature(self, x: Dict[str, float], p_pa: float) -> float:
        """T (K) at which liquid x starts to boil at p_pa: sum K_i x_i = 1."""
        x = self._composition(x)
        lo, hi = self._bracket(x, p_pa)
        if hi - lo < 1e-9:
            return lo

        def f(t):
            return sum(self.psat(n, t) * xi for n, xi in x.items()) / p_pa - 1.0

        return _bisect(f, lo, hi)

    def dew_temperature(self, y: Dict[str, float], p_pa: float) -> float:
        """T (K) at which vapour y starts to condense at p_pa: sum y_i / K_i = 1."""
        y = self._composition(y)
        lo, hi = self._bracket(y, p_pa)
        if hi - lo < 1e-9:
            return lo

        def f(t):
            return 1.0 - sum(yi * p_pa / self.psat(n, t) for n, yi in y.items())

        return _bisect(f, lo, hi)

    def equilibrium_vapor(self, x: Dict[str, float], p_pa: float):
        """Bubble point of liquid x: returns (T in K, vapour composition y)."""
        x = self._composition(x)
        t = self.bubble_temperature(x, p_pa)
        y = {n: self.psat(n, t) * xi / p_pa for n, xi in x.items()}
        total = sum(y.values())
        return t, {n: v / total for n, v in y.items()}

    def flash_vapor_fraction(self, z: Dict[str, float], t_k: float, p_pa: float) -> float:
        """
        Isothermal flash: molar vapour fraction psi of feed z at (t_k, p_pa),
        from the Rachford-Rice equation sum z_i (K_i - 1) / (1 + psi (K_i - 1)) = 0.
        Returns 0 for a subcooled liquid and 1 for a superheated vapour.
        """
        z = self._composition(z)
        k = self.k_values(t_k, p_pa, z)

        def rr(psi):
            return sum(zi * (k[n] - 1.0) / (1.0 + psi * (k[n] - 1.0)) for n, zi in z.items())

        if rr(0.0) <= 0.0:
            return 0.0
        if rr(1.0) >= 0.0:
            return 1.0
        return _bisect(lambda psi: -rr(psi), 0.0, 1.0)

    # ------------------------------------------------------------------
    # Mixture properties
    # ------------------------------------------------------------------
    def mixture_mw(self, x: Dict[str, float]) -> float:
        """g/mol."""
        x = self._composition(x)
        return sum(xi * self.molecular_weight(n) for n, xi in x.items())

    def mixture_liquid_density(self, x: Dict[str, float], t_k: float) -> float:
        """kg/m3, ideal (additive) volumes: 1/rho = sum w_i / rho_i."""
        x = self._composition(x)
        mw = self.mixture_mw(x)
        inv = sum(xi * self.molecular_weight(n) / mw / self.liquid_density(n, t_k) for n, xi in x.items())
        return 1.0 / inv

    def mixture_vapor_density(self, y: Dict[str, float], t_k: float, p_pa: float) -> float:
        """kg/m3, ideal gas."""
        return p_pa * self.mixture_mw(y) / 1000.0 / (R_GAS * t_k)

    def mixture_liquid_viscosity(self, x: Dict[str, float], t_k: float) -> float:
        """Pa.s, ideal logarithmic mixing: ln mu = sum x_i ln mu_i."""
        x = self._composition(x)
        return math.exp(sum(xi * math.log(self.liquid_viscosity(n, t_k)) for n, xi in x.items()))

    def mixture_latent_heat(self, x: Dict[str, float], t_k: float) -> float:
        """J/mol, mole-fraction average of the pure-component latent heats."""
        x = self._composition(x)
        return sum(xi * self.latent_heat(n, t_k) for n, xi in x.items())

    def mixture_liquid_cp(self, x: Dict[str, float], t_k: float) -> float:
        """J/mol-K, mole-fraction average."""
        x = self._composition(x)
        return sum(xi * self.liquid_cp(n, t_k) for n, xi in x.items())


def _bisect(f, lo: float, hi: float, tol: float = 1e-9, max_iter: int = 300) -> float:
    """Root of an increasing-or-decreasing f on [lo, hi] that changes sign."""
    f_lo, f_hi = f(lo), f(hi)
    if f_lo == 0.0:
        return lo
    if f_hi == 0.0:
        return hi
    if f_lo * f_hi > 0:
        raise ValueError(f"No sign change between {lo} and {hi} ({f_lo}, {f_hi}).")
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if f_mid == 0.0 or hi - lo < tol:
            return mid
        if (f_mid < 0) == (f_lo < 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
