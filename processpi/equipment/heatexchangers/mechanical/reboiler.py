"""
processpi/equipment/heatexchangers/reboiler.py

Improved Reboiler design module — aligned with other exchanger modules
(evaporator, condenser, shell_tube, double_pipe).

Key improvements that this implementation provides:
- Single `hx: HeatExchanger` input (uses hx.hot_in / hx.cold_in streams)
- Robust unit/property extraction via `_safe_prop_get()`
- Zone-wise iterative U <-> A convergence with damping and numeric guards
- Uses packing routine (if available) for bundle sizing
- Conservatively falls back to heuristics when component methods are missing
- Attaches result to `hx.design_results`

This module expects your existing helper modules: `.kern_method` and
`.bell_method` (same names as in your repo). Adapt imports if your helpers
have different names/signatures.
"""

from typing import Dict, Any
import math

from ....streams.material import MaterialStream
from ..base import HeatExchanger
from .kern_method import lmtd, overall_U, tube_htc, shell_htc, required_area, heat_duty
from .bell_method import bell_delaware_pressure_drop, check_flooding

# try to reuse packing routine from shell_tube if available
try:
    from .shell_tube import pack_tubes_in_shell
except Exception:
    def pack_tubes_in_shell(D_shell: float, D_tube: float, pitch: float, layout: str = "triangular"):
        # simple fallback: estimate tube count from area
        return [], max(1, int(max(6, math.floor((D_shell/D_tube)**2))))

# defaults
DEFAULT_FOUL_HOT = 1e-4
DEFAULT_FOUL_COLD = 2e-4
DEFAULT_TUBE_K = 16.0
GRAVITY = 9.81


def _safe_prop_get(component, fn_name: str, *args, fallback=None):
    """Call component property safely and extract numeric value or fallback."""
    try:
        fn = getattr(component, fn_name)
        val = fn(*args)
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


