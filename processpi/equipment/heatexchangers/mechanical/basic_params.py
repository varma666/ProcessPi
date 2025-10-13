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
 
    if hx.cold_in is None or hx.hot_in is None:
         return ValueError(f"Inlet and Outlet Stream Temperatures are Must")
    
    hot_fluid_inlet_temperature = hx.hot_in.temperature.to("K")    
    if hx.hot_out is None:
         hot_fluid_outlet_temperature = None
    else:
         hot_fluid_outlet_temperature = hx.hot_out.temperature.to("K")
    cold_fluid_inlet_temperature = hx.cold_in.temperature.to("K")
    if hx.cold_out is None:
         cold_fluid_outlet_temperature = None
    else:
         cold_fluid_outlet_temperature = hx.cold_out.temperature.to("K")
    
    if hx.hot_in.mass_flow() is None and hx.cold_in.mass_flow() is None:
        return ValueError(f"At least one of the fluid flow rates must be specified")
    
    if hx.hot_in.mass_flow() is None:
         hot_fluid_flowrate = None
    else:
         hot_fluid_flowrate = hx.hot_in.mass_flow().to("kg/s")

    if hx.cold_in.mass_flow() is None:
         cold_fluid_flowrate = None
    else:
         cold_fluid_flowrate = hx.cold_in.mass_flow().to("kg/s")

    #print(hx.hot_in.specific_heat)
    hot_fluid_cp = hx.hot_in.specific_heat.to("J/kgK")
    #print(hot_fluid_cp)
    cold_fluid_cp = hx.cold_in.specific_heat.to("J/kgK")

    # -----------------------------
    # Calculate basic parameters
    # -----------------------------
    # Heat capacity rates
    Ch = hot_fluid_flowrate * hot_fluid_cp
    Cc = cold_fluid_flowrate * cold_fluid_cp

    # Maximum possible heat transfer
    C_min = min(Ch, Cc)
    C_max = max(Ch, Cc)

    results.update({
        "Th_in": hot_fluid_inlet_temperature,
        "Tc_in": cold_fluid_inlet_temperature,
        "m_hot": hot_fluid_flowrate,
        "m_cold": cold_fluid_flowrate,
        "cp_hot": hot_fluid_cp,
        "cp_cold": cold_fluid_cp,
        "Ch": Ch,
        "Cc": Cc,
        "C_min": C_min,
        "C_max": C_max,
        "delta_T_max": abs(hot_fluid_inlet_temperature - cold_fluid_inlet_temperature)
    })

    # Optional: allow user to override values via kwargs
    results.update(kwargs)

    return results

