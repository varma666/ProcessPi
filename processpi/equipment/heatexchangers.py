from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from processpi.streams import MaterialStream, EnergyStream
from processpi.calculations.lmtd import lmtd
from processpi.calculations.ntu import ntu


class HeatExchanger(Equipment):
    """
    Heat Exchanger Equipment.

    Supports both LMTD and NTU methods for outlet temperature predictions.
    Uses MaterialStream to auto-fetch thermophysical properties from Component.
    Can optionally log energy duties to an EnergyStream.
    """

    def __init__(self, method: str = "LMTD", 
                 U: Optional[float] = None,
                 area: Optional[float] = None,
                 effectiveness: Optional[float] = None,
                 energy_stream: Optional[EnergyStream] = None):
        super().__init__("HeatExchanger")
        self.method = method.upper()
        self.U = U
        self.area = area
        self.effectiveness = effectiveness
        self.energy_stream = energy_stream

        # Streams
        self.hot_in: Optional[MaterialStream] = None
        self.hot_out: Optional[MaterialStream] = None
        self.cold_in: Optional[MaterialStream] = None
        self.cold_out: Optional[MaterialStream] = None

        if self.energy_stream:
            self.energy_stream.bind_equipment(self)

    def attach_stream(self, stream: MaterialStream, port: str):
        """
        Attach material streams to the exchanger.
        """
        if port == "hot_in":
            self.hot_in = stream
            stream.connect_outlet(self)
        elif port == "hot_out":
            self.hot_out = stream
            stream.connect_inlet(self)
        elif port == "cold_in":
            self.cold_in = stream
            stream.connect_outlet(self)
        elif port == "cold_out":
            self.cold_out = stream
            stream.connect_inlet(self)
        else:
            raise ValueError(f"Invalid port: {port}")

    def simulate(self) -> Dict[str, Any]:
        """
        Run heat exchanger simulation.
        """
        if not all([self.hot_in, self.cold_in]):
            raise ValueError("Both hot_in and cold_in streams must be attached.")

        # Fetch inlet conditions
        Th_in = self.hot_in.temperature.to("K").value
        Tc_in = self.cold_in.temperature.to("K").value
        m_hot = self.hot_in.mass_flow().to("kg/s").value
        m_cold = self.cold_in.mass_flow().to("kg/s").value

        # Heat capacities (J/kg-K) from component
        cp_hot = self.hot_in.component.get_cp(self.hot_in.temperature)
        cp_cold = self.cold_in.component.get_cp(self.cold_in.temperature)

        Ch = m_hot * cp_hot
        Cc = m_cold * cp_cold

        results = {}

        if self.method == "LMTD":
            if not (self.U and self.area):
                raise ValueError("U and area must be specified for LMTD method.")

            # Use inlet values if outlet not pre-defined
            Th_out_guess = self.hot_out.temperature.to("K").value if self.hot_out and self.hot_out.temperature else Th_in
            Tc_out_guess = self.cold_out.temperature.to("K").value if self.cold_out and self.cold_out.temperature else Tc_in

            deltaT1 = Th_in - Tc_out_guess
            deltaT2 = Th_out_guess - Tc_in

            deltaT_lm = lmtd(deltaT1, deltaT2)
            Q = self.U * self.area * deltaT_lm

            # Update outlet streams (phase auto-updated inside MaterialStream)
            if self.hot_out:
                self.hot_out.update_from_enthalpy(h=None, P=self.hot_in.pressure, deltaQ=-Q)
            if self.cold_out:
                self.cold_out.update_from_enthalpy(h=None, P=self.cold_in.pressure, deltaQ=Q)

            results.update({
                "method": "LMTD",
                "Q": Q,
                "deltaT_lm": deltaT_lm,
                "Th_out": self.hot_out.temperature if self.hot_out else None,
                "Tc_out": self.cold_out.temperature if self.cold_out else None
            })

        elif self.method == "NTU":
            if not (self.U and self.area and self.effectiveness):
                raise ValueError("U, area, and effectiveness must be specified for NTU method.")

            results_ntu = ntu(Cc, Ch, self.U, self.area, self.effectiveness, Th_in, Tc_in)
            Q = results_ntu["Q"]

            if self.hot_out:
                self.hot_out.update_from_enthalpy(h=None, P=self.hot_in.pressure, deltaQ=-Q)
            if self.cold_out:
                self.cold_out.update_from_enthalpy(h=None, P=self.cold_in.pressure, deltaQ=Q)

            results.update({
                "method": "NTU",
                **results_ntu,
                "Th_out": self.hot_out.temperature if self.hot_out else None,
                "Tc_out": self.cold_out.temperature if self.cold_out else None
            })

        else:
            raise ValueError(f"Unknown method: {self.method}")

        # EnergyStream logging
        if self.energy_stream:
            self.energy_stream.record(Q, tag="Q_exchanger", equipment=self.name)

        return results
