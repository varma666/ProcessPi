"""
processpi/equipment/heatexchangers/double_pipe.py

Complete double-pipe heat exchanger design routine:
- Iterative convergence: Re -> f (Colebrook/Haaland) -> Nu -> h -> U -> A/L -> Re
- Tube (inner) vs Annulus (outer) swap and auto-selection
- Multi-pass support (series / parallel), parallel annuli
- NTU -> epsilon -> Ft integration for LMTD correction
- Optional chart-based Ft for common pass layouts (Kern-style heuristics)
- Uses your unit wrappers: Diameter, Length, Pressure, etc. (assumed in ....units)
- Expects hx.simulated_params to contain Hot/Cold temps, m_hot/m_cold, cP_hot/cP_cold, and optional given_length.
"""

import math
from typing import Dict, Any, Optional, Tuple, List
from ....units import Diameter, Length, Pressure, Temperature, MassFlowRate, Conductivity, Variable
from ....streams.material import MaterialStream
from ..base import HeatExchanger

# ------------------------------------------------------------------
# TUNABLE DEFAULTS
# ------------------------------------------------------------------
_DEFAULT_WALL_K = 16.0  # W/m-K, pipe material (carbon steel)
_DEFAULT_ROUGHNESS = 1.5e-5  # m (commercial steel)
_DEFAULT_FOULING_TUBE = 1e-4  # m2K/W
_DEFAULT_FOULING_SHELL = 2e-4  # m2K/W
_DEFAULT_MAX_ITERS = 200
_DEFAULT_TOL = 1e-4

# ------------------------------------------------------------------
# Utilities: must match your units API (adapt if needed)
# ------------------------------------------------------------------
def _get_parms(hx: HeatExchanger) -> Dict[str, Any]:
    if not isinstance(hx, HeatExchanger):
        raise TypeError("hx must be HeatExchanger")
    if hx.simulated_params is None:
        raise ValueError("Heat exchanger has not been simulated (simulated_params missing).")
    return hx.simulated_params

def _val(v, name: str):
    """Extract numeric value from unit-wrapped type or raw number."""
    if v is None:
        return None
    if hasattr(v, "value"):
        return v.value
    if isinstance(v, (int, float)):
        return float(v)
    raise TypeError(f"{name} must be numeric or unit-wrapped.")

# ------------------------------------------------------------------
# Friction factor helpers (Haaland + Colebrook fallback)
# ------------------------------------------------------------------
def _haaland_f(Re: float, eps_rel: float) -> float:
    if Re <= 0:
        return 1e6
    if Re < 2300:
        return 64.0 / max(Re, 1e-12)
    # Haaland
    try:
        term = -1.8 * math.log10((eps_rel / 3.7) ** 1.11 + 6.9 / Re)
        f = (1.0 / term) ** 2
        return f
    except Exception:
        return 0.02

def _colebrook_f(Re: float, eps_rel: float) -> float:
    """Iterative Colebrook; start from Haaland initial guess."""
    if Re < 2300:
        return 64.0 / max(Re, 1e-12)
    f = _haaland_f(Re, eps_rel)
    for _ in range(30):
        # Colebrook residual: 1/sqrt(f) + 2*log10(eps/3.7 + 2.51/(Re*sqrt(f))) = 0
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f)))
        res = lhs - rhs
        # derivative approximate (numerical small-step)
        df = 1e-6
        f2 = max(f*(1+df), 1e-12)
        lhs2 = 1.0 / math.sqrt(f2)
        rhs2 = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f2)))
        res2 = lhs2 - rhs2
        dres_df = (res2 - res) / (f2 - f)
        if abs(dres_df) < 1e-12:
            break
        f_new = f - res / dres_df
        if f_new <= 0:
            break
        if abs(f_new - f) / f_new < 1e-8:
            f = f_new
            break
        f = f_new
    return max(f, 1e-12)

# ------------------------------------------------------------------
# Nusselt correlations (Gnielinski + fallback Dittus-Boelter)
# ------------------------------------------------------------------
def _prandtl(cp: float, mu: float, k: float) -> float:
    return cp * mu / k

