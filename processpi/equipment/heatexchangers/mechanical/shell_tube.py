"""
processpi/equipment/heatexchangers/shell_tube.py

Shell-and-Tube Heat Exchanger advanced design:
- Bell-Delaware shell-side heat transfer and pressure-drop model (detailed)
- bundle packing routine for triangular and square pitches (exact geometric layering)
- header / nozzle / manifold basic design and K-losses
- NTU → epsilon → Ft integrated into LMTD area equation
- multi-pass tube arrangements supported
- mechanical summary (weld counts, material weight estimate)

Notes:
- This is a practical engineering implementation with documented approximations.
- Replace constants or correlation pieces if you have more accurate vendor correlations.
"""

import math
from typing import Dict, Any, Optional, Tuple, List, Union
from ....units import Diameter, Length, Pressure, Conductivity, Variable
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
_DEFAULT_MAX_ITERS = 200
_DEFAULT_TOL = 1e-4

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
    for _ in range(30):
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f)))
        res = lhs - rhs
        # numerical derivative approximation
        df = 1e-6
        f2 = max(f*(1+df), 1e-12)
        lhs2 = 1.0 / math.sqrt(f2)
        rhs2 = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f2)))
        dres = (lhs2 - rhs2) - (lhs - rhs)
        dfd = (f2 - f)
        if abs(dfd) < 1e-12:
            break
        slope = dres / dfd
        if abs(slope) < 1e-12:
            break
        f_new = f - (lhs - rhs) / slope
        if f_new <= 0:
            break
        if abs(f_new - f)/f_new < 1e-8:
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
    # determine grid extents based on pitch
    # For triangular layout, rows are offset by 0.5*pitch horizontally every other row; vertical spacing = sqrt(3)/2*pitch
    if layout == "triangular":
        dy = math.sqrt(3)/2 * pitch
        nx = int(math.floor((2*R) / pitch)) + 3
        ny = int(math.floor((2*R) / dy)) + 3
        # center grid roughly around zero
        y0 = - (ny//2) * dy
        for j in range(ny):
            y = y0 + j*dy
            row_offset = (0.5 * pitch) if (j % 2 == 1) else 0.0
            # compute x limit for this y: x_max = sqrt(R^2 - y^2)
            x_max = math.sqrt(max(0.0, R*R - y*y))
            nx_row = int(math.ceil((2*x_max) / pitch)) + 3
            x0 = - (nx_row//2) * pitch
            for i in range(nx_row):
                x = x0 + i*pitch + row_offset
                # check if tube center is within allowable radius considering tube outer radius
                if x*x + y*y <= (R - 0.5*D_tube)**2:
                    centers.append((x,y))
    else:
        # square layout: vertical spacing = pitch, horizontal spacing = pitch
        dy = pitch
        nx = int(math.floor((2*R) / pitch)) + 3
        ny = int(math.floor((2*R) / pitch)) + 3
        y0 = - (ny//2) * dy
        for j in range(ny):
            y = y0 + j*dy
            x_max = math.sqrt(max(0.0, R*R - y*y))
            nx_row = int(math.ceil((2*x_max) / pitch)) + 3
            x0 = - (nx_row//2) * pitch
            for i in range(nx_row):
                x = x0 + i*pitch
                if x*x + y*y <= (R - 0.5*D_tube)**2:
                    centers.append((x,y))
    return centers, len(centers)

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
    Bell-Delaware full-style calculation (engineer-grade implementation).
    Returns: (h_shell_W_m2K, dp_shell_total_Pa, dp_breakdown_dict)

    dp_breakdown_dict includes:
      - dp_window: window entry/exit losses
      - dp_bundle: crossflow bundle losses (bundle crossing)
      - dp_leakage: leakage through clearances
      - dp_bypass: bypass around bundle
      - dp_shell_passes: sum over shell passes (n_passes)
      - dp_total: sum total
    Note: many parameters are geometric and approximate; see TODO tags to refine.
    """

    # Number of tubes
    N_tubes = len(centers)
    if N_tubes == 0:
        raise ValueError("No tubes in centers list (N_tubes=0).")

    # 1) Geometric params
    A_shell_cs = math.pi * Ds**2 / 4.0                       # shell cross-sectional area
    A_tube_proj = N_tubes * (Do * Di_t) / 4.0 if Di_t>0 else N_tubes * Do**2 * 0.25
    # Effective flow area between tubes — conservative reduction for bundle blockage
    A_flow = max( A_shell_cs - N_tubes * (math.pi * Do**2 / 4.0), 1e-6 ) * 0.7

    # Equivalent hydraulic diameter for crossflow (De)
    # Bell-Delaware uses De ~ 4*(free flow area)/(wetted perimeter). We'll approximate:
    # Wetted perimeter ≈ N_tubes * Do (projected)
    P_wet = max(N_tubes * Do, 1e-6)
    De = 4.0 * A_flow / P_wet if P_wet>0 else (Do * 0.9)

    # 2) Mass velocity and Re/Pr
    Gs = m_shell_total / A_flow  # kg/m2-s
    Re_s = Gs * De / mu_s
    Pr_s = _prandtl(cp_s, mu_s, k_s)

    # 3) Ideal j-factor for bundle (Zukauskas-like / Kern baseline)
    # Use common engineering j-correlation for cross-flow bundles:
    # j = C * Re^(-m) * Pr^(-0.36) with C,m depending on Re. We'll use a smooth fit.
    if Re_s < 100:
        j_ideal = 0.6 * Re_s**0.4 * Pr_s**-0.36
    elif Re_s < 1000:
        j_ideal = 0.2 * Re_s**-0.2 * Pr_s**-0.6
    else:
        j_ideal = 0.2 * Re_s**-0.2 * Pr_s**-0.6

    h0 = j_ideal * Gs * cp_s / De   # ideal (no correction) W/m2K

    # ---------------------------------------------------------------------
    # Bell-Delaware correction factors (detailed)
    # ---------------------------------------------------------------------
    # # A) Baffle-cut & window correction J_c
    # baffle_cut is fraction (0-1) of shell diameter open to window
    # Here caller passes baffle_spacing; infer baffle_cut fraction from local geometry if needed.
    # For backward compatibility assume typical baffle cut 25% if not derivable.
    # TODO: if you have explicit baffle_cut param, use it. For now compute approximate percent:
    baffle_cut_fraction = min(0.45, max(0.05, 0.25))  # default 25% (0.25)
    # Jc empirical from Bell-Delaware (approx):
    J_c = 0.8 + 0.2 * (1.0 - baffle_cut_fraction)  # maps cut -> correction (higher cut -> lower Jc)
    # Note: this is a smooth conservative approximation; vendor formulas use geometry of window and number of tube rows in window.

    # # B) Leakage correction J_l
    # Leakage arises from gaps: baffle-to-shell and baffle-to-tube-sheet clearances
    # Estimate leakage area as fraction of shell area
    # TODO: replace gaps with user inputs if available
    gap_shell = 0.002  # m, typical shell-to-baffle gap
    gap_tubes = 0.0005  # m, typical tube-to-baffle clearance per tube
    A_leak_shell = math.pi * Ds * gap_shell
    A_leak_tubes = N_tubes * math.pi * Do * gap_tubes
    A_leak_total = A_leak_shell + A_leak_tubes
    frac_leak = min(0.5, A_leak_total / A_flow)
    # Bell-Delaware suggests J_l = exp(-alpha * frac_leak) with alpha ~ 3-6 depending on geometry
    J_l = math.exp(-4.0 * frac_leak)

    # # C) Bypass correction J_b (bypass flow between shell and bundle)
    # Bypass area approximated from clearances; use conservative model
    clearance = 0.005 * Ds  # m circumferential clearance (heuristic)
    A_bypass = math.pi * ((Ds/2.0)**2 - ((Ds/2.0) - clearance)**2)
    frac_bypass = min(0.5, A_bypass / A_flow)
    J_b = 1.0 / (1.0 + 5.0 * frac_bypass)  # strong penalization for large bypass

    # # D) Bundle geometry factor J_r (pitch/layout)
    if layout.lower().startswith("tri"):
        J_r = 1.0  # triangular slightly better heat transfer
    else:
        J_r = 0.92  # square pitch slightly worse (typical)

    # # E) Window / window-flow factor J_w
    # Number of tube rows in window (approx): use sqrt(N_tubes)/3 heuristic
    n_rows_window = max(1, int(round(math.sqrt(max(1, N_tubes))/3.0)))
    # window factor reduces transfer if many rows are in window or small baffle cut
    J_w = 1.0 / (1.0 + 0.12 * (n_rows_window - 1) + 0.7 * (baffle_cut_fraction - 0.25)) if baffle_cut_fraction>0 else 0.8
    J_w = max(0.4, min(1.0, J_w))

    # Combine multiplicative correction (Bell-Delaware style)
    J_total = J_c * J_l * J_b * J_r * J_w
    h_shell = h0 * J_total

    # ---------------------------------------------------------------------
    # Pressure-drop components (detailed breakdown)
    # We'll compute:
    # - dp_window (entrance/exit & contraction at windows)
    # - dp_bundle_crossing (bundle crossflow losses across tube rows)
    # - dp_leakage (losses through leaks)
    # - dp_bypass (bypass around bundle)
    # - dp_shell_passes = n_passes * (sum of above)  (approx)
    # ---------------------------------------------------------------------
    # Characteristic shell velocity based on crossflow area
    V_char = Gs / max(rho_s, 1e-12)  # m/s (mass velocity / density)

    # Bundle crossing friction: use f_bundle ~ 0.044 * Re^-0.2 (engineering)
    if Re_s <= 0:
        f_bundle = 0.3
    else:
        f_bundle = 0.044 * (Re_s ** -0.2)

    # bundle crossing dp per baffle (per crossflow section)
    dp_bundle_per_section = f_bundle * 0.5 * rho_s * V_char**2 * (Do / De if De>0 else 1.0)

    # Number of crossflow sections = approx L_shell / baffle_spacing
    n_sections = max(1, int(math.ceil(L_shell / max(baffle_spacing, 0.05))))

    dp_bundle = dp_bundle_per_section * n_sections

    # Window losses: typically K_window ~ 1-3 depending on cut and flow; use conservative K
    # K_window increases when window is small and baffle cut small
    K_window = 1.0 + 2.0 * (0.25 / max(0.01, baffle_cut_fraction))  # heuristic: smaller cut -> larger K
    dp_window = K_window * 0.5 * rho_s * V_char**2

    # Leakage losses: proportional to amount leaking and velocity through leak paths
    # approximate velocity in leaks as V_leak = V_char * (A_flow / A_leak_total)
    if A_leak_total <= 0:
        dp_leak = 0.0
    else:
        V_leak = V_char * math.sqrt(A_flow / max(A_leak_total, 1e-9))
        # loss coefficient for leak K_leak ~ 2-5
        K_leak = 3.0
        dp_leak = K_leak * 0.5 * rho_s * V_leak**2

    # Bypass losses: flow circumventing bundle experiences different K; estimate as fraction of dp_bundle
    dp_bypass = 0.5 * dp_bundle * frac_bypass

    # Shell passes: if multiple shell passes exist (not implemented here explicitly),
    # multiply by number of shell passes; for double-pass, typically *2
    n_shell_passes = 1
    dp_shell_passes = (dp_window + dp_bundle + dp_leak + dp_bypass) * n_shell_passes

    # Total dp (safety clamp)
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

    # final return: h_shell, dp_total, breakdown
    return max(1.0, h_shell), max(0.0, dp_total), dp_breakdown

# -------------------------------------------------------------------------
# Header / nozzle / manifold model (simple K factor based)
# - estimates nozzle size based on continuity and nominal velocity criterion
# - computes manifold pressure drop based on K-factors and velocities
# -------------------------------------------------------------------------
def header_and_manifold_design(
    flow_rate: float,
    rho: float,
    preferred_nozzle_velocity: float = 5.0
) -> Dict[str, Any]:
    """
    Very simple header sizing:
    - Choose nozzle area = flow_rate / (rho * preferred_nozzle_velocity)
    - Convert to nearest standard nozzle diameter (round up)
    - Compute K-losses: entrance + elbows + local tees (approx)
    Returns dict: nozzle_diameter_m, nozzle_area_m2, K_total, dp_estimated (Pa)
    """
    # required flow area (m2) based on preferred velocity (m/s)
    A_req = flow_rate / (rho * preferred_nozzle_velocity) if preferred_nozzle_velocity>0 else flow_rate / (rho * 5.0)
    # choose nozzle diameter by area
    D_nozzle = math.sqrt(4.0 * A_req / math.pi)
    # round nozzle diameter to standard nominal (approx): pick next standard metric: 0.02,0.025,0.03,0.04,0.05...
    standard_diams = [0.01,0.015,0.02,0.025,0.03,0.04,0.05,0.075,0.1]
    # choose nearest larger diameter
    D_choice = standard_diams[-1]
    for d in standard_diams:
        if d >= D_nozzle:
            D_choice = d
            break
    A_choice = math.pi * D_choice**2 / 4.0
    v_nozzle = flow_rate / (rho * A_choice) if rho>0 else 0.0
    # approximate K_total (inlet+elbow+exit)
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
# NTU/Epsilon & Ft helpers (reuse patterns from double-pipe code)
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
def design_shell_tube_bell_delaware(
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
    wall_k: Union[float, Conductivity] = _DEFAULT_WALL_K,
    roughness: float = _DEFAULT_ROUGHNESS,
    fouling_tube: float = _DEFAULT_FOULING_TUBE,
    fouling_shell: float = _DEFAULT_FOULING_SHELL,
    max_iters: int = _DEFAULT_MAX_ITERS,
    tol: float = _DEFAULT_TOL,
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
    Q = Q_hot if abs(Q_hot) > 0 else Q_cold

    # Convert input options
    wall_k_val = wall_k.value if hasattr(wall_k, "value") else float(wall_k)
    target_dp_t_val = target_dp_tube.to("Pa").value if target_dp_tube else None
    target_dp_s_val = target_dp_shell.to("Pa").value if target_dp_shell else None

    # Tube candidate extraction from pipe_schedule_db or fallback
    tube_candidates = []
    if pipe_schedule_db is None:
        pipe_schedule_db = PIPE_SCHEDULES  # may be None
    if tube_nominal is not None and pipe_schedule_db is not None:
        schedule = tube_schedule if tube_schedule in pipe_schedule_db.get(tube_nominal, {}) else list(pipe_schedule_db.get(tube_nominal, {}).keys())[0]
        _, Do_tube, Di_tube = pipe_schedule_db[tube_nominal][schedule]
        Do_t = Do_tube.to("m").value if hasattr(Do_tube, "to") else Do_tube.value
        Di_t = Di_tube.to("m").value if hasattr(Di_tube, "to") else Di_tube.value
        tube_candidates.append((Do_t, Di_t))
    elif pipe_schedule_db is not None:
        # pick commonly used tube sizes from DB
        for nominal, schedules in pipe_schedule_db.items():
            sched = list(schedules.keys())[0]
            _, Do_tube, Di_tube = schedules[sched]
            Do_t = Do_tube.to("m").value if hasattr(Do_tube, "to") else Do_tube.value
            Di_t = Di_tube.to("m").value if hasattr(Di_tube, "to") else Di_tube.value
            tube_candidates.append((Do_t, Di_t))
    else:
        tube_candidates = [(0.01905, 0.016), (0.0254, 0.021), (0.03175,0.027)]

    # shell diam candidates
    shell_candidates = []
    if shell_do is not None:
        shell_candidates = [shell_do.to("m").value if hasattr(shell_do, "to") else shell_do]
    else:
        # heuristics: multiples of tube OD
        shell_candidates = []  # will be filled for each tube candidate below

    # tube passes
    if tube_passes_options is None:
        tube_passes_options = [1,2,4]

    assignments = [("hot_tube","cold_shell"), ("cold_tube","hot_shell")]

    best = None
    best_score = float("inf")

    # Loop over tube sizes
    for Do_t, Di_t in tube_candidates:
        # choose shell diam multiples
        candidate_shells = []
        if shell_candidates:
            candidate_shells = shell_candidates
        else:
            for mult in [6,8,10,12]:
                candidate_shells.append(max(0.1, Do_t * mult))

        # pitch
        pitch = pitch_factor * Do_t

        for Ds in candidate_shells:
            # compute packing coordinates and N_tubes for both layouts
            centers_tri, N_tri = pack_tubes_in_shell(Ds, Do_t, pitch, layout="triangular")
            centers_sq, N_sq = pack_tubes_in_shell(Ds, Do_t, pitch, layout="square")

            # choose layout based on user preference
            if tube_layout == "triangular":
                centers = centers_tri
                N_tubes = N_tri
            else:
                centers = centers_sq
                N_tubes = N_sq

            # rows approx
            N_rows = int(round(math.sqrt(N_tubes))) if N_tubes>0 else 1

            # baffle spacing fallback
            bspacing = baffle_spacing.to("m").value if baffle_spacing is not None and hasattr(baffle_spacing, "to") else (0.2 * Ds if baffle_spacing is None else float(baffle_spacing))

            for passes_cnt in tube_passes_options:
                if passes_cnt > N_tubes:
                    continue

                for assign in assignments:
                    # map fluids
                    if assign[0] == "hot_tube":
                        tube_stream = hx.hot_in; shell_stream = hx.cold_in
                        m_tube_total = m_hot; m_shell_total = m_cold
                        cp_tube_val = cp_hot; cp_shell_val = cp_cold
                    else:
                        tube_stream = hx.cold_in; shell_stream = hx.hot_in
                        m_tube_total = m_cold; m_shell_total = m_hot
                        cp_tube_val = cp_cold; cp_shell_val = cp_hot

                    # per-channel flows for tube passes
                    n_tube_channels = passes_cnt if (passes_cnt>1 and passes_cnt<=N_tubes) else 1
                    m_tube_chan = m_tube_total / n_tube_channels
                    m_shell_chan = m_shell_total  # shell side not usually split among channels

                    # initial guesses
                    L_tube = 3.0  # initial tube length (m)
                    U_guess = 300.0
                    converged = False

                    # iterative loop
                    for it in range(_DEFAULT_MAX_ITERS):
                        # compute film temps as simple averages (can be improved)
                        if assign[0] == "hot_tube":
                            T_tube_bulk = 0.5 * (_val(parms.get("Hot in Temp")), _val(parms.get("Hot out Temp")))
                            T_shell_bulk = 0.5 * (_val(parms.get("Cold in Temp")), _val(parms.get("Cold out Temp")))
                        else:
                            T_tube_bulk = 0.5 * (_val(parms.get("Cold in Temp")), _val(parms.get("Cold out Temp")))
                            T_shell_bulk = 0.5 * (_val(parms.get("Hot in Temp")), _val(parms.get("Hot out Temp")))

                        # properties
                        mu_t = tube_stream.component.viscosity(T_tube_bulk).to("Pa*s").value
                        rho_t = tube_stream.component.density(T_tube_bulk).to("kg/m^3").value
                        k_t = tube_stream.component.thermal_conductivity(T_tube_bulk).to("W/m-K").value
                        try:
                            cp_t = tube_stream.component.specific_heat(T_tube_bulk).to("J/kg-K").value
                        except Exception:
                            cp_t = cp_tube_val

                        mu_s = shell_stream.component.viscosity(T_shell_bulk).to("Pa*s").value
                        rho_s = shell_stream.component.density(T_shell_bulk).to("kg/m^3").value
                        k_s = shell_stream.component.thermal_conductivity(T_shell_bulk).to("W/m-K").value
                        try:
                            cp_s = shell_stream.component.specific_heat(T_shell_bulk).to("J/kg-K").value
                        except Exception:
                            cp_s = cp_shell_val

                        # tube hydraulic
                        A_tube_flow = math.pi * (Di_t**2) / 4.0
                        v_tube = m_tube_chan / (rho_t * A_tube_flow) if rho_t>0 else 0.0
                        Re_t = rho_t * v_tube * Di_t / mu_t if mu_t>0 else 0.0
                        Pr_t = _prandtl(cp_t, mu_t, k_t) if k_t>0 else 1.0
                        f_t = _colebrook_f(max(Re_t,1e-6), roughness / Di_t) if Di_t>0 else 0.02
                        Nu_t = _nusselt_gnielinski(max(Re_t,1e-6), max(Pr_t,1e-6), f_t)
                        h_t = Nu_t * k_t / Di_t if Di_t>0 else Nu_t * k_t / 0.01

                        # shell-side Bell-Delaware (now returns dp breakdown)
                        h_s, dp_shell_est, dp_breakdown = _bell_delaware_shell(
                            Ds, Do_t, Di_t, pitch, tube_layout, centers, L_tube, bspacing,
                            mu_s, rho_s, k_s, cp_s, m_shell_total, leakage_frac=0.05
                        )

                        # overall U (inner area basis)
                        R_conv_t = 1.0 / h_t if h_t>0 else 1e6
                        R_wall = math.log(Do_t / Di_t) / (2.0 * wall_k_val) if wall_k_val != 0 and Di_t>0 else 0.0
                        R_conv_s = (Di_t / Do_t) * (1.0 / h_s) if Do_t>0 and h_s>0 else 1e6
                        R_foul_t = fouling_tube
                        R_foul_s = fouling_shell * (Di_t / Do_t) if Do_t>0 else fouling_shell
                        R_total_inner = R_conv_t + R_wall + R_conv_s + R_foul_t + R_foul_s
                        U_new = 1.0 / R_total_inner if R_total_inner>0 else 1e-12

                        # NTU, epsilon, Ft
                        Ch = m_tube_total * cp_t
                        Cc = m_shell_total * cp_s
                        Cmin = min(Ch, Cc)
                        Cmax = max(Ch, Cc)
                        C_ratio = Cmin/Cmax if Cmax>0 else 0.0

                        total_inner_area = N_tubes * math.pi * Di_t * L_tube if N_tubes>0 else 1e-6
                        UA = U_new * total_inner_area
                        NTU_raw = UA / Cmin if Cmin>0 else 0.0

                        # apply pass-scaling heuristic for multiple tube passes in series or parallel
                        ntu_scale = 1.0
                        if passes_cnt > 1:
                            ntu_scale = 1.85 if passes_cnt==2 else (3.5 if passes_cnt==4 else passes_cnt*0.9)
                        NTU_effective = NTU_raw * ntu_scale

                        eps = _epsilon_from_arrangement(arrangement, NTU_effective, C_ratio)

                        # delta_T_lm
                        dT1 = Th_in - Tc_out
                        dT2 = Th_out - Tc_in
                        if dT1 * dT2 <= 0:
                            delta_T_lm = max(abs(dT1), abs(dT2), 1e-6)
                        else:
                            delta_T_lm = (dT1 - dT2) / math.log(dT1 / dT2)

                        delta_T_in = Th_in - Tc_in

                        # compute Ft via chart if pass_layout else NTU identity
                        Ft = None
                        # If user supplied pass_layout, you may have Ft chart functions; fallback to NTU method
                        try:
                            if pass_layout:
                                # use earlier chart function if available in scope (if you added it)
                                Ft = globals().get("Ft_chart_shell", lambda *_: None)(pass_layout, NTU_raw, C_ratio)
                        except Exception:
                            Ft = None
                        if Ft is None:
                            if NTU_raw <= 1e-12 or delta_T_lm==0:
                                Ft = 1.0
                            else:
                                Ft = (eps * delta_T_in) / (NTU_raw * delta_T_lm)
                                Ft = max(1e-6, min(1.0, Ft))

                        # required area and L mapping
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

                    # end iterative loop

                    # final dp calculations
                    # tube-side dp (Darcy-Weisbach)
                    f_t_final = _colebrook_f(max(Re_t,1e-6), roughness / Di_t) if Di_t>0 else 0.02
                    dp_tube_per_len = f_t_final * 0.5 * rho_t * v_tube**2 / Di_t if Di_t>0 else 0.0
                    dp_tube_total = dp_tube_per_len * L_tube * (passes_cnt if True else 1)

                    # dp shell from bell_delaware earlier (dp_shell_est scaled to L_tube)
                    dp_shell_total = dp_shell_est  # already returned by bell_delaware implementation

                    total_dp = dp_tube_total + dp_shell_total

                    # header design (tube-side header and shell-side nozzle)
                    hdr_tube = header_and_manifold_design(m_tube_total, rho_t)
                    hdr_shell = header_and_manifold_design(m_shell_total, rho_s)

                    # mechanical summary: weight estimates & weld counts
                    # Tube weight: volume = tube outer area * length * N_tubes
                    t_wall = (Do_t - Di_t) / 2.0 if Do_t>Di_t else max((Do_t*0.1), 0.001)
                    tube_outer_area = math.pi * (Do_t**2) / 4.0
                    tube_vol = tube_outer_area * L_tube * N_tubes
                    tube_mass = tube_vol * _STEEL_DENSITY

                    # Shell weight (approx cylinder only, ignore heads): shell thickness approximated 6 mm
                    shell_thickness = 0.006
                    shell_vol = math.pi * ((Ds/2.0 + shell_thickness)**2 - (Ds/2.0)**2) * L_tube
                    shell_mass = shell_vol * _STEEL_DENSITY

                    # approximate welds: one weld per tube (tube-to-tubesheet) + shell flanges
                    weld_count = N_tubes + 4
                    # simple cost/weight summary
                    mechanical = {
                        "tube_mass_kg": tube_mass,
                        "shell_mass_kg": shell_mass,
                        "total_mass_kg": tube_mass + shell_mass,
                        "weld_count_est": weld_count,
                        "header_tube": hdr_tube,
                        "header_shell": hdr_shell
                    }

                    # compute penalty for dp target exceedance
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
                        "assignment": assign
                    }

                    if score < best_score:
                        best_score = score
                        best = design

    if best is None:
        raise RuntimeError("No feasible design found for shell-and-tube with given options.")

    # attach to hx and return
    hx.design_results = best
    return best
