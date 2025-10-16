"""
Kern Method Heat Exchanger Helper Functions
-------------------------------------------
Provides simplified heat exchanger design calculations:
- Log mean temperature difference (LMTD)
- Overall heat transfer coefficient (U)
- Shell-side and tube-side pressure drop (single-phase)
- Area estimation
- Fouling & wall resistance included

References:
-----------
- Kern, D.Q., "Process Heat Transfer", 1950
- TEMA Standards
"""

import math
from typing import Optional

# ----------------------------------------------------------------------
# Log Mean Temperature Difference
# ----------------------------------------------------------------------
def lmtd(T_hot_in: float, T_hot_out: float, T_cold_in: float, T_cold_out: float, Ft: Optional[float] = 1.0) -> float:
    """
    Calculate log mean temperature difference, optionally corrected by Ft
    """
    deltaT1 = T_hot_in - T_cold_out
    deltaT2 = T_hot_out - T_cold_in
    if abs(deltaT1 - deltaT2) < 1e-6:
        return deltaT1 * Ft
    return ((deltaT1 - deltaT2) / math.log(deltaT1 / deltaT2)) * Ft

# ----------------------------------------------------------------------
# Overall Heat Transfer Coefficient
# ----------------------------------------------------------------------
def overall_U(h_tube: float, h_shell: float, R_fouling_tube: float = 0.0002,
              R_fouling_shell: float = 0.0002, R_wall: float = 0.001) -> float:
    """
    Compute overall heat transfer coefficient, including fouling & wall
    """
    return 1 / (1/h_tube + R_fouling_tube + R_wall + R_fouling_shell + 1/h_shell)

# ----------------------------------------------------------------------
# Tube-side Reynolds number
# ----------------------------------------------------------------------
def reynolds_tube(rho: float, v: float, D_i: float, mu: float) -> float:
    return rho * v * D_i / mu

# ----------------------------------------------------------------------
# Nusselt number (Dittus-Boelter)
# ----------------------------------------------------------------------
def nusselt_tube(Re: float, Pr: float, heating: bool = True) -> float:
    """
    Dittus-Boelter correlation
    """
    n = 0.3 if heating else 0.4
    return 0.023 * Re**0.8 * Pr**n

# ----------------------------------------------------------------------
# Tube-side convective HTC
# ----------------------------------------------------------------------
def tube_htc(k: float, D_i: float, Re: float, Pr: float, heating: bool = True) -> float:
    Nu = nusselt_tube(Re, Pr, heating)
    return Nu * k / D_i

# ----------------------------------------------------------------------
# Shell-side HTC (simplified Kern method)
# ----------------------------------------------------------------------
def shell_htc(rho: float, mu: float, k: float, D_s: float, m_dot: float, Pr: float, N_tubes: int) -> float:
    """
    Simplified Kern method for crossflow shell-side single-phase
    """
    v = m_dot / (rho * math.pi * D_s**2 / 4)  # average velocity
    Re = rho * v * D_s / mu
    Nu = 0.36 * Re**0.55 * Pr**0.33  # Kern correlation
    return Nu * k / D_s

# ----------------------------------------------------------------------
# Heat duty
# ----------------------------------------------------------------------
def heat_duty(m_dot_hot: float, cp_hot: float, T_hot_in: float, T_hot_out: float) -> float:
    return m_dot_hot * cp_hot * (T_hot_in - T_hot_out)

# ----------------------------------------------------------------------
# Required area
# ----------------------------------------------------------------------
def required_area(Q: float, U: float, LMTD: float) -> float:
    return Q / (U * LMTD)

# ----------------------------------------------------------------------
# Tube-side velocity
# ----------------------------------------------------------------------
def tube_velocity(m_dot: float, rho: float, D_i: float, N_tubes: int) -> float:
    A_total = N_tubes * math.pi * D_i**2 / 4
    return m_dot / (rho * A_total)

# ----------------------------------------------------------------------
# Tube-side pressure drop (single-phase)
# ----------------------------------------------------------------------
def tube_pressure_drop(rho: float, v: float, L: float, D_i: float, f: float = 0.02) -> float:
    """
    Simple Darcy–Weisbach tube-side ΔP
    """
    return f * L / D_i * 0.5 * rho * v**2

# ----------------------------------------------------------------------
# Bundle diameter rough estimate
# ----------------------------------------------------------------------
def bundle_diameter(N_tubes: int, D_o: float, pitch_ratio: float = 1.25, layout: str = "triangular") -> float:
    pitch_factor = 0.866 if layout.lower() == "triangular" else 1.0
    return math.sqrt(N_tubes * D_o**2 / pitch_factor)

