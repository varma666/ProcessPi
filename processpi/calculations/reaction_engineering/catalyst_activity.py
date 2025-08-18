# processpi/calculations/reaction_engineering/catalyst_activity.py

from typing import Dict, Optional
from ..base import CalculationBase


class CatalystActivity(CalculationBase):
    """
    Catalyst activity decay & temperature correction utilities.

    Workflows (select with `model`):
    --------------------------------
    1) First-order deactivation:
        model = "first_order"
        Inputs:
            k_d or (A_d, Ea_d, T[, R])   # deactivation constant (1/time) or Arrhenius params
            t: float                     # time on stream
            a0: float = 1.0              # initial activity
        Output:
            {"a": float}
        Equation:
            a(t) = a0 * exp(-k_d * t)

    2) Power-law deactivation order n:
        model = "power_order"
        Inputs:
            n: float                      # deactivation order (n >= 0)
            k_d or (A_d, Ea_d, T[, R])    # deactivation constant or Arrhenius
            t: float
            a0: float = 1.0
        Output:
            {"a": float}
        Equation:
            da/dt = -k_d * a^n
            => if n = 1: a = a0 exp(-k_d t)
               if n != 1: a = a0 * [1 + (n-1) k_d t / a0^{(n-1)}]^(-1/(n-1))

    3) Temperature correction for activity-related constants (Arrhenius):
        model = "arrhenius_correction"
        Inputs:
            A_d, Ea_d, T[, R]
        Output:
            {"k_d": float}
        Equation:
            k_d = A_d * exp(-Ea_d/(R*T))

    Notes
    -----
    * For consistency, default R = 8.314 if not supplied.
    * a0 typically in [0,1], but any positive value is allowed for generic scaling.
    """

    def validate_inputs(self):
        model = self.inputs.get("model", "first_order").lower()
        if model not in ("first_order", "power_order", "arrhenius_correction"):
            raise ValueError("model must be 'first_order', 'power_order', or 'arrhenius_correction'.")

        if model in ("first_order", "power_order"):
            if "t" not in self.inputs:
                raise ValueError("Missing required input: t")
            if "k_d" not in self.inputs and not all(k in self.inputs for k in ("A_d", "Ea_d", "T")):
                raise ValueError("Provide 'k_d' or Arrhenius params (A_d, Ea_d, T).")
            if model == "power_order" and "n" not in self.inputs:
                raise ValueError("power_order requires 'n'.")

        if model == "arrhenius_correction":
            for k in ("A_d", "Ea_d", "T"):
                if k not in self.inputs:
                    raise ValueError(f"Missing required input: {k}")

    def _arrhenius_kd(self) -> float:
        """Compute k_d from Arrhenius parameters if needed."""
        import math
        A = float(self.inputs["A_d"])
        Ea = float(self.inputs["Ea_d"])
        T = float(self.inputs["T"])
        R = float(self.inputs.get("R", 8.314))
        return A * math.exp(-Ea / (R * T))

    def calculate(self) -> Dict:
        import math
        model = self.inputs.get("model", "first_order").lower()

        if model == "arrhenius_correction":
            return {"k_d": self._arrhenius_kd()}

        # Common pieces for models producing activity a(t)
        t = float(self.inputs["t"])
        a0 = float(self.inputs.get("a0", 1.0))
        k_d = float(self.inputs.get("k_d", self._arrhenius_kd()))
        if t < 0 or a0 <= 0 or k_d < 0:
            raise ValueError("Require t >= 0, a0 > 0, k_d >= 0.")

        if model == "first_order":
            a = a0 * math.exp(-k_d * t)
            return {"a": a}

        # power_order
        n = float(self.inputs["n"])
        if n == 1.0:
            a = a0 * math.exp(-k_d * t)
        else:
            # a = a0 * [1 + (n-1) k_d t / a0^{(n-1)}]^(-1/(n-1))
            denom = 1.0 + (n - 1.0) * k_d * t / (a0 ** (n - 1.0))
            if denom <= 0:
                # Model breakdown; clamp to small positive value
                denom = 1e-12
            a = a0 * (denom ** (-1.0 / (n - 1.0)))
        return {"a": a}
