from typing import Dict, Any
from . import HeatExchanger
from processpi.calculations.lmtd import lmtd
from processpi.calculations.ntu import ntu

def run_simulation(hx: HeatExchanger) -> Dict[str, Any]:
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

    results: Dict[str, Any] = {}

    if hx.method == "LMTD":
        if not (hx.U and hx.area):
            raise ValueError(f"{hx.name}: U and area must be specified for LMTD method.")
        # ... LMTD calculation logic here ...
        results["method"] = "LMTD"

    elif hx.method == "NTU":
        if not (hx.U and hx.area and hx.effectiveness):
            raise ValueError(f"{hx.name}: U, area, and effectiveness must be specified for NTU method.")
        # ... NTU calculation logic here ...
        results["method"] = "NTU"

    else:
        raise ValueError(f"{hx.name}: unknown method {hx.method}")

    return results