def _nusselt_gnielinski(Re: float, Pr: float, f: float) -> float:
    if Re <= 2300:
        return 3.66
    Nu = (f / 8.0) * (Re - 1000.0) * Pr / (1.0 + 12.7 * (f / 8.0) ** 0.5 * (Pr ** (2.0/3.0) - 1.0))
    return max(3.66, Nu)

def _nusselt_dittus(Re: float, Pr: float, exponent_pr: float = 0.4) -> float:
    if Re <= 2300:
        return 3.66
    return 0.023 * (Re ** 0.8) * (Pr ** exponent_pr)

# Annulus correction (heuristic)
def _nusselt_annulus(Re: float, Pr: float, Do: float, Di: float, f: float) -> float:
    Dh = Do - Di
    Nu = _nusselt_gnielinski(Re, Pr, f)
    ratio = Di / Do
    corr = 1.0 - 0.15 * max(0.0, (ratio - 0.4))
    return max(3.0, Nu * corr)

# ------------------------------------------------------------------
# NTU-effectiveness functions (parallel / counterflow)
# ------------------------------------------------------------------
def _epsilon_parallel(NTU: float, C: float) -> float:
    if NTU <= 0:
        return 0.0
    return (1.0 - math.exp(-NTU * (1.0 + C))) / (1.0 + C)

def _epsilon_counterflow(NTU: float, C: float) -> float:
    if NTU <= 0:
        return 0.0
    if abs(1.0 - C) < 1e-12:
        return NTU / (1.0 + NTU)
    exp_term = math.exp(-NTU * (1.0 - C))
    return (1.0 - exp_term) / (1.0 - C * exp_term)

def _epsilon_from_arrangement(arrangement: str, NTU: float, C: float) -> float:
    arrangement = arrangement.lower()
    if arrangement == "counterflow":
        return _epsilon_counterflow(NTU, C)
    elif arrangement == "parallel":
        return _epsilon_parallel(NTU, C)
    else:
        # default to counterflow if unknown
        return _epsilon_counterflow(NTU, C)

# ------------------------------------------------------------------
# Pass-scaling heuristic for NTU (replaceable by chart correlations)
# ------------------------------------------------------------------
def _ntuscaling_for_passes(inner_mode: str, passes: int) -> float:
    # documented heuristic:
    if passes <= 1:
        return 1.0
    if inner_mode == "series":
        # approximate increase in effective NTU for series passes (bend losses reduce ideal linearity)
        if passes == 2:
            return 1.85
        if passes == 4:
            return 3.5
        return float(passes) * 0.9
    elif inner_mode == "parallel":
        return 1.0 / float(passes)
    return 1.0

# ------------------------------------------------------------------
# Chart-based Ft for common pass layouts (Kern-style approximations)
# These functions return Ft (0 < Ft <= 1). Comments cite classic formulas.
# ------------------------------------------------------------------
def Ft_chart_1_1(NTU: float, C: float) -> float:
    # For single-pass counterflow, Ft ~ 1 (counterflow ideal)
    return 1.0

def Ft_chart_1_2(NTU: float, C: float) -> float:
    # 1 shell pass, 2 tube passes (1-2 layout) — approximate using Kern/Table lookups
    # Use empirical adjustment: Ft = 1 - 0.1*(1 - exp(-0.5*NTU))*(1 - C)
    return max(0.1, min(1.0, 1.0 - 0.1 * (1.0 - math.exp(-0.5 * NTU)) * (1.0 - C)))

def Ft_chart_2_1(NTU: float, C: float) -> float:
    # 2 shell passes, 1 tube pass - heuristic mirror
    return Ft_chart_1_2(NTU, C)

def Ft_chart_1_4(NTU: float, C: float) -> float:
    # 1 shell pass, 4 tube passes - larger reduction
    return max(0.05, min(1.0, 1.0 - 0.25 * (1.0 - math.exp(-0.4 * NTU)) * (1.0 - C)))

def Ft_chart_2_2(NTU: float, C: float) -> float:
    # 2 by 2 multipass layout
    return max(0.05, min(1.0, 1.0 - 0.18 * (1.0 - math.exp(-0.45 * NTU)) * (1.0 - C)))

# choose chart function by layout key
_CHART_FT_MAP = {
    "1-1": Ft_chart_1_1,
    "1-2": Ft_chart_1_2,
    "2-1": Ft_chart_2_1,
    "1-4": Ft_chart_1_4,
    "2-2": Ft_chart_2_2,
}

