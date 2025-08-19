# processpi/pipelines/design_rules.py

"""
Pipeline Design Rules Module

This module defines pipeline design rules inspired by industry practices 
(similar to Aspen). It does not contain calculation logic directly, 
but instead integrates functions from processpi.calculations to validate 
pipeline designs against engineering standards.

Each function acts as a design "rule" or "check".
"""

from processpi.calculations.fluids.reynolds_number import ReynoldsNumber
from processpi.calculations.fluids.friction_factor import ColebrookWhite
from processpi.calculations.fluids.flow_type import FlowType
from processpi.calculations.fluids.optimum_pipe_diameter import OptimumPipeDiameter
from processpi.calculations.pressure.drop import PressureDrop  # assumed module
from processpi.calculations.velocity import Velocity           # assumed module


def check_flow_regime(velocity: float, diameter: float, density: float, viscosity: float) -> str:
    """
    Rule: Determine if flow is laminar, transition, or turbulent.
    """
    Re = ReynoldsNumber(velocity, diameter, density, viscosity).calculate()
    return FlowType(Re).calculate()


def check_pressure_drop(flowrate: float, diameter: float, length: float, density: float, viscosity: float, roughness: float) -> float:
    """
    Rule: Calculate pressure drop across the pipeline.
    """
    return PressureDrop(flowrate, diameter, length, density, viscosity, roughness).calculate()


def check_friction_factor(Re: float, diameter: float, roughness: float) -> float:
    """
    Rule: Calculate friction factor using Colebrook-White.
    """
    return ColebrookWhite(Re, diameter, roughness).calculate()


def recommend_optimum_diameter(flowrate: float, density: float) -> float:
    """
    Rule: Recommend optimum diameter based on economic sizing correlation.
    """
    return OptimumPipeDiameter(flowrate, density).calculate()


def check_velocity_limits(velocity: float, fluid_type: str = "liquid") -> bool:
    """
    Rule: Check if velocity is within recommended design limits.

    Typical guidelines:
    - Liquids: 1–3 m/s (avoid erosion/cavitation)
    - Gases/steam: 10–20 m/s
    """
    if fluid_type.lower() == "liquid":
        return 1.0 <= velocity <= 3.0
    elif fluid_type.lower() in ["gas", "steam"]:
        return 10.0 <= velocity <= 20.0
    return False


def check_pressure_drop_limit(pressure_drop: float, limit: float = 10.0) -> bool:
    """
    Rule: Ensure pressure drop per 100 m of pipe length is within design limits (default 10 kPa/100 m).
    """
    return pressure_drop <= limit


def check_design_compliance(flowrate: float, diameter: float, length: float, density: float, viscosity: float, roughness: float, fluid_type: str = "liquid") -> dict:
    """
    Perform a complete design compliance check.
    Returns a dictionary summarizing pass/fail status of all rules.
    """
    velocity = Velocity(flowrate, diameter).calculate()
    Re = ReynoldsNumber(velocity, diameter, density, viscosity).calculate()
    flow_regime = FlowType(Re).calculate()
    friction_factor = ColebrookWhite(Re, diameter, roughness).calculate()
    pressure_drop = PressureDrop(flowrate, diameter, length, density, viscosity, roughness).calculate()
    optimum_d = OptimumPipeDiameter(flowrate, density).calculate()

    return {
        "flow_regime": flow_regime,
        "velocity_ok": check_velocity_limits(velocity, fluid_type),
        "pressure_drop_ok": check_pressure_drop_limit(pressure_drop),
        "friction_factor": friction_factor,
        "optimum_diameter_mm": optimum_d,
    }
