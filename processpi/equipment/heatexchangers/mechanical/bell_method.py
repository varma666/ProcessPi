"""
Bell–Delaware Shell-Side Calculations
-------------------------------------
Provides all helper functions for shell-side pressure drop,
baffle correction, and velocity/flooding checks.

References:
-----------
- Bell, K.J., AIChE 1963
- Kern, D.Q., Process Heat Transfer
- TEMA Standards
"""

import math
from typing import Optional

# Constants
GRAVITY = 9.81  # m/s²
GAMMA_MAX = 0.8  # fraction of max allowable vapor velocity
DEFAULT_BAFFLE_CUT = 0.25

# ----------------------------------------------------------------------
# Shell-side velocity and Re
# ----------------------------------------------------------------------
def shell_velocity(m_dot_s: float, rho_s: float, D_o: float, D_s: float, baffle_cut: float = DEFAULT_BAFFLE_CUT) -> float:
    """
    Computes equivalent shell-side velocity for crossflow between baffles
    """
    A_cross = math.pi * (D_s**2 - D_o**2) / 4 * (1 - baffle_cut)
    return m_dot_s / (rho_s * A_cross)

def reynolds_shell(rho_s: float, v_s: float, D_o: float, mu_s: float) -> float:
    """
    Shell-side Reynolds number
    """
    return rho_s * v_s * D_o / mu_s

# ----------------------------------------------------------------------
# Friction factor
# ----------------------------------------------------------------------
def friction_factor_shell(Re_s: float) -> float:
    """
    Turbulent friction factor for smooth tubes, Dittus–Boelter type
    """
    if Re_s < 2300:
        return 64 / Re_s  # laminar
    else:
        return 0.316 * Re_s**(-0.25)  # turbulent

# ----------------------------------------------------------------------
# Bell–Delaware pressure drop
# ----------------------------------------------------------------------
def bell_delaware_pressure_drop(
    rho_s: float,
    mu_s: float,
    m_dot_s: float,
    D_s: float,
    D_o: float,
    baffle_cut: float = DEFAULT_BAFFLE_CUT,
    N_baffles: int = 10,
    passes: int = 1
) -> float:
    """
    Calculates shell-side pressure drop using simplified Bell–Delaware.
    Includes crossflow correction, baffle factor, and friction factor.
    """
    v_s = shell_velocity(m_dot_s, rho_s, D_o, D_s, baffle_cut)
    Re_s = reynolds_shell(rho_s, v_s, D_o, mu_s)
    f = friction_factor_shell(Re_s)
    deltaP = f * N_baffles * rho_s * v_s**2 / 2
    return deltaP

# ----------------------------------------------------------------------
# Flooding / velocity limits
# ----------------------------------------------------------------------
def flooding_velocity(rho_v: float, rho_l: float, tube_area: float) -> float:
    """
    Maximum allowable vapor velocity before flooding (vertical)
    """
    return math.sqrt((rho_l - rho_v) * GRAVITY * tube_area / rho_v)

def check_flooding(vapor_mass_flow: float, rho_v: float, rho_l: float, tube_area: float,
                   vertical: bool = True, gamma_max: float = GAMMA_MAX) -> bool:
    """
    Check if the shell/tube is at risk of flooding.
    """
    if not vertical:
        return False
    v_max = flooding_velocity(rho_v, rho_l, tube_area)
    v_actual = vapor_mass_flow / (rho_v * tube_area)
    return v_actual > gamma_max * v_max

# ----------------------------------------------------------------------
# Baffle correction factor
# ----------------------------------------------------------------------
def baffle_correction_factor(cut: float, pitch_ratio: float = 0.866) -> float:
    """
    Simple crossflow baffle correction factor.
    """
    return 0.8 * (1 - cut) * pitch_ratio

