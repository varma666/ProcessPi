"""
Binary McCabe-Thiele stage stepping (constant molar overflow, total condenser,
partial reboiler counted as a stage).

Stepping starts at the top, (x_D, x_D), and alternates a horizontal step to the
equilibrium curve with a vertical step to the operating line. The feed goes on
the first stage whose liquid is leaner than the intersection of the two
operating lines (the optimum feed stage), and the stepping ends on the first
stage whose liquid reaches x_B; that stage is the reboiler.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple


def operating_lines_intersection(x_d: float, z_f: float, q: float, r: float) -> Tuple[float, float]:
    """Where the rectifying line meets the q-line."""
    slope_r = r / (r + 1.0)
    intercept_r = x_d / (r + 1.0)
    if abs(q - 1.0) < 1e-12:
        x = z_f
    else:
        slope_q = q / (q - 1.0)
        intercept_q = -z_f / (q - 1.0)
        if abs(slope_r - slope_q) < 1e-15:
            raise ValueError("The rectifying line is parallel to the q-line.")
        x = (intercept_q - intercept_r) / (slope_r - slope_q)
    return x, slope_r * x + intercept_r


def constant_alpha_curves(alpha: float) -> Tuple[Callable[[float], float], Callable[[float], float]]:
    """y(x) and x(y) for a constant relative volatility."""
    if alpha <= 1.0:
        raise ValueError("alpha must be greater than 1.")

    def y_eq(x: float) -> float:
        return alpha * x / (1.0 + (alpha - 1.0) * x)

    def x_eq(y: float) -> float:
        return y / (alpha - (alpha - 1.0) * y)

    return y_eq, x_eq


def step_stages(x_d: float, x_b: float, z_f: float, q: float, r: float,
                y_eq: Callable[[float], float], x_eq: Callable[[float], float],
                max_stages: int = 500) -> Dict:
    """
    Step off theoretical stages for a binary column.

    Args:
        x_d, x_b, z_f: light-component mole fractions in distillate, bottoms, feed.
        q: feed thermal condition.
        r: reflux ratio L/D.
        y_eq: equilibrium vapour composition as a function of liquid composition.
        x_eq: its inverse.
    Returns:
        N (stages, reboiler included), N_fractional (last stage counted as the
        fraction of a step actually needed), feed_stage (from the top),
        the operating-line intersection and the stage compositions.
    """
    if not (0.0 < x_b < z_f < x_d < 1.0):
        raise ValueError("McCabe-Thiele needs 0 < x_B < z_F < x_D < 1 (light-component fractions).")
    if r <= 0:
        raise ValueError("Reflux ratio must be positive.")

    x_int, y_int = operating_lines_intersection(x_d, z_f, q, r)
    if not (x_b < x_int < x_d):
        raise ValueError(f"The operating lines meet at x = {x_int:.4g}, outside x_B..x_D; check q and the compositions.")
    if y_int >= y_eq(x_int):
        raise ValueError(f"Reflux ratio {r:.4g} is at or below the minimum: the operating lines cross the equilibrium curve (pinch).")

    slope_r, intercept_r = r / (r + 1.0), x_d / (r + 1.0)
    slope_s = (y_int - x_b) / (x_int - x_b)
    intercept_s = x_b - slope_s * x_b

    stages: List[Tuple[float, float]] = []
    feed_stage = None
    y = x_d
    x_prev = x_d
    for n in range(1, max_stages + 1):
        x = x_eq(y)
        stages.append((x, y))
        if feed_stage is None and x < x_int:
            feed_stage = n
        if x <= x_b:
            fraction = (x_prev - x_b) / (x_prev - x)
            return {
                "N": n,
                "N_fractional": n - 1 + fraction,
                "feed_stage": feed_stage if feed_stage is not None else n,
                "intersection": (x_int, y_int),
                "stages": stages,
            }
        if feed_stage is None:
            y = slope_r * x + intercept_r
        else:
            y = slope_s * x + intercept_s
        x_prev = x
    raise ValueError(f"No convergence within {max_stages} stages; the design is too close to a pinch.")
