# processpi/equipment/heatexchangers/mechanical/double_pipe.py
"""
Double-pipe mechanical design for ProcessPI (units-aware).

- Iterative convergence loop (Re -> Nu -> hi/ho -> U -> area -> length)
- Minor-loss (entrance/exit/fittings) K-factors
- Parallel annuli support (split cold mass flow into N channels)
- Wraps numeric outputs with ProcessPI unit classes (Diameter, Area, MassFlowRate, Velocity, Pressure, etc.)
  falling back to lightweight shim if imports fail (so unit tests or isolated runs still work).

References:
- ProcessPI Units overview & class pages (Diameter, MassFlowRate, etc.). See project docs.
"""
from typing import Dict, Any, Optional
from math import pi, log

# --- Attempt to import ProcessPI unit classes (per docs) ---
_HAS_PROC_UNITS = False
try:
    from processpi.units import (
        Diameter,
        Area,
        MassFlowRate,
        Velocity,
        Pressure,
        Temperature,
        HeatTransferCoefficient,
        HeatFlux,
        ThermalConductivity,
        Power,
    )
    _HAS_PROC_UNITS = True
except Exception:
    _HAS_PROC_UNITS = False

    class _ShimQuantity:
        def __init__(self, value, units: str = ""):
            self.value = float(value)
            self.units = units
        def __float__(self):
            return float(self.value)
        def __repr__(self):
            return f"{self.__class__.__name__}({self.value}, '{self.units}')"

    class Diameter(_ShimQuantity): pass
    class Area(_ShimQuantity): pass
    class MassFlowRate(_ShimQuantity): pass
    class Velocity(_ShimQuantity): pass
    class Pressure(_ShimQuantity): pass
    class Temperature(_ShimQuantity): pass
    class HeatTransferCoefficient(_ShimQuantity): pass
    class HeatFlux(_ShimQuantity): pass
    class ThermalConductivity(_ShimQuantity): pass
    class Power(_ShimQuantity): pass


# --- Helpers ---
def _wrap(value: float, unit_class, units: str = ""):
    try:
        return unit_class(value, units)
    except Exception:
        try:
            return unit_class(value)
        except Exception:
            return value

def hydraulic_diameter_annulus(D_inner_outer: float, D_outer_inner: float) -> float:
    return D_outer_inner - D_inner_outer

def reynolds(rho: float, V: float, Dh: float, mu: float) -> float:
    return rho * V * Dh / mu

def prandtl(cp: float, mu: float, k: float) -> float:
    return cp * mu / k

def friction_factor_blasius_or_laminar(Re: float) -> float:
    if Re <= 0: return 0.0
    if Re < 2300: return 64.0 / Re
    return 0.079 * (Re ** -0.25)

def dittus_boelter_nusselt(Re: float, Pr: float, heating: bool = True) -> float:
    if Re <= 0 or Pr <= 0: return 0.0
    n = 0.4 if heating else 0.3
    return 0.023 * (Re ** 0.8) * (Pr ** n)

def sieder_tate_visc_corr(mu_bulk: float, mu_wall: float) -> float:
    if mu_wall <= 0 or mu_bulk <= 0: return 1.0
    return (mu_bulk / mu_wall) ** 0.14

def darcy_weisbach_dp(f: float, L: float, Dh: float, rho: float, V: float) -> float:
    return f * (L / Dh) * (rho * V * V / 2.0)


