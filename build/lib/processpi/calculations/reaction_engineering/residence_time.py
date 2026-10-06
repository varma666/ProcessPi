# processpi/calculations/reaction_engineering/residence_time.py

from typing import Dict, Literal
from ..base import CalculationBase


class ResidenceTime(CalculationBase):
    """
    Space time (τ) and conversion relations for ideal reactors.

    Workflows (select with `mode`):
    -------------------------------
    1) Space time:
        mode = "tau"
        Inputs:
            V: float            # reactor volume
            Q: float            # volumetric flow rate
        Output:
            {"tau": float, "space_velocity": float}
        Equations:
            τ = V / Q
            SV = 1 / τ

    2) Conversion for first-order kinetics (isothermal, constant density):
        mode = "conversion"
        Inputs:
            reactor: "CSTR" or "PFR"
            k: float            # first-order rate constant (1/time)
            tau: float          # space time (V/Q)
        Output:
            {"X": float}
        Equations:
            CSTR:   X = (k τ) / (1 + k τ)
            PFR:    X = 1 - exp(-k τ)
    """

    def validate_inputs(self):
        mode = self.inputs.get("mode", "tau").lower()
        if mode not in ("tau", "conversion"):
            raise ValueError("mode must be 'tau' or 'conversion'.")

        if mode == "tau":
            for k in ("V", "Q"):
                if k not in self.inputs:
                    raise ValueError(f"Missing required input: {k}")
            if float(self.inputs["V"]) <= 0 or float(self.inputs["Q"]) <= 0:
                raise ValueError("V and Q must be > 0.")

        else:  # conversion
            for k in ("reactor", "k", "tau"):
                if k not in self.inputs:
                    raise ValueError(f"Missing required input: {k}")
            reactor = str(self.inputs["reactor"]).upper()
            if reactor not in ("CSTR", "PFR"):
                raise ValueError("reactor must be 'CSTR' or 'PFR'.")
            if float(self.inputs["k"]) < 0 or float(self.inputs["tau"]) < 0:
                raise ValueError("k and tau must be >= 0.")

    def calculate(self) -> Dict:
        mode = self.inputs.get("mode", "tau").lower()

        if mode == "tau":
            V = float(self.inputs["V"])
            Q = float(self.inputs["Q"])
            tau = V / Q
            SV = 1.0 / tau
            return {"tau": tau, "space_velocity": SV}

        # conversion
        import math
        reactor = str(self.inputs["reactor"]).upper()
        k = float(self.inputs["k"])
        tau = float(self.inputs["tau"])

        if reactor == "CSTR":
            X = (k * tau) / (1.0 + k * tau) if (1.0 + k * tau) > 0 else 0.0
        else:  # PFR
            X = 1.0 - math.exp(-k * tau)

        return {"X": X}
