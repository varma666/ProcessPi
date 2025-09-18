# processpi/equipment/heat_exchanger.py

from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from processpi.streams import MaterialStream
from processpi.calculations.lmtd import lmtd
from processpi.calculations.ntu import ntu


class HeatExchanger(Equipment):
    """
    Heat Exchanger Equipment.

    Supports both LMTD and NTU methods for outlet temperature predictions.
    Uses MaterialStream to auto-fetch thermophysical properties from Component.
    """

    def __init__(self, method: str = "LMTD", U: Optional[float] = None,
                 area: Optional[float] = None, effectiveness: Optional[float] = None):
        super().__init__("HeatExchanger")
        self.method = method.upper()
        self.U = U
        self.area = area
        self.effectiveness = effectiveness

        # Streams
        self.hot_in: Optional[MaterialStream] = None
        self.hot_out: Optional[MaterialStream] = None
        self.cold_in: Optional[MaterialStream] = None
        self.cold_out: Optional[MaterialStream] = None

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

        # Fetch stream properties
        Th_in = self.hot_in.temperature
        Tc_in = self.cold_in.temperature
        m_hot = self.hot_in.mass_flow
        m_cold = self.cold_in.mass_flow

        # Fetch cp from component (T-dependent)
        cp_hot = self.hot_in.component.get_cp(Th_in)
        cp_cold = self.cold_in.component.get_cp(Tc_in)

        Ch = m_hot * cp_hot
        Cc = m_cold * cp_cold

        results = {}

        if self.method == "LMTD":
            if not (self.U and self.area):
                raise ValueError("U and area must be specified for LMTD method.")

            # Assume counterflow
            deltaT1 = Th_in - self.cold_out.temperature if self.cold_out else (Th_in - Tc_in)
            deltaT2 = self.hot_out.temperature - Tc_in if self.hot_out else (Th_in - Tc_in)

            deltaT_lm = lmtd(deltaT1, deltaT2)
            Q = self.U * self.area * deltaT_lm

            # Update outlet temps if not provided
            if self.hot_out:
                self.hot_out.temperature = Th_in - Q / Ch
            if self.cold_out:
                self.cold_out.temperature = Tc_in + Q / Cc

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

            # NTU method calc
            results_ntu = ntu(Cc, Ch, self.U, self.area, self.effectiveness, Th_in, Tc_in)
            Q = results_ntu["Q"]

            # Update outlet temps
            if self.hot_out:
                self.hot_out.temperature = Th_in - Q / Ch
            if self.cold_out:
                self.cold_out.temperature = Tc_in + Q / Cc

            results.update({
                "method": "NTU",
                **results_ntu,
                "Th_out": self.hot_out.temperature if self.hot_out else None,
                "Tc_out": self.cold_out.temperature if self.cold_out else None
            })

        else:
            raise ValueError(f"Unknown method: {self.method}")

        return results
