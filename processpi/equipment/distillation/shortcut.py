"""
Fenske-Underwood-Gilliland-Kirkbride shortcut design for a simple column
(one feed, a distillate and a bottoms product, constant molar overflow,
constant relative volatility).

Sources for the equations used here:
- Fenske minimum stages and the total-reflux component split, Underwood feed
  and distillate equations, Kirkbride feed location, Eduljee's form of the
  Gilliland correlation: OpenExamPrep PE Chemical study guide, section 11.4
  "Multicomponent Distillation Fundamentals and Key Components",
  https://open-exam-prep.com/study-guides/pe-chemical/distillation-operations/multicomponent-distillation
  (its worked example is reproduced in tests/test_distillation_shortcut.py).
- Molokanov et al. (1972) form of the Gilliland correlation: M. A. Soliman,
  "A Shortcut Method for Binary Distillation Column Design",
  J. King Saud Univ. Eng. Sci. 21(1) (2009) 1-5, eq. (1).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

GILLILAND_CORRELATIONS = ("molokanov", "eduljee")


def fenske_minimum_stages(d_lk: float, b_lk: float, d_hk: float, b_hk: float, alpha_lk_hk: float) -> float:
    """
    N_min = ln[(d_LK / b_LK) (b_HK / d_HK)] / ln(alpha_LK,HK).

    N_min counts equilibrium stages at total reflux, the partial reboiler
    included and a total condenser not.
    """
    if alpha_lk_hk <= 1.0:
        raise ValueError(f"The light key must be more volatile than the heavy key (alpha = {alpha_lk_hk:.4g}).")
    for label, value in (("d_LK", d_lk), ("b_LK", b_lk), ("d_HK", d_hk), ("b_HK", b_hk)):
        if value <= 0:
            raise ValueError(f"{label} must be positive for the Fenske equation, got {value}.")
    separation = (d_lk / b_lk) * (b_hk / d_hk)
    if separation <= 1.0:
        raise ValueError("The specified key recoveries ask for no separation at all.")
    return math.log(separation) / math.log(alpha_lk_hk)


def fenske_split(feed: Dict[str, float], alpha_hk: Dict[str, float], heavy_key: str,
                 d_hk: float, b_hk: float, n_min: float) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Total-reflux split of every component: d_i / b_i = (d_HK / b_HK) alpha_i,HK ^ N_min.

    Args:
        feed: component molar flows.
        alpha_hk: relative volatilities with respect to the heavy key.
    Returns:
        (distillate flows, bottoms flows).
    """
    ratio_hk = d_hk / b_hk
    d, b = {}, {}
    for name, f in feed.items():
        if name == heavy_key:
            d[name], b[name] = d_hk, b_hk
            continue
        # Work with the logarithm: alpha^N_min overflows for very light components.
        log_ratio = math.log(ratio_hk) + n_min * math.log(alpha_hk[name])
        if log_ratio > 700:
            frac_d = 1.0
        elif log_ratio < -700:
            frac_d = 0.0
        else:
            r = math.exp(log_ratio)
            frac_d = r / (1.0 + r)
        d[name] = f * frac_d
        b[name] = f - d[name]
    return d, b


def _underwood_feed_function(theta: float, alpha: Dict[str, float], z: Dict[str, float], q: float) -> float:
    return sum(alpha[n] * z[n] / (alpha[n] - theta) for n in z) - (1.0 - q)


def underwood_roots(alpha: Dict[str, float], z: Dict[str, float], q: float,
                    light_key: str, heavy_key: str) -> List[float]:
    """
    Roots theta of sum_i alpha_i z_i / (alpha_i - theta) = 1 - q lying between
    alpha_HK and alpha_LK: one root in each gap between neighbouring
    volatilities, so one root for adjacent keys and one more for every
    component whose volatility lies between the keys.
    """
    present = [n for n in z if z[n] > 0]
    ordered = sorted(present, key=lambda n: alpha[n], reverse=True)
    i_lk, i_hk = ordered.index(light_key), ordered.index(heavy_key)
    if i_lk >= i_hk:
        raise ValueError("The light key must be more volatile than the heavy key.")
    roots = []
    for j in range(i_lk, i_hk):
        upper, lower = alpha[ordered[j]], alpha[ordered[j + 1]]
        if upper - lower < 1e-12:
            raise ValueError(f"{ordered[j]} and {ordered[j + 1]} have the same volatility; Underwood needs distinct values.")
        # The function rises from -inf just above `lower` to +inf just below
        # `upper`, so a bracket always exists; shrink it off the poles.
        span = upper - lower
        lo, hi = lower + 1e-12 * span, upper - 1e-12 * span
        f = lambda t: _underwood_feed_function(t, alpha, z, q)
        for _ in range(300):
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                hi = mid
            else:
                lo = mid
            if hi - lo < 1e-14 * max(1.0, upper):
                break
        roots.append(0.5 * (lo + hi))
    return roots


