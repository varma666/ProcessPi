"""
processpi/equipment/heatexchangers/double_pipe.py

Updated double-pipe heat exchanger design routine:
- Iterative convergence: Re -> f (Colebrook/Haaland) -> Nu -> h -> U -> A/L -> Re
- Tube (inner) vs Annulus (outer) swap and auto-selection
- Multi-pass support (series / parallel), parallel annuli
- NTU -> epsilon -> Ft integration
- Chart-based Ft heuristics
- Minor-loss K_total handling (dp_minor = K_total * 0.5 * rho * v^2)
- Hairpin counting helper and fouling utilities for textbook problems
- Uses your unit wrappers: Diameter, Length, Pressure, Temperature, MassFlowRate, Conductivity, Variable
- Expects hx.simulated_params to contain Hot/Cold temps, m_hot/m_cold, cP_hot/cP_cold, and optionally given_length.
"""

import math
from typing import Dict, Any, Optional, Tuple, List, Union

from processpi.calculations.heat_transfer.overall_u import OverallHeatTransferCoefficient
from ....units import *
from ....streams.material import MaterialStream
from ..base import HeatExchanger
from ....pipelines import Pipe
from ..standards import get_typical_k

# ------------------------------------------------------------------
# TUNABLE DEFAULTS
# ------------------------------------------------------------------
_DEFAULT_WALL_K = 16.0  # W/m-K, pipe material (carbon steel)
_DEFAULT_ROUGHNESS = 1.5e-5  # m (commercial steel)
_DEFAULT_FOULING_TUBE = 1e-4  # m2K/W
_DEFAULT_FOULING_SHELL = 2e-4  # m2K/W
_DEFAULT_MAX_ITERS = 300
_DEFAULT_TOL = 1e-5
_DEFAULT_K_MINOR_TUBE = 2.5   # typical total K for bends + entrance/exit for hairpin
_DEFAULT_K_MINOR_ANNULUS = 1.5

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
    for _ in range(40):
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f)))
        res = lhs - rhs
        # numerical derivative
        df = 1e-8
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
        if abs(f_new - f) / f_new < 1e-9:
            f = f_new
            break
        f = f_new
    return max(f, 1e-12)

# ------------------------------------------------------------------
# Nusselt correlations (Gnielinski + fallback Dittus-Boelter)
# ------------------------------------------------------------------
def _prandtl(cp: float, mu: float, k: float) -> float:
    # cp [J/kg-K], mu [Pa.s], k [W/m-K] -> Pr dimensionless
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
        return _epsilon_counterflow(NTU, C)

# ------------------------------------------------------------------
# Pass-scaling heuristic for NTU
# ------------------------------------------------------------------
def _ntuscaling_for_passes(inner_mode: str, passes: int) -> float:
    if passes <= 1:
        return 1.0
    if inner_mode == "series":
        if passes == 2:
            return 1.85
        if passes == 4:
            return 3.5
        return float(passes) * 0.9
    elif inner_mode == "parallel":
        return 1.0 / float(passes)
    return 1.0

# ------------------------------------------------------------------
# Chart-based Ft for common pass layouts
# ------------------------------------------------------------------
def Ft_chart_1_1(NTU: float, C: float) -> float:
    return 1.0

def Ft_chart_1_2(NTU: float, C: float) -> float:
    return max(0.1, min(1.0, 1.0 - 0.1 * (1.0 - math.exp(-0.5 * NTU)) * (1.0 - C)))

def Ft_chart_2_1(NTU: float, C: float) -> float:
    return Ft_chart_1_2(NTU, C)

def Ft_chart_1_4(NTU: float, C: float) -> float:
    return max(0.05, min(1.0, 1.0 - 0.25 * (1.0 - math.exp(-0.4 * NTU)) * (1.0 - C)))

def Ft_chart_2_2(NTU: float, C: float) -> float:
    return max(0.05, min(1.0, 1.0 - 0.18 * (1.0 - math.exp(-0.45 * NTU)) * (1.0 - C)))

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
# Fouling helpers
# ------------------------------------------------------------------
def fouling_from_U(Uc: float, Ud: float) -> float:
    """
    Return equivalent area-based fouling resistance R_f (m2K/W) given clean Uc and dirty Ud.
    R_f = 1/Ud - 1/Uc (area referenced to same area)
    """
    if Uc <= 0 or Ud <= 0:
        raise ValueError("Uc and Ud must be positive")
    return max(0.0, (1.0 / Ud) - (1.0 / Uc))

