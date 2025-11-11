"""
processpi/equipment/heatexchangers/shell_tube.py

Shell-and-Tube Heat Exchanger advanced design — merged & improved:
- Bell-Delaware shell-side heat transfer and pressure-drop model (detailed)
- Exact triangular & square packing (robust layering)
- Improved hydraulic diameter calculation (cell-based) for Dh/De
- Header / nozzle / manifold basic design and K-losses
- NTU → epsilon → Ft integrated into LMTD area equation
- tube_side_hot default = True (tube side treated as HOT unless overridden)
- Multi-pass tube arrangements supported
- Mechanical summary (weld counts, material weight estimate)

Notes:
- This is a practical engineering implementation with documented approximations.
- Replace constants or correlation pieces if you have more accurate vendor correlations.
"""

import math
from typing import Dict, Any, Optional, Tuple, List, Union
from ....units import Diameter, Length, Pressure, ThermalConductivity, Variable
from ....streams.material import MaterialStream
from ..base import HeatExchanger

# Optional: if your repo provides pipe schedules/standards, import them
try:
    from ...standards import PIPE_SCHEDULES, STANDARD_SIZES
except Exception:
    PIPE_SCHEDULES = None
    STANDARD_SIZES = None

# -------------------------------------------------------------------------
# Defaults and constants (tuneable)
# -------------------------------------------------------------------------
_DEFAULT_WALL_K = 16.0       # W/m-K for carbon steel tube wall conduction
_DEFAULT_ROUGHNESS = 1.5e-5  # m absolute roughness
_DEFAULT_FOULING_TUBE = 1e-4  # m2K/W
_DEFAULT_FOULING_SHELL = 2e-4  # m2K/W
_STEEL_DENSITY = 7850.0      # kg/m^3 for weight estimation
_DEFAULT_MAX_ITERS = 300
_DEFAULT_TOL = 1e-5

# Header/manifold K-factors defaults (engineering approximations)
_HEADER_KS = {
    "inlet_nozzle": 0.5,
    "outlet_nozzle": 1.0,
    "elbow": 0.9,
    "tee_branch": 2.0,
    "tee_run": 1.0,
    "entrance": 0.5,
    "exit": 1.0
}

# -------------------------------------------------------------------------
# Small utilities
# -------------------------------------------------------------------------
def _get_parms(hx: HeatExchanger) -> Dict[str, Any]:
    if hx.simulated_params is None:
        raise ValueError("Heat exchanger has not been simulated yet (simulated_params missing).")
    return hx.simulated_params

def _val(v, name: str):
    if v is None:
        return None
    if hasattr(v, "value"):
        return v.value
    if isinstance(v, (int, float)):
        return float(v)
    raise TypeError(f"{name} must be numeric or unit-wrapped.")

# -------------------------------------------------------------------------
# Friction factor helpers (Haaland + Colebrook)
# -------------------------------------------------------------------------
def _haaland_f(Re: float, eps_rel: float) -> float:
    if Re <= 0:
        return 1e6
    if Re < 2300:
        return 64.0 / max(Re, 1e-12)
    term = -1.8 * math.log10((eps_rel / 3.7) ** 1.11 + 6.9 / Re)
    return (1.0 / term) ** 2

def _colebrook_f(Re: float, eps_rel: float) -> float:
    if Re < 2300:
        return 64.0 / max(Re, 1e-12)
    f = _haaland_f(Re, eps_rel)
    for _ in range(40):
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f)))
        res = lhs - rhs
        # numerical derivative approximation
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

# -------------------------------------------------------------------------
# Tube-side correlations (Gnielinski + Dittus–Boelter)
# -------------------------------------------------------------------------
def _prandtl(cp: float, mu: float, k: float) -> float:
    return cp * mu / k

