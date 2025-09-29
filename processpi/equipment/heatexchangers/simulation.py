from typing import Dict, Any
from . import HeatExchanger
from processpi.calculations.lmtd import lmtd
from processpi.calculations.ntu import ntu


# --------------------------
# Helper Functions
# --------------------------
def fetch_inlet_conditions(hx: HeatExchanger) -> Dict[str, Any]:
    """Fetch mass flows, temperatures, and heat capacities of hot and cold streams."""
    if not hx.hot_in or not hx.cold_in:
        raise ValueError(f"{hx.name}: both hot_in and cold_in streams must be attached.")

    Th_in = hx.hot_in.temperature.to("K").value
    Tc_in = hx.cold_in.temperature.to("K").value
    m_hot = hx.hot_in.mass_flow().to("kg/s").value
    m_cold = hx.cold_in.mass_flow().to("kg/s").value

    cp_hot = hx.hot_in.component.get_cp(hx.hot_in.temperature)
    cp_cold = hx.cold_in.component.get_cp(hx.cold_in.temperature)

    Ch = m_hot * cp_hot
    Cc = m_cold * cp_cold

    return {
        "Th_in": Th_in,
        "Tc_in": Tc_in,
        "m_hot": m_hot,
        "m_cold": m_cold,
        "cp_hot": cp_hot,
        "cp_cold": cp_cold,
        "Ch": Ch,
        "Cc": Cc
    }


def update_outlets(hx: HeatExchanger, Q: float):
    """Update hot and cold outlet streams with heat duty."""
    if hx.hot_out:
        hx.hot_out.update_from_enthalpy(h=None, P=hx.hot_in.pressure, deltaQ=-Q)
    if hx.cold_out:
        hx.cold_out.update_from_enthalpy(h=None, P=hx.cold_in.pressure, deltaQ=Q)


def log_energy(hx: HeatExchanger, Q: float):
    """Record energy duty in the associated energy stream."""
    hx.energy_stream.record(Q, tag="Q_exchanger", equipment=hx.name)


# --------------------------
# Main Simulation Function
# --------------------------
def run_simulation(hx: HeatExchanger) -> Dict[str, Any]:
    """Run heat exchanger simulation for LMTD or NTU method."""
    conds = fetch_inlet_conditions(hx)
    Th_in = conds["Th_in"]
    Tc_in = conds["Tc_in"]
    Ch = conds["Ch"]
    Cc = conds["Cc"]

    results: Dict[str, Any] = {}

    # --------------------------
    # LMTD Method
    # --------------------------
    if hx.method == "LMTD":
        if not (hx.U and hx.area):
            raise ValueError(f"{hx.name}: U and area must be specified for LMTD method.")

        Th_out_guess = hx.hot_out.temperature.to("K").value if hx.hot_out and hx.hot_out.temperature else Th_in
        Tc_out_guess = hx.cold_out.temperature.to("K").value if hx.cold_out and hx.cold_out.temperature else Tc_in

        deltaT1 = Th_in - Tc_out_guess
        deltaT2 = Th_out_guess - Tc_in
        deltaT_lm = lmtd(deltaT1, deltaT2)
        Q = hx.U * hx.area * deltaT_lm

        update_outlets(hx, Q)

        results.update({
            "method": "LMTD",
            "Q": Q,
            "deltaT_lm": deltaT_lm,
            "Th_out": hx.hot_out.temperature if hx.hot_out else None,
            "Tc_out": hx.cold_out.temperature if hx.cold_out else None
        })

    # --------------------------
    # NTU Method
    # --------------------------
    elif hx.method == "NTU":
        if not (hx.U and hx.area and hx.effectiveness):
            raise ValueError(f"{hx.name}: U, area, and effectiveness must be specified for NTU method.")

        results_ntu = ntu(Cc, Ch, hx.U, hx.area, hx.effectiveness, Th_in, Tc_in)
        Q = results_ntu["Q"]

        update_outlets(hx, Q)

        results.update({
            "method": "NTU",
            **results_ntu,
            "Th_out": hx.hot_out.temperature if hx.hot_out else None,
            "Tc_out": hx.cold_out.temperature if hx.cold_out else None
        })

    else:
        raise ValueError(f"{hx.name}: unknown method {hx.method}")

    log_energy(hx, Q)
    return results
