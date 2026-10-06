# processpi/calculations/mass_transfer/drying_rate.py

from typing import Dict, Optional
from ..base import CalculationBase


class DryingRate(CalculationBase):
    """
    Detailed batch drying time and flux calculations across
    constant-rate and falling-rate periods.

    Two workflows:

    (A) Use direct constant-rate flux + falling-rate coefficient
        Inputs:
            M_dry: float                  # Dry solid mass (kg dry basis)
            A: float                      # Exposed drying area (m^2)
            X_i: float                    # Initial moisture content (kg water/kg dry solid)
            X_f: float                    # Final moisture content (kg water/kg dry solid)
            X_c: float                    # Critical moisture content (kg/kg dry solid)
            X_star: float                 # Equilibrium moisture content (kg/kg dry solid)
            N_c: float                    # Constant-rate flux (kg/m^2/s), e.g., measured or from HT/MT analysis
            k_f: float                    # Falling-rate coefficient (1/s) with linear-w.r.t-free-moisture assumption
        Output:
            {
              "t_constant_s": float,
              "t_falling_s": float,
              "t_total_s": float,
              "avg_flux_kg_m2_s": float
            }

        Model:
          * Constant-rate period:
                t_c = (M_dry/A) * (X_i - X_c) / N_c
          * Falling-rate (linear w.r.t free moisture X - X*):
                N = k_f * (X - X_star)
                t_f = (M_dry/A) * ln( (X_c - X_star) / (X_f - X_star) ) / k_f

    (B) Compute constant-rate flux from a mass-transfer coefficient (Lewis analogy style)
        Inputs:
            M_dry, A, X_i, X_f, X_c, X_star  (as above)
            h_m: float                # Mass-transfer coefficient (m/s)
            rho_v: float              # Vapor density at interface/film (kg/m^3)
            Y_s: float                # Humidity ratio (kg vapor/kg dry gas) at surface (saturation)
            Y_inf: float              # Humidity ratio in bulk gas (kg/kg_dry_gas)
            k_f: float                # Falling-rate coefficient (1/s)
        Output: same keys as (A)
        Model:
            N_c = h_m * rho_v * (Y_s - Y_inf)
    """

    def validate_inputs(self):
        mode = self.inputs.get("mode", "direct").lower()
        if mode not in ("direct", "with_km"):
            raise ValueError("mode must be either 'direct' (A) or 'with_km' (B).")

        required_common = ("M_dry", "A", "X_i", "X_f", "X_c", "X_star", "k_f")
        for k in required_common:
            if k not in self.inputs:
                raise ValueError(f"Missing required input: {k}")

        M_dry = float(self.inputs["M_dry"])
        A = float(self.inputs["A"])
        X_i = float(self.inputs["X_i"])
        X_f = float(self.inputs["X_f"])
        X_c = float(self.inputs["X_c"])
        X_star = float(self.inputs["X_star"])
        k_f = float(self.inputs["k_f"])

        if M_dry <= 0 or A <= 0:
            raise ValueError("M_dry and A must be > 0.")
        if not (X_star <= X_f < X_c <= X_i):
            raise ValueError("Require X_star <= X_f < X_c <= X_i.")

        if k_f <= 0:
            raise ValueError("k_f must be > 0.")

        if mode == "direct":
            if "N_c" not in self.inputs:
                raise ValueError("Missing required input for 'direct' mode: N_c")
            if float(self.inputs["N_c"]) <= 0:
                raise ValueError("N_c must be > 0.")

        if mode == "with_km":
            for k in ("h_m", "rho_v", "Y_s", "Y_inf"):
                if k not in self.inputs:
                    raise ValueError(f"Missing required input for 'with_km' mode: {k}")

    def calculate(self) -> Dict:
        mode = self.inputs.get("mode", "direct").lower()

        # Common data
        M_dry = float(self.inputs["M_dry"])
        A = float(self.inputs["A"])
        X_i = float(self.inputs["X_i"])
        X_f = float(self.inputs["X_f"])
        X_c = float(self.inputs["X_c"])
        X_star = float(self.inputs["X_star"])
        k_f = float(self.inputs["k_f"])

        # Constant-rate flux
        if mode == "direct":
            N_c = float(self.inputs["N_c"])
        else:
            h_m = float(self.inputs["h_m"])
            rho_v = float(self.inputs["rho_v"])
            Y_s = float(self.inputs["Y_s"])
            Y_inf = float(self.inputs["Y_inf"])
            N_c = h_m * rho_v * (Y_s - Y_inf)

        # Constant-rate time
        t_c = (M_dry / A) * (X_i - X_c) / N_c

        # Falling-rate time (linear model: N = k_f (X - X*))
        # t_f = (M/A) * ∫ dX / (k_f (X - X*)) from X_f..X_c
        #     = (M/A) * [ln((X_c - X*)/(X_f - X*))] / k_f
        import math
        t_f = (M_dry / A) * math.log((X_c - X_star) / (X_f - X_star)) / k_f

        t_total = t_c + t_f

        # Average flux over whole drying:
        # Total water removed per area = (M/A) * (X_i - X_f)
        total_water_per_area = (M_dry / A) * (X_i - X_f)
        avg_flux = total_water_per_area / t_total

        return {
            "t_constant_s": t_c,
            "t_falling_s": t_f,
            "t_total_s": t_total,
            "avg_flux_kg_m2_s": avg_flux
        }
