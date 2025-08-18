# processpi/calculations/reaction_engineering/reaction_rate.py

from typing import Dict, Optional, Mapping
from ..base import CalculationBase


class ReactionRate(CalculationBase):
    """
    General reaction-rate calculator supporting several kinetic models.

    Workflows (select with `model`):
    --------------------------------
    1) Power law (elementary / empirical):
        model = "power_law"
        Inputs:
            C: Mapping[str, float]         # species concentrations, mol/L (or consistent units)
            exponents: Mapping[str, float] # reaction orders for each species (e.g., {"A":1, "B":1})
            k: float                       # rate constant (units consistent with orders & C)
            (optional) A, Ea, T, R         # If k not given, compute k via Arrhenius: k = A*exp(-Ea/(R*T))
        Output: {"rate": float}

        Equation:
            r = k * Π_i C_i^{a_i}

    2) Langmuir–Hinshelwood (adsorption + surface reaction):
        model = "langmuir_hinshelwood"
        Inputs:
            k or (A, Ea, T, R)             # rate constant or Arrhenius params
            C: Mapping[str, float]         # species concentrations (e.g., {"A":..., "B":...})
            K: Mapping[str, float]         # adsorption constants for species present
            numerator: Mapping[str, float] # stoich exponents in numerator (default {"A":1})
            denom_power: float = 1.0       # overall power on denominator (default 1)
        Output: {"rate": float}

        Equation (generic):
            r = k * Π_j (C_j)^{ν_j} / [ 1 + Σ_i K_i C_i ]^{denom_power}

    3) Michaelis–Menten (enzymatic form, optional):
        model = "michaelis_menten"
        Inputs:
            Vmax: float
            Km: float
            S: float                        # substrate concentration
        Output: {"rate": float}

        Equation:
            r = Vmax * S / (Km + S)

    Notes
    -----
    * Units are your responsibility; keep them consistent.
    * If both `k` and (A,Ea,T[,R]) are provided, `k` is used and Arrhenius params ignored.
    * Default R = 8.314 if not supplied and Arrhenius is used.
    """

    def validate_inputs(self):
        model = self.inputs.get("model", "power_law").lower()
        if model not in ("power_law", "langmuir_hinshelwood", "michaelis_menten"):
            raise ValueError("model must be 'power_law', 'langmuir_hinshelwood', or 'michaelis_menten'.")

        if model == "power_law":
            if "C" not in self.inputs or "exponents" not in self.inputs:
                raise ValueError("power_law requires 'C' and 'exponents'.")
            C = self.inputs["C"]
            exps = self.inputs["exponents"]
            if not isinstance(C, Mapping) or not isinstance(exps, Mapping):
                raise ValueError("'C' and 'exponents' must be mappings.")
            # Either k or Arrhenius parameters:
            if "k" not in self.inputs and not all(k in self.inputs for k in ("A", "Ea", "T")):
                raise ValueError("Provide 'k' or Arrhenius params (A, Ea, T) for power_law.")

        elif model == "langmuir_hinshelwood":
            for key in ("C", "K"):
                if key not in self.inputs:
                    raise ValueError(f"langmuir_hinshelwood requires '{key}'.")
            if "k" not in self.inputs and not all(k in self.inputs for k in ("A", "Ea", "T")):
                raise ValueError("Provide 'k' or Arrhenius params (A, Ea, T) for langmuir_hinshelwood.")

        elif model == "michaelis_menten":
            for key in ("Vmax", "Km", "S"):
                if key not in self.inputs:
                    raise ValueError(f"michaelis_menten requires '{key}'.")

    def _arrhenius_k(self) -> float:
        """Compute k via Arrhenius if A, Ea, T present. Default R=8.314 unless provided."""
        if all(k in self.inputs for k in ("A", "Ea", "T")):
            import math
            A = float(self.inputs["A"])
            Ea = float(self.inputs["Ea"])
            T = float(self.inputs["T"])
            R = float(self.inputs.get("R", 8.314))
            return A * math.exp(-Ea / (R * T))
        raise ValueError("Arrhenius parameters (A, Ea, T) are required to compute k.")

    def calculate(self) -> Dict:
        model = self.inputs.get("model", "power_law").lower()

        if model == "power_law":
            C: Mapping[str, float] = self.inputs["C"]
            exps: Mapping[str, float] = self.inputs["exponents"]
            k = float(self.inputs.get("k", self._arrhenius_k()))
            rate = k
            for sp, a in exps.items():
                c = float(C.get(sp, 0.0))
                if c < 0:
                    raise ValueError(f"Negative concentration for species '{sp}'.")
                rate *= c ** float(a)
            return {"rate": rate}

        if model == "langmuir_hinshelwood":
            C: Mapping[str, float] = self.inputs["C"]
            K: Mapping[str, float] = self.inputs["K"]
            k = float(self.inputs.get("k", self._arrhenius_k()))
            numerator = self.inputs.get("numerator", {"A": 1.0})
            denom_power = float(self.inputs.get("denom_power", 1.0))

            # numerator term
            num = k
            for sp, nu in numerator.items():
                c = float(C.get(sp, 0.0))
                if c < 0:
                    raise ValueError(f"Negative concentration for species '{sp}'.")
                num *= c ** float(nu)

            # denominator term (1 + Σ K_i C_i)^{denom_power}
            denom_sum = 1.0
            for sp, Ki in K.items():
                c = float(C.get(sp, 0.0))
                if c < 0:
                    raise ValueError(f"Negative concentration for species '{sp}'.")
                denom_sum += float(Ki) * c

            rate = num / (denom_sum ** denom_power)
            return {"rate": rate}

        # michaelis_menten
        Vmax = float(self.inputs["Vmax"])
        Km = float(self.inputs["Km"])
        S = float(self.inputs["S"])
        if Vmax < 0 or Km < 0 or S < 0:
            raise ValueError("Vmax, Km, and S must be non-negative.")
        rate = Vmax * S / (Km + S) if (Km + S) > 0 else 0.0
        return {"rate": rate}
