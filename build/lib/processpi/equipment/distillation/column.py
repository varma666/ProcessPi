"""
Simple distillation column: one feed, a total condenser, a partial reboiler,
a distillate and a bottoms product.

Design is by the Fenske-Underwood-Gilliland-Kirkbride shortcut (multicomponent),
with a McCabe-Thiele cross-check for binary feeds, followed by a tray column
sizing: O'Connell efficiency, Fair flooding diameter, tray-section height and
the condenser and reboiler duties.

Example:
    from processpi.components import Benzene, Toluene
    from processpi.streams import MaterialStream
    from processpi.units import MolarFlowRate, Pressure, Temperature
    from processpi.equipment.distillation import DistillationColumn

    feed = MaterialStream(
        "Feed",
        composition={"Benzene": 0.4, "Toluene": 0.6},
        molar_flow=MolarFlowRate(100, "kmol/h"),
        temperature=Temperature(95, "C"),
        pressure=Pressure(1.01325, "bar"),
    )
    column = DistillationColumn(
        feed=feed,
        components=[Benzene(), Toluene()],
        light_key="Benzene", heavy_key="Toluene",
        distillate_lk_fraction=0.97, bottoms_lk_fraction=0.02,
    )
    print(column.design().summary())
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from processpi.streams.material import MaterialStream
from processpi.units import (
    Area, Density, Diameter, HeatFlow, Length, MassFlowRate, MolarFlowRate, Pressure,
    Temperature, Velocity, Viscosity,
)

from ..base import Equipment
from . import hydraulics, mccabe_thiele, shortcut
from .results import DistillationResults
from .vle import IdealVLE


class DistillationColumn(Equipment):
    """
    Shortcut design and tray sizing of a simple distillation column.

    Ports: inlet ``feed``; outlets ``distillate`` and ``bottoms``.

    Specs (keyword arguments):
        light_key, heavy_key (str): key component names, as in the feed composition.
        Separation, one of:
            light_key_recovery (fraction of the feed light key to the distillate)
            and heavy_key_recovery (fraction of the feed heavy key to the bottoms); or,
            for a binary feed only, distillate_lk_fraction and bottoms_lk_fraction
            (light-key mole fractions in the products).
        Equilibrium, one of:
            components: list of ProcessPI components (ideal Raoult's-law VLE,
                which also gives temperatures, duties, diameter and efficiency); or
            relative_volatility: dict of constant volatilities (any reference).
                Stage counts only, unless tray_efficiency is given.
        pressure: column pressure (Pressure, or Pa). Default: feed pressure.
            The same pressure is used top and bottom.
        q: feed thermal condition. Default: from the feed temperature
            (subcooled or two-phase feed); a superheated feed needs q.
        reflux_ratio: operating L/D; or reflux_ratio_factor: R / R_min
            (default 1.3, inside the usual 1.15-1.40 range quoted by the
            OpenExamPrep guide cited in shortcut.py).
        gilliland_correlation: "molokanov" (default) or "eduljee".
        tray_efficiency: overall efficiency as a fraction; overrides O'Connell.
        tray_spacing: Length, or m (default 0.6 m).
        flood_fraction: design fraction of flooding velocity (default 0.80; the
            source of the flooding correlation caps it at 0.85).
        downcomer_area_fraction: downcomer share of the column area (default 0.12).
        surface_tension: N/m (default 0.020, where Fair's correction is 1;
            ProcessPI components carry no surface tension yet).
        flooding_k_factor: tray-geometry factor K on the flooding velocity (default 1.0).

    The defaults for tray spacing, flood fraction and downcomer area are
    common starting values for a first sizing, not code requirements; each
    one is reported in the results' assumptions list.
    """

    DEFAULTS: Dict[str, Any] = {
        "reflux_ratio_factor": 1.3,
        "gilliland_correlation": "molokanov",
        "tray_spacing": 0.6,
        "flood_fraction": 0.80,
        "downcomer_area_fraction": 0.12,
        "surface_tension": 0.020,
        "flooding_k_factor": 1.0,
    }

    def __init__(self, name: str = "DistillationColumn", feed: Optional[MaterialStream] = None,
                 distillate: Optional[MaterialStream] = None, bottoms: Optional[MaterialStream] = None,
                 **specs: Any):
        super().__init__(name, inlet_names=["feed"], outlet_names=["distillate", "bottoms"])
        if feed is not None:
            self.connect_inlet("feed", feed)
        if distillate is not None:
            self.connect_outlet("distillate", distillate)
        if bottoms is not None:
            self.connect_outlet("bottoms", bottoms)
        self.specs: Dict[str, Any] = specs
        self._vle: Optional[IdealVLE] = None
        self._results: Optional[DistillationResults] = None

    # ------------------------------------------------------------------
    # Ports
    # ------------------------------------------------------------------
    @property
    def feed(self) -> Optional[MaterialStream]:
        return self.inlets["feed"]

    @property
    def distillate(self) -> Optional[MaterialStream]:
        return self.outlets["distillate"]

    @property
    def bottoms(self) -> Optional[MaterialStream]:
        return self.outlets["bottoms"]

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------
    def _spec(self, key: str):
        value = self.specs.get(key)
        return self.DEFAULTS.get(key) if value is None else value

    @staticmethod
    def _si(value: Any, name: str) -> float:
        """A unit object's stored SI value (K, Pa, m, mol/s), or a plain number taken as SI."""
        if value is None:
            raise ValueError(f"{name} is required.")
        if hasattr(value, "to") and hasattr(value, "value"):
            return float(value.value)
        return float(value)

    def _feed_state(self) -> Dict[str, Any]:
        feed = self.feed
        if feed is None:
            raise ValueError(f"{self.name}: inlet port 'feed' is not connected.")
        if getattr(feed, "component", None) is not None and len(feed.components) <= 1:
            raise ValueError(f"{self.name}: the feed is a single component; a column needs a mixture (use `composition=`).")
        if len(feed.components) < 2:
            raise ValueError(f"{self.name}: the feed composition needs at least two components.")

        z_raw: Dict[str, float] = {}
        for key, value in feed.components.items():
            name = self._resolve_name(key)
            z_raw[name] = z_raw.get(name, 0.0) + float(value)

        if getattr(feed, "basis", "mole") == "mass":
            mws = self._molecular_weights(feed, z_raw)
            moles = {n: w / mws[n] for n, w in z_raw.items()}
            total = sum(moles.values())
            z = {n: m / total for n, m in moles.items()}
        else:
            total = sum(z_raw.values())
            z = {n: v / total for n, v in z_raw.items()}

        flow = feed._molar_flow
        if flow is None:
            mass = feed.mass_flow()
            if mass is None:
                raise ValueError(f"{self.name}: the feed needs a molar_flow or a mass flow.")
            mws = self._molecular_weights(feed, z)
            mw_mix = sum(z[n] * mws[n] for n in z)  # g/mol
            f_mol_s = mass.value / (mw_mix / 1000.0)
        else:
            f_mol_s = self._si(flow, "feed molar flow")
        if f_mol_s <= 0:
            raise ValueError(f"{self.name}: the feed flow must be positive.")

        return {
            "z": z,
            "F": f_mol_s,
            "temperature_k": feed.temperature.value if feed.temperature is not None else None,
            "pressure_pa": feed.pressure.value if feed.pressure is not None else None,
        }

    def _resolve_name(self, name: str) -> str:
        """Map a feed or key name onto the component data's own name."""
        if self.specs.get("components") is not None:
            vle = self._get_vle()
            try:
                return vle.resolve(name)
            except KeyError:
                raise KeyError(f"{self.name}: {name!r} has no component data; known: {sorted(vle.names)}.") from None
        alpha = self.specs.get("relative_volatility")
        if alpha is not None and name not in alpha:
            raise KeyError(f"{self.name}: relative_volatility has no value for {name!r}.")
        return name

    def _molecular_weights(self, feed: MaterialStream, names) -> Dict[str, float]:
        mws = {}
        for n in names:
            if self._vle is not None and n in self._vle.names:
                mws[n] = self._vle.molecular_weight(n)
            elif feed.molecular_weights.get(n):
                mws[n] = float(feed.molecular_weights[n])
            else:
                raise ValueError(f"{self.name}: no molecular weight for {n} to convert the mass basis.")
        return mws

    def _get_vle(self) -> IdealVLE:
        if self._vle is None:
            self._vle = IdealVLE(self.specs["components"])
        return self._vle

    def _key_flows(self, z: Dict[str, float], f: float, lk: str, hk: str) -> Dict[str, float]:
        s = self.specs
        by_recovery = s.get("light_key_recovery") is not None or s.get("heavy_key_recovery") is not None
        by_fraction = s.get("distillate_lk_fraction") is not None or s.get("bottoms_lk_fraction") is not None
        if by_recovery == by_fraction:
            raise ValueError(
                f"{self.name}: give either light_key_recovery and heavy_key_recovery, "
                "or (binary feed) distillate_lk_fraction and bottoms_lk_fraction."
            )
        f_lk, f_hk = f * z[lk], f * z[hk]
        if by_recovery:
            rec_lk, rec_hk = s.get("light_key_recovery"), s.get("heavy_key_recovery")
            if rec_lk is None or rec_hk is None:
                raise ValueError(f"{self.name}: both light_key_recovery and heavy_key_recovery are needed.")
            for label, rec in (("light_key_recovery", rec_lk), ("heavy_key_recovery", rec_hk)):
                if not (0.0 < rec < 1.0):
                    raise ValueError(f"{self.name}: {label} must be between 0 and 1 (exclusive), got {rec}.")
            d_lk = rec_lk * f_lk
            b_hk = rec_hk * f_hk
        else:
            if len(z) != 2:
                raise ValueError(f"{self.name}: product mole fractions are only accepted for a binary feed; use key recoveries.")
            x_d, x_b = s.get("distillate_lk_fraction"), s.get("bottoms_lk_fraction")
            if x_d is None or x_b is None:
                raise ValueError(f"{self.name}: both distillate_lk_fraction and bottoms_lk_fraction are needed.")
            if not (0.0 < x_b < z[lk] < x_d < 1.0):
                raise ValueError(f"{self.name}: need 0 < bottoms_lk_fraction < feed fraction ({z[lk]:.4g}) < distillate_lk_fraction < 1.")
            d_total = f * (z[lk] - x_b) / (x_d - x_b)
            d_lk = d_total * x_d
            b_hk = (f - d_total) * (1.0 - x_b)
        return {"d_lk": d_lk, "b_lk": f_lk - d_lk, "d_hk": f_hk - b_hk, "b_hk": b_hk}

    # ------------------------------------------------------------------
    # Feed condition
    # ------------------------------------------------------------------
    def _feed_q(self, z: Dict[str, float], t_feed: Optional[float], p: float,
                vle: Optional[IdealVLE], assumptions: List[str]) -> Dict[str, Any]:
        if self.specs.get("q") is not None:
            return {"q": float(self.specs["q"]), "source": "specified"}
        if vle is None:
            raise ValueError(f"{self.name}: give q when the column uses relative_volatility instead of components.")
        t_bub = vle.bubble_temperature(z, p)
        t_dew = vle.dew_temperature(z, p)
        if t_feed is None:
            assumptions.append("Feed has no temperature: taken as saturated liquid (q = 1).")
            return {"q": 1.0, "source": "assumed saturated liquid", "bubble_point": t_bub, "dew_point": t_dew}
        if t_feed > t_dew + 1e-6:
            raise ValueError(
                f"{self.name}: the feed ({t_feed:.2f} K) is superheated (dew point {t_dew:.2f} K); "
                "vapour heat capacities are not available, so give q explicitly."
            )
        if t_feed < t_bub:
            # Subcooled: q = 1 + cp_L (T_bubble - T_F) / lambda.
            t_mid = 0.5 * (t_feed + t_bub)
            q = 1.0 + vle.mixture_liquid_cp(z, t_mid) * (t_bub - t_feed) / vle.mixture_latent_heat(z, t_bub)
            source = "subcooled liquid feed"
        else:
            # Two-phase: q is the liquid fraction from an isothermal flash.
            q = 1.0 - vle.flash_vapor_fraction(z, t_feed, p)
            source = "two-phase feed (isothermal flash)"
        return {"q": q, "source": source, "bubble_point": t_bub, "dew_point": t_dew}

    # ------------------------------------------------------------------
    # Design
    # ------------------------------------------------------------------
    def design(self) -> DistillationResults:
        s = self.specs
        warnings: List[str] = []
        assumptions: List[str] = [
            "Constant molar overflow, total condenser, partial reboiler counted as a theoretical stage.",
            "Column pressure taken as uniform top to bottom.",
        ]
        lk, hk = s.get("light_key"), s.get("heavy_key")
        if not lk or not hk:
            raise ValueError(f"{self.name}: light_key and heavy_key are required.")
        has_components = s.get("components") is not None
        has_alpha = s.get("relative_volatility") is not None
        if has_components == has_alpha:
            raise ValueError(f"{self.name}: give exactly one of `components` or `relative_volatility`.")

        vle = self._get_vle() if has_components else None
        lk, hk = self._resolve_name(lk), self._resolve_name(hk)
        feed = self._feed_state()
        z, f = feed["z"], feed["F"]
        for key in (lk, hk):
            if z.get(key, 0.0) <= 0:
                raise ValueError(f"{self.name}: key component {key!r} is not in the feed.")

        p = s.get("pressure")
        p = self._si(p, "pressure") if p is not None else feed["pressure_pa"]
        if p is None or p <= 0:
            raise ValueError(f"{self.name}: give the column pressure, or a feed pressure.")
        if vle is not None:
            assumptions.append("Ideal vapour-liquid equilibrium (Raoult's law) from the components' DIPPR vapour pressures.")

        keys = self._key_flows(z, f, lk, hk)

        # Relative volatilities, LK/HK-referenced, and the product split.
        if vle is None:
            alpha_in = {n: float(a) for n, a in s["relative_volatility"].items()}
            alpha = {n: alpha_in[n] / alpha_in[hk] for n in z}
            assumptions.append("Constant relative volatilities as specified.")
            split = self._fenske_iteration(z, f, lk, hk, keys, alpha_fixed=alpha)
            t_top = t_bottom = None
        else:
            split = self._fenske_iteration(z, f, lk, hk, keys, vle=vle, p=p)
            t_top, t_bottom = split["t_top"], split["t_bottom"]
            alpha = split["alpha"]
        if alpha[lk] <= 1.0:
            raise ValueError(f"{self.name}: {lk} is not more volatile than {hk} at column conditions (alpha = {alpha[lk]:.4g}).")

        d, b = split["distillate"], split["bottoms"]
        d_total, b_total = sum(d.values()), sum(b.values())
        x_d = {n: d[n] / d_total for n in d}
        x_b = {n: b[n] / b_total for n in b}
        n_min = split["N_min"]

        feed_q = self._feed_q(z, feed["temperature_k"], p, vle, assumptions)
        q = feed_q["q"]

        underwood = shortcut.underwood_minimum_reflux(alpha, z, q, {n: d[n] / f for n in d}, lk, hk)
        r_min = underwood["R_min"]
        if r_min <= 0:
            raise ValueError(f"{self.name}: Underwood gives R_min = {r_min:.4g}; the specification is too loose for a reflux design.")

        if s.get("reflux_ratio") is not None:
            r = float(s["reflux_ratio"])
            if r <= r_min:
                raise ValueError(f"{self.name}: reflux_ratio {r:.4g} is not above R_min = {r_min:.4g}.")
            r_source = "specified"
        else:
            factor = float(self._spec("reflux_ratio_factor"))
            if factor <= 1.0:
                raise ValueError(f"{self.name}: reflux_ratio_factor must be greater than 1.")
            r = factor * r_min
            r_source = f"{factor:g} x R_min"

        gilliland = shortcut.gilliland_stages(n_min, r_min, r, str(self._spec("gilliland_correlation")))
        n_theo = gilliland["N"]
        ratio = shortcut.kirkbride_ratio(z[lk], z[hk], x_b[lk], x_d[hk], b_total, d_total)
        n_rect = n_theo * ratio / (1.0 + ratio)
        n_strip = n_theo - n_rect
        feed_stage = int(round(n_rect)) + 1

        # Internal flows (mol/s).
        l_top = r * d_total
        v_top = (r + 1.0) * d_total
        l_bottom = l_top + q * f
        v_bottom = v_top - (1.0 - q) * f
        if v_bottom <= 0:
            raise ValueError(f"{self.name}: no boil-up below the feed (V' = {v_bottom:.4g} mol/s); increase the reflux or check q.")

        data: Dict[str, Any] = {
            "name": self.name,
            "light_key": lk,
            "heavy_key": hk,
            "method": "Fenske-Underwood-Gilliland-Kirkbride",
            "gilliland_correlation": str(self._spec("gilliland_correlation")).lower(),
            "pressure": Pressure(p, "Pa"),
            "feed": {"F": MolarFlowRate(f, "mol/s"), "z": z, "q": q, "q_source": feed_q["source"]},
            "distillate": {"D": MolarFlowRate(d_total, "mol/s"), "x": x_d, "flows": {n: MolarFlowRate(v, "mol/s") for n, v in d.items()}},
            "bottoms": {"B": MolarFlowRate(b_total, "mol/s"), "x": x_b, "flows": {n: MolarFlowRate(v, "mol/s") for n, v in b.items()}},
            "key_recoveries": {"light_key_to_distillate": d[lk] / (f * z[lk]), "heavy_key_to_bottoms": b[hk] / (f * z[hk])},
            "relative_volatility": alpha,
            "N_min": n_min,
            "underwood_theta": underwood["theta"],
            "R_min": r_min,
            "reflux_ratio": r,
            "reflux_ratio_source": r_source,
            "R_over_R_min": r / r_min,
            "gilliland": {"X": gilliland["X"], "Y": gilliland["Y"]},
            "N_theoretical": n_theo,
            "N_rectifying": n_rect,
            "N_stripping": n_strip,
            "feed_stage": feed_stage,
            "internal_flows": {
                "L_rectifying": MolarFlowRate(l_top, "mol/s"),
                "V_rectifying": MolarFlowRate(v_top, "mol/s"),
                "L_stripping": MolarFlowRate(l_bottom, "mol/s"),
                "V_stripping": MolarFlowRate(v_bottom, "mol/s"),
            },
            "assumptions": assumptions,
            "warnings": warnings,
        }
        if underwood["distributing_components"]:
            data["underwood_distillate_at_R_min"] = {
                n: MolarFlowRate(underwood["distillate"][n] * f, "mol/s") for n in underwood["distributing_components"]
            }
        if "alpha_top" in split:
            data["relative_volatility_top"] = split["alpha_top"]
            data["relative_volatility_bottom"] = split["alpha_bottom"]
        if feed_q.get("bubble_point") is not None:
            data["feed"]["bubble_point"] = Temperature(feed_q["bubble_point"], "K")
            data["feed"]["dew_point"] = Temperature(feed_q["dew_point"], "K")

        if len(z) == 2:
            data["mccabe_thiele"] = self._mccabe_thiele(vle, alpha, lk, hk, x_d[lk], x_b[lk], z[lk], q, r, p)

        if vle is not None:
            self._thermal_and_sizing(data, vle, p, x_d, x_b, z, t_top, t_bottom,
                                     l_top, v_top, l_bottom, v_bottom, alpha[lk], n_theo, n_rect)
        elif s.get("tray_efficiency") is not None:
            self._actual_trays(data, float(s["tray_efficiency"]), n_theo, n_rect, "specified")
        else:
            warnings.append("No component data: temperatures, duties, efficiency and diameter were not calculated.")

        self._results = DistillationResults(data)
        return self._results

    def _fenske_iteration(self, z, f, lk, hk, keys, alpha_fixed=None, vle=None, p=None) -> Dict[str, Any]:
        """
        Fenske N_min and the total-reflux split. With component data the
        volatilities are the geometric mean of the top (dew point of the
        distillate) and bottom (bubble point of the bottoms) values, which
        depend on the split, so iterate.
        """
        feed_flows = {n: f * z[n] for n in z}
        if alpha_fixed is not None:
            alpha = alpha_fixed
            n_min = shortcut.fenske_minimum_stages(keys["d_lk"], keys["b_lk"], keys["d_hk"], keys["b_hk"], alpha[lk])
            d, b = shortcut.fenske_split(feed_flows, alpha, hk, keys["d_hk"], keys["b_hk"], n_min)
            d[lk], b[lk] = keys["d_lk"], keys["b_lk"]
            return {"alpha": alpha, "N_min": n_min, "distillate": d, "bottoms": b}

        t_feed = vle.bubble_temperature(z, p)
        alpha = vle.relative_volatilities(t_feed, p, hk)
        alpha = {n: alpha[n] for n in z}
        n_min_prev = None
        for _ in range(100):
            if alpha[lk] <= 1.0:
                raise ValueError(f"{self.name}: {lk} is not more volatile than {hk} (alpha = {alpha[lk]:.4g}).")
            n_min = shortcut.fenske_minimum_stages(keys["d_lk"], keys["b_lk"], keys["d_hk"], keys["b_hk"], alpha[lk])
            d, b = shortcut.fenske_split(feed_flows, alpha, hk, keys["d_hk"], keys["b_hk"], n_min)
            d[lk], b[lk] = keys["d_lk"], keys["b_lk"]
            t_top = vle.dew_temperature(d, p)
            t_bottom = vle.bubble_temperature(b, p)
            a_top = vle.relative_volatilities(t_top, p, hk)
            a_bot = vle.relative_volatilities(t_bottom, p, hk)
            alpha = {n: math.sqrt(a_top[n] * a_bot[n]) for n in z}
            if n_min_prev is not None and abs(n_min - n_min_prev) < 1e-9:
                break
            n_min_prev = n_min
        n_min = shortcut.fenske_minimum_stages(keys["d_lk"], keys["b_lk"], keys["d_hk"], keys["b_hk"], alpha[lk])
        d, b = shortcut.fenske_split(feed_flows, alpha, hk, keys["d_hk"], keys["b_hk"], n_min)
        d[lk], b[lk] = keys["d_lk"], keys["b_lk"]
        return {
            "alpha": alpha,
            "alpha_top": {n: a_top[n] for n in z},
            "alpha_bottom": {n: a_bot[n] for n in z},
            "N_min": n_min,
            "distillate": d,
            "bottoms": b,
            "t_top": vle.dew_temperature(d, p),
            "t_bottom": vle.bubble_temperature(b, p),
        }

    def _mccabe_thiele(self, vle, alpha, lk, hk, x_d, x_b, z_f, q, r, p) -> Dict[str, Any]:
        if vle is None:
            y_eq, x_eq = mccabe_thiele.constant_alpha_curves(alpha[lk])
            curve = f"constant alpha = {alpha[lk]:.4g}"
        else:
            def y_eq(x):
                _, y = vle.equilibrium_vapor({lk: x, hk: 1.0 - x}, p)
                return y.get(lk, 0.0)

            def x_eq(y):
                t = vle.dew_temperature({lk: y, hk: 1.0 - y}, p)
                return y * p / vle.psat(lk, t)

            curve = "ideal VLE at column pressure"
        try:
            mt = mccabe_thiele.step_stages(x_d, x_b, z_f, q, r, y_eq, x_eq)
        except ValueError as exc:
            return {"error": str(exc), "equilibrium": curve}
        return {
            "N_theoretical": mt["N"],
            "N_fractional": mt["N_fractional"],
            "feed_stage": mt["feed_stage"],
            "equilibrium": curve,
            "stages": mt["stages"],
        }

    def _actual_trays(self, data, efficiency, n_theo, n_rect, source) -> None:
        if not (0.0 < efficiency <= 1.0):
            raise ValueError(f"{self.name}: tray efficiency must be in (0, 1], got {efficiency}.")
        # The partial reboiler is a theoretical stage but not a tray.
        trays_theoretical = max(n_theo - 1.0, 0.0)
        trays = int(math.ceil(trays_theoretical / efficiency - 1e-9))
        trays_above_feed = int(math.ceil(round(n_rect) / efficiency - 1e-9))
        data["tray_efficiency"] = efficiency
        data["tray_efficiency_source"] = source
        data["actual_trays"] = trays
        data["feed_tray"] = min(trays_above_feed + 1, trays)

    def _thermal_and_sizing(self, data, vle, p, x_d, x_b, z, t_top, t_bottom,
                            l_top, v_top, l_bottom, v_bottom, alpha_lk, n_theo, n_rect) -> None:
        s = self.specs
        warnings, assumptions = data["warnings"], data["assumptions"]

        t_condenser = vle.bubble_temperature(x_d, p)
        _, y_reboiler = vle.equilibrium_vapor(x_b, p)
        data["temperatures"] = {
            "condenser": Temperature(t_condenser, "K"),
            "top_stage": Temperature(t_top, "K"),
            "reboiler": Temperature(t_bottom, "K"),
        }

        # Duties: the overhead vapour is condensed to saturated liquid; the
        # boil-up is vaporised from the bottoms liquid.
        q_cond = v_top * vle.mixture_latent_heat(x_d, t_condenser)
        q_reb = v_bottom * vle.mixture_latent_heat(x_b, t_bottom)
        data["condenser_duty"] = HeatFlow(q_cond, "W")
        data["reboiler_duty"] = HeatFlow(q_reb, "W")
        assumptions.append("Duties from latent heats only (saturated reflux, sensible heat of products neglected).")

        # Efficiency: O'Connell with the feed liquid viscosity at the mean column temperature.
        t_mean = 0.5 * (t_top + t_bottom)
        mu = vle.mixture_liquid_viscosity(z, t_mean)
        data["liquid_viscosity"] = Viscosity(mu, "Pa·s")
        if s.get("tray_efficiency") is not None:
            self._actual_trays(data, float(s["tray_efficiency"]), n_theo, n_rect, "specified")
        else:
            eff = hydraulics.oconnell_efficiency(mu * 1000.0, alpha_lk)
            if eff > 1.0:
                warnings.append(f"O'Connell gives an efficiency of {eff:.3f}; capped at 1.0.")
                eff = 1.0
            self._actual_trays(data, eff, n_theo, n_rect, "O'Connell")

        # Diameter at the top and bottom of the column; the larger one governs.
        spacing = self._si(self._spec("tray_spacing"), "tray_spacing")
        flood = float(self._spec("flood_fraction"))
        if flood > hydraulics.MAX_FLOOD_FRACTION:
            warnings.append(f"flood_fraction {flood:.2f} is above the {hydraulics.MAX_FLOOD_FRACTION} design limit of the flooding correlation.")
        downcomer = float(self._spec("downcomer_area_fraction"))
        sigma = float(self._spec("surface_tension"))
        k_factor = float(self._spec("flooding_k_factor"))
        if s.get("surface_tension") is None:
            assumptions.append("Surface tension 0.020 N/m (no component data); give `surface_tension` to correct the flooding velocity.")
        for key, label in (("tray_spacing", "Tray spacing 0.6 m"), ("flood_fraction", "Design at 80 % of flooding"),
                           ("downcomer_area_fraction", "Downcomer area 12 % of column area")):
            if s.get(key) is None:
                assumptions.append(f"{label} (default).")

        sections = {}
        for section, x_liq, y_vap, t_liq, t_vap, l_mol, v_mol in (
            ("top", x_d, x_d, t_condenser, t_top, l_top, v_top),
            ("bottom", x_b, y_reboiler, t_bottom, t_bottom, l_bottom, v_bottom),
        ):
            mw_l, mw_v = vle.mixture_mw(x_liq), vle.mixture_mw(y_vap)
            rho_l = vle.mixture_liquid_density(x_liq, t_liq)
            rho_v = vle.mixture_vapor_density(y_vap, t_vap, p)
            l_mass, v_mass = l_mol * mw_l / 1000.0, v_mol * mw_v / 1000.0
            sizing = hydraulics.tray_diameter(v_mass, l_mass, rho_v, rho_l, spacing, sigma, flood, downcomer, k_factor)
            warnings.extend(f"{section} section: {w}" for w in sizing["warnings"])
            sections[section] = {
                "liquid_density": Density(rho_l, "kg/m3"),
                "vapor_density": Density(rho_v, "kg/m3"),
                "flow_parameter": sizing["flow_parameter"],
                "csb": Velocity(sizing["csb"], "m/s"),
                "flooding_velocity": Velocity(sizing["flooding_velocity"], "m/s"),
                "net_velocity": Velocity(sizing["net_velocity"], "m/s"),
                "area": Area(sizing["area"], "m2"),
                "diameter": Diameter(sizing["diameter"], "m"),
            }
        governing = max(sections, key=lambda k: sections[k]["diameter"].value)
        data["hydraulics"] = sections
        data["diameter"] = sections[governing]["diameter"]
        data["diameter_governed_by"] = governing
        data["tray_spacing"] = Length(spacing, "m")
        data["flood_fraction"] = flood
        data["tray_section_height"] = Length(data["actual_trays"] * spacing, "m")

    # ------------------------------------------------------------------
    # Flowsheet
    # ------------------------------------------------------------------
    def simulate(self) -> Dict[str, Any]:
        """
        Solve the column as a flowsheet unit: run design() and write the
        products to the streams on the ``distillate`` and ``bottoms`` ports.
        """
        for port in ("distillate", "bottoms"):
            if self.outlets[port] is None:
                raise ValueError(f"{self.name}: outlet port '{port}' is not connected.")
        results = self.design()
        data = results.data
        temps = data.get("temperatures", {})
        vle = self._vle
        for port, key, t_key in (("distillate", "D", "condenser"), ("bottoms", "B", "reboiler")):
            product = data[port]
            self._write_product(self.outlets[port], product["x"], product[key], data["pressure"], temps.get(t_key), vle)
        return {
            "distillate_flow": data["distillate"]["D"],
            "bottoms_flow": data["bottoms"]["B"],
            "N_theoretical": data["N_theoretical"],
            "reflux_ratio": data["reflux_ratio"],
            "condenser_duty": data.get("condenser_duty"),
            "reboiler_duty": data.get("reboiler_duty"),
            "diameter": data.get("diameter"),
        }

    @staticmethod
    def _write_product(stream: MaterialStream, x: Dict[str, float], flow: MolarFlowRate,
                       pressure: Pressure, temperature: Optional[Temperature], vle: Optional[IdealVLE]) -> None:
        stream.components = dict(x)
        stream.basis = "mole"
        stream.component = None
        stream._molar_flow = flow
        stream._mass_flow = None
        stream.flow_rate = None
        stream.pressure = pressure
        stream.temperature = temperature
        stream.phase = "liquid"
        stream.specific_heat = None
        if vle is not None:
            stream.molecular_weights = {n: vle.molecular_weight(n) for n in x}
            # MaterialStream.mass_flow() does not derive a mass flow from a molar one.
            stream._mass_flow = MassFlowRate(flow.value * vle.mixture_mw(x) / 1000.0, "kg/s")
            stream.density = Density(vle.mixture_liquid_density(x, temperature.value), "kg/m3") if temperature is not None else None
        else:
            stream.density = None

    def results(self) -> DistillationResults:
        if self._results is None:
            raise RuntimeError("Run the column first with design() or simulate().")
        return self._results

    def summary(self) -> Optional[str]:
        return self._results.summary() if self._results is not None else None