def _nusselt_gnielinski(Re: float, Pr: float, f: float) -> float:
    """Gnielinski correlation for turbulent flow inside tubes."""
    if Re <= 2300:
        return 3.66
    Nu = (f/8.0) * (Re - 1000.0) * Pr / (1.0 + 12.7 * (f/8.0)**0.5 * (Pr**(2.0/3.0) - 1.0))
    return max(3.66, Nu)

def _nusselt_dittus(Re: float, Pr: float, n_pr: float = 0.4) -> float:
    if Re <= 2300:
        return 3.66
    return 0.023 * (Re ** 0.8) * (Pr ** n_pr)

# -------------------------------------------------------------------------
# Bundle packing: triangular & square layouts (exact layer algorithm)
# Returns tube center coordinates and counts for a round shell
# -------------------------------------------------------------------------
def pack_tubes_in_shell(D_shell: float, D_tube: float, pitch: float, layout: str = "triangular") -> Tuple[List[Tuple[float,float]], int]:
    """
    Compute tube center coordinates (x,y) that fit in circular shell.
    layout: 'triangular' or 'square'
    pitch: center-to-center distance between adjacent tubes
    Return: (list_of_centers, N_tubes)
    Notes:
      - coordinates are in m, shell center at (0,0)
      - This routine performs grid/hexagonal layering then filters points inside shell
    """
    centers: List[Tuple[float,float]] = []
    R = D_shell / 2.0
    if layout == "triangular":
        dy = math.sqrt(3)/2 * pitch
        # determine reasonable extents to search (extend a few pitches beyond theoretical)
        y_min = -R - pitch
        y_max = R + pitch
        j = 0
        y = y_min
        row = 0
        while y <= y_max:
            row_offset = (0.5 * pitch) if (row % 2 == 1) else 0.0
            # x limits for this row's tube centers
            x_min = -R - pitch
            x_max = R + pitch
            x = x_min
            while x <= x_max:
                xc = x + row_offset
                yc = y
                if xc*xc + yc*yc <= (R - 0.5*D_tube)**2:
                    centers.append((xc, yc))
                x += pitch
            row += 1
            y += dy
    else:
        dy = pitch
        y_min = -R - pitch
        y_max = R + pitch
        y = y_min
        while y <= y_max:
            x = -R - pitch
            while x <= R + pitch:
                if x*x + y*y <= (R - 0.5*D_tube)**2:
                    centers.append((x, y))
                x += pitch
            y += dy
    return centers, len(centers)

# -------------------------------------------------------------------------
# Improved hydraulic diameter from representative cell (triangular/square)
# -------------------------------------------------------------------------
def _cell_properties(pitch: float, Do: float, layout: str) -> Tuple[float, float]:
    """
    Returns (A_flow_cell, P_wet_cell) for one pitch cell.
    For triangular: equilateral triangle cell area = sqrt(3)/4 * pitch^2
    For square: cell area = pitch^2
    P_wet_cell approximated as projected tube perimeter fraction in the cell.
    """
    if layout.lower().startswith("tri"):
        cell_area = (math.sqrt(3.0) / 4.0) * pitch * pitch
    else:
        cell_area = pitch * pitch
    tube_area = math.pi * Do*Do / 4.0
    A_flow = max(1e-12, cell_area - tube_area)
    # wetted perimeter: fraction of tube circumference projected into cell
    P_wet = max(1e-12, 0.5 * math.pi * Do)
    return A_flow, P_wet

def _hydraulic_diameter_from_cell(A_flow_cell: float, P_wet_cell: float) -> float:
    Dh = 4.0 * max(A_flow_cell, 1e-12) / max(P_wet_cell, 1e-12)
    return max(Dh, 1e-4)

