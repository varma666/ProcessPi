from typing import Dict, Any
from .__init__ import HeatExchanger
from processpi.calculations.heat_transfer.lmtd import LMTD
from processpi.calculations.heat_transfer.ntu import NTUHeatExchanger
from processpi.components import *
from ...streams.material import MaterialStream
from ...units import *


def run_simulation(hx: HeatExchanger) -> Dict[str, Any]:
    """Run heat exchanger simulation for LMTD or NTU method."""
    results = {}
    parms = _get_parms(hx)
    Th_in = _get_value(parms["Th_in"], "Hot In")
    Th_out = _get_value(parms["Th_out"], "Hot Out")
    Tc_in = _get_value(parms["Tc_in"], "Cold In")
    Tc_out = _get_value(parms["Tc_out"], "Cold Out")
    m_hot = _get_value(parms["m_hot"], "Hot Flow Rate")
    m_cold = _get_value(parms["m_cold"], "Cold Flow Rate")
    cP_hot = _get_value(parms["cP_hot"], "Hot Specific Heat")
    cP_cold = _get_value(parms["cP_cold"], "Cold Specific Heat")

    if m_hot is not None and m_cold is None:
         if Th_in is not None and Th_out is not None and Tc_in is not None and Tc_out is not None:
              Q_hot = m_hot * cP_hot * (Th_in - Th_out)
              m_cold = Q_hot / (cP_cold * (Tc_out - Tc_in))
    if m_cold is not None and m_hot is None:
         if Th_in is not None and Th_out is not None and Tc_in is not None and Tc_out is not None:
              Q_cold = m_cold * cP_cold * (Tc_out - Tc_in)
              m_hot = Q_cold / (cP_hot * (Th_in - Th_out))

    if Th_out is None or Tc_out is None:
        Th_out,Tc_out = _get_outlet_temperature(Th_in,Tc_in,m_hot,m_cold,cP_hot,cP_cold) 

    
    Q_hot = m_hot * cP_hot * (Th_in - Th_out)
    Q_cold = m_cold * cP_cold * (Tc_out - Tc_in)
    dT1 = Th_in - Tc_out
    dT2 = Th_out - Tc_in
    delta_Tlm = LMTD(dT1=dT1, dT2=dT2).calculate()

    if hx.U is None:
         if hx.hot_in.component is None or hx.cold_in.component is None:
              raise ValueError(f"U is Not initiated please initiate U or add a component")
         else:
              hot_fluid = hx.hot_in.component.name
              cold_fluid = hx.cold_in.component.name
              U = get_U(hot_fluid,cold_fluid)
              print("U Not Declared")

         
    else:
         U = hx.U

    results = {
         "Q_hot" : Q_hot,
         "Q_cold" : Q_cold,
         "Hot in Temp" : Th_in,
         "Hot Out Temp" : Th_out,
         "Cold in Temp" : Tc_in,
         "Cold Out Temp" : Tc_out,
         "m_hot" : m_hot,
         "m_cold" : m_cold,
         "cP_hot" : cP_hot,
         "cP_cold" : cP_cold,
         "delta_Tlm" : delta_Tlm
    }
    
    return results


def _get_outlet_temperature(Th_in,Tc_in,m_hot,m_cold,cP_hot,cP_cold):
     
    C_hot = m_hot * cP_hot
    C_cold = m_cold * cP_cold
    deltaT_max = Th_in - Tc_in
    Q = min(C_cold,C_hot) * deltaT_max

    if C_hot < C_cold:
        Th_out = Th_in - Q / C_hot
        Tc_out = Tc_in + Q / C_cold

    else:
        Th_out = Th_in - Q / C_hot
        Tc_out = Tc_in + Q / C_cold

    return Th_out,Tc_out
         

def _get_parms(hx: HeatExchanger) -> Dict[str, Any]:

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


    hot_fluid_cp = hx.hot_in.specific_heat.to("J/kgK")
    cold_fluid_cp = hx.cold_in.specific_heat.to("J/kgK")

    results = {
        "Th_in" : hot_fluid_inlet_temperature,
        "Th_out" : hot_fluid_outlet_temperature,
        "Tc_in" : cold_fluid_inlet_temperature,
        "Tc_out" : cold_fluid_outlet_temperature,
        "m_hot" : hot_fluid_flowrate,
        "m_cold" : cold_fluid_flowrate,
        "cP_hot" : hot_fluid_cp,
        "cP_cold" : cold_fluid_cp
    }

    return results

def _get_value(x, name):
        """
        A static utility method to extract the numeric value from an input.

        This method handles both simple numeric types (like `int`, `float`)
        and custom objects that have a `.value` attribute, such as unit objects.
        It raises a `TypeError` if the value cannot be interpreted as a number.

        Args:
            x: The input value, which can be a number or a unit object.
            name (str): The name of the input, used for a more informative
                        error message.

        Returns:
            float: The numeric value of the input.

        Raises:
            TypeError: If the input value cannot be converted to a float.
        """
        if x is None:
             return None
        
        if hasattr(x, "value"):
            return x.value
        try:
            # Accept numpy/scalar numbers.
            return float(x)
        except (TypeError, ValueError):
            raise TypeError(f"Could not interpret {name} value: {x!r}")


