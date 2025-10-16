"""
Advanced Evaporator Module
--------------------------
Features:
- Superheating + boiling + optional subcooling
- Zone-wise LMTD & U iterative convergence
- Bell–Delaware shell-side ΔP
- Flooding check for vertical orientation
- Uses Kern and Bell methods
"""

from typing import Dict, Any
from processpi.streams.material import MaterialStream
from ..base import HeatExchanger
from .kern_method import lmtd, overall_U, tube_htc, shell_htc, required_area, heat_duty
from .bell_method import bell_delaware_pressure_drop, check_flooding
import math

DEFAULT_FOUL_HOT = 0.0001
DEFAULT_FOUL_COLD = 0.0002
DEFAULT_TUBE_K = 16.0
GRAVITY = 9.81
GAMMA_MAX = 0.8

def design_evaporator(hot_in: MaterialStream, cold_in: MaterialStream,
                      orientation: str = "horizontal",
                      passes: int = 1,
                      Ft: float = 1.0,
                      fouling_hot: float = DEFAULT_FOUL_HOT,
                      fouling_cold: float = DEFAULT_FOUL_COLD,
                      layout: str = "triangular",
                      **kwargs) -> Dict[str, Any]:
    """
    Evaporator design with superheating, boiling, and optional subcooling zones.
    """

    T_hot_in = hot_in.temperature.to("K").value
    T_cold_in = cold_in.temperature.to("K").value
    T_sat = cold_in.component.saturation_temperature().to("K").value
    m_dot_hot = hot_in.mass_flowrate.to("kg/s").value
    cp_hot = hot_in.cp.to("J/kg-K").value
    m_dot_cold = cold_in.mass_flowrate.to("kg/s").value
    cp_cold = cold_in.cp.to("J/kg-K").value

    # Zone duties
    deltaT_super = max(T_cold_in - T_sat, 0)
    deltaT_subcool = max(T_hot_in - T_sat, 0)
    duty_super = heat_duty(m_dot_cold, cp_cold, T_cold_in, T_sat + deltaT_super)
    duty_boil = m_dot_cold * cold_in.component.latent_heat().to("J/kg").value
    duty_sub = heat_duty(m_dot_hot, cp_hot, T_hot_in, T_sat + deltaT_subcool)
    Q_total = duty_super + duty_boil + duty_sub

    def zone_convergence(duty, T_hot_start, T_hot_end, T_cold_start, T_cold_end,
                         h_tube_guess=500, max_iter=20, tol=1e-3):
        U = h_tube_guess
        for _ in range(max_iter):
            lmtd_val = lmtd(T_hot_start, T_hot_end, T_cold_start, T_cold_end, Ft)
            A_req = required_area(duty, U, lmtd_val)
            v_tube = m_dot_hot / (hot_in.component.density().to("kg/m³").value * A_req)
            Re = hot_in.component.density().to("kg/m³").value * v_tube * 0.025 / hot_in.component.viscosity().to("kg/m-s").value
            h_tube = tube_htc(hot_in.component.thermal_conductivity().to("W/m-K").value, 0.025, Re,
                              hot_in.cp.to("J/kg-K").value / hot_in.component.thermal_conductivity().to("W/m-K").value)
            U_new = overall_U(h_tube, h_tube, fouling_hot, fouling_cold, R_wall=0.001)
            if abs(U_new - U)/U < tol:
                U = U_new
                break
            U = U_new
        return A_req, U, lmtd_val

    # Zone-wise calculation
    A_super, U_super, LMTD_super = zone_convergence(duty_super, T_hot_in, T_hot_in - deltaT_super, T_cold_in, T_sat)
    A_boil, U_boil, LMTD_boil = zone_convergence(duty_boil, T_hot_in - deltaT_super, T_hot_in - deltaT_super, T_sat, T_sat)
    A_sub, U_sub, LMTD_sub = zone_convergence(duty_sub, T_hot_in - deltaT_super, T_hot_in - deltaT_super - deltaT_subcool, T_sat, T_cold_in)

    A_total = A_super + A_boil + A_sub

    tube_OD = 0.0254
    tube_pitch = 1.25 * tube_OD
    pitch_ratio = 0.866 if layout == "triangular" else 1.0
    bundle_diam = math.sqrt(A_total / (math.pi * tube_OD * passes))
    N_tubes = int(pitch_ratio * (bundle_diam / tube_pitch)**2)
    tube_length = A_total / (math.pi * tube_OD * N_tubes)
    shell_ID = bundle_diam * 1.1

    rho_s = hot_in.component.density().to("kg/m³").value
    mu_s = hot_in.component.viscosity().to("kg/m-s").value
    deltaP_shell = bell_delaware_pressure_drop(rho_s, mu_s, m_dot_hot, shell_ID, tube_OD)
    flooded = check_flooding(cold_in, tube_OD**2 * math.pi/4, vertical=(orientation=="vertical"))

    return {
        "Duty [W]": Q_total,
        "Overall U [W/m²-K]": (U_super + U_boil + U_sub)/3,
        "Area Superheat [m²]": A_super,
        "Area Boiling [m²]": A_boil,
        "Area Subcooling [m²]": A_sub,
        "Total Area [m²]": A_total,
        "Tube Count": N_tubes,
        "Tube Length [m]": tube_length,
        "Bundle Diameter [m]": bundle_diam,
        "Shell ID [m]": shell_ID,
        "Shell-side ΔP [Pa]": deltaP_shell,
        "Flooding Risk": flooded,
        "LMTD Zones [K]": {"Superheat": LMTD_super, "Boiling": LMTD_boil, "Subcool": LMTD_sub},
        "U Zones [W/m²-K]": {"Superheat": U_super, "Boiling": U_boil, "Subcool": U_sub},
    }