# -------------------------------------------------------------------------
# Detailed Bell-Delaware shell-side heat transfer & pressure-drop model
# Full set of correction factors and DP breakdown (window, bundle crossing,
# leakage, bypass, shell passes)
# -------------------------------------------------------------------------
def _bell_delaware_shell(
    Ds: float,
    Do: float,
    Di_t: float,
    pitch: float,
    layout: str,
    centers: List[Tuple[float,float]],
    L_shell: float,
    baffle_spacing: float,
    mu_s: float,
    rho_s: float,
    k_s: float,
    cp_s: float,
    m_shell_total: float,
    leakage_frac: float = 0.05
) -> Tuple[float, float, Dict[str, float]]:
    """
    Bell-Delaware style calculation returning (h_shell, dp_shell, breakdown)
    """
    N_tubes = len(centers)
    if N_tubes == 0:
        raise ValueError("No tubes in centers list (N_tubes=0).")

    # geometric
    A_shell_cs = math.pi * Ds**2 / 4.0
    A_tube_proj = N_tubes * (Do * Di_t) / 4.0 if Di_t>0 else N_tubes * Do**2 * 0.25
    # free flow available
    A_flow = max(A_shell_cs - N_tubes*(math.pi*Do*Do/4.0), 1e-6) * 0.7

    # representative cell properties
    A_cell, P_wet = _cell_properties(pitch, Do, layout)
    De = _hydraulic_diameter_from_cell(A_cell, P_wet)

    # 2) mass velocity & Re
    Gs = m_shell_total / A_flow
    Re_s = Gs * De / max(mu_s, 1e-12)
    Pr_s = _prandtl(cp_s, mu_s, k_s)

    # 3) baseline j-factor (heuristic Zukauskas-like)
    if Re_s < 100:
        j_ideal = 0.6 * Re_s**0.4 * Pr_s**-0.36
    elif Re_s < 1000:
        j_ideal = 0.2 * Re_s**-0.2 * Pr_s**-0.6
    else:
        j_ideal = 0.2 * Re_s**-0.2 * Pr_s**-0.6

    h0 = j_ideal * Gs * cp_s / max(De, 1e-12)

    # Bell-Delaware correction factors (conservative heuristics)
    baffle_cut_fraction = min(0.45, max(0.05, 0.25))
    J_c = 0.8 + 0.2 * (1.0 - baffle_cut_fraction)

    gap_shell = 0.002
    gap_tubes = 0.0005
    A_leak_shell = math.pi * Ds * gap_shell
    A_leak_tubes = N_tubes * math.pi * Do * gap_tubes
    A_leak_total = A_leak_shell + A_leak_tubes
    frac_leak = min(0.5, A_leak_total / max(A_flow, 1e-12))
    J_l = math.exp(-4.0 * frac_leak)

    clearance = 0.005 * Ds
    A_bypass = math.pi * ((Ds/2.0)**2 - ((Ds/2.0) - clearance)**2)
    frac_bypass = min(0.5, A_bypass / max(A_flow, 1e-12))
    J_b = 1.0 / (1.0 + 5.0 * frac_bypass)

    J_r = 1.0 if layout.lower().startswith("tri") else 0.92

    n_rows_window = max(1, int(round(math.sqrt(max(1, N_tubes))/3.0)))
    J_w = 1.0 / (1.0 + 0.12 * (n_rows_window - 1) + 0.7 * (baffle_cut_fraction - 0.25)) if baffle_cut_fraction>0 else 0.8
    J_w = max(0.4, min(1.0, J_w))

    J_total = J_c * J_l * J_b * J_r * J_w
    h_shell = h0 * J_total

    # pressure drop breakdown
    V_char = Gs / max(rho_s, 1e-12)
    if Re_s <= 0:
        f_bundle = 0.3
    else:
        f_bundle = 0.044 * (Re_s ** -0.2)
    dp_bundle_per_section = f_bundle * 0.5 * rho_s * V_char**2 * (Do / De if De>0 else 1.0)
    n_sections = max(1, int(math.ceil(L_shell / max(baffle_spacing, 0.05))))
    dp_bundle = dp_bundle_per_section * n_sections

    K_window = 1.0 + 2.0 * (0.25 / max(0.01, baffle_cut_fraction))
    dp_window = K_window * 0.5 * rho_s * V_char**2

    if A_leak_total <= 0:
        dp_leak = 0.0
    else:
        V_leak = V_char * math.sqrt(max(A_flow,1e-12) / max(A_leak_total,1e-12))
        K_leak = 3.0
        dp_leak = K_leak * 0.5 * rho_s * V_leak**2

    dp_bypass = 0.5 * dp_bundle * frac_bypass
    n_shell_passes = 1
    dp_shell_passes = (dp_window + dp_bundle + dp_leak + dp_bypass) * n_shell_passes
    dp_total = max(0.0, dp_shell_passes)

    dp_breakdown = {
        "dp_window_Pa": dp_window,
        "dp_bundle_crossing_Pa": dp_bundle,
        "dp_leakage_Pa": dp_leak,
        "dp_bypass_Pa": dp_bypass,
        "dp_shell_passes_Pa": dp_shell_passes,
        "dp_total_Pa": dp_total,
        "J_c": J_c,
        "J_l": J_l,
        "J_b": J_b,
        "J_r": J_r,
        "J_w": J_w,
        "J_total": J_total,
        "Re_s": Re_s,
        "De": De,
        "Gs": Gs
    }

    return max(1.0, h_shell), max(0.0, dp_total), dp_breakdown