def fouling_rate_from_temp_trend(U_initial: float, Thot_in: float, Thot_out_initial: float,
                                 Thot_out_later: float, months: float, C_hot: float,
                                 C_cold: float, A: float) -> float:
    """
    Rough linear fouling-rate estimate (R_f per month) from observed hot outlet temperature trend.
    - U_initial: initial overall U (W/m2K)
    - Thot_in/out initial & later (°C)
    - months: months between measurements
    - C_hot/C_cold: heat capacity rates (W/K) for hot and cold
    - A: hot-side area (m2)
    Returns fouling rate (m2K/W per month).
    NOTE: heuristic / approximate; textbooks often use change in heat transfer coefficient.
    """
    # Compute Q initial and later from hot side measured temperatures (approx)
    Q_initial = C_hot * (Thot_in - Thot_out_initial)
    Q_later = C_hot * (Thot_in - Thot_out_later)
    if Q_initial <= 0:
        return 0.0
    # infer Ud_initial and Ud_later from Q = U*A*LMTD_effective => assume LMTD approx same
    # thus Ud_later / Ud_initial = Q_later / Q_initial
    if Q_initial == 0:
        return 0.0
    Ud_ratio = Q_later / Q_initial
    Ud_later = U_initial * Ud_ratio
    # fouling change
    Rf_initial = fouling_from_U(U_initial, U_initial)  # zero
    Rf_later = fouling_from_U(U_initial, Ud_later)
    # per month
    if months <= 0:
        return Rf_later
    return Rf_later / months