# --- Main run ---
def run(hx, **kwargs) -> Dict[str, Any]:
    """
    Perform mechanical design of a double-pipe heat exchanger.

    Requires hx._basic_params (from BasicParameters).
    """
    if not hasattr(hx, "_basic_params"):
        raise ValueError(f"{hx.name}: Basic parameters not calculated. Run BasicParameters first.")
    bp = hx._basic_params
    results: Dict[str, Any] = {}

    # --- Required basic params ---
    def _fetch_bp(key: str, default: Optional[float] = None) -> float:
        val = kwargs.get(key, bp.get(key, default))
        if val is None:
            raise KeyError(f"Missing required basic parameter: {key}")
        return float(val)

    m_hot = _fetch_bp("m_hot")
    m_cold = _fetch_bp("m_cold")
    Ch = _fetch_bp("Ch")
    Cc = _fetch_bp("Cc")
    C_min = _fetch_bp("C_min")
    Th_in = _fetch_bp("Th_in")
    Tc_in = _fetch_bp("Tc_in")

    # --- Design inputs ---
    Di = float(kwargs.get("tube_diameter_m", 0.025))
    Do = float(kwargs.get("tube_outer_diameter_m", 0.032))
    Dout = float(kwargs.get("shell_inner_diameter_m", 0.05))
    k_wall = float(kwargs.get("wall_k_W_mK", 16.0))
    flow_type = kwargs.get("flow_type", "counter")
    max_dp_allowed = float(kwargs.get("max_pressure_drop_pa", 2e4))

    iterations = int(kwargs.get("iterations", 5))
    tol_length_rel = float(kwargs.get("tol_length_rel", 1e-3))

    include_minor_losses = bool(kwargs.get("include_minor_losses", True))
    parallel_annuli_n = max(1, int(kwargs.get("parallel_annuli_n", 1)))

    # K-factors
    K_hot = sum(float(kwargs.get(k, v)) for k, v in {
        "K_entrance_hot": 0.5, "K_exit_hot": 1.0, "K_fittings_hot_total": 0.5
    }.items())
    K_cold = sum(float(kwargs.get(k, v)) for k, v in {
        "K_entrance_cold": 0.5, "K_exit_cold": 1.0, "K_fittings_cold_total": 0.5
    }.items())

    # Fluid properties
    def fetch_prop(side: str, key: str, default: Optional[float] = None) -> float:
        val = kwargs.get(f"{side}_{key}", bp.get(f"{side}_{key}", default))
        if val is None:
            raise KeyError(f"Missing property {side}_{key}")
        return float(val)

    rho_hot, mu_hot, k_hot, cp_hot = [fetch_prop("hot", k, d) for k, d in [
        ("rho", 1000.0), ("mu", 1e-3), ("k", 0.6), ("cp", 4180.0)
    ]]
    rho_cold, mu_cold, k_cold, cp_cold = [fetch_prop("cold", k, d) for k, d in [
        ("rho", 1000.0), ("mu", 1e-3), ("k", 0.15), ("cp", 2000.0)
    ]]

    # Geometry
    A_tube = pi * Di**2 / 4.0
    A_annulus = pi * (Dout**2 - Do**2) / 4.0
    if A_annulus <= 0: raise ValueError("Invalid annulus geometry")

    m_cold_ch = m_cold / parallel_annuli_n

    # Initial guesses
    V_hot = m_hot / (rho_hot * A_tube)
    V_cold_ch = m_cold_ch / (rho_cold * A_annulus)
    Dh_tube, Dh_ann = Di, hydraulic_diameter_annulus(Do, Dout)
    Re_tube, Pr_tube = reynolds(rho_hot, V_hot, Dh_tube, mu_hot), prandtl(cp_hot, mu_hot, k_hot)
    Re_ann, Pr_ann = reynolds(rho_cold, V_cold_ch, Dh_ann, mu_cold), prandtl(cp_cold, mu_cold, k_cold)

    # Heat duty
    Q = C_min * (Th_in - Tc_in)

    length_prev, converged = None, False
    for _ in range(iterations):
        Nu_tube = (dittus_boelter_nusselt(Re_tube, Pr_tube, True) * sieder_tate_visc_corr(mu_hot, mu_hot)
                   if Re_tube >= 2300 else 3.66)
        Nu_ann = (dittus_boelter_nusselt(Re_ann, Pr_ann, False) * sieder_tate_visc_corr(mu_cold, mu_cold)
                  if Re_ann >= 2300 else 4.0)

        hi, ho = Nu_tube * k_hot / Dh_tube, Nu_ann * k_cold / Dh_ann
        R_conv_in, R_conv_out = 1/(hi*pi*Di), 1/(ho*pi*Dout)
        R_wall = log(Do/Di)/(2*pi*k_wall)
        UA_per_len = 1 / (R_conv_in + R_wall + R_conv_out)

        Th_out, Tc_out = Th_in - Q/Ch, Tc_in + Q/Cc
        dT1, dT2 = (Th_in - Tc_out, Th_out - Tc_in) if flow_type=="counter" else (Th_in-Tc_in, Th_out-Tc_out)
        LMTD = (dT1-dT2)/log(dT1/dT2) if abs(dT1-dT2)>1e-12 else dT1

        A_req = Q / (UA_per_len * LMTD)
        length = A_req / (pi*Di)

        if length_prev and abs(length-length_prev)/length_prev < tol_length_rel:
            converged = True
            break
        length_prev = length

        V_hot, V_cold_ch = m_hot/(rho_hot*A_tube), m_cold_ch/(rho_cold*A_annulus)
        Re_tube, Re_ann = reynolds(rho_hot,V_hot,Dh_tube,mu_hot), reynolds(rho_cold,V_cold_ch,Dh_ann,mu_cold)

    # Pressure drops
    f_tube, f_ann = friction_factor_blasius_or_laminar(Re_tube), friction_factor_blasius_or_laminar(Re_ann)
    dp_tube = darcy_weisbach_dp(f_tube, length, Dh_tube, rho_hot, V_hot)
    dp_ann = darcy_weisbach_dp(f_ann, length, Dh_ann, rho_cold, V_cold_ch)
    if include_minor_losses:
        dp_tube += K_hot * (rho_hot*V_hot**2/2)
        dp_ann += K_cold * (rho_cold*V_cold_ch**2/2)

    total_dp = dp_tube + dp_ann
    ok_design = total_dp <= max_dp_allowed
    suggestions = [f"Total ΔP = {total_dp:.1f} Pa {'OK' if ok_design else 'too high'}"]

    # Results
    results["geometry"] = {
        "Di": _wrap(Di, Diameter, "m"),
        "Do": _wrap(Do, Diameter, "m"),
        "Dout": _wrap(Dout, Diameter, "m"),
        "length_m": _wrap(length, Diameter, "m"),
        "parallel_annuli_n": parallel_annuli_n,
    }
    results["flows"] = {
        "m_hot": _wrap(m_hot, MassFlowRate, "kg/s"),
        "m_cold": _wrap(m_cold, MassFlowRate, "kg/s"),
        "Re_tube": Re_tube, "Re_ann": Re_ann,
        "V_hot": _wrap(V_hot, Velocity, "m/s"),
        "V_cold_channel": _wrap(V_cold_ch, Velocity, "m/s"),
    }
    results["thermal"] = {
        "Q_W": _wrap(Q, Power, "W"),
        "hi": _wrap(hi, HeatTransferCoefficient, "W/m2-K"),
        "ho": _wrap(ho, HeatTransferCoefficient, "W/m2-K"),
        "U_per_len": UA_per_len,
        "LMTD": LMTD,
    }
    results["pressure"] = {
        "dp_tube": _wrap(dp_tube, Pressure, "Pa"),
        "dp_annulus": _wrap(dp_ann, Pressure, "Pa"),
        "total_dp": _wrap(total_dp, Pressure, "Pa"),
    }
    results["ok_design"] = ok_design
    results["suggestions"] = suggestions
    return results