# -------------------------------------------------------------------------
# Header / nozzle / manifold model (simple K factor based)
# -------------------------------------------------------------------------
def header_and_manifold_design(
    flow_rate: float,
    rho: float,
    preferred_nozzle_velocity: float = 5.0
) -> Dict[str, Any]:
    A_req = flow_rate / (rho * preferred_nozzle_velocity) if preferred_nozzle_velocity>0 else flow_rate / (rho * 5.0)
    D_nozzle = math.sqrt(4.0 * A_req / math.pi)
    standard_diams = [0.01,0.015,0.02,0.025,0.03,0.04,0.05,0.075,0.1]
    D_choice = standard_diams[-1]
    for d in standard_diams:
        if d >= D_nozzle:
            D_choice = d
            break
    A_choice = math.pi * D_choice**2 / 4.0
    v_nozzle = flow_rate / (rho * A_choice) if rho>0 else 0.0
    K_total = _HEADER_KS["entrance"] + _HEADER_KS["elbow"]*2 + _HEADER_KS["exit"]
    dp_total = K_total * 0.5 * rho * v_nozzle**2
    return {
        "nozzle_d_m": D_choice,
        "nozzle_area_m2": A_choice,
        "nozzle_velocity_m_s": v_nozzle,
        "K_total": K_total,
        "dp_total_Pa": dp_total
    }

# -------------------------------------------------------------------------
# NTU/Epsilon helpers
# -------------------------------------------------------------------------
def _epsilon_counterflow(NTU: float, C: float) -> float:
    if NTU <= 0:
        return 0.0
    if abs(1.0 - C) < 1e-12:
        return NTU / (1.0 + NTU)
    exp_term = math.exp(-NTU * (1.0 - C))
    return (1.0 - exp_term) / (1.0 - C * exp_term)

def _epsilon_parallel(NTU: float, C: float) -> float:
    if NTU <= 0:
        return 0.0
    return (1.0 - math.exp(-NTU * (1.0 + C))) / (1.0 + C)

def _epsilon_from_arrangement(arr: str, NTU: float, C: float) -> float:
    if arr.lower() == "counterflow":
        return _epsilon_counterflow(NTU, C)
    else:
        return _epsilon_parallel(NTU, C)

