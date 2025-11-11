"""
processpi/equipment/heatexchangers/condenser.py

Improved Condenser design module — made consistent with other ProcessPI
heat exchanger modules (evaporator, shell_tube, double_pipe).

Key changes vs. the raw snippet provided:
- Single `hx: HeatExchanger` input (with hot_in / cold_in streams) for API
  consistency with other modules.
- Robust unit/property extraction via `_safe_prop_get()`.
- Zone-wise iterative U <-> A convergence with damping and numeric guards.
- Optional `tube_side_hot` flag to control which stream is treated as tube-side.
- Conservative fallbacks for missing fluid property methods (latent heat, cp, etc.).

This file expects your existing helper modules and preserves calls to
`bell_delaware_pressure_drop()` and `check_flooding()` from `.bell_method`.
"""

from typing import Dict, Any
import math

from ....streams.material import MaterialStream
from ..base import HeatExchanger
from .kern_method import lmtd, overall_U, tube_htc, shell_htc, required_area, heat_duty
from .bell_method import bell_delaware_pressure_drop, check_flooding

# defaults
DEFAULT_FOUL_HOT = 1e-4
DEFAULT_FOUL_COLD = 2e-4
DEFAULT_TUBE_K = 16.0
GRAVITY = 9.81


def _safe_prop_get(component, fn_name: str, *args, fallback=None):
    """Call a component property function safely and return numeric value or fallback."""
    try:
        fn = getattr(component, fn_name)
        val = fn(*args)
        # Extract numeric value from pint-like wrappers if possible
        if hasattr(val, "to"):
            try:
                return float(val.value)
            except Exception:
                try:
                    return float(val.to("K").value)
                except Exception:
                    return fallback
        if isinstance(val, (int, float)):
            return float(val)
        return fallback
    except Exception:
        return fallback


