# processpi/components/nozzle.py
from ..units import Pressure, VolumetricFlowRate

class Nozzle:
    def __init__(self, name: str, cv: float):
        self.name = name
        self.cv = cv

    def pressure_drop_at_flow(self, q: VolumetricFlowRate) -> Pressure:
        # Simplified formula: dP = (Q / Cv)^2 * constant (depends on units)
        # Using a more general form: dP = k * Q^2
        # where k is a constant determined by the nozzle's Cv value.
        # For this example, we'll model k as a simple constant for simplicity.
        # A more robust model would be dP = rho * (Q / (Cd * A))^2 / 2
        # We'll use a simpler form for demonstration purposes.
        k = (1 / self.cv)**2
        return Pressure(k * q.value**2, 'Pa')