# -------------------------------------------------------------------------
# Top-level design function using Bell-Delaware, packing, header design, mechanical summary
# -------------------------------------------------------------------------
def design_shelltube(
    hx: HeatExchanger,
    *,
    tube_nominal: Optional[Diameter] = None,
    tube_schedule: Optional[str] = None,
    shell_do: Optional[Length] = None,
    tube_layout: str = "triangular",      # 'triangular' or 'square'
    pitch_factor: float = 1.25,           # pitch = pitch_factor * Do_tube
    tube_passes_options: Optional[List[int]] = None,
    pass_layout: Optional[str] = None,    # used for chart Ft fallback
    arrangement: str = "counterflow",     # 'counterflow' or 'parallel'
    baffle_spacing: Optional[Length] = None,
    target_dp_tube: Optional[Pressure] = None,
    target_dp_shell: Optional[Pressure] = None,
    pipe_schedule_db: Optional[Dict] = None,
    wall_k: Union[float, ThermalConductivity] = _DEFAULT_WALL_K,
    roughness: float = _DEFAULT_ROUGHNESS,
    fouling_tube: float = _DEFAULT_FOULING_TUBE,
    fouling_shell: float = _DEFAULT_FOULING_SHELL,
    max_iters: int = _DEFAULT_MAX_ITERS,
    tol: float = _DEFAULT_TOL,
    tube_side_hot: bool = True  # DEFAULT: tube side is HOT
) -> Dict[str, Any]:
    """
    Full Bell-Delaware based shell-and-tube design.
    Returns dict with detailed thermal, hydraulic and mechanical summary.
    """
    parms = _get_parms(hx)
    Th_in = _val(parms.get("Hot in Temp"), "Hot In")
    Th_out = _val(parms.get("Hot out Temp"), "Hot Out")
    Tc_in = _val(parms.get("Cold in Temp"), "Cold In")
    Tc_out = _val(parms.get("Cold out Temp"), "Cold Out")
    m_hot = _val(parms.get("m_hot"), "m_hot")
    m_cold = _val(parms.get("m_cold"), "m_cold")
    cp_hot = _val(parms.get("cP_hot"), "cP_hot")
    cp_cold = _val(parms.get("cP_cold"), "cP_cold")

    Q_hot = m_hot * cp_hot * (Th_in - Th_out)
    Q_cold = m_cold * cp_cold * (Tc_out - Tc_in)
    Q = 0.5 * (Q_hot + Q_cold) if abs(Q_hot)>0 and abs(Q_cold)>0 else (Q_hot if abs(Q_hot)>0 else Q_cold)

    wall_k_val = wall_k.value if hasattr(wall_k, "value") else float(wall_k)
    target_dp_t_val = target_dp_tube.to("Pa").value if target_dp_tube else None
    target_dp_s_val = target_dp_shell.to("Pa").value if target_dp_shell else None

    # Tube candidate extraction
    tube_candidates = []
    if pipe_schedule_db is None:
        pipe_schedule_db = PIPE_SCHEDULES
    if tube_nominal is not None and pipe_schedule_db is not None:
        schedule = tube_schedule if tube_schedule in pipe_schedule_db.get(tube_nominal, {}) else list(pipe_schedule_db.get(tube_nominal, {}).keys())[0]
        _, Do_tube, Di_tube = pipe_schedule_db[tube_nominal][schedule]
        Do_t = Do_tube.to("m").value if hasattr(Do_tube, "to") else Do_tube.value
        Di_t = Di_tube.to("m").value if hasattr(Di_tube, "to") else Di_tube.value
        tube_candidates.append((Do_t, Di_t))
    elif pipe_schedule_db is not None:
        for nominal, schedules in pipe_schedule_db.items():
            sched = list(schedules.keys())[0]
            _, Do_tube, Di_tube = schedules[sched]
            Do_t = Do_tube.to("m").value if hasattr(Do_tube, "to") else Do_tube.value
            Di_t = Di_tube.to("m").value if hasattr(Di_tube, "to") else Di_tube.value
            tube_candidates.append((Do_t, Di_t))
    else:
        tube_candidates = [(0.01905, 0.016), (0.0254, 0.021), (0.03175,0.027)]

    # shell candidates
    shell_candidates = []
    if shell_do is not None:
        shell_candidates = [shell_do.to("m").value if hasattr(shell_do, "to") else shell_do]

    if tube_passes_options is None:
        tube_passes_options = [1,2,4]

    # assignments order: prefer tube-side-hot mapping first if tube_side_hot True
    if tube_side_hot:
        assignments = [("hot_tube","cold_shell"), ("cold_tube","hot_shell")]
    else:
        assignments = [("cold_tube","hot_shell"), ("hot_tube","cold_shell")]

    best = None
    best_score = float("inf")

    for Do_t, Di_t in tube_candidates:
        candidate_shells = shell_candidates[:] if shell_candidates else []
        if not candidate_shells:
            for mult in [6,8,10,12]:
                candidate_shells.append(max(0.1, Do_t * mult))

        pitch = pitch_factor * Do_t

        for Ds in candidate_shells:
            centers_tri, N_tri = pack_tubes_in_shell(Ds, Do_t, pitch, layout="triangular")
            centers_sq, N_sq = pack_tubes_in_shell(Ds, Do_t, pitch, layout="square")
            centers = centers_tri if tube_layout=="triangular" else centers_sq
            N_tubes = N_tri if tube_layout=="triangular" else N_sq
            N_rows = int(round(math.sqrt(N_tubes))) if N_tubes>0 else 1
            bspacing = baffle_spacing.to("m").value if baffle_spacing is not None and hasattr(baffle_spacing, "to") else (0.2 * Ds if baffle_spacing is None else float(baffle_spacing))

            for passes_cnt in tube_passes_options:
                if passes_cnt > max(1, N_tubes):
                    continue

                for assign in assignments:
                    if assign[0] == "hot_tube":
                        tube_stream = hx.hot_in; shell_stream = hx.cold_in
                        m_tube_total = m_hot; m_shell_total = m_cold
                        cp_tube_val = cp_hot; cp_shell_val = cp_cold
                    else:
                        tube_stream = hx.cold_in; shell_stream = hx.hot_in
                        m_tube_total = m_cold; m_shell_total = m_hot
                        cp_tube_val = cp_cold; cp_shell_val = cp_hot

                    n_tube_channels = passes_cnt if (passes_cnt>1 and passes_cnt<=N_tubes) else 1
                    m_tube_chan = m_tube_total / n_tube_channels

                    L_tube = 3.0
                    U_guess = 300.0
                    converged = False

                    for it in range(max_iters):
                        # film temps
                        if assign[0] == "hot_tube":
                            T_tube_bulk = 0.5 * (Th_in + Th_out)
                            T_shell_bulk = 0.5 * (Tc_in + Tc_out)
                        else:
                            T_tube_bulk = 0.5 * (Tc_in + Tc_out)
                            T_shell_bulk = 0.5 * (Th_in + Th_out)

                        # properties with safe fallbacks
                        try:
                            mu_t = tube_stream.component.viscosity(T_tube_bulk).to("Pa.s").value
                            rho_t = tube_stream.component.density(T_tube_bulk).to("kg/m3").value
                            k_t = tube_stream.component.thermal_conductivity(T_tube_bulk).to("W/mK").value
                            cp_t = tube_stream.component.specific_heat(T_tube_bulk).to("J/kgK").value
                        except Exception:
                            mu_t = 1e-3; rho_t = 1000.0; k_t = 0.13; cp_t = cp_tube_val

                        try:
                            mu_s = shell_stream.component.viscosity(T_shell_bulk).to("Pa.s").value
                            rho_s = shell_stream.component.density(T_shell_bulk).to("kg/m3").value
                            k_s = shell_stream.component.thermal_conductivity(T_shell_bulk).to("W/mK").value
                            cp_s = shell_stream.component.specific_heat(T_shell_bulk).to("J/kgK").value
                        except Exception:
                            mu_s = 1e-3; rho_s = 1000.0; k_s = 0.13; cp_s = cp_shell_val

                        # tube hydraulics
                        A_tube_flow = math.pi * (Di_t**2) / 4.0
                        v_tube = m_tube_chan / (rho_t * A_tube_flow) if rho_t>0 else 0.0
                        Re_t = rho_t * v_tube * Di_t / max(mu_t, 1e-12)
                        Pr_t = _prandtl(cp_t, mu_t, k_t)
                        f_t = _colebrook_f(max(Re_t,1e-6), roughness / Di_t) if Di_t>0 else 0.02
                        Nu_t = _nusselt_gnielinski(max(Re_t,1e-6), max(Pr_t,1e-6), f_t)
                        h_t = Nu_t * k_t / Di_t if Di_t>0 else Nu_t * k_t / 0.01

                        # shell-side Bell-Delaware
                        h_s, dp_shell_est, dp_breakdown = _bell_delaware_shell(
                            Ds, Do_t, Di_t, pitch, tube_layout, centers, L_tube, bspacing,
                            mu_s, rho_s, k_s, cp_s, m_shell_total, leakage_frac=0.05
                        )

                        # U calculation (inner-area ref)
                        R_conv_t = 1.0 / max(h_t,1e-12)
                        R_wall = math.log(Do_t / Di_t) / (2.0 * wall_k_val) if wall_k_val != 0 and Di_t>0 else 0.0
                        R_conv_s = (Di_t / Do_t) * (1.0 / max(h_s,1e-12)) if Do_t>0 else 1e6
                        R_foul_t = fouling_tube
                        R_foul_s = fouling_shell * (Di_t / Do_t) if Do_t>0 else fouling_shell
                        R_total_inner = R_conv_t + R_wall + R_conv_s + R_foul_t + R_foul_s
                        U_new = 1.0 / max(R_total_inner, 1e-12)

                        # NTU/epsilon
                        Ch = m_tube_total * cp_t
                        Cc = m_shell_total * cp_s
                        Cmin = min(Ch, Cc)
                        Cmax = max(Ch, Cc)
                        C_ratio = Cmin/Cmax if Cmax>0 else 0.0

                        total_inner_area = N_tubes * math.pi * Di_t * L_tube if N_tubes>0 else 1e-6
                        UA = U_new * total_inner_area
                        NTU_raw = UA / Cmin if Cmin>0 else 0.0

                        ntu_scale = 1.0
                        if passes_cnt > 1:
                            ntu_scale = 1.85 if passes_cnt==2 else (3.5 if passes_cnt==4 else passes_cnt*0.9)
                        NTU_effective = NTU_raw * ntu_scale

                        eps = _epsilon_from_arrangement(arrangement, NTU_effective, C_ratio)

                        # LMTD
                        dT1 = Th_in - Tc_out
                        dT2 = Th_out - Tc_in
                        if dT1 * dT2 <= 0:
                            delta_T_lm = max(abs(dT1), abs(dT2), 1e-6)
                        else:
                            delta_T_lm = (dT1 - dT2) / math.log(dT1 / dT2)

                        delta_T_in = Th_in - Tc_in

                        # Ft via chart or NTU identity
                        Ft = None
                        if pass_layout:
                            try:
                                Ft = globals().get("Ft_chart_shell", lambda *_: None)(pass_layout, NTU_raw, C_ratio)
                            except Exception:
                                Ft = None
                        if Ft is None:
                            if NTU_raw <= 1e-12 or delta_T_lm==0:
                                Ft = 1.0
                            else:
                                Ft = (eps * delta_T_in) / (NTU_raw * delta_T_lm)
                                Ft = max(1e-6, min(1.0, Ft))

                        # area requirements
                        if U_new <= 0 or delta_T_lm * Ft == 0:
                            A_required = float("inf")
                        else:
                            A_required = abs(Q) / (U_new * delta_T_lm * Ft)
                        L_required = A_required / (N_tubes * math.pi * Di_t) if (N_tubes * math.pi * Di_t)>0 else float("inf")

                        # damping & convergence
                        if it == 0:
                            U_ref = U_new
                        else:
                            U_ref = 0.6 * U_new + 0.4 * U_ref
                        L_tube_new = 0.6 * L_required + 0.4 * L_tube

                        if abs(L_tube_new - L_tube)/max(1e-9, L_tube_new) < tol and abs(U_new - U_ref)/max(1e-9, U_ref) < tol:
                            L_tube = L_tube_new
                            converged = True
                            break

                        L_tube = L_tube_new

                    # final dp calculations
                    f_t_final = _colebrook_f(max(Re_t,1e-6), roughness / Di_t) if Di_t>0 else 0.02
                    dp_tube_per_len = f_t_final * 0.5 * rho_t * v_tube**2 / Di_t if Di_t>0 else 0.0
                    dp_tube_total = dp_tube_per_len * L_tube * (passes_cnt if True else 1)
                    dp_shell_total = dp_shell_est
                    total_dp = dp_tube_total + dp_shell_total

                    # header design
                    hdr_tube = header_and_manifold_design(m_tube_total, rho_t)
                    hdr_shell = header_and_manifold_design(m_shell_total, rho_s)

                    # mechanical summary
                    t_wall = (Do_t - Di_t) / 2.0 if Do_t>Di_t else max((Do_t*0.1), 0.001)
                    tube_outer_area = math.pi * (Do_t**2) / 4.0
                    tube_vol = tube_outer_area * L_tube * N_tubes
                    tube_mass = tube_vol * _STEEL_DENSITY

                    shell_thickness = 0.006
                    shell_vol = math.pi * ((Ds/2.0 + shell_thickness)**2 - (Ds/2.0)**2) * L_tube
                    shell_mass = shell_vol * _STEEL_DENSITY

                    weld_count = N_tubes + 4
                    mechanical = {
                        "tube_mass_kg": tube_mass,
                        "shell_mass_kg": shell_mass,
                        "total_mass_kg": tube_mass + shell_mass,
                        "weld_count_est": weld_count,
                        "header_tube": hdr_tube,
                        "header_shell": hdr_shell
                    }

                    penalty = 0.0
                    if target_dp_t_val is not None and dp_tube_total > target_dp_t_val:
                        penalty += 1e6 + (dp_tube_total - target_dp_t_val)
                    if target_dp_s_val is not None and dp_shell_total > target_dp_s_val:
                        penalty += 1e6 + (dp_shell_total - target_dp_s_val)

                    score = L_tube + penalty

                    design = {
                        "tube_Do_m": Do_t,
                        "tube_Di_m": Di_t,
                        "shell_Do_m": Ds,
                        "N_tubes": N_tubes,
                        "pitch_m": pitch,
                        "layout": tube_layout,
                        "tube_passes": passes_cnt,
                        "L_tube_m": L_tube,
                        "U_W_m2K": U_ref,
                        "Ft": Ft,
                        "A_required_m2": A_required,
                        "Q_W": Q,
                        "Re_tube": Re_t,
                        "Re_shell": dp_breakdown.get("Re_s"),
                        "h_tube_W_m2K": h_t,
                        "h_shell_W_m2K": h_s,
                        "dp_tube_Pa": dp_tube_total,
                        "dp_shell_Pa": dp_shell_total,
                        "total_dp_Pa": total_dp,
                        "dp_breakdown": dp_breakdown,
                        "headers": mechanical,
                        "converged": converged,
                        "iterations": it+1,
                        "assignment": assign,
                        "tube_side_hot": tube_side_hot
                    }

                    if score < best_score:
                        best_score = score
                        best = design

    if best is None:
        raise RuntimeError("No feasible design found for shell-and-tube with given options.")

    hx.design_results = best
    return best