def design_condenser(
    hx: HeatExchanger,
    *,
    orientation: str = "horizontal",
    passes: int = 1,
    Ft: float = 1.0,
    fouling_hot: float = DEFAULT_FOUL_HOT,
    fouling_cold: float = DEFAULT_FOUL_COLD,
    layout: str = "triangular",
    tube_OD: float = 0.0254,
    tube_pitch_factor: float = 1.25,
    tube_side_hot: bool = False,  # default: condenser tube-side commonly used for coolant (cold) -> set False
    max_zone_iter: int = 30,
    tol: float = 1e-3,
    **kwargs
) -> Dict[str, Any]:
    """
    Condenser design wrapper expecting hx (HeatExchanger) with `hot_in` and
    `cold_in` MaterialStream attributes. Performs zone-wise design for:
      - superheat (if any)
      - condensation (latent)
      - subcooling (if any)

    Returns detailed sizing, U-values, LMTDs, dp estimates and a flooding flag.
    """
    if not isinstance(hx, HeatExchanger):
        raise TypeError("hx must be a HeatExchanger instance")

    hot = hx.hot_in
    cold = hx.cold_in

    # Extract temperatures (try Kelvin) with fallbacks
    try:
        T_hot_in = float(hot.temperature.to("K").value)
    except Exception:
        T_hot_in = float(getattr(hot, "temperature", getattr(hot, "T", 350.0)))
    try:
        T_cold_in = float(cold.temperature.to("K").value)
    except Exception:
        T_cold_in = float(getattr(cold, "temperature", getattr(cold, "T", 300.0)))

    # saturation temperature for hot (condensing) stream
    T_sat = _safe_prop_get(hot.component, "saturation_temperature", fallback=None) or _safe_prop_get(hot.component, "dew_point", fallback=None)
    if T_sat is None:
        T_sat = T_hot_in

    # mass flows and cp
    try:
        m_hot = float(hot.mass_flowrate.to("kg/s").value)
    except Exception:
        m_hot = float(getattr(hot, "mass_flowrate", getattr(hot, "m_dot", 1.0)))
    try:
        m_cold = float(cold.mass_flowrate.to("kg/s").value)
    except Exception:
        m_cold = float(getattr(cold, "mass_flowrate", getattr(cold, "m_dot", 1.0)))

    try:
        cp_hot = float(hot.cp.to("J/kg-K").value)
    except Exception:
        cp_hot = _safe_prop_get(hot.component, "specific_heat", fallback=2000.0)
    try:
        cp_cold = float(cold.cp.to("J/kg-K").value)
    except Exception:
        cp_cold = _safe_prop_get(cold.component, "specific_heat", fallback=4200.0)

    # Zones: superheat (hot above sat), condensation (latent), subcool (cold side)
    deltaT_super = max(T_hot_in - T_sat, 0.0)
    deltaT_subcool = max(T_sat - T_cold_in, 0.0)

    duty_super = 0.0
    if deltaT_super > 0:
        duty_super = heat_duty(m_hot, cp_hot, T_hot_in, T_hot_in - deltaT_super)

    h_fg = _safe_prop_get(hot.component, "latent_heat", fallback=None) or _safe_prop_get(hot.component, "latent_heat_of_vaporization", fallback=None)
    if h_fg is None:
        h_fg = 2.257e6
    duty_cond = m_hot * float(h_fg)

    duty_sub = 0.0
    if deltaT_subcool > 0:
        duty_sub = heat_duty(m_cold, cp_cold, T_cold_in, T_cold_in + deltaT_subcool)

    Q_total = duty_super + duty_cond + duty_sub

    # Which side is tube vs shell
    if tube_side_hot:
        tube_stream = hot
        shell_stream = cold
        m_tube_total = m_hot
        m_shell_total = m_cold
        cp_tube = cp_hot
        cp_shell = cp_cold
    else:
        tube_stream = cold
        shell_stream = hot
        m_tube_total = m_cold
        m_shell_total = m_hot
        cp_tube = cp_cold
        cp_shell = cp_hot

    # helper: iterative zone convergence (U <-> A)
    def zone_iter(duty: float, T_hot_start: float, T_hot_end: float, T_cold_start: float, T_cold_end: float, U_guess: float = 500.0):
        U = max(1.0, U_guess)
        lmtd_val = lmtd(T_hot_start, T_hot_end, T_cold_start, T_cold_end, Ft)
        A_req = float('inf')
        for _ in range(max_zone_iter):
            if lmtd_val == 0 or U <= 0:
                A_req = float('inf')
                break
            A_req = required_area(duty, U, lmtd_val)
            # estimate representative geometry
            L_guess = max(1.0, A_req / (math.pi * tube_OD * 10.0))
            tube_count_est = max(1, int(math.ceil(A_req / (math.pi * tube_OD * L_guess))))

            # film temps
            T_f_tube = 0.5 * (T_hot_start + T_hot_end)
            T_f_shell = 0.5 * (T_cold_start + T_cold_end)

            mu_t = _safe_prop_get(tube_stream.component, "viscosity", T_f_tube, fallback=1e-3)
            rho_t = _safe_prop_get(tube_stream.component, "density", T_f_tube, fallback=1000.0)
            k_t = _safe_prop_get(tube_stream.component, "thermal_conductivity", T_f_tube, fallback=0.13)
            cp_t_loc = _safe_prop_get(tube_stream.component, "specific_heat", T_f_tube, fallback=cp_tube)

            mu_s = _safe_prop_get(shell_stream.component, "viscosity", T_f_shell, fallback=1e-3)
            rho_s = _safe_prop_get(shell_stream.component, "density", T_f_shell, fallback=1000.0)
            k_s = _safe_prop_get(shell_stream.component, "thermal_conductivity", T_f_shell, fallback=0.13)
            cp_s_loc = _safe_prop_get(shell_stream.component, "specific_heat", T_f_shell, fallback=cp_shell)

            # tube-side HTC
            A_tube_flow = math.pi * ((tube_OD - 2e-3) ** 2) / 4.0
            v_tube = (m_tube_total / max(1, tube_count_est)) / max(rho_t * A_tube_flow, 1e-12)
            Re_t = rho_t * v_tube * max(tube_OD - 2e-3, 1e-6) / max(mu_t, 1e-12)
            Pr_t = (cp_t_loc * mu_t / max(k_t, 1e-12)) if k_t>0 else 1.0
            try:
                h_t = tube_htc(k_t, (tube_OD - 2e-3), Re_t, Pr_t)
            except Exception:
                h_t = 200.0

            # shell-side HTC (condensing surface) — use bell_method helper or fallback
            try:
                h_s = shell_htc(rho_s, mu_s, k_s, cp_s_loc, m_shell_total, Ds=0.5, pitch=tube_pitch_factor*tube_OD)
            except Exception:
                # conservative fallback for condensation
                h_s = 1000.0 if duty_cond>0 else 150.0

            U_new = overall_U(h_t, h_s, fouling_hot, fouling_cold, R_wall=0.001)
            if abs(U_new - U) / max(1e-12, U) < tol:
                U = U_new
                break
            U = 0.6 * U_new + 0.4 * U
        return max(A_req, 0.0), U, lmtd_val

    # Run zones
    A_super = U_super = LMTD_super = 0.0
    A_cond = U_cond = LMTD_cond = 0.0
    A_sub = U_sub = LMTD_sub = 0.0

    if duty_super > 0:
        A_super, U_super, LMTD_super = zone_iter(duty_super, T_hot_in, T_sat, T_cold_in, T_cold_in + duty_super/(m_cold*cp_cold) if m_cold*cp_cold>0 else T_cold_in)

    A_cond, U_cond, LMTD_cond = zone_iter(duty_cond, T_sat, T_sat, T_cold_in + duty_super/(m_cold*cp_cold) if m_cold*cp_cold>0 else T_cold_in, T_cold_in + (duty_super + duty_cond)/(m_cold*cp_cold) if m_cold*cp_cold>0 else T_cold_in)

    if duty_sub > 0:
        A_sub, U_sub, LMTD_sub = zone_iter(duty_sub, T_sat, T_sat - deltaT_subcool, T_cold_in + (duty_super + duty_cond)/(m_cold*cp_cold) if m_cold*cp_cold>0 else T_cold_in, T_cold_in + Q_total/(m_cold*cp_cold) if m_cold*cp_cold>0 else T_cold_in)

    A_total = A_super + A_cond + A_sub

    # bundle/tube sizing heuristics
    pitch = tube_pitch_factor * tube_OD
    pitch_ratio = 0.866 if layout == "triangular" else 1.0
    bundle_diam = math.sqrt(A_total / (math.pi * tube_OD * max(1.0, passes))) if A_total>0 else 0.0
    N_tubes = max(1, int(pitch_ratio * (bundle_diam / pitch)**2))
    tube_length = A_total / (math.pi * tube_OD * N_tubes) if N_tubes>0 else 0.0
    shell_ID = bundle_diam * 1.1 if bundle_diam>0 else max(0.2, tube_OD*12)

    # shell-side dp and flooding
    try:
        rho_s_for_dp = _safe_prop_get(hot.component, "density", T_hot_in, fallback=1000.0)
        mu_s_for_dp = _safe_prop_get(hot.component, "viscosity", T_hot_in, fallback=1e-3)
        deltaP_shell = bell_delaware_pressure_drop(rho_s_for_dp, mu_s_for_dp, m_hot, shell_ID, tube_OD)
    except Exception:
        deltaP_shell = 0.0

    flooded = False
    try:
        flooded = check_flooding(hot, math.pi*(tube_OD**2)/4.0, vertical=(orientation=="vertical"))
    except Exception:
        flooded = False

    result = {
        "Duty_W": Q_total,
        "Overall_U_W_m2K": (U_super + U_cond + U_sub) / max(1, sum([1 if x>0 else 0 for x in (U_super, U_cond, U_sub)])),
        "Area_super_m2": A_super,
        "Area_cond_m2": A_cond,
        "Area_sub_m2": A_sub,
        "A_total_m2": A_total,
        "N_tubes": N_tubes,
        "tube_length_m": tube_length,
        "bundle_diameter_m": bundle_diam,
        "shell_ID_m": shell_ID,
        "deltaP_shell_Pa": deltaP_shell,
        "flooding_risk": flooded,
        "LMTD_zones_K": {"superheat": LMTD_super, "condensation": LMTD_cond, "subcool": LMTD_sub},
        "U_zones_W_m2K": {"superheat": U_super, "condensation": U_cond, "subcool": U_sub}
    }

    hx.design_results = result
    return result
