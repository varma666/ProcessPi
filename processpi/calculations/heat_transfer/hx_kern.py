from __future__ import annotations

import math

from ..base import CalculationBase
from ...units import HeatFlow, HeatTransferCoefficient, Pressure


class SensibleDuty(CalculationBase):
    def validate_inputs(self):
        for key in ("m_dot", "cp", "t_in", "t_out"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        m = self._get_value(self.inputs["m_dot"], "m_dot")
        cp = self._get_value(self.inputs["cp"], "cp")
        t_in = self._get_value(self.inputs["t_in"], "t_in")
        t_out = self._get_value(self.inputs["t_out"], "t_out")
        return HeatFlow(abs(m * cp * (t_in - t_out)), "W")


class LatentDuty(CalculationBase):
    def validate_inputs(self):
        for key in ("m_dot", "latent_heat"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        m = self._get_value(self.inputs["m_dot"], "m_dot")
        latent = self._get_value(self.inputs["latent_heat"], "latent_heat")
        return HeatFlow(abs(m * latent), "W")


class Reynolds(CalculationBase):
    def validate_inputs(self):
        for key in ("density", "velocity", "diameter", "viscosity"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        rho = self._get_value(self.inputs["density"], "density")
        v = self._get_value(self.inputs["velocity"], "velocity")
        d = self._get_value(self.inputs["diameter"], "diameter")
        mu = self._get_value(self.inputs["viscosity"], "viscosity")
        return (rho * v * d) / mu


class DittusBoelter(CalculationBase):
    def validate_inputs(self):
        for key in ("reynolds", "prandtl"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        re = self._get_value(self.inputs["reynolds"], "reynolds")
        pr = self._get_value(self.inputs["prandtl"], "prandtl")
        n = self.inputs.get("n", 0.4)
        return 0.023 * re**0.8 * pr**n

class KernShellNu(CalculationBase):
    def validate_inputs(self):
        for key in ("reynolds", "prandtl"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        re = self._get_value(self.inputs["reynolds"], "reynolds")
        pr = self._get_value(self.inputs["prandtl"], "prandtl")
        return 0.36 * re**0.55 * pr**(1 / 3)


class ConvectiveH(CalculationBase):
    def validate_inputs(self):
        for key in ("nusselt", "k", "diameter"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        nu = self._get_value(self.inputs["nusselt"], "nusselt")
        k = self._get_value(self.inputs["k"], "k")
        d = self._get_value(self.inputs["diameter"], "diameter")
        return HeatTransferCoefficient((nu * k) / d, "W/m2K")


class TubeCountFromArea(CalculationBase):
    def validate_inputs(self):
        for key in ("area", "tube_od", "tube_length"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        area = self._get_value(self.inputs["area"], "area")
        d_o = self._get_value(self.inputs["tube_od"], "tube_od")
        l_t = self._get_value(self.inputs["tube_length"], "tube_length")
        return max(1, math.ceil(area / (math.pi * d_o * l_t)))


class ShellDiameterEstimate(CalculationBase):
    def validate_inputs(self):
        for key in ("tube_count", "tube_pitch"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        n_t = self._get_value(self.inputs["tube_count"], "tube_count")
        p_t = self._get_value(self.inputs["tube_pitch"], "tube_pitch")
        return 0.637 * p_t * (n_t ** 0.5)


class DarcyDrop(CalculationBase):
    def validate_inputs(self):
        for key in ("f", "length", "diameter", "density", "velocity"):
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        f = self._get_value(self.inputs["f"], "f")
        l = self._get_value(self.inputs["length"], "length")
        d = self._get_value(self.inputs["diameter"], "diameter")
        rho = self._get_value(self.inputs["density"], "density")
        v = self._get_value(self.inputs["velocity"], "velocity")
        return Pressure(f * (l / d) * rho * v * v / 2.0, "Pa")