# ------------------------------------------------------------------
# Pressure drop (Darcy-Weisbach)
# ------------------------------------------------------------------
def _deltaP_darcy(f: float, L: float, D_h: float, rho: float, v: float) -> float:
    return f * (L / D_h) * 0.5 * rho * v * v

# ------------------------------------------------------------------
# Top-level design function (end-to-end)
# ------------------------------------------------------------------
def design_double_pipe_aspen_like(
    hx: HeatExchanger,
    *,
    innerpipe_dia: Optional[Diameter] = None,
    outerpipe_dia: Optional[Diameter] = None,
    schedule_inner: Optional[str] = None,
    schedule_outer: Optional[str] = None,
    inner_mode: str = "series",        # "series" or "parallel"
    passes: int = 1,                   # 1,2,4 supported
    annulus_parallel: int = 1,         # number of parallel annuli
    arrangement: str = "counterflow",  # 'counterflow' or 'parallel' (used for epsilon)
    pass_layout: Optional[str] = None, # e.g., "1-1","1-2","2-1","1-4","2-2" -> use chart Ft if provided
    target_dp: Optional[Pressure] = None,
    pipe_library: Optional[Dict[Diameter, Dict[str, Tuple[Length, Diameter, Diameter]]]] = None,
    wall_k: Union[float, Conductivity] = _DEFAULT_WALL_K,
    roughness: float = _DEFAULT_ROUGHNESS,
    fouling_tube: float = _DEFAULT_FOULING_TUBE,
    fouling_shell: float = _DEFAULT_FOULING_SHELL,
    max_iters: int = _DEFAULT_MAX_ITERS,
    tol: float = _DEFAULT_TOL,
) -> Dict[str, Any]:
    """
    Perform a detailed double-pipe heat exchanger design with Ft integration.
    Returns a results dict with U, L, Ft, Re, Nu, dp, chosen pipe, and iteration info.

    Behavior:
    - If inner/outer provided, design that geometry.
    - Otherwise automatic search through pipe_library (if provided) or minimal built-in set.
    - Tries both tube-fluid assignments (hot inside vs cold inside) and picks best.
    - Compute Ft either via NTU->epsilon method or chart-based function if pass_layout given.
    """

    parms = _get_parms(hx)

    # Extract required simulated params (must exist)
    Th_in = _val(parms.get("Hot in Temp"), "Hot In Temp")
    Th_out = _val(parms.get("Hot out Temp"), "Hot Out Temp")
    Tc_in = _val(parms.get("Cold in Temp"), "Cold In Temp")
    Tc_out = _val(parms.get("Cold out Temp"), "Cold Out Temp")
    m_hot = _val(parms.get("m_hot"), "m_hot")
    m_cold = _val(parms.get("m_cold"), "m_cold")
    cp_hot = _val(parms.get("cP_hot"), "cP_hot")
    cp_cold = _val(parms.get("cP_cold"), "cP_cold")
    delta_Tlm_param = parms.get("delta_Tlm")  # optional; keep unit-wrapped

    # Q (W); preferring hot side energy removal if possible
    Q_hot = m_hot * cp_hot * (Th_in - Th_out)
    Q_cold = m_cold * cp_cold * (Tc_out - Tc_in)
    Q = Q_hot if abs(Q_hot) > 0 else Q_cold

    # convert options
    wall_k_val = wall_k.value if hasattr(wall_k, "value") else float(wall_k)
    dp_limit = target_dp.to("Pa").value if target_dp is not None and hasattr(target_dp, "to") else (target_dp.value if hasattr(target_dp, "value") else (target_dp if isinstance(target_dp, (int,float)) else None))

    # pipe library fallback (very small set if not provided)
    if pipe_library is None:
        # simple available (ID_inner_m, OD_outer_m) pairs as fallback
        pipe_pairs = [(0.0127, 0.0213), (0.01905, 0.0267), (0.0254, 0.0334), (0.03175, 0.0422), (0.0508, 0.0635)]
    else:
        # flatten pipe_library to (inner_id_m, outer_id_m) for default schedule selection
        pipe_pairs = []
        for nominal_d, schedules in pipe_library.items():
            # choose schedule_outer if provided else first schedule
            sched_keys = list(schedules.keys())
            chosen = schedule_inner if schedule_inner in schedules else sched_keys[0]
            _, od, id_inner = schedules[chosen]
            # note: here id_inner is already a Diameter object; convert to meters
            try:
                Di = id_inner.to("m").value
            except Exception:
                Di = id_inner.value if hasattr(id_inner, "value") else float(id_inner)
            # for outer pipe we'll search matching nominal (we approximate OD by nominal*1.5)
            # This routine primarily uses inner pipe ID and a larger outer ID; user can pass explicit outerpipe_dia
            # For simplicity, pair with next larger nominal if available - but if user passed outerpipe_dia below will be used
            pipe_pairs.append((Di, float(od.value) if hasattr(od, "value") else float(od)))

    # If user supplied explicit inner/outer diameters, override
    if innerpipe_dia is not None and outerpipe_dia is not None:
        pipe_pairs = [(innerpipe_dia.to("m").value, outerpipe_dia.to("m").value)]

    # Two tube/annulus assignments to try
    assignments = [
        ("hot_tube", "cold_annulus"),  # hot inside, cold outside
        ("cold_tube", "hot_annulus"),  # cold inside, hot outside
    ]

    best_result = None
    best_score = float("inf")

    # Loop over configurations
    for (Di, Do) in pipe_pairs:
        # require Do > Di + small clearance
        if Do <= Di * 1.05:
            continue

        for assignment in assignments:
            # Map assignment to streams used for tube/annulus
            if assignment[0] == "hot_tube":
                tube_stream = hx.hot_in
                ann_stream = hx.cold_in
                m_tube = m_hot; m_ann = m_cold
                cp_tube = cp_hot; cp_ann = cp_cold
            else:
                tube_stream = hx.cold_in
                ann_stream = hx.hot_in
                m_tube = m_cold; m_ann = m_hot
                cp_tube = cp_cold; cp_ann = cp_hot

            # per-channel flows depending on inner_mode / parallel
            if inner_mode == "parallel":
                n_inner_channels = passes
                m_tube_channel = m_tube / n_inner_channels
            else:
                n_inner_channels = 1
                m_tube_channel = m_tube

            n_ann_channels = annulus_parallel
            m_ann_channel = m_ann / n_ann_channels

            # initial guesses
            L_total = 2.0  # m (initial)
            U_ref = 300.0  # W/m2K initial guess
            converged = False
            iteration = 0

            for iteration in range(max_iters):
                # per-pass/per-tube length interpretation
                if inner_mode == "series":
                    L_per_pass = L_total / max(passes, 1)
                else:
                    L_per_pass = L_total

                # film temperatures (simple mean)
                T_tube_bulk = 0.5 * ((_val(parms.get("Hot in Temp"),"Hot In") if assignment[0]=="hot_tube" else _val(parms.get("Cold in Temp"),"Cold In")) +
                                     (_val(parms.get("Hot out Temp"),"Hot Out") if assignment[0]=="hot_tube" else _val(parms.get("Cold out Temp"),"Cold Out")))
                T_ann_bulk = 0.5 * ((_val(parms.get("Cold in Temp"),"Cold In") if assignment[0]=="hot_tube" else _val(parms.get("Hot in Temp"),"Hot In")) +
                                     (_val(parms.get("Cold out Temp"),"Cold Out") if assignment[0]=="hot_tube" else _val(parms.get("Hot out Temp"),"Hot Out")))

                # get properties via component (assumed methods take temperature or ignore)
                mu_t = tube_stream.component.viscosity(T_tube_bulk).to("Pa*s").value
                rho_t = tube_stream.component.density(T_tube_bulk).to("kg/m^3").value
                k_t = tube_stream.component.thermal_conductivity(T_tube_bulk).to("W/m-K").value
                try:
                    cp_t = tube_stream.component.specific_heat(T_tube_bulk).to("J/kg-K").value
                except Exception:
                    cp_t = cp_tube

                mu_a = ann_stream.component.viscosity(T_ann_bulk).to("Pa*s").value
                rho_a = ann_stream.component.density(T_ann_bulk).to("kg/m^3").value
                k_a = ann_stream.component.thermal_conductivity(T_ann_bulk).to("W/m-K").value
                try:
                    cp_a = ann_stream.component.specific_heat(T_ann_bulk).to("J/kg-K").value
                except Exception:
                    cp_a = cp_ann

                # Cross-sectional areas
                A_tube_single = math.pi * Di * Di / 4.0
                A_annulus_single = math.pi * (Do**2 - Di**2) / 4.0

                # velocities (per channel)
                v_tube = m_tube_channel / (rho_t * A_tube_single)
                v_ann = m_ann_channel / (rho_a * A_annulus_single)

                # Reynolds and Prandtl
                Re_t = rho_t * v_tube * Di / mu_t
                Re_a = rho_a * v_ann * (Do - Di) / mu_a  # hydraulic diameter approx = Do - Di
                Pr_t = _prandtl(cp_t, mu_t, k_t)
                Pr_a = _prandtl(cp_a, mu_a, k_a)

                # friction factors (Colebrook/Haaland)
                eps_rel_t = roughness / Di
                eps_rel_a = roughness / max((Do - Di), Di*1e-6)
                f_t = _colebrook_f(max(Re_t, 1e-6), eps_rel_t)
                f_a = _colebrook_f(max(Re_a, 1e-6), eps_rel_a)

                # Nusselt numbers (Gnielinski preferred, Dittus fallback)
                Nu_t = _nusselt_gnielinski(max(Re_t,1e-6), max(Pr_t,1e-6), f_t)
                Nu_a = _nusselt_annulus(max(Re_a,1e-6), max(Pr_a,1e-6), Do, Di, f_a)

                # film coefficients
                h_t = Nu_t * k_t / Di
                h_a = Nu_a * k_a / max((Do - Di), Di*1e-6)

                # Resistances referenced to inner area (per inner tube)
                R_conv_i = 1.0 / h_t
                R_wall = (Di * math.log(Do / Di)) / (2.0 * wall_k_val)  # inner-area ref
                R_conv_o = (Di / Do) * (1.0 / h_a)

                # Fouling added in area-basis
                R_foul_i = fouling_tube
                R_foul_o = fouling_shell * (Di / Do)

                R_total_area = R_conv_i + R_wall + R_conv_o + R_foul_i + R_foul_o
                U_new = 1.0 / R_total_area  # W/m2K (inner area reference)

                # --------------------------
                # NTU -> epsilon -> Ft block
                # --------------------------
                # Capacity rates
                Ch = m_tube * cp_t
                Cc = m_ann * cp_a
                Cmin = min(Ch, Cc)
                Cmax = max(Ch, Cc)
                C_ratio = (Cmin / Cmax) if Cmax>0 else 0.0

                # raw area guess using previous U_ref and L_total:
                # compute current total inner area available for heat transfer
                if inner_mode == "parallel":
                    total_inner_area = n_inner_channels * math.pi * Di * L_per_pass
                else:
                    total_inner_area = math.pi * Di * (L_per_pass * passes)

                UA = U_new * total_inner_area
                NTU_raw = UA / Cmin if Cmin>0 else 0.0

                # apply pass-scaling heuristic to NTU
                ntu_scale = _ntuscaling_for_passes(inner_mode, passes)
                NTU_effective = NTU_raw * ntu_scale

                # epsilon for chosen arrangement
                eps = _epsilon_from_arrangement(arrangement, NTU_effective, C_ratio)

                # delta_T_in and delta_T_lm definitions
                delta_T_in = (Th_in - Tc_in)
                # compute delta_T_lm guarded
                dT1 = Th_in - Tc_out
                dT2 = Th_out - Tc_in
                if dT1 * dT2 <= 0:
                    delta_T_lm = max(abs(dT1), abs(dT2), 1e-6)
                else:
                    delta_T_lm = (dT1 - dT2) / math.log(dT1 / dT2)

                # compute Ft: either chart-based (if pass_layout provided) or NTU-derived
                Ft = 1.0
                if pass_layout and pass_layout in _CHART_FT_MAP:
                    # use chart approximations with NTU_raw and C_ratio
                    Ft_func = _CHART_FT_MAP[pass_layout]
                    Ft = Ft_func(NTU_raw, C_ratio)
                else:
                    # NTU-derived formula: Ft = (eps * delta_T_in) / (NTU_raw * delta_T_lm)
                    if NTU_raw <= 1e-12 or delta_T_lm == 0:
                        Ft = 1.0
                    else:
                        Ft = (eps * delta_T_in) / (NTU_raw * delta_T_lm)
                        Ft = max(1e-6, min(1.0, Ft))

                # required total area (including Ft correction)
                A_required = abs(Q) / (U_new * delta_T_lm * Ft) if (U_new*delta_T_lm*Ft) > 0 else float("inf")

                # translate required area to total L_total (inner-area basis)
                L_required = A_required / (math.pi * Di)

                # damping & convergence on L and U
                # mix new U & old U to stabilize
                U_ref = 0.6 * U_new + 0.4 * (U_new if iteration==0 else U_ref if 'U_ref' in locals() else U_new)
                # update L_total with damping
                L_total_new = 0.6 * L_required + 0.4 * L_total
                if abs(L_total_new - L_total) / max(1e-9, L_total_new) < tol and abs(U_new - U_ref) / max(1e-9, U_ref) < tol:
                    L_total = L_total_new
                    U_ref = U_new
                    converged = True
                    break

                L_total = L_total_new
                U_ref = U_new

            # end iteration loop

            # Final recomputation after converge/exit
            # compute final per-channel velocities and Re for pressure drop
            if inner_mode == "parallel":
                n_inner_channels = passes
                m_tube_channel = m_tube / n_inner_channels
            else:
                n_inner_channels = 1
                m_tube_channel = m_tube

            m_ann_channel = m_ann / n_ann_channels

            A_tube_single = math.pi * Di * Di / 4.0
            A_annulus_single = math.pi * (Do**2 - Di**2) / 4.0

            v_tube = m_tube_channel / (rho_t * A_tube_single)
            v_ann = m_ann_channel / (rho_a * A_annulus_single)

            Re_t_final = rho_t * v_tube * Di / mu_t
            Re_a_final = rho_a * v_ann * (Do - Di) / mu_a

            f_t_final = _colebrook_f(max(Re_t_final,1e-6), roughness / Di)
            f_a_final = _colebrook_f(max(Re_a_final,1e-6), roughness / max((Do - Di), 1e-6))

            # dp per channel
            dp_tube_channel = _deltaP_darcy(f_t_final, L_per_pass, Di, rho_t, v_tube)
            # scale dp for series passes
            dp_tube_system = dp_tube_channel * (passes if inner_mode=="series" else 1)
            dp_ann_channel = _deltaP_darcy(f_a_final, L_per_pass, (Do - Di), rho_a, v_ann)
            # parallel annuli share same dp (pump sees per-channel dp)
            dp_ann_system = dp_ann_channel

            total_dp = dp_tube_system + dp_ann_system

            # apply dp_limit penalty if provided
            penalty = 0.0
            if dp_limit is not None:
                if dp_tube_system > dp_limit or dp_ann_system > dp_limit:
                    penalty = 1e6 + (dp_tube_system + dp_ann_system - dp_limit)

            # scoring metric: minimize total length, penalize dp violation
            score = L_total + penalty

            result = {
                "pipe_Di_m": Di,
                "pipe_Do_m": Do,
                "assignment": assignment,
                "inner_mode": inner_mode,
                "passes": passes,
                "annulus_parallel": annulus_parallel,
                "L_total_m": L_total,
                "L_per_pass_m": L_per_pass,
                "U_ref_W_m2K": U_ref,
                "Ft": Ft,
                "A_required_m2": A_required,
                "Q_W": Q,
                "Re_tube": Re_t_final,
                "Re_annulus": Re_a_final,
                "Nu_tube": Nu_t,
                "Nu_annulus": Nu_a,
                "dp_tube_Pa": dp_tube_system,
                "dp_annulus_Pa": dp_ann_system,
                "total_dp_Pa": total_dp,
                "converged": converged,
                "iterations": iteration+1,
            }

            if score < best_score:
                best_score = score
                best_result = result

    if best_result is None:
        raise RuntimeError("No feasible design found with given options / pipe library.")

    # attach design to hx for downstream use
    hx.design_results = best_result
    return best_result