# ------------------------------------------------------------------
# Top-level design function (end-to-end)
# ------------------------------------------------------------------
def design_doublepipe(
    hx: HeatExchanger,
    *,
    innerpipe_dia: Optional[Diameter] = None,
    outerpipe_dia: Optional[Diameter] = None,
    schedule_inner: Optional[str] = None,
    schedule_outer: Optional[str] = None,
    inner_mode: str = "series",        # "series" or "parallel"
    passes: int = 1,                   # 1,2,4 supported (tube-side logical passes)
    annulus_parallel: int = 1,         # number of parallel annuli
    arrangement: str = "counterflow",  # 'counterflow' or 'parallel' (used for epsilon)
    pass_layout: Optional[str] = None, # e.g., "1-1","1-2","2-1","1-4","2-2" -> use chart Ft if provided
    target_dp: Optional[Pressure] = None,
    pipe_library: Optional[Dict[Diameter, Dict[str, Tuple[Length, Diameter, Diameter]]]] = None,
    wall_k: Union[float, ThermalConductivity] = _DEFAULT_WALL_K,
    roughness: float = _DEFAULT_ROUGHNESS,
    fouling_tube: float = _DEFAULT_FOULING_TUBE,
    fouling_shell: float = _DEFAULT_FOULING_SHELL,
    k_minor_tube: float = _DEFAULT_K_MINOR_TUBE,
    k_minor_annulus: float = _DEFAULT_K_MINOR_ANNULUS,
    max_iters: int = _DEFAULT_MAX_ITERS,
    tol: float = _DEFAULT_TOL,
    hairpin_length: Optional[float] = None,   # if provided, compute hairpin count
    hairpin_pipe_inner_id: Optional[float] = None,  # required if hairpin counting requested
    hairpin_pipe_outer_od: Optional[float] = None,
    inner_pipe: Optional[Pipe] = None,
    outer_pipe: Optional[Pipe] = None
) -> Dict[str, Any]:
    """
    Perform a detailed double-pipe heat exchanger design with Ft integration.
    Returns a results dict with U, L, Ft, Re, Nu, dp, chosen pipe, hairpin count (if requested) and iteration info.

    Notes:
    - Multi-pass tube handling: mass flow remains constant; effective heat transfer area is
      inner_area * passes for NTU calculation (as requested).
    - Minor losses are added as dp_minor = K_total * 0.5 * rho * v^2 for each stream.
    """
    parms = _get_parms(hx)

    # Extract required simulated params (must exist)
    #print("Extracting parameters...")
    Th_in = _val(parms.get("Hot in Temp"), "Hot In Temp")
    Th_out = _val(parms.get("Hot out Temp"), "Hot Out Temp")
    Tc_in = _val(parms.get("Cold in Temp"), "Cold In Temp")
    Tc_out = _val(parms.get("Cold out Temp"), "Cold Out Temp")
    m_hot = _val(parms.get("m_hot"), "m_hot")          # kg/s
    m_cold = _val(parms.get("m_cold"), "m_cold")      # kg/s
    cp_hot = _val(parms.get("cP_hot"), "cP_hot") * 1000      # converting kJ/kgK to J/kg-K
    cp_cold = _val(parms.get("cP_cold"), "cP_cold") * 1000      # converting kJ/kgK to J/kg-K   # J/kg-K
    delta_Tlm_param = parms.get("delta_Tlm")  # optional; keep unit-wrapped
    #print("Parameters extracted.")

    # energy
    Q_hot = m_hot * cp_hot * (Th_in - Th_out)
    Q_cold = m_cold * cp_cold * (Tc_out - Tc_in)
    # Prefer the average of two when both exist to avoid sign issues
    #print("Calculating heat duty...")
    if abs(Q_hot) > 0 and abs(Q_cold) > 0:
        Q = 0.5 * (Q_hot + Q_cold)
    else:
        Q = Q_hot if abs(Q_hot) > 0 else Q_cold

    # convert options
    #print("Converting options...")
    if inner_pipe is not None:
        wall_k_val = get_typical_k(inner_pipe.material)
    else:
        wall_k_val = wall_k.value if hasattr(wall_k, "value") else float(wall_k)
    dp_limit = None
    if target_dp is not None:
        try:
            dp_limit = target_dp.to("Pa").value
        except Exception:
            dp_limit = target_dp.value if hasattr(target_dp, "value") else float(target_dp)

    # pipe library fallback (inner ID, outer OD) pairs in meters
    #print("Selecting pipe library...")
    if pipe_library is None:
        pipe_pairs = [
            (0.0127, 0.0213),  # 1/2" ID ~12.7mm, OD ~21.3mm
            (0.01905, 0.0267),
            (0.0254, 0.0334),
            (0.03175, 0.0422),
            (0.0508, 0.0635),
        ]
    else:
        pipe_pairs = []
        for nominal_d, schedules in pipe_library.items():
            sched_keys = list(schedules.keys())
            chosen = schedule_inner if schedule_inner in schedules else sched_keys[0]
            _, od, id_inner = schedules[chosen]
            try:
                Di = id_inner.to("m").value
            except Exception:
                Di = id_inner.value if hasattr(id_inner, "value") else float(id_inner)
            try:
                Od = od.to("m").value
            except Exception:
                Od = od.value if hasattr(od, "value") else float(od)
            pipe_pairs.append((Di, Od))

    # override if explicit diameters provided

    if innerpipe_dia is not None and outerpipe_dia is not None:
        pipe_pairs = [(innerpipe_dia.to("m").value, outerpipe_dia.to("m").value)]

    # assignments to try
    #print("Setting up assignments...")
    assignments = [
        ("hot_tube", "cold_annulus"),
        ("cold_tube", "hot_annulus"),
    ]

    best_result = None
    best_score = float("inf")
    #print("Starting design iterations...")
    for (Di, Do) in pipe_pairs:
        if Do <= Di * 1.05:
            continue
        #print(f"Trying pipe pair: Inner Diameter = {Di} m, Outer Diameter = {Do} m")

        for assignment in assignments:
            # map streams
            if assignment[0] == "hot_tube":
                tube_stream = hx.hot_in
                ann_stream = hx.cold_in
                m_tube = m_hot; m_ann = m_cold
                cp_tube_nom = cp_hot; cp_ann_nom = cp_cold
            else:
                tube_stream = hx.cold_in
                ann_stream = hx.hot_in
                m_tube = m_cold; m_ann = m_hot
                cp_tube_nom = cp_cold; cp_ann_nom = cp_hot

            # per-channel flows depend on inner_mode but mass flow remains constant across passes
            if inner_mode == "parallel":
                n_inner_channels = passes
            else:
                n_inner_channels = 1

            m_tube_channel = m_tube / n_inner_channels
            n_ann_channels = annulus_parallel
            m_ann_channel = m_ann / n_ann_channels

            # initial guesses
            L_total = 2.0  # m
            U_ref = 200.0
            converged = False
            iteration = 0
            #print("Starting iterations...")
            for iteration in range(max_iters):
                # per-pass length
                if inner_mode == "series":
                    L_per_pass = L_total / max(passes, 1)
                else:
                    L_per_pass = L_total

                # film temperatures (simple mean of inlet/outlet for each side depending assignment)
                if assignment[0] == "hot_tube":
                    T_tube_bulk = 0.5 * ((_val(parms.get("Hot in Temp"), "Hot In")) + (_val(parms.get("Hot out Temp"), "Hot Out")))
                    T_ann_bulk = 0.5 * ((_val(parms.get("Cold in Temp"), "Cold In")) + (_val(parms.get("Cold out Temp"), "Cold Out")))
                else:
                    T_tube_bulk = 0.5 * ((_val(parms.get("Cold in Temp"), "Cold In")) + (_val(parms.get("Cold out Temp"), "Cold Out")))
                    T_ann_bulk = 0.5 * ((_val(parms.get("Hot in Temp"), "Hot In")) + (_val(parms.get("Hot out Temp"), "Hot Out")))

                # fetch fluid properties from stream components at film temps; fall back to cp_nom if missing
                try:
                    mu_t = tube_stream.component.viscosity(T_tube_bulk).to("Pa.s").value
                    rho_t = tube_stream.component.density(T_tube_bulk).to("kg/m3").value
                    k_t = tube_stream.component.thermal_conductivity(T_tube_bulk).to("W/mK").value
                    cp_t = tube_stream.component.specific_heat(T_tube_bulk).to("J/kgK").value
                except Exception:
                    # fallback assumptions (less ideal)
                    mu_t = 1e-3
                    rho_t = 1000.0
                    k_t = 0.12
                    cp_t = cp_tube_nom

                try:
                    mu_a = ann_stream.component.viscosity(T_ann_bulk).to("Pa.s").value
                    rho_a = ann_stream.component.density(T_ann_bulk).to("kg/m3").value
                    k_a = ann_stream.component.thermal_conductivity(T_ann_bulk).to("W/mK").value
                    cp_a = ann_stream.component.specific_heat(T_ann_bulk).to("J/kgK").value
                except Exception:
                    mu_a = 1e-3
                    rho_a = 1000.0
                    k_a = 0.12
                    cp_a = cp_ann_nom

                # Cross-sectional areas (single inner tube and single annulus)
                A_tube_single = math.pi * (Di ** 2) / 4.0
                A_annulus_single = math.pi * (Do ** 2 - Di ** 2) / 4.0

                # velocities (per channel)
                v_tube = m_tube_channel / (rho_t * A_tube_single)
                v_ann = m_ann_channel / (rho_a * A_annulus_single)

                # Reynolds and Prandtl
                Re_t = rho_t * v_tube * Di / max(mu_t, 1e-12)
                Re_a = rho_a * v_ann * max((Do - Di), 1e-6) / max(mu_a, 1e-12)  # Dh ≈ Do - Di
                Pr_t = _prandtl(cp_t, mu_t, k_t)
                Pr_a = _prandtl(cp_a, mu_a, k_a)

                # friction factors
                eps_rel_t = roughness / Di
                eps_rel_a = roughness / max((Do - Di), Di * 1e-6)
                f_t = _colebrook_f(max(Re_t, 1e-6), eps_rel_t)
                f_a = _colebrook_f(max(Re_a, 1e-6), eps_rel_a)

                # Nusselt numbers
                Nu_t = _nusselt_gnielinski(max(Re_t, 1e-6), max(Pr_t, 1e-6), f_t)
                Nu_a = _nusselt_annulus(max(Re_a, 1e-6), max(Pr_a, 1e-6), Do, Di, f_a)

                # film coefficients
                h_t = Nu_t * k_t / Di
                h_a = Nu_a * k_a / max((Do - Di), Di * 1e-6)

                # ------------------------------------------------------------------
                # Step 10: Clean Uc (area refs to inner area)
                # Resistances referenced to inner-surface area (m2 K/W)
                R_conv_i = 1.0 / max(h_t, 1e-12)
                # wall resistance per inner-area reference: (Di * ln(Do/Di)) / (2 * k_wall)
                R_wall = (Di * math.log(Do / Di)) / (2.0 * wall_k_val)
                R_conv_o = (Di / Do) * (1.0 / max(h_a, 1e-12))
                R_foul_i = fouling_tube
                R_foul_o = fouling_shell * (Di / Do)
                R_total_area = R_conv_i + R_wall + R_conv_o + R_foul_i + R_foul_o
                U_new = 1.0 / max(R_total_area, 1e-12)  # W/m2K (inner area reference)
                # ------------------------------------------------------------------

                # --------------------------
                # NTU -> epsilon -> Ft block
                # --------------------------
                Ch = m_tube * cp_t
                Cc = m_ann * cp_a
                Cmin = min(Ch, Cc)
                Cmax = max(Ch, Cc)
                C_ratio = (Cmin / Cmax) if Cmax > 0 else 0.0

                # compute total inner area available for heat transfer:
                # as requested => effective area = inner_perimeter * L_per_pass * passes * n_inner_channels
                # Note: the user's choice was **mass flow constant** and **effective area × passes** in NTU.
                inner_perimeter = math.pi * Di
                effective_inner_area = inner_perimeter * L_per_pass * passes * n_inner_channels

                UA = U_new * effective_inner_area
                NTU_raw = UA / Cmin if Cmin > 0 else 0.0

                ntu_scale = _ntuscaling_for_passes(inner_mode, passes)
                NTU_effective = NTU_raw * ntu_scale

                eps = _epsilon_from_arrangement(arrangement, NTU_effective, C_ratio)

                # delta_T_lm
                dT1 = Th_in - Tc_out
                dT2 = Th_out - Tc_in
                if dT1 * dT2 <= 0:
                    delta_T_lm = max(abs(dT1), abs(dT2), 1e-6)
                else:
                    delta_T_lm = (dT1 - dT2) / math.log(dT1 / dT2)

                # compute Ft either from chart or NTU-derived
                Ft = 1.0
                if pass_layout and pass_layout in _CHART_FT_MAP:
                    Ft = _CHART_FT_MAP[pass_layout](NTU_raw, C_ratio)
                else:
                    if NTU_raw <= 1e-12 or delta_T_lm == 0:
                        Ft = 1.0
                    else:
                        Ft_calc = (eps * (Th_in - Tc_in)) / (NTU_raw * delta_T_lm)
                        Ft = max(1e-6, min(1.0, Ft_calc))

                # required total inner area (based on current U_new and Ft)
                denom = U_new * delta_T_lm * Ft
                if denom <= 0:
                    A_required = float("inf")
                else:
                    A_required = abs(Q) / denom

                L_required = A_required / (math.pi * Di * passes * n_inner_channels)  # distribute area over passes & channels

                # damping for stable convergence
                U_ref = 0.6 * U_new + 0.4 * U_ref
                L_total_new = 0.6 * L_required + 0.4 * L_total

                # stopping criteria: relative change in L and U
                if abs(L_total_new - L_total) / max(1e-9, L_total_new) < tol and abs(U_new - U_ref) / max(1e-9, U_ref) < tol:
                    L_total = L_total_new
                    U_ref = U_new
                    converged = True
                    break

                L_total = L_total_new
                U_ref = U_new
                #print(f"Iteration {iteration+1}: L_total = {L_total}, U_ref = {U_ref}")
            # end iterative loop
            #print("Design iterations completed.")
            # Final recomputation after converge/exit for dp calculations
            #print("Recomputing pressure drops and final parameters...")
            if inner_mode == "parallel":
                n_inner_channels = passes
            else:
                n_inner_channels = 1
            m_tube_channel = m_tube / n_inner_channels
            m_ann_channel = m_ann / n_ann_channels

            A_tube_single = math.pi * (Di ** 2) / 4.0
            A_annulus_single = math.pi * (Do ** 2 - Di ** 2) / 4.0

            v_tube = m_tube_channel / (rho_t * A_tube_single)
            v_ann = m_ann_channel / (rho_a * A_annulus_single)

            Re_t_final = rho_t * v_tube * Di / max(mu_t, 1e-12)
            Re_a_final = rho_a * v_ann * max((Do - Di), 1e-6) / max(mu_a, 1e-12)

            f_t_final = _colebrook_f(max(Re_t_final, 1e-6), roughness / Di)
            f_a_final = _colebrook_f(max(Re_a_final, 1e-6), roughness / max((Do - Di), 1e-6))

            dp_tube_fric = _deltaP_darcy(f_t_final, L_per_pass, Di, rho_t, v_tube)
            dp_tube_system = dp_tube_fric * (passes if inner_mode == "series" else 1)
            dp_tube_minor = k_minor_tube * 0.5 * rho_t * v_tube * v_tube
            dp_tube_total = dp_tube_system + dp_tube_minor

            dp_ann_fric = _deltaP_darcy(f_a_final, L_per_pass, (Do - Di), rho_a, v_ann)
            dp_ann_system = dp_ann_fric  # annulus typically single pass length
            dp_ann_minor = k_minor_annulus * 0.5 * rho_a * v_ann * v_ann
            dp_ann_total = dp_ann_system + dp_ann_minor

            total_dp = dp_tube_total + dp_ann_total

            penalty = 0.0
            if dp_limit is not None:
                if dp_tube_total > dp_limit or dp_ann_total > dp_limit:
                    penalty = 1e6 + (dp_tube_total + dp_ann_total - dp_limit)

            # scoring metric: minimize total length + dp penalty
            score = L_total + penalty

            # hairpin counting if requested (hairpin_length provided)
            hairpin_info = {}
            if hairpin_length and hairpin_pipe_inner_id and hairpin_pipe_outer_od:
                # area per hairpin (single hairpin has inner_perimeter * length * passes_per_hairpin)
                # hairpin is typically one U-turn: treat each hairpin as a single inner tube of length hairpin_length
                hairpin_area_per = math.pi * hairpin_pipe_inner_id * hairpin_length
                hairpins_required = math.ceil((A_required) / hairpin_area_per) if A_required != float("inf") else None
                hairpin_info = {
                    "hairpin_length_m": hairpin_length,
                    "hairpin_area_m2": hairpin_area_per,
                    "hairpins_required": hairpins_required
                }

            result = {
                "innerpipe_dia": Diameter(Di,"m"),
                "outerpipe_dia": Diameter(Do,"m"), 
                "assignment": assignment,
                "inner_mode": inner_mode,
                "passes": passes,
                "annulus_parallel": annulus_parallel,
                "total_length": Length(L_total,"m"),
                "length_per_pass": Length(L_per_pass,"m"),
                "U_ref": HeatTransferCoefficient(U_ref,"W/m2K"),
                "U_max": HeatTransferCoefficient(U_new,"W/m2K"),
                "Ft": Ft,
                "required_area": Area(A_required,"m2"),
                "effective_area": Area(effective_inner_area,"m2"),
                "Q": HeatFlow(Q,"W"),
                "Re_tube": Dimensionless(Re_t_final),
                "Re_annulus": Dimensionless(Re_a_final),
                "Nu_tube": Dimensionless(Nu_t),
                "Nu_annulus": Dimensionless(Nu_a),
                "dp_tube": Pressure(dp_tube_total,"Pa"),
                "dp_annulus": Pressure(dp_ann_total,"Pa"),
                "total_dp": Pressure(total_dp,"Pa"),
                "converged": converged,
                "iterations": iteration + 1,
                "hairpin_info": hairpin_info,
            }

            if score < best_score:
                best_score = score
                best_result = result

    if best_result is None:
        raise RuntimeError("No feasible design found with given options / pipe library.")

    # attach design to hx for downstream use
    hx.design_results = best_result
    return best_result
