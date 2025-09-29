# processpi/equipment/valve.py

from __future__ import annotations
from typing import Optional, Dict, Any, Union

from .base import Equipment
from ..streams import MaterialStream
from ..units import Pressure, Diameter, Length
from .standards import get_equivalent_length, get_k_factor


class Valve(Equipment):
    """
    Unified Valve / Throttle:
    - Flowsheet mode: isenthalpic throttling (h_in = h_out).
    - Pipeline mode: pressure loss via K-factor or equivalent length.
    """

    def __init__(
        self,
        name: str,
        delta_p: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
        fitting_type: Optional[str] = None,
        diameter: Optional[Diameter] = None,
        quantity: int = 1,
    ):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.delta_p = delta_p
        self.outlet_pressure = outlet_pressure

        # Pipeline attributes
        self.fitting_type = fitting_type
        self.diameter = diameter
        self.quantity = quantity

        # validate pipeline args
        if self.fitting_type and (not isinstance(self.quantity, int) or self.quantity <= 0):
            raise ValueError("`quantity` must be a positive integer.")

    # ---------------------
    # Pipeline calcs
    # ---------------------
    def equivalent_length(self) -> Optional[Length]:
        if not self.fitting_type:
            return None
        return get_equivalent_length(self.fitting_type)

    def k_factor(self) -> Optional[float]:
        if not self.fitting_type:
            return None
        return get_k_factor(self.fitting_type)

    # ---------------------
    # Simulation
    # ---------------------
    def simulate(self) -> Dict[str, Any]:
        if self.inlets and self.outlets:  # Flowsheet mode
            inlet: MaterialStream = self.inlets[0]
            outlet: MaterialStream = self.outlets[0]

            if inlet is None or outlet is None:
                raise ValueError(f"Valve {self.name} must have inlet and outlet streams attached.")

            # Decide outlet pressure
            if self.outlet_pressure is not None:
                P_out = self.outlet_pressure
            elif self.delta_p is not None:
                P_out = inlet.pressure - self.delta_p
            else:
                raise ValueError("Either delta_p or outlet_pressure must be specified for flowsheet mode.")

            if P_out <= 0:
                raise ValueError("Outlet pressure must be positive.")

            # Isenthalpic expansion
            h_in = inlet.enthalpy
            outlet.copy_from(inlet)
            outlet.pressure = P_out
            outlet.update_from_enthalpy(h_in, P_out)

            return {
                "mode": "flowsheet",
                "inlet_P": inlet.pressure,
                "outlet_P": outlet.pressure,
                "enthalpy": h_in,
                "phase": outlet.phase,
            }

        elif self.fitting_type:  # Pipeline mode
            le = self.equivalent_length()
            k = self.k_factor()
            return {
                "mode": "pipeline",
                "fitting_type": self.fitting_type,
                "quantity": self.quantity,
                "diameter_in": self.diameter.to("in").value if self.diameter else None,
                "diameter_m": self.diameter.to("m").value if self.diameter else None,
                "equivalent_length_m": le.to("m").value if le else None,
                "k_factor": k,
            }

        else:
            raise RuntimeError(
                f"Valve {self.name} cannot determine mode — "
                f"attach MaterialStreams (flowsheet) or set fitting_type (pipeline)."
            )

    def __repr__(self):
        if self.fitting_type:
            return f"Valve(name={self.name}, type={self.fitting_type}, qty={self.quantity})"
        return f"Valve(name={self.name}, ΔP={self.delta_p}, outlet_P={self.outlet_pressure})"