def design_reboiler(
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
    tube_side_hot: bool = True,  # tube-side hot by default for reboilers
    max_zone_iter: int = 30,
    tol: float = 1e-3,
    **kwargs
) -> Dict[str, Any]:
    """
    Reboiler design wrapper expecting hx (HeatExchanger) with `hot_in` and
    `cold_in` MaterialStream attributes. Calculates heating, boiling and
    optional superheat zones with iterative U <-> A convergence.
    """
    if not isinstance(hx, HeatExchanger):
        raise TypeError("hx must be a HeatExchanger instance")

    hot = hx.hot_in
    cold = hx.cold_in

    # temperatures (Kelvin preferred)
    try:
        T_hot_in = float(hot.temperature.to("K").value)
    except Exception:
        T_hot_in = float(getattr(hot, "temperature", getattr(hot, "T", 350.0)))
    try:
        T_cold_in = float(cold.temperature.to("K").value)
    except Exception:
        T_cold_in = float(getattr(cold, "temperature", getattr(cold, "T", 300.0)))

    # saturation temperature of the cold (boiling) stream
    T_sat = _safe_prop_get(cold.component, "saturation_temperature", fallback=None) or _safe_prop_get(cold.component, "boiling_point", fallback=None)
    if T_sat is None:
        # fallback assume cold is the boiling stream; if unknown use inlet
        T_sat = T_cold_in

    # mass flows and heat capacities
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

    # Zone duties
    # heating: bring hot from inlet down (or cold up) — user semantics vary; we mimic textbook reboiler
    deltaT_heat = max(T_hot_in - T_sat, 0.0)
    deltaT_super = max(T_sat - T_hot_in, 0.0)  # if hot inlet hotter than sat

    duty_heat = 0.0
    if deltaT_heat > 0:
        # heat required to raise cold to near saturation using hot energy
        duty_heat = heat_duty(m_cold, cp_cold, T_cold_in, T_sat)

    # boiling duty (latent on cold side)
    h_fg = _safe_prop_get(cold.component, "latent_heat", fallback=None) or _safe_prop_get(cold.component, "latent_heat_of_vaporization", fallback=None)
    if h_fg is None:
        # fallback water-like
        h_fg = 2.257e6
    duty_boil = m_cold * float(h_fg)

    # optional superheat of vapor leaving reboiler (usually small)
    duty_super = 0.0
    if T_hot_in > T_sat:
        duty_super = heat_duty(m_hot, cp_hot, T_hot_in, T_sat)

    Q_total = duty_heat + duty_boil + duty_super

    # which side is tube vs shell
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

    # iterative zone solver
    def zone_iter(duty: float, T_hot_start: float, T_hot_end: float, T_cold_start: float, T_cold_end: float, U_guess: float = 500.0):
        U = max(1.0, U_guess)
        lmtd_val = lmtd(T_hot_start, T_hot_end, T_cold_start, T_cold_end, Ft)
        A_req = float('inf')
        for _ in range(max_zone_iter):
            if lmtd_val == 0 or U <= 0:
                A_req = float('inf')
                break
            A_req = required_area(duty, U, lmtd_val)

            # estimate flow geometry
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

            # tube-side heat transfer
            A_tube_flow = math.pi * ((tube_OD - 2e-3) ** 2) / 4.0
            v_tube = (m_tube_total / max(1, tube_count_est)) / max(rho_t * A_tube_flow, 1e-12)
            Re_t = rho_t * v_tube * max(tube_OD - 2e-3, 1e-6) / max(mu_t, 1e-12)
            Pr_t = (cp_t_loc * mu_t / max(k_t, 1e-12)) if k_t>0 else 1.0
            try:
                h_t = tube_htc(k_t, (tube_OD - 2e-3), Re_t, Pr_t)
            except Exception:
                h_t = 200.0

            # shell-side (boiling) — boiling HTC guess or shell_htc helper
            try:
                h_s = shell_htc(rho_s, mu_s, k_s, cp_s_loc, m_shell_total, Ds=0.5, pitch=tube_pitch_factor*tube_OD)
            except Exception:
                # conservative boiling film fallback
                h_s = 500.0

            U_new = overall_U(h_t, h_s, fouling_hot, fouling_cold, R_wall=0.001)
            if abs(U_new - U) / max(1e-12, U) < tol:
                U = U_new
                break
            U = 0.6 * U_new + 0.4 * U
        return max(A_req, 0.0), U, lmtd_val

    # run zones
    A_heat = U_heat = LMTD_heat = 0.0
    A_boil = U_boil = LMTD_boil = 0.0
    A_super = U_super = LMTD_super = 0.0

    if duty_heat > 0:
        A_heat, U_heat, LMTD_heat = zone_iter(duty_heat, T_hot_in, T_sat, T_cold_in, T_sat)

    A_boil, U_boil, LMTD_boil = zone_iter(duty_boil, T_sat, T_sat, T_cold_in, T_sat)

    if duty_super > 0:
        A_super, U_super, LMTD_super = zone_iter(duty_super, T_hot_in, T_hot_in - 1.0, T_sat, T_sat + 1.0)

    A_total = A_heat + A_boil + A_super

    # bundle sizing using packing routine when available
    pitch = tube_pitch_factor * tube_OD
    bundle_diam_guess = math.sqrt(A_total / (math.pi * tube_OD * max(1.0, passes))) if A_total>0 else 0.0
    Ds = max(0.1, bundle_diam_guess)
    centers, N_packed = pack_tubes_in_shell(Ds, tube_OD, pitch, layout=layout)
    attempts = 0
    while (not centers or len(centers) < 4) and attempts < 5:
        Ds *= 1.25
        centers, N_packed = pack_tubes_in_shell(Ds, tube_OD, pitch, layout=layout)
        attempts += 1

    if centers and len(centers) > 0:
        max_r = max(math.hypot(x, y) for x, y in centers)
        bundle_diam = max(2.0 * max_r, Ds)
        N_tubes = len(centers)
    else:
        pitch_ratio = 0.866 if layout == "triangular" else 1.0
        N_tubes = max(1, int(pitch_ratio * (bundle_diam_guess / pitch)**2))
        bundle_diam = bundle_diam_guess

    tube_length = A_total / (math.pi * tube_OD * N_tubes) if N_tubes>0 else 0.0
    shell_ID = bundle_diam * 1.1 if bundle_diam>0 else max(0.2, tube_OD*12)

    # shell-side dp and flooding
    try:
        rho_s_for_dp = _safe_prop_get(shell_stream.component, "density", T_cold_in, fallback=1000.0)
        mu_s_for_dp = _safe_prop_get(shell_stream.component, "viscosity", T_cold_in, fallback=1e-3)
        deltaP_shell = bell_delaware_pressure_drop(rho_s_for_dp, mu_s_for_dp, m_shell_total, shell_ID, tube_OD)
    except Exception:
        deltaP_shell = 0.0

    flooded = False
    try:
        flooded = check_flooding(cold, math.pi*(tube_OD**2)/4.0, vertical=(orientation=="vertical"))
    except Exception:
        flooded = False

    result = {
        "Duty_W": Q_total,
        "Overall_U_W_m2K": (U_heat + U_boil + U_super) / max(1, sum([1 if x>0 else 0 for x in (U_heat, U_boil, U_super)])),
        "Area_heat_m2": A_heat,
        "Area_boil_m2": A_boil,
        "Area_super_m2": A_super,
        "A_total_m2": A_total,
        "N_tubes": N_tubes,
        "tube_length_m": tube_length,
        "bundle_diameter_m": bundle_diam,
        "shell_ID_m": shell_ID,
        "deltaP_shell_Pa": deltaP_shell,
        "flooding_risk": flooded,
        "LMTD_zones_K": {"heating": LMTD_heat, "boiling": LMTD_boil, "superheat": LMTD_super},
        "U_zones_W_m2K": {"heating": U_heat, "boiling": U_boil, "superheat": U_super}
    }

    hx.design_results = result
    return result
