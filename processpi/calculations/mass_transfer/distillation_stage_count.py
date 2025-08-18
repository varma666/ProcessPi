# processpi/calculations/mass_transfer/distillation_stage_count.py

from typing import Dict, List, Tuple, Callable, Optional
from ..base import CalculationBase
from ...units import *

class DistillationStageCount(CalculationBase):
    """
    Detailed distillation stage calculations.

    Supports two workflows:
    1) Fenske minimum stages (binary):
        - Inputs:
            alpha_avg: float                   # Average relative volatility (LK relative to HK), alpha > 1
            xD: float                          # LK mole fraction in distillate
            xB: float                          # LK mole fraction in bottoms
        - Output:
            {"Nmin_theoretical": float}

    2) McCabe–Thiele graphical stepping (binary):
        - Inputs:
            xD: float                          # LK in distillate
            xB: float                          # LK in bottoms
            zF: float                          # LK in feed
            R: float                           # Reflux ratio (L/D)
            q: float                           # Feed thermal condition (q-line slope param)
            eq_curve: List[Tuple[float,float]] or callable x->y_eq
                                              # Equilibrium data: y = f(x). You can pass:
                                              #   - list of (x,y) pairs (monotonic in x), OR
                                              #   - a callable y_eq(x)
            total_condenser: bool = True       # If True, add total condenser stage
            partial_reboiler: bool = True      # If True, count reboiler as a stage
            max_stages: int = 300              # Safety limit for stepping
            tol: float = 1e-6                  # Numeric tolerance
        - Assumptions:
            * Binary system (LK/HK).
            * Constant molar overflow (straight rectifying/stripping lines).
            * Feed plate determined by q-line intersection.
        - Output:
            {
              "N_theoretical": int,
              "rectifying_stages": int,
              "stripping_stages": int,
              "includes_total_condenser": bool,
              "includes_partial_reboiler": bool
            }

    Notes
    -----
    * The McCabe–Thiele stepper uses piecewise linear interpolation of eq data if provided as (x,y) pairs.
    * Rectifying operating line:    y = (R/(R+1)) x + xD/(R+1)
    * q-line (feed):                y = (q/(q-1)) x - zF/(q-1)     (q != 1 case)
      Special cases:
        - q = 1 (saturated liquid): vertical line at x = zF
        - q = 0 (saturated vapor):  line slope 0 through y = zF
    * Stripping line is constructed through feed intersection and (xB, xB) pinch.
    """

    # ------------- Interface -------------
    def validate_inputs(self):
        mode = self.inputs.get("mode", "fenske").lower()
        if mode not in ("fenske", "mccabe_thiele"):
            raise ValueError("mode must be either 'fenske' or 'mccabe_thiele'.")

        if mode == "fenske":
            for k in ("alpha_avg", "xD", "xB"):
                if k not in self.inputs:
                    raise ValueError(f"Missing required input for Fenske: {k}")
            alpha = float(self.inputs["alpha_avg"])
            xD = float(self.inputs["xD"])
            xB = float(self.inputs["xB"])
            if alpha <= 1.0:
                raise ValueError("alpha_avg must be > 1 for binary Fenske.")
            for x in (xD, xB):
                if not (0.0 < x < 1.0):
                    raise ValueError("xD and xB must be in (0,1).")

        if mode == "mccabe_thiele":
            required = ("xD", "xB", "zF", "R", "q", "eq_curve")
            for k in required:
                if k not in self.inputs:
                    raise ValueError(f"Missing required input for McCabe–Thiele: {k}")

            xD = float(self.inputs["xD"])
            xB = float(self.inputs["xB"])
            zF = float(self.inputs["zF"])
            R = float(self.inputs["R"])
            q = float(self.inputs["q"])

            for x in (xD, xB, zF):
                if not (0.0 < x < 1.0):
                    raise ValueError("Compositions xD, xB, zF must be in (0,1).")
            if not (xB < zF < xD):
                raise ValueError("Must satisfy xB < zF < xD (LK is more volatile).")
            if R <= 0:
                raise ValueError("Reflux ratio R must be > 0.")
            # eq_curve can be callable or list of tuples
            eq_curve = self.inputs["eq_curve"]
            if not (callable(eq_curve) or (isinstance(eq_curve, list) and all(len(t) == 2 for t in eq_curve))):
                raise ValueError("eq_curve must be a callable y_eq(x) or a list of (x,y) pairs.")

    def calculate(self) -> Dict:
        mode = self.inputs.get("mode", "fenske").lower()
        if mode == "fenske":
            return self._calc_fenske_minimum_stages()
        else:
            return self._calc_mccabe_thiele()

    # ------------- Fenske minimum stages -------------
    def _calc_fenske_minimum_stages(self) -> Dict:
        alpha = float(self.inputs["alpha_avg"])
        xD = float(self.inputs["xD"])  # LK in distillate
        xB = float(self.inputs["xB"])  # LK in bottoms

        # Fenske equation (binary; min stages at total reflux):
        # N_min = ln[(xD/(1-xD)) * ((1-xB)/xB)] / ln(alpha)
        import math
        term_top = xD / (1.0 - xD)
        term_bottom = (1.0 - xB) / xB
        Nmin = math.log(term_top * term_bottom) / math.log(alpha)

        return {"Nmin_theoretical": Nmin}

    # ------------- McCabe–Thiele stepping -------------
    def _calc_mccabe_thiele(self) -> Dict:
        xD = float(self.inputs["xD"])
        xB = float(self.inputs["xB"])
        zF = float(self.inputs["zF"])
        R = float(self.inputs["R"])
        q = float(self.inputs["q"])
        total_condenser = bool(self.inputs.get("total_condenser", True))
        partial_reboiler = bool(self.inputs.get("partial_reboiler", True))
        max_stages = int(self.inputs.get("max_stages", 300))
        tol = float(self.inputs.get("tol", 1e-6))

        # Build y_eq(x)
        y_eq = self._make_y_eq(self.inputs["eq_curve"])

        # Rectifying operating line
        # y = (R/(R+1))*x + xD/(R+1)
        def y_rect(x: float) -> float:
            return (R / (R + 1.0)) * x + xD / (R + 1.0)

        # q-line
        q_is_one = abs(q - 1.0) < 1e-12
        q_is_zero = abs(q) < 1e-12
        if q_is_one:
            # vertical line at x = zF
            q_line = ("vertical", zF)
        elif q_is_zero:
            # horizontal line at y = zF
            q_line = ("horizontal", zF)
        else:
            # general form y = m_q * x + b_q, with slope q/(q-1)
            m_q = q / (q - 1.0)
            b_q = -zF / (q - 1.0)
            q_line = ("line", (m_q, b_q))

        # Find intersection of rectifying line with q-line -> (xF_int, yF_int)
        xF_int, yF_int = self._intersect_rectifying_with_qline(y_rect, q_line)

        # Stripping line through intersection and (xB, xB)
        # y = m_s * x + b_s
        m_s = (yF_int - xB) / (xF_int - xB)
        b_s = xB - m_s * xB

        def y_strip(x: float) -> float:
            return m_s * x + b_s

        # McCabe–Thiele stepping:
        # start at (xD, y = xD) for total condenser; otherwise start at (xD, y_rect(xD))
        stages = 0
        rect_stages = 0
        strip_stages = 0

        # Starting point:
        x_cur = xD
        y_cur = xD if total_condenser else y_rect(xD)  # horizontal to equilibrium first if total condenser

        # Stage loop
        while stages < max_stages and x_cur - xB > tol:
            # 1) Horizontal to equilibrium curve (constant y)
            # Find x_eq such that y_eq(x_eq) = y_cur
            x_eq = self._x_from_y_on_eq(y_cur, y_eq, x_min=xB, x_max=xD)
            if x_eq is None:
                # If it fails, try clipping
                x_eq = max(min(x_cur, xD), xB)

            # 2) Vertical to operating line:
            # if x_eq >= xF_int -> rectifying, else stripping
            if x_eq >= xF_int:
                # rectifying
                y_next = y_rect(x_eq)
                rect_stages += 1
            else:
                # stripping
                y_next = y_strip(x_eq)
                strip_stages += 1

            stages += 1
            x_cur, y_cur = x_eq, y_next

            # stopping if we reached the bottoms composition roughly
            if abs(x_cur - xB) <= tol:
                break

        # Add reboiler stage if required
        if partial_reboiler:
            stages += 1
            strip_stages += 1

        # Add condenser stage if total condenser and at least one rectifying stage
        if total_condenser and rect_stages > 0:
            # condenser stage already inherently counted by starting at y=xD then stepping horizontal to eq,
            # so we don't add an extra here. (Many conventions treat this first horizontal as the condenser stage.)
            pass

        return {
            "N_theoretical": stages,
            "rectifying_stages": rect_stages,
            "stripping_stages": strip_stages,
            "includes_total_condenser": total_condenser,
            "includes_partial_reboiler": partial_reboiler,
        }

    # ------------- Helpers -------------
    @staticmethod
    def _make_y_eq(eq_curve: "Callable[[float], float] | List[Tuple[float,float]]") -> Callable[[float], float]:
        """
        Return y_eq(x) callable from either a function or list of (x,y) data (piecewise-linear).
        """
        if callable(eq_curve):
            return eq_curve

        # Build linear interpolator on sorted x
        data = sorted(eq_curve, key=lambda t: t[0])
        xs = [t[0] for t in data]
        ys = [t[1] for t in data]

        def interp(x: float) -> float:
            if x <= xs[0]:
                return ys[0]
            if x >= xs[-1]:
                return ys[-1]
            # find bracket
            import bisect
            i = bisect.bisect_right(xs, x) - 1
            x0, y0 = xs[i], ys[i]
            x1, y1 = xs[i + 1], ys[i + 1]
            # linear interpolation
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)

        return interp

    @staticmethod
    def _intersect_rectifying_with_qline(y_rect: Callable[[float], float],
                                         q_line_spec) -> Tuple[float, float]:
        """
        Compute intersection point (x*, y*) between rectifying line and q-line spec.
        q_line_spec is either:
          ("vertical", x0), ("horizontal", y0), or ("line", (m, b)) with y = m x + b
        """
        mode = q_line_spec[0]
        if mode == "vertical":
            x0 = q_line_spec[1]
            return x0, y_rect(x0)
        elif mode == "horizontal":
            y0 = q_line_spec[1]
            # solve y_rect(x) = y0  -> (R/(R+1))x + xD/(R+1) = y0
            # general invert via simple 1D solve
            def f(x): return y_rect(x) - y0
            x = DistillationStageCount._solve_scalar(f, 0.0, 1.0)
            return x, y0
        else:
            m, b = q_line_spec[1]
            # solve y_rect(x) = m x + b
            # r(x) = a x + c; set a x + c = m x + b -> (a - m)x = b - c
            # where a = R/(R+1), c = xD/(R+1). We don't know R & xD here, but y_rect contains them.
            # Use numeric solve:
            def f(x): return y_rect(x) - (m * x + b)
            x = DistillationStageCount._solve_scalar(f, 0.0, 1.0)
            return x, y_rect(x)

    @staticmethod
    def _x_from_y_on_eq(y_target: float, y_eq: Callable[[float], float],
                        x_min: float, x_max: float, tol: float = 1e-8) -> Optional[float]:
        """
        Given y_target, solve y_eq(x) = y_target on [x_min, x_max] by bisection.
        Returns None if not bracketed (shouldn’t happen with monotone eq data).
        """
        f_min = y_eq(x_min) - y_target
        f_max = y_eq(x_max) - y_target
        if f_min * f_max > 0:
            # No bracket
            return None
        # Bisection
        a, b = x_min, x_max
        for _ in range(200):
            c = 0.5 * (a + b)
            fc = y_eq(c) - y_target
            if abs(fc) < tol:
                return c
            if f_min * fc <= 0:
                b = c
                f_max = fc
            else:
                a = c
                f_min = fc
        return 0.5 * (a + b)

    @staticmethod
    def _solve_scalar(f: Callable[[float], float], lo: float, hi: float,
                      tol: float = 1e-10, maxit: int = 200) -> float:
        """
        Robust bisection for continuous root on [lo, hi].
        If no sign change, will expand interval inwardly and try secant fallback.
        """
        flo, fhi = f(lo), f(hi)
        # If no bracket, try a simple secant fallback
        if flo * fhi > 0:
            x0, x1 = lo, hi
            f0, f1 = flo, fhi
            for _ in range(maxit):
                if abs(f1 - f0) < 1e-16:
                    break
                x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
                f2 = f(x2)
                if abs(f2) < tol:
                    return x2
                x0, f0 = x1, f1
                x1, f1 = x2, f2
            # fallback mid
            return 0.5 * (lo + hi)

        a, b = lo, hi
        for _ in range(maxit):
            c = 0.5 * (a + b)
            fc = f(c)
            if abs(fc) < tol:
                return c
            if flo * fc <= 0:
                b, fhi = c, fc
            else:
                a, flo = c, fc
        return 0.5 * (a + b)
