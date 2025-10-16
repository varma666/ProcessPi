"""
Advanced double-pipe mechanical design with iterative convergence and Aspen-like features.
Drop into processpi heat exchanger helpers. Assumes unit types and MaterialStream/Component API.
"""

import math
from typing import Dict, Any, Optional, Union, List, Tuple
from ....units import Diameter, Length, Conductivity, Pressure, Temperature, MassFlowRate
from ....streams.material import MaterialStream
from ..base import HeatExchanger

# Tolerances / defaults
_CONV_TOL = 1e-4
_MAX_ITERS = 200
_G = 9.80665

# Standard pipe library (Di, Do) in meters (inner dia, outer pipe inner dia for annulus)
_STANDARD_PIPES = {
    "1/2\"": (0.0159, 0.0213),
    "3/4\"": (0.0209, 0.0267),
    "1\"": (0.0254, 0.0334),
    "1.25\"": (0.0317, 0.0397),
    "1.5\"": (0.0409, 0.0483),
    "2\"": (0.0525, 0.0603),
    "2.5\"": (0.0627, 0.0730),
    "3\"": (0.078, 0.0889),
    "4\"": (0.1023, 0.1143),
}


# ---------- Utility functions ----------
def _get_parms(hx: HeatExchanger) -> Dict[str, Any]:
    if not isinstance(hx, HeatExchanger):
        raise TypeError("hx must be HeatExchanger")
    if hx.simulated_params is None:
        raise ValueError("Heat exchanger has not been simulated; call simulate() first.")
    return hx.simulated_params


def _get_value(v, name: str):
    if v is None:
        return None
    if hasattr(v, "value"):
        return v.value
    if isinstance(v, (int, float)):
        return float(v)
    raise TypeError(f"{name} must be numeric or have .value")


def _ftemp(T1: float, T2: float) -> float:
    return 0.5 * (T1 + T2)


def _prandtl(cp: float, mu: float, k: float) -> float:
    return cp * mu / k


def _haaland_f(Re: float, eps_rel: float = 1e-6) -> float:
    """Haaland explicit approx to Colebrook (eps_rel = roughness / D)."""
    if Re <= 0:
        return 1e6
    if Re < 2300:
        return 64.0 / max(Re, 1e-12)
    # Haaland
    term = -1.8 * math.log10((eps_rel / 3.7) ** 1.11 + 6.9 / Re)
    f = (1.0 / term) ** 2
    return f


def _colebrook_f(Re: float, eps_rel: float = 1e-6) -> float:
    """Solve Colebrook using fixed-point / Newton — fallback to Haaland for stability."""
    if Re < 2300:
        return 64.0 / max(Re, 1e-12)
    # start with Haaland
    f = _haaland_f(Re, eps_rel)
    for _ in range(20):
        # Colebrook residual: 1/sqrt(f) + 2*log10( eps/(3.7) + 2.51/(Re*sqrt(f)) ) = 0
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_rel / 3.7 + 2.51 / (Re * math.sqrt(f)))
        res = lhs - rhs
        # derivative approx
        df = -0.5 * f ** (-1.5) - (-2.0) * ( (2.51 / (2 * Re)) * f ** (-1.5) ) / ( (eps_rel/3.7) + 2.51/(Re*math.sqrt(f)) ) / math.log(10)
        # avoid tiny df
        if abs(df) < 1e-12:
            break
        f_new = f - res / df
        if f_new <= 0:
            break
        if abs(f_new - f) / f_new < 1e-8:
            f = f_new
            break
        f = f_new
    return f


def _nusselt_gnielinski(Re: float, Pr: float, f: float) -> float:
    if Re <= 2300:
        return 3.66
    Nu = (f / 8.0) * (Re - 1000.0) * Pr / (1.0 + 12.7 * (f / 8.0) ** 0.5 * (Pr ** (2.0 / 3.0) - 1.0))
    return max(Nu, 3.66)


