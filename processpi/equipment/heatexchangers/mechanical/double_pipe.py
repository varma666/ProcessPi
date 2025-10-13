from ....units import *
from ....streams.material import MaterialStream
from ....components import Component
from typing import Dict, Any, Optional, Union
from ..base import HeatExchanger
from processpi.calculations.heat_transfer import *

def _get_parms(hx: HeatExchanger) -> Dict[str, Optional[Union[float, Temperature, MassFlowRate, SpecificHeat]]]:
    """Extract parameters from heat exchanger simulation."""
    if not isinstance(hx, HeatExchanger):
        raise TypeError("Input must be a HeatExchanger instance")
    if hx.simulated_params is None:
        raise ValueError("Heat exchanger has not been simulated yet. Please run simulate() first.")
    return hx.simulated_params
def _get_value(value: Optional[Union[float, Temperature, MassFlowRate, SpecificHeat]], name: str) -> Optional[float]:
    """Convert parameter to float if it has a 'value' attribute."""
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    elif isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"{name} must be a numeric type or a unit-wrapped type with a 'value' attribute.")

def run(hx: HeatExchanger, **kwargs) -> Dict[str, Any]:
    """Run heat exchanger simulation for LMTD or NTU method."""
    results = {}
    parms = _get_parms(hx)
    Th_in = _get_value(parms["Hot in Temp"], "Hot In")
    Th_out = _get_value(parms["Hot out Temp"], "Hot Out")
    Tc_in = _get_value(parms["Cold in Temp"], "Cold In")
    Tc_out = _get_value(parms["Cold out Temp"], "Cold Out")
    m_hot = _get_value(parms["m_hot"], "Hot Flow Rate")
    m_cold = _get_value(parms["m_cold"], "Cold Flow Rate")
    cP_hot = _get_value(parms["cP_hot"], "Hot Specific Heat")
    cP_cold = _get_value(parms["cP_cold"], "Cold Specific Heat")
    delta_Tlm = _get_value(parms["delta_Tlm"], "Log Mean Temperature Difference")
    Ch = m_hot * cP_hot
    Cc = m_cold * cP_cold
    C_min = min(Ch, Cc)
    C_max = max(Ch, Cc)

    Di = kwargs.get("innerpipe_dia", Diameter(0.115,"ft"))  # Assumed inner diameter
    Nre = (4 * m_hot) / (3.14 * Di.value * hx.hot_in.component.viscosity().to("cP").value)
    print(Nre)
    

