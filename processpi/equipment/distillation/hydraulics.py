"""
Tray column hydraulics: diameter from Fair's entrainment-flooding correlation,
overall tray efficiency from O'Connell.

Sources:
- Flooding velocity, flow parameter and the 85 % design limit:
  C. A. P. Souza et al., "Improved Correlations for Threshold Flooding and
  Entrainment in Sieve Trays in Distillation/Absorption Columns",
  Ind. Eng. Chem. Res. 64 (2025) 2256-2273, https://doi.org/10.1021/acs.iecr.4c03115,
  eqs. (1)-(3):  u_n <= 0.85 u_flood,
  u_flood = K C_sb sqrt((rho_L - rho_V) / rho_V) (sigma / 0.02)^0.2,
  F_LV = (L / V) sqrt(rho_V / rho_L)  (mass flows).
- C_sb, Lygeros and Magoulas (Hydrocarbon Processing 65(12) (1986) 43) fit of
  Fair's chart, as given by Souza et al. eq. (5) and Table 1:
  C_sb [m/s] = 0.0105 + 0.1496 l_t^0.755 exp(-1.463 F_LV^0.842), l_t in m.
  Souza et al. Table 5 puts its error against Fair's curves at 2.5-5 %
  on average and 4.6-21.5 % at worst, for tray spacings 0.1524-0.9144 m.
- Overall (section) efficiency, O'Connell: eta = 0.503 (mu_L alpha)^-0.226,
  mu_L in mPa.s. M. Duss and R. Taylor, "Predict Distillation Tray
  Efficiency", Chem. Eng. Prog. July 2018, 24-30, eq. (2).
"""

from __future__ import annotations

import math
from typing import Dict, List

# Fair's chart, as digitised by Souza et al.: tray spacings 6 to 36 in.
FAIR_TRAY_SPACING_RANGE_M = (0.1524, 0.9144)
# The flow-parameter axis of Fair's chart (Souza et al. Fig. 1).
FAIR_FLV_RANGE = (0.01, 2.0)
# Souza et al. eq. (1).
MAX_FLOOD_FRACTION = 0.85


def souders_brown_csb(tray_spacing_m: float, flv: float) -> float:
    """Lygeros-Magoulas fit of Fair's C_sb, in m/s."""
    if tray_spacing_m <= 0 or flv <= 0:
        raise ValueError("Tray spacing and flow parameter must be positive.")
    return 0.0105 + 0.1496 * tray_spacing_m ** 0.755 * math.exp(-1.463 * flv ** 0.842)


def flow_parameter(l_mass: float, v_mass: float, rho_l: float, rho_v: float) -> float:
    return (l_mass / v_mass) * math.sqrt(rho_v / rho_l)


def flooding_velocity(csb: float, rho_l: float, rho_v: float, surface_tension_n_m: float, k_factor: float = 1.0) -> float:
    """Net-area vapour velocity at flood, m/s."""
    if rho_l <= rho_v:
        raise ValueError(f"Liquid density {rho_l:.4g} must exceed vapour density {rho_v:.4g} kg/m3.")
    return k_factor * csb * math.sqrt((rho_l - rho_v) / rho_v) * (surface_tension_n_m / 0.02) ** 0.2


def tray_diameter(v_mass: float, l_mass: float, rho_v: float, rho_l: float, tray_spacing_m: float,
                  surface_tension_n_m: float, flood_fraction: float, downcomer_area_fraction: float,
                  k_factor: float = 1.0) -> Dict:
    """
    Column diameter for one section (top or bottom) of a tray column.

    The vapour flows through the net area A_n = A_column - A_downcomer at
    flood_fraction of the flooding velocity.
    """
    if not (0 < flood_fraction < 1):
        raise ValueError("flood_fraction must be between 0 and 1.")
    if not (0 <= downcomer_area_fraction < 1):
        raise ValueError("downcomer_area_fraction must be in [0, 1).")
    warnings: List[str] = []
    flv = flow_parameter(l_mass, v_mass, rho_l, rho_v)
    lo, hi = FAIR_FLV_RANGE
    if not (lo <= flv <= hi):
        warnings.append(f"Flow parameter F_LV = {flv:.3g} is outside Fair's chart ({lo} to {hi}); C_sb is extrapolated.")
    lo, hi = FAIR_TRAY_SPACING_RANGE_M
    if not (lo <= tray_spacing_m <= hi):
        warnings.append(f"Tray spacing {tray_spacing_m:.3g} m is outside Fair's data ({lo} to {hi} m); C_sb is extrapolated.")
    csb = souders_brown_csb(tray_spacing_m, flv)
    u_flood = flooding_velocity(csb, rho_l, rho_v, surface_tension_n_m, k_factor)
    u_net = flood_fraction * u_flood
    net_area = v_mass / (rho_v * u_net)
    area = net_area / (1.0 - downcomer_area_fraction)
    return {
        "flow_parameter": flv,
        "csb": csb,
        "flooding_velocity": u_flood,
        "net_velocity": u_net,
        "net_area": net_area,
        "area": area,
        "diameter": math.sqrt(4.0 * area / math.pi),
        "warnings": warnings,
    }


def oconnell_efficiency(liquid_viscosity_mpa_s: float, alpha: float) -> float:
    """O'Connell overall tray efficiency, as a fraction."""
    group = liquid_viscosity_mpa_s * alpha
    if group <= 0:
        raise ValueError("mu_L * alpha must be positive.")
    return 0.503 * group ** -0.226
