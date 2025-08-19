# processpi/pipelines/engine.py

from typing import Dict, Any, Type
from processpi.calculations import (
    ReynoldsNumber,
    ColebrookWhite,
    OptimumPipeDiameter,
    PressureDropDarcyWeisbach,
    VelocityFromFlow,
)
from .pipes import Pipe


class PipelineEngine:
    """
    Generic pipeline engine that orchestrates pipeline hydraulics calculations.
    
    Uses registered calculation classes from processpi.calculations to evaluate
    flow, velocity, pressure drop, etc.
    """

    def __init__(self, flowrate: float, fluid: Dict[str, Any], length: float, **kwargs):
        """
        Initialize the engine.

        Args:
            flowrate (float): Volumetric flow rate (m³/s).
            fluid (dict): Fluid properties (dict containing density, viscosity, etc.).
            length (float): Pipeline length (m).
            kwargs: Additional pipeline design parameters.
        """
        self.flowrate = flowrate
        self.fluid = fluid
        self.length = length
        self.kwargs = kwargs
        self.pipe: Pipe | None = None

    def optimize_diameter(self) -> float:
        """
        Compute optimum diameter based on flow and fluid.
        """
        opt_dia = OptimumPipeDiameter(
            flowrate=self.flowrate,
            density=self.fluid["density"]
        )
        return opt_dia.compute()

    def assign_pipe(self, material: str = "CS", schedule: str = "40") -> Pipe:
        """
        Assign a pipe with optimized diameter.
        """
        diameter = self.optimize_diameter()
        self.pipe = Pipe(
            nominal_diameter=diameter,
            schedule=schedule,
            material=material,
            length=self.length,
        )
        return self.pipe

    def calculate_velocity(self) -> float:
        """
        Calculate velocity using pipe diameter and flowrate.
        """
        if not self.pipe:
            self.assign_pipe()
        velocity_calc = VelocityFromFlow(
            flowrate=self.flowrate,
            diameter=self.pipe.internal_diameter() / 1000  # mm → m
        )
        return velocity_calc.compute()

    def calculate_reynolds(self) -> float:
        """
        Calculate Reynolds number.
        """
        velocity = self.calculate_velocity()
        re_calc = ReynoldsNumber(
            density=self.fluid["density"],
            velocity=velocity,
            diameter=self.pipe.internal_diameter() / 1000,
            viscosity=self.fluid["viscosity"],
        )
        return re_calc.compute()

    def calculate_pressure_drop(self) -> float:
        """
        Calculate pressure drop using Darcy-Weisbach.
        """
        re = self.calculate_reynolds()
        friction_calc = ColebrookWhite(
            reynolds_number=re,
            relative_roughness=self.pipe.roughness / self.pipe.internal_diameter(),
        )
        f = friction_calc.compute()

        dp_calc = PressureDropDarcyWeisbach(
            friction_factor=f,
            length=self.pipe.length,
            diameter=self.pipe.internal_diameter() / 1000,
            density=self.fluid["density"],
            velocity=self.calculate_velocity(),
        )
        return dp_calc.compute()

    def run(self) -> Dict[str, Any]:
        """
        Run full pipeline hydraulics analysis.

        Returns:
            dict: Results with diameter, velocity, Re, and ΔP.
        """
        if not self.pipe:
            self.assign_pipe()

        results = {
            "optimum_diameter_mm": self.pipe.internal_diameter(),
            "velocity_m_s": self.calculate_velocity(),
            "reynolds_number": self.calculate_reynolds(),
            "pressure_drop_Pa": self.calculate_pressure_drop(),
        }
        return results