def underwood_minimum_reflux(alpha: Dict[str, float], z: Dict[str, float], q: float,
                             distillate: Dict[str, float], light_key: str, heavy_key: str) -> Dict:
    """
    Underwood minimum reflux.

    With adjacent keys, V_min = sum_i alpha_i d_i / (alpha_i - theta). With
    components between the keys there is one root per gap, and the equations
    are solved together for V_min and the distillate flows of those
    distributing components (all other d_i are taken from `distillate`).

    Args:
        alpha: relative volatilities (any common reference).
        z: feed mole fractions.
        q: feed thermal condition.
        distillate: distillate molar flows (absolute units, any).
    Returns:
        dict with theta (list), V_min, D, R_min and the distillate flows used.
    """
    roots = underwood_roots(alpha, z, q, light_key, heavy_key)
    a_lk, a_hk = alpha[light_key], alpha[heavy_key]
    between = [n for n in z if z[n] > 0 and a_hk < alpha[n] < a_lk]
    d = dict(distillate)

    if between:
        # Unknowns: V_min, then d_i for each component between the keys.
        # Row k: V_min - sum_between alpha_i d_i / (alpha_i - theta_k) = sum_fixed alpha_i d_i / (alpha_i - theta_k)
        rows, rhs = [], []
        for theta in roots:
            rows.append([1.0] + [-alpha[n] / (alpha[n] - theta) for n in between])
            rhs.append(sum(alpha[n] * d[n] / (alpha[n] - theta) for n in d if n not in between))
        solution = _solve_linear(rows, rhs)
        v_min = solution[0]
        for name, value in zip(between, solution[1:]):
            d[name] = value
    else:
        theta = roots[0]
        v_min = sum(alpha[n] * d[n] / (alpha[n] - theta) for n in d)

    d_total = sum(d.values())
    return {
        "theta": roots,
        "V_min": v_min,
        "D": d_total,
        "R_min": v_min / d_total - 1.0,
        "distillate": d,
        "distributing_components": between,
    }


def gilliland_stages(n_min: float, r_min: float, r: float, correlation: str = "molokanov") -> Dict[str, float]:
    """
    Theoretical stages N at reflux ratio R from the Gilliland correlation,
    X = (R - R_min) / (R + 1), Y = (N - N_min) / (N + 1):

    - molokanov: Y = 1 - exp[((1 + 54.4 X) / (11 + 117.2 X)) ((X - 1) / X^0.5)]
    - eduljee:   Y = 0.75 (1 - X^0.5668)
    """
    correlation = correlation.lower()
    if correlation not in GILLILAND_CORRELATIONS:
        raise ValueError(f"correlation must be one of {GILLILAND_CORRELATIONS}, got {correlation!r}.")
    if r <= r_min:
        raise ValueError(f"Reflux ratio {r:.4g} is not above the minimum {r_min:.4g}; the column would need infinite stages.")
    x = (r - r_min) / (r + 1.0)
    if correlation == "molokanov":
        y = 1.0 - math.exp(((1.0 + 54.4 * x) / (11.0 + 117.2 * x)) * ((x - 1.0) / math.sqrt(x)))
    else:
        y = 0.75 * (1.0 - x ** 0.5668)
    n = (n_min + y) / (1.0 - y)
    return {"X": x, "Y": y, "N": n}


def kirkbride_ratio(z_lk: float, z_hk: float, x_b_lk: float, x_d_hk: float, b: float, d: float) -> float:
    """
    N_R / N_S from log10(N_R / N_S) = 0.206 log10[(z_HK / z_LK) (x_B,LK / x_D,HK)^2 (B / D)].
    """
    for label, value in (("z_LK", z_lk), ("z_HK", z_hk), ("x_B,LK", x_b_lk), ("x_D,HK", x_d_hk), ("B", b), ("D", d)):
        if value <= 0:
            raise ValueError(f"{label} must be positive for the Kirkbride equation, got {value}.")
    group = (z_hk / z_lk) * (x_b_lk / x_d_hk) ** 2 * (b / d)
    return 10.0 ** (0.206 * math.log10(group))


def _solve_linear(a: List[List[float]], b: List[float]) -> List[float]:
    """Gaussian elimination with partial pivoting for the small Underwood systems."""
    n = len(b)
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-300:
            raise ValueError("Singular Underwood system.")
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= factor * m[col][c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (m[r][n] - sum(m[r][c] * x[c] for c in range(r + 1, n))) / m[r][r]
    return x
