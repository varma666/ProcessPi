# processpi/equipment/flash.py

from __future__ import annotations
from typing import Optional, Dict, Any
from .base import Equipment
from ..streams import MaterialStream
from ..thermo.vle import flash_equilibrium  # placeholder VLE calc function

class FlashDrum(Equipment):
    """
    Flash Drum for vapor-liquid separation.

    Modes:
    - T, P specified (isothermal flash)
    - P, Q specified (adiabatic flash with duty)
    """

    def __init__(self, name: str):
        super().__init__(name, inlet_ports=1, outlet_ports=2)
        self.vapor_out: Optional[MaterialStream] = None
        self.liquid_out: Optional[MaterialStream] = None

    def attach_stream(self, stream: MaterialStream, port: str):
        if port == "in":
            self.inlets[0] = stream
            stream.connect_outlet(self)
        elif port == "vapor":
            self.vapor_out = stream
            stream.connect_inlet(self)
        elif port == "liquid":
            self.liquid_out = stream
            stream.connect_inlet(self)
        else:
            raise ValueError(f"Invalid port: {port}")

    def simulate(self,
                 pressure: Optional[float] = None,
                 temperature: Optional[float] = None,
                 duty: Optional[float] = None) -> Dict[str, Any]:
        """
        Perform flash separation.

        Parameters:
        - pressure: operating P [Pa]
        - temperature: operating T [K]
        - duty: optional heat duty (W)

        Returns:
        - dict with vapor_fraction, liquid_fraction, compositions, enthalpies
        """
        feed = self.inlets[0]
        if feed is None or self.vapor_out is None or self.liquid_out is None:
            raise ValueError(f"{self.name}: must attach feed, vapor, and liquid streams")

        # Use feed enthalpy/composition
        z = feed.components
        P = pressure or feed.pressure.value
        T = temperature or feed.temperature.value

        # Call thermo package (placeholder)
        flash_results = flash_equilibrium(z, T, P, duty=duty)

        Vfrac = flash_results["vapor_fraction"]
        Lfrac = 1 - Vfrac

        # Update outlet streams
        self.vapor_out.set_composition(flash_results["y"], basis="mole")
        self.vapor_out.pressure = feed.pressure
        self.vapor_out.temperature = feed.temperature
        self.vapor_out.phase = "vapor"

        self.liquid_out.set_composition(flash_results["x"], basis="mole")
        self.liquid_out.pressure = feed.pressure
        self.liquid_out.temperature = feed.temperature
        self.liquid_out.phase = "liquid"

        return {
            "Vfrac": Vfrac,
            "Lfrac": Lfrac,
            "y": flash_results["y"],
            "x": flash_results["x"],
            "T": T,
            "P": P
        }
