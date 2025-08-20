# processpi/pipelines/engine.py

from typing import Dict, Any, Type

from .standards import *
from ..components import *
from ..units import *
from ..calculations.fluids import (
    ReynoldsNumber,
    ColebrookWhite,
    OptimumPipeDiameter,
    PressureDropDarcy,
    FluidVelocity ,
    TypeOfFlow
)

from .pipes import Pipe


class PipelineEngine:
    """
    Generic pipeline engine that orchestrates pipeline hydraulics calculations.
    
    Uses registered calculation classes from processpi.calculations to evaluate
    flow, velocity, pressure drop, etc.
    """

    def __init__(self, flowrate: VolumetricFlowRate, fluid: Component, length: float, **kwargs):
        """
        Initialize the engine.

        Args:
            flowrate (VolumetricFlowRate): Volumetric flow rate (m³/s).
            fluid (Component): Fluid properties (density, viscosity, etc.).
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
            flow_rate=self.flowrate.to("m3/s"),
            density=self.fluid.density()
        )
        calculated_diameter = opt_dia.calculate()
        selected_diameter = get_nearest_diameter(calculated_diameter)
        #print(f"Calculated Optimum Diameter: {calculated_diameter}, Selected Diameter: {selected_diameter}")
        return selected_diameter

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
        velocity_calc = FluidVelocity(
            volumetric_flow_rate=self.flowrate,
            diameter=self.pipe.nominal_diameter # m
        )
        return velocity_calc.calculate()

    def calculate_reynolds(self) -> float:
        """
        Calculate Reynolds number.
        """
        velocity = self.calculate_velocity()
        re_calc = ReynoldsNumber(
            density=self.fluid.density(),
            velocity=velocity,
            diameter=self.pipe.nominal_diameter,  # m
            viscosity=self.fluid.viscosity(),
        )
        return re_calc.calculate()

    def calculate_pressure_drop(self) -> float:
        """
        Calculate pressure drop using Darcy-Weisbach.
        """
        re = self.calculate_reynolds()
        friction_calc = ColebrookWhite(
            reynolds_number=re,
            roughness=self.pipe.roughness ,
            diameter=self.pipe.nominal_diameter
        )
        f = friction_calc.calculate()

        dp_calc = PressureDropDarcy(
            friction_factor=f,
            length=self.pipe.length,
            diameter=self.pipe.nominal_diameter,  # m
            density=self.fluid.density(),
            velocity=self.calculate_velocity(),
        )
        return dp_calc.calculate()

    def run(self) -> Dict[str, Any]:
        """
        Run full pipeline hydraulics analysis.

        Returns:
            dict: Results with diameter, velocity, Re, and ΔP.
        """
        if not self.pipe:
            self.assign_pipe()

        results = {
            "optimum_diameter_in": self.pipe.nominal_diameter.to("in"),
            "velocity_m_s": self.calculate_velocity(),
            "reynolds_number": self.calculate_reynolds(),
            "pressure_drop_Pa": self.calculate_pressure_drop(),
        }
        return results
