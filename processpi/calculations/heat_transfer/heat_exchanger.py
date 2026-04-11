from __future__ import annotations

from ..base import CalculationBase
from ...units import HeatFlow, HeatTransferCoefficient, Pressure


class SensibleHeatDuty(CalculationBase):
    """Q = m * Cp * (Tin - Tout)."""

    def validate_inputs(self):
        required = ["mass_flow_rate", "specific_heat", "t_in", "t_out"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        m = self._get_value(self.inputs["mass_flow_rate"], "mass_flow_rate")
        cp = self._get_value(self.inputs["specific_heat"], "specific_heat")
        t_in = self._get_value(self.inputs["t_in"], "t_in")
        t_out = self._get_value(self.inputs["t_out"], "t_out")
        return HeatFlow(abs(m * cp * (t_in - t_out)), "W")


class LatentHeatDuty(CalculationBase):
    """Q = m * lambda."""

    def validate_inputs(self):
        required = ["mass_flow_rate", "latent_heat"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        m = self._get_value(self.inputs["mass_flow_rate"], "mass_flow_rate")
        latent = self._get_value(self.inputs["latent_heat"], "latent_heat")
        return HeatFlow(abs(m * latent), "W")


class KernNusselt(CalculationBase):
    """Nu = 0.023 * Re^0.8 * Pr^n."""

    def validate_inputs(self):
        required = ["reynolds", "prandtl"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        re = self._get_value(self.inputs["reynolds"], "reynolds")
        pr = self._get_value(self.inputs["prandtl"], "prandtl")
        n = self.inputs.get("n", 0.4)
        return 0.023 * (re ** 0.8) * (pr ** n)


class ConvectiveCoefficient(CalculationBase):
    """h = Nu * k / D."""

    def validate_inputs(self):
        required = ["nusselt", "thermal_conductivity", "characteristic_diameter"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        nu = self._get_value(self.inputs["nusselt"], "nusselt")
        k = self._get_value(self.inputs["thermal_conductivity"], "thermal_conductivity")
        d = self._get_value(self.inputs["characteristic_diameter"], "characteristic_diameter")
        return HeatTransferCoefficient((nu * k) / d, "W/m2K")


class DarcyPressureDrop(CalculationBase):
    """dP = f * (L / D) * (rho * v^2 / 2)."""

    def validate_inputs(self):
        required = ["friction_factor", "length", "diameter", "density", "velocity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        f = self._get_value(self.inputs["friction_factor"], "friction_factor")
        length = self._get_value(self.inputs["length"], "length")
        diameter = self._get_value(self.inputs["diameter"], "diameter")
        rho = self._get_value(self.inputs["density"], "density")
        vel = self._get_value(self.inputs["velocity"], "velocity")
        return Pressure(f * (length / diameter) * (rho * vel * vel / 2.0), "Pa")


class ReynoldsFromProperties(CalculationBase):
    """Re = rho * v * D / mu."""

    def validate_inputs(self):
        required = ["density", "velocity", "diameter", "viscosity"]
        for key in required:
            if key not in self.inputs:
                raise ValueError(f"Missing required input: {key}")

    def calculate(self):
        rho = self._get_value(self.inputs["density"], "density")
        vel = self._get_value(self.inputs["velocity"], "velocity")
        dia = self._get_value(self.inputs["diameter"], "diameter")
        mu = self._get_value(self.inputs["viscosity"], "viscosity")
        return (rho * vel * dia) / mu