def _nusselt_annulus(Re: float, Pr: float, Do: float, Di: float, f: float) -> float:
    """Approximate annulus Nusselt using hydraulic diameter Dh = Do - Di and Gnielinski on Dh.
       Slightly adjust for curvature by multiplying with factor dependent on Do/Di ratio."""
    Dh = Do - Di
    Nu = _nusselt_gnielinski(Re, Pr, f)
    # correction: tighter annulus -> reduced Nu. use factor ~ (1 - 0.1*(Di/Do - 0.5)) clamped
    ratio = Di / Do
    corr = 1.0 - 0.2 * max(0.0, (ratio - 0.4))
    return max(3.0, Nu * corr)


def _area_inner(Di: float, L: float) -> float:
    return math.pi * Di * L


def _hydraulic_d_annulus(Do: float, Di: float) -> float:
    return Do - Di


def _pressure_drop_darcy(f: float, L: float, D_h: float, rho: float, v: float) -> float:
    return f * (L / D_h) * 0.5 * rho * v * v


# ---------- Core iterative design function for one geometry ----------
def _design_for_geometry(
    hx: HeatExchanger,
    Di: float,
    Do: float,
    *,
    inner_passes: int = 1,
    inner_mode: str = "series",  # "series" or "parallel"
    annulus_parallel: int = 1,
    k_wall: float = 16.0,
    roughness: float = 1.5e-5,  # absolute roughness (m) default commercial steel ~15 micron
    fouling_tube: float = 0.0001,  # m2K/W
    fouling_shell: float = 0.0002,  # m2K/W
    minor_loss_K: Dict[str, float] = None,
    use_gnielinski: bool = True,
    tol: float = _CONV_TOL,
    max_iter: int = _MAX_ITERS,
    L_initial: float = 1.0,
    allow_effectiveness_mode: bool = True,
) -> Dict[str, Any]:
    """
    Design for given Di/Do. Performs iterative Re->Nu->h->U->L loop.
    Returns results dict with fields similar to Aspen outputs.
    """

    if minor_loss_K is None:
        minor_loss_K = {"entrance": 0.5, "exit": 1.0, "bend": 0.9}  # generic K-factors

    parms = _get_parms(hx)
    # extract required params (unit-aware)
    Th_in = _get_value(parms.get("Hot in Temp"), "Hot in Temp")
    Th_out = _get_value(parms.get("Hot out Temp"), "Hot out Temp")
    Tc_in = _get_value(parms.get("Cold in Temp"), "Cold in Temp")
    Tc_out = _get_value(parms.get("Cold out Temp"), "Cold out Temp")
    m_hot = _get_value(parms.get("m_hot"), "m_hot")
    m_cold = _get_value(parms.get("m_cold"), "m_cold")
    cp_hot_param = _get_value(parms.get("cP_hot"), "cP_hot")
    cp_cold_param = _get_value(parms.get("cP_cold"), "cP_cold")
    delta_Tlm_param = _get_value(parms.get("delta_Tlm"), "delta_Tlm")

    # basic checks
    if None in (Th_in, Th_out, Tc_in, Tc_out, m_hot, m_cold, cp_hot_param, cp_cold_param):
        raise ValueError("Missing required hx simulated params (temps, flows, cp).")

    # film temperatures (start)
    T_hot_bulk = _ftemp(Th_in, Th_out)
    T_cold_bulk = _ftemp(Tc_in, Tc_out)

    # get component property calls (assume methods accept temperature or ignore)
    hot_comp = hx.hot_in.component
    cold_comp = hx.cold_in.component

    def prop_hot(T):
        # return dict with mu, rho, k, cp
        mu = hot_comp.viscosity(T).to("Pa*s").value
        rho = hot_comp.density(T).to("kg/m^3").value
        k = hot_comp.thermal_conductivity(T).to("W/m-K").value
        try:
            cp = hot_comp.specific_heat(T).to("J/kg-K").value
        except Exception:
            cp = cp_hot_param
        return mu, rho, k, cp

    def prop_cold(T):
        mu = cold_comp.viscosity(T).to("Pa*s").value
        rho = cold_comp.density(T).to("kg/m^3").value
        k = cold_comp.thermal_conductivity(T).to("W/m-K").value
        try:
            cp = cold_comp.specific_heat(T).to("J/kg-K").value
        except Exception:
            cp = cp_cold_param
        return mu, rho, k, cp

    # geometry helpers
    A_single_inner = math.pi * Di * Di / 4.0
    A_annulus_single = math.pi * (Do ** 2 - Di ** 2) / 4.0
    Dh_ann = _hydraulic_d_annulus(Do, Di)

    # determine per-channel mass flows depending on pass / parallel choices
    if inner_mode == "parallel":
        n_inner_channels = inner_passes
        m_hot_channel = m_hot / n_inner_channels
    else:
        n_inner_channels = 1
        m_hot_channel = m_hot

    n_annulus_channels = annulus_parallel
    m_cold_channel = m_cold / n_annulus_channels

    # initial guess for L (total length in series interpretation)
    L_total = L_initial
    iteration = 0
    converged = False
    prev_L = L_total

    # If L is provided by user via simulated_params["given_length"], respect that -> effectiveness mode
    given_length = _get_value(parms.get("given_length"), "given_length")
    effectiveness_mode = False
    if given_length is not None and allow_effectiveness_mode:
        effectiveness_mode = True
        L_total = given_length

    while iteration < max_iter:
        iteration += 1

        # per-pass length logic
        if inner_mode == "series":
            L_per_pass = L_total / max(inner_passes, 1)
            L_used_for_dp = L_per_pass  # we will scale dp for series by number of passes later
        else:
            L_per_pass = L_total
            L_used_for_dp = L_per_pass

        # compute properties at film temps (update film temps each iteration)
        # approximate film temps as local bulk temperatures (could iterate with wall temp)
        mu_h, rho_h, k_h, cp_h = prop_hot(T_hot_bulk)
        mu_c, rho_c, k_c, cp_c = prop_cold(T_cold_bulk)

        # velocities per channel
        A_inner_channel = A_single_inner
        A_annulus_channel = A_annulus_single
        v_hot_channel = m_hot_channel / (rho_h * A_inner_channel)
        v_cold_channel = m_cold_channel / (rho_c * A_annulus_channel)

        # Reynolds & Pr
        Re_hot = rho_h * v_hot_channel * Di / mu_h
        Re_cold = rho_c * v_cold_channel * Dh_ann / mu_c
        Pr_hot = _prandtl(cp_h, mu_h, k_h)
        Pr_cold = _prandtl(cp_c, mu_c, k_c)

        # friction factors (Colebrook/Haaland)
        eps_rel_hot = roughness / Di
        eps_rel_cold = roughness / Dh_ann if Dh_ann > 0 else roughness / Di
        f_hot = _colebrook_f(max(Re_hot, 1e-6), eps_rel_hot)
        f_cold = _colebrook_f(max(Re_cold, 1e-6), eps_rel_cold)

        # Nu correlations
        Nu_hot = _nusselt_gnielinski(max(Re_hot, 1e-6), max(Pr_hot, 1e-6), f_hot) if use_gnielinski else max(3.66, 0.023 * Re_hot ** 0.8 * Pr_hot ** 0.4)
        Nu_cold = _nusselt_annulus(max(Re_cold, 1e-6), max(Pr_cold, 1e-6), Do, Di, f_cold) if use_gnielinski else max(3.66, 0.023 * Re_cold ** 0.8 * Pr_cold ** 0.4)

        # film coefficients
        h_hot = Nu_hot * k_h / Di
        h_cold = Nu_cold * k_c / Dh_ann

        # resistances referenced to inner area (A_i = pi*Di*L_per_pass for each inner tube)
        R_conv_i = 1.0 / h_hot
        R_wall = (Di * math.log(Do / Di)) / (2.0 * k_wall)
        R_conv_o = (Di / Do) * (1.0 / h_cold)
        # add fouling resistances on both sides
        R_foul_i = fouling_tube / (math.pi * Di) * 0  # converted in area basis below; easier add after Ucalc
        # simpler: add fouling resistances directly to 1/U (per inner-area basis)
        R_foul_i_area = fouling_tube
        R_foul_o_area = fouling_shell * (Di / Do)

        R_total_area_ref = R_conv_i + R_wall + R_conv_o + R_foul_i_area + R_foul_o_area
        U_ref_inner = 1.0 / R_total_area_ref

        # Heat duty and area
        # Prefer to use hot side energy if outlet provided, else cold side
        Q_hot = m_hot * cp_h * (Th_in - Th_out)
        Q_cold = m_cold * cp_c * (Tc_out - Tc_in) if 'cp_c' in locals() else None
        Q_total = Q_hot if Q_hot != 0 else (Q_cold if Q_cold is not None else 0.0)
        if delta_Tlm_param is None:
            # compute delta_Tlm from temps in parms
            dT1 = Th_in - Tc_out
            dT2 = Th_out - Tc_in
            if dT1 * dT2 <= 0:
                # fallback: use simple log-mean with small offset
                delta_Tlm = max(abs(dT1), abs(dT2))
            else:
                delta_Tlm = (dT1 - dT2) / math.log(dT1 / dT2)
        else:
            delta_Tlm = delta_Tlm_param

        # Required total inner-area (sum of all inner tubes area)
        A_required_total = abs(Q_total) / (U_ref_inner * delta_Tlm)
        # compute total inner area for configuration:
        if inner_mode == "parallel":
            total_inner_area_available = n_inner_channels * math.pi * Di * L_per_pass
        else:
            total_inner_area_available = 1.0 * math.pi * Di * (L_per_pass * inner_passes)

        # update length based on required area (unless effectiveness_mode uses given L)
        if not effectiveness_mode:
            L_calc_total = A_required_total / (math.pi * Di)
            # interpret L_calc_total as total length for series mode; for parallel inner tubes it's length per tube
            if inner_mode == "parallel":
                L_total_new = L_calc_total  # length of each parallel tube
            else:
                L_total_new = L_calc_total  # total length which is split into passes below
        else:
            L_total_new = L_total  # keep given

        # compute new film temps (rough update using log-mean wall approximation if desired)
        # compute overall UA
        U_curr = U_ref_inner
        # check convergence on length
        if abs(L_total_new - L_total) / max(1e-9, L_total_new) < tol:
            converged = True
            L_total = L_total_new
            break

        # update loop variables for next iteration
        L_total = L_total_new

        # update film/bulk temps: (simple energy balance to estimate exit temps if needed)
        # Update film temps toward bulk mean (small relaxation)
        T_hot_bulk = 0.5 * (Th_in + Th_out)
        T_cold_bulk = 0.5 * (Tc_in + Tc_out)

    # End iteration

    # Final recomputations at converged L_total
    if inner_mode == "series":
        L_per_pass = L_total / max(inner_passes, 1)
    else:
        L_per_pass = L_total

    # final properties
    mu_h, rho_h, k_h, cp_h = prop_hot(T_hot_bulk)
    mu_c, rho_c, k_c, cp_c = prop_cold(T_cold_bulk)
    v_h = (m_hot / (n_inner_channels)) / (rho_h * A_single_inner) if inner_mode == "parallel" else m_hot / (rho_h * A_single_inner)
    v_c = (m_cold / n_annulus_channels) / (rho_c * A_annulus_single)
    Re_h = rho_h * v_h * Di / mu_h
    Re_c = rho_c * v_c * Dh_ann / mu_c
    f_h = _colebrook_f(max(Re_h, 1e-6), roughness / Di)
    f_c = _colebrook_f(max(Re_c, 1e-6), roughness / Dh_ann)
    Nu_h = _nusselt_gnielinski(max(Re_h, 1e-6), max(_prandtl(cp_h, mu_h, k_h), 1e-6), f_h)
    Nu_c = _nusselt_annulus(max(Re_c, 1e-6), max(_prandtl(cp_c, mu_c, k_c), 1e-6), Do, Di, f_c)
    h_h = Nu_h * k_h / Di
    h_c = Nu_c * k_c / Dh_ann
    R_conv_i = 1.0 / h_h
    R_wall = (Di * math.log(Do / Di)) / (2.0 * k_wall)
    R_conv_o = (Di / Do) * (1.0 / h_c)
    R_total_area_ref = R_conv_i + R_wall + R_conv_o + fouling_tube + fouling_shell * (Di / Do)
    U_ref_inner = 1.0 / R_total_area_ref

    # Final Q based on L_total
    total_inner_surface = math.pi * Di * L_total * (n_inner_channels if inner_mode == "parallel" else 1.0)
    Q_calc = U_ref_inner * total_inner_surface * delta_Tlm

    # Pressure drops (include minor losses)
    # hot side: per channel dp then scale for series/parallel:
    dp_hot_per_channel = _pressure_drop_darcy(f_h, L_per_pass, Di, rho_h, v_h)
    # add entrance/exit K
    dp_hot_per_channel += (minor_loss_K.get("entrance", 0.5) + minor_loss_K.get("exit", 1.0)) * 0.5 * rho_h * v_h ** 2
    # if series: total dp_hot = dp_per_pass * number_of_passes
    dp_hot_system = dp_hot_per_channel * (inner_passes if inner_mode == "series" else 1)

    # cold side dp per annulus channel
    dp_cold_per_channel = _pressure_drop_darcy(f_c, L_per_pass, Dh_ann, rho_c, v_c)
    dp_cold_per_channel += (minor_loss_K.get("entrance", 0.5) + minor_loss_K.get("exit", 1.0)) * 0.5 * rho_c * v_c ** 2
    dp_cold_system = dp_cold_per_channel  # parallel annuli same dp

    results = {
        "Di_m": Di,
        "Do_m": Do,
        "inner_mode": inner_mode,
        "inner_passes": inner_passes,
        "annulus_parallel": annulus_parallel,
        "L_total_m": L_total,
        "L_per_pass_m": L_per_pass,
        "total_inner_area_m2": total_inner_surface,
        "Q_calc_W": Q_calc,
        "U_ref_inner_W_m2K": U_ref_inner,
        "h_hot_W_m2K": h_h,
        "h_cold_W_m2K": h_c,
        "Re_hot": Re_h,
        "Re_cold": Re_c,
        "Nu_hot": Nu_h,
        "Nu_cold": Nu_c,
        "f_hot": f_h,
        "f_cold": f_c,
        "dp_hot_Pa": dp_hot_system,
        "dp_cold_Pa": dp_cold_system,
        "iterations": iteration,
        "converged": converged,
        "notes": "Iterative Re->Nu->U->L loop with fouling and Colebrook friction. Approximations used for annulus Nu and multiple channels.",
    }

    return results


