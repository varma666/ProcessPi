# processpi/pipelines/pumps.py

from typing import Optional, Dict, Union, Any
from .base import PipelineBase
from ..units import *                   
from .standards import PUMP_EFFICIENCIES


class Pump(PipelineBase):
    """
    Represents a pump in a pipeline system.

    Attributes:
        name (str): The name of the pump.
        pump_type (str): Type of pump (e.g., 'centrifugal', 'positive_displacement').
        flow_rate (Optional[FlowRate]): Volumetric flow rate.
        head (Optional[Length]): Pump head, representing the energy added per unit
                                 weight of fluid.
        density (Density): Fluid density.
        efficiency (float): Pump efficiency (0 < η <= 1).
        inlet_pressure (Optional[Pressure]): Inlet pressure to the pump.
        outlet_pressure (Optional[Pressure]): Outlet pressure from the pump.
        start_node (Optional[Any]): The node object at the pump's inlet.
        end_node (Optional[Any]): The node object at the pump's outlet.
    """

    def __init__(
        self,
        name: str,
        pump_type: str,
        flow_rate: Optional[VolumetricFlowRate] = None,
        head: Optional[Length] = None,
        density: Optional[Density] = None,
        efficiency: Optional[float] = None,
        inlet_pressure: Optional[Pressure] = None,
        outlet_pressure: Optional[Pressure] = None,
    ):
        """
        Initializes a Pump instance.

        Args:
            name (str): A unique name for the pump.
            pump_type (str): The general type of the pump.
            flow_rate (Optional[FlowRate]): The design flow rate.
            head (Optional[Length]): The required head to be provided by the pump.
            density (Optional[Density]): The fluid density. Defaults to 1000 kg/m³.
            efficiency (Optional[float]): The pump's efficiency. Defaults to a
                                          standard value based on pump type.
            inlet_pressure (Optional[Pressure]): The pressure at the pump inlet.
            outlet_pressure (Optional[Pressure]): The pressure at the pump outlet.

        Raises:
            ValueError: If neither head nor inlet/outlet pressures are provided.
        """
        super().__init__(name)

        if head is None and (inlet_pressure is None or outlet_pressure is None):
            raise ValueError(
                "A Pump must be initialized with either 'head' or both 'inlet_pressure' and 'outlet_pressure'."
            )
        
        self.pump_type: str = pump_type
        self.flow_rate: Optional[VolumetricFlowRate] = flow_rate
        self.density: Density = density or Density(1000, "kg/m3")
        self.inlet_pressure: Optional[Pressure] = inlet_pressure
        self.outlet_pressure: Optional[Pressure] = outlet_pressure

        # Calculate head if pressures are provided, otherwise use the provided head.
        if inlet_pressure and outlet_pressure:
            dp_pa = (outlet_pressure.to("Pa").value - inlet_pressure.to("Pa").value)
            # Head H = ΔP / (ρ * g)
            calculated_head_m = dp_pa / (self.density.to("kg/m3").value * 9.81)
            self.head: Length = Length(calculated_head_m, "m")
        else:
            self.head: Optional[Length] = head or Length(0.0, "m")

        self.efficiency: float = efficiency or PUMP_EFFICIENCIES.get(pump_type, 0.7)

        # Node connections (set by the network builder)
        self.start_node: Optional[Any] = None
        self.end_node: Optional[Any] = None

    def hydraulic_power(self) -> Optional[Power]:
        """
        Calculates the hydraulic power (fluid power) delivered by the pump.
        Formula: P_h = ρ * g * Q * H
        
        Returns:
            Optional[Power]: The hydraulic power as a Power object (W), or None if
                             flow rate or head is not defined.
        """
        if self.flow_rate is None or self.head is None:
            return None
            
        g = 9.81  # m/s²
        power_W = (
            self.density.to("kg/m³").value
            * g
            * self.flow_rate.to("m³/s").value
            * self.head.to("m").value
        )
        return Power(power_W, "W")

    def brake_power(self) -> Optional[Power]:
        """
        Calculates the brake power (shaft power) required to drive the pump,
        considering its efficiency.
        Formula: P_b = P_h / η
        
        Returns:
            Optional[Power]: The brake power as a Power object (W), or None if
                             hydraulic power cannot be calculated.
        """
        hydraulic_p = self.hydraulic_power()
        if hydraulic_p is None:
            return None
        
        if self.efficiency <= 0:
            return Power(float('inf'), "W")  # Infinite power for zero efficiency
        
        brake_p_W = hydraulic_p.to("W").value / self.efficiency
        return Power(brake_p_W, "W")

    def to_dict(self) -> Dict[str, Any]:
        """
        Exports pump properties and calculations as a dictionary for reporting.
        """
        return {
            "name": self.name,
            "type": self.pump_type,
            "head": self.head.to_dict() if self.head else None,
            "flow_rate": self.flow_rate.to_dict() if self.flow_rate else None,
            "density": self.density.to_dict(),
            "efficiency": self.efficiency,
            "hydraulic_power": self.hydraulic_power().to_dict() if self.hydraulic_power() else None,
            "brake_power": self.brake_power().to_dict() if self.brake_power() else None,
            "inlet_pressure": self.inlet_pressure.to_dict() if self.inlet_pressure else None,
            "outlet_pressure": self.outlet_pressure.to_dict() if self.outlet_pressure else None,
        }

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the object."""
        return (
            f"Pump(name='{self.name}', type='{self.pump_type}', "
            f"head={self.head}, efficiency={self.efficiency})"
        )

    def calculate(self) -> Dict[str, Any]:
        """
        This method serves as a wrapper to perform calculations and return
        the results as a dictionary.
        """
        return self.to_dict()
