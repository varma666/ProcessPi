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
    Automatically creates an EnergyStream if none is supplied.
    """

    def __init__(self, name: str = "HeatExchanger",
                 method: str = "LMTD",
                 U: Optional[float] = None,
                 area: Optional[float] = None,
                 effectiveness: Optional[float] = None,
                 energy_stream: Optional[EnergyStream] = None):
        # Explicitly register 2 inlets (hot_in, cold_in) and 2 outlets (hot_out, cold_out)
        super().__init__(name, inlet_ports=2, outlet_ports=2)

        self.method = method.upper()
        self.U = U
        self.area = area
        self.effectiveness = effectiveness

        # Auto-create EnergyStream if none provided
        if energy_stream is None:
            self.energy_stream = EnergyStream(name=f"{name}_Q")
        else:
            self.energy_stream = energy_stream

        # Bind to this equipment
        self.energy_stream.bind_equipment(self)

    def attach_stream(self, stream: MaterialStream, port: str, index: Optional[int] = None):
        """
        Attach material streams to the exchanger by logical name.

        Ports:
        - hot_in   (inlet[0])
        - hot_out  (outlet[0])
        - cold_in  (inlet[1])
        - cold_out (outlet[1])
        """
        if port == "hot_in":
            self.attach_registered_stream(stream, "inlet", 0)
        elif port == "hot_out":
            self.attach_registered_stream(stream, "outlet", 0)
        elif port == "cold_in":
            self.attach_registered_stream(stream, "inlet", 1)
        elif port == "cold_out":
            self.attach_registered_stream(stream, "outlet", 1)
        else:
            raise ValueError(f"Invalid port: {port}")

    @property
    def hot_in(self) -> Optional[MaterialStream]:
        return self.inlets[0]

    @property
    def hot_out(self) -> Optional[MaterialStream]:
        return self.outlets[0]

    @property
    def cold_in(self) -> Optional[MaterialStream]:
        return self.inlets[1]

    @property
    def cold_out(self) -> Optional[MaterialStream]:
        return self.outlets[1]

    def simulate(self) -> Dict[str, Any]:
        """
        Run heat exchanger simulation.
        """
        if not self.hot_in or not self.cold_in:
            raise ValueError(f"{self.name}: both hot_in and cold_in streams must be attached.")

        # Fetch inlet conditions
        Th_in = self.hot_in.temperature.to("K").value
        Tc_in = self.cold_in.temperature.to("K").value
        m_hot = self.hot_in.mass_flow().to("kg/s").value
        m_cold = self.cold_in.mass_flow().to("kg/s").value

        # Heat capacities (J/kg-K) from components
        cp_hot = self.hot_in.component.get_cp(self.hot_in.temperature)
        cp_cold = self.cold_in.component.get_cp(self.cold_in.temperature)

        Ch = m_hot * cp_hot
        Cc = m_cold * cp_cold

        results: Dict[str, Any] = {}

        if self.method == "LMTD":
            if not (self.U and self.area):
                raise ValueError(f"{self.name}: U and area must be specified for LMTD method.")

            Th_out_guess = (
                self.hot_out.temperature.to("K").value
                if self.hot_out and self.hot_out.temperature else Th_in
            )
            Tc_out_guess = (
                self.cold_out.temperature.to("K").value
                if self.cold_out and self.cold_out.temperature else Tc_in
            )

            deltaT1 = Th_in - Tc_out_guess
            deltaT2 = Th_out_guess - Tc_in

            deltaT_lm = lmtd(deltaT1, deltaT2)
            Q = self.U * self.area * deltaT_lm

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
                raise ValueError(f"{self.name}: U, area, and effectiveness must be specified for NTU method.")

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
            raise ValueError(f"{self.name}: unknown method {self.method}")

        # Log energy duty
        self.energy_stream.record(Q, tag="Q_exchanger", equipment=self.name)

        return results