# ---------- Top-level user-facing design routine ----------
def design_double_pipe_aspen_like(
    hx: HeatExchanger,
    *,
    innerpipe_dia: Optional[Diameter] = None,
    outerpipe_dia: Optional[Diameter] = None,
    k_wall: Union[float, Conductivity] = 16.0,
    roughness: float = 1.5e-5,
    fouling_tube: float = 0.0001,
    fouling_shell: float = 0.0002,
    inner_passes_options: Optional[List[int]] = None,
    inner_mode: str = "series",
    annulus_parallel_options: Optional[List[int]] = None,
    target_dp: Optional[Pressure] = None,
    max_dp_default: float = 1e5,
    minor_loss_K: Optional[Dict[str, float]] = None,
    tol: float = _CONV_TOL,
    max_iter: int = _MAX_ITERS,
    allow_effectiveness_mode: bool = True,
    pipe_library: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Dict[str, Any]:
    """
    Aspen-like top-level design wrapper. If diameters given, design that geometry.
    Otherwise automatic search across standard pipes and pass configurations.
    """

    if pipe_library is None:
        pipe_library = _STANDARD_PIPES

    if inner_passes_options is None:
        inner_passes_options = [1, 2, 4]
    if annulus_parallel_options is None:
        annulus_parallel_options = [1, 2]

    # convert target dp to Pa if provided
    target_dp_val = None
    if target_dp is not None:
        target_dp_val = target_dp.to("Pa").value if hasattr(target_dp, "to") else float(target_dp)

    # quick path: fixed geometry
    if innerpipe_dia is not None and outerpipe_dia is not None:
        Di = innerpipe_dia.to("m").value
        Do = outerpipe_dia.to("m").value
        return _design_for_geometry(
            hx,
            Di,
            Do,
            inner_passes=inner_passes_options[0],
            inner_mode=inner_mode,
            annulus_parallel=annulus_parallel_options[0],
            k_wall=k_wall.value if hasattr(k_wall, "value") else k_wall,
            roughness=roughness,
            fouling_tube=fouling_tube,
            fouling_shell=fouling_shell,
            minor_loss_K=minor_loss_K,
            tol=tol,
            max_iter=max_iter,
            allow_effectiveness_mode=allow_effectiveness_mode,
        )

    # automatic search over library & configs
    candidates = []
    for name, (Di, Do) in pipe_library.items():
        # basic clearance check
        if Do <= Di * 1.05:
            continue
        for n_pass in inner_passes_options:
            for n_ann in annulus_parallel_options:
                try:
                    res = _design_for_geometry(
                        hx,
                        Di,
                        Do,
                        inner_passes=n_pass,
                        inner_mode=inner_mode,
                        annulus_parallel=n_ann,
                        k_wall=k_wall.value if hasattr(k_wall, "value") else k_wall,
                        roughness=roughness,
                        fouling_tube=fouling_tube,
                        fouling_shell=fouling_shell,
                        minor_loss_K=minor_loss_K,
                        tol=tol,
                        max_iter=max_iter,
                        allow_effectiveness_mode=allow_effectiveness_mode,
                    )
                except Exception as e:
                    # skip failing combinations
                    continue
                res["pipe_name"] = name
                res["score_length"] = res["L_total_m"]
                res["total_dp"] = res["dp_hot_Pa"] + res["dp_cold_Pa"]
                candidates.append(res)

    if not candidates:
        raise RuntimeError("No valid configurations found in pipe library.")

    # selection logic: if target_dp requested, prefer dp closeness then length; else minimize length under max dp
    if target_dp_val is not None:
        best = min(candidates, key=lambda r: (abs(r["total_dp"] - target_dp_val), r["score_length"]))
        err = abs(best["total_dp"] - target_dp_val) / (target_dp_val + 1e-12)
        if err > 0.2:
            best["warning"] = f"Closest ΔP differs by {err*100:.1f}% from target."
    else:
        valid = [c for c in candidates if c["total_dp"] < max_dp_default]
        best = min(valid, key=lambda r: r["score_length"]) if valid else min(candidates, key=lambda r: r["score_length"])
        if best["total_dp"] >= max_dp_default:
            best["warning"] = f"No candidate under max_dp_default ({max_dp_default} Pa); selecting minimum length."

    # attach meta & return
    best["unit_notes"] = "meters (m), Pa, W, W/m2K. Approximations used; refine with detailed header/bundle design for manufacturing."
    return best
