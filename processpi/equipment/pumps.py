# processpi/equipment/pump.py
from ..units import Pressure, Length, Power, Density, VolumetricFlowRate
from ..streams.energy import EnergyStream
from .base import Equipment

class Pump(Equipment):
    """
    Unified Pump class:
    - Works in flowsheet mode (MaterialStream + EnergyStream)
    - Works in pipeline mode (flow_rate, head, pressures)
    """

    def __init__(
        self,
        name: str,
        pump_type: str = "centrifugal",
        efficiency: float = 0.7,
        flow_rate: VolumetricFlowRate = None,
        head: Length = None,
        density: Density = None,
        inlet_pressure: Pressure = None,
        outlet_pressure: Pressure = None,
        energy_stream: EnergyStream = None,
    ):
        super().__init__(name, inlet_ports=1, outlet_ports=1)
        self.pump_type = pump_type
        self.efficiency = efficiency
        self.flow_rate = flow_rate
        self.head = head
        self.density = density
        self.inlet_pressure = inlet_pressure
        self.outlet_pressure = outlet_pressure

        # Energy stream: auto-create if not supplied
        self.energy_stream = energy_stream or EnergyStream(name=f"{name}_duty")

    # ---------- Physics ----------
    def calc_head(self, dp: float, rho: float) -> float:
        g = 9.81
        return dp / (rho * g)

    def hydraulic_power(self, rho: float, Q: float, H: float) -> Power:
        g = 9.81
        return Power(rho * g * Q * H, "W")

    def brake_power(self, hydraulic: Power) -> Power:
        if self.efficiency <= 0:
            return Power(float("inf"), "W")
        return Power(hydraulic.to("W").value / self.efficiency, "W")

    # ---------- Simulation ----------
    def simulate(self):
        if self.inlets and self.outlets:  # Flowsheet mode
            inlet, outlet = self.inlets[0], self.outlets[0]
            dp = outlet.pressure.to("Pa").value - inlet.pressure.to("Pa").value
            rho = inlet.density().value
            Q = inlet.flow_rate.to("m3/s").value
        else:  # Pipeline mode
            if self.flow_rate is None:
                raise ValueError("Flow rate must be provided for pipeline mode.")
            if self.density is None:
                raise ValueError("Density must be provided for pipeline mode.")

            Q = self.flow_rate.to("m3/s").value
            rho = self.density.to("kg/m3").value
            if self.head:
                dp = rho * 9.81 * self.head.to("m").value
            elif self.inlet_pressure and self.outlet_pressure:
                dp = self.outlet_pressure.to("Pa").value - self.inlet_pressure.to("Pa").value
            else:
                raise ValueError("Either head or pressures must be provided in pipeline mode.")

        # Head and power
        H = self.calc_head(dp, rho)
        hydraulic = self.hydraulic_power(rho, Q, H)
        brake = self.brake_power(hydraulic)

        # Log energy duty
        self.energy_stream.record(duty=brake.to("W").value, tag="PumpDuty", equipment=self.name)

        return {
            "name": self.name,
            "pump_type": self.pump_type,
            "flow_rate": Q,
            "head": H,
            "hydraulic_power": hydraulic.to("kW"),
            "brake_power": brake.to("kW"),
            "efficiency": self.efficiency,
        }

    def __repr__(self):
        return f"Pump(name={self.name}, type={self.pump_type}, eff={self.efficiency})"
