# processpi/equipment/heatexchangers/mechanical/basic_params.py

from typing import Dict, Any

def run(hx, **kwargs) -> Dict[str, Any]:
    """
    Calculate basic design parameters for a heat exchanger.

    Parameters:
        hx : HeatExchanger instance
        **kwargs : optional arguments (e.g., design method override)

    Returns:
        Dict[str, Any]: Basic design parameters, ready for downstream calculations
    """
    results: Dict[str, Any] = {}

    # -----------------------------
    # Fetch stream info safely
    # -----------------------------
    hot_in = hx.hot_in
    cold_in = hx.cold_in

    if not hot_in or not cold_in:
        raise ValueError(f"{hx.name}: Both hot_in and cold_in streams must be attached.")

    # Mass flow rates in kg/s
    m_hot = hot_in.mass_flow().to("kg/s").value
    m_cold = cold_in.mass_flow().to("kg/s").value

    # Heat capacities (J/kg-K)
    cp_hot = hot_in.component.get_cp(hot_in.temperature)
    cp_cold = cold_in.component.get_cp(cold_in.temperature)

    # Inlet temperatures
    Th_in = hot_in.temperature.to("K").value
    Tc_in = cold_in.temperature.to("K").value

    # -----------------------------
    # Calculate basic parameters
    # -----------------------------
    # Heat capacity rates
    Ch = m_hot * cp_hot
    Cc = m_cold * cp_cold

    # Maximum possible heat transfer
    C_min = min(Ch, Cc)
    C_max = max(Ch, Cc)

    results.update({
        "Th_in": Th_in,
        "Tc_in": Tc_in,
        "m_hot": m_hot,
        "m_cold": m_cold,
        "cp_hot": cp_hot,
        "cp_cold": cp_cold,
        "Ch": Ch,
        "Cc": Cc,
        "C_min": C_min,
        "C_max": C_max,
        "delta_T_max": abs(Th_in - Tc_in)
    })

    # Optional: allow user to override values via kwargs
    results.update(kwargs)

    return results

