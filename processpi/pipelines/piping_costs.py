# processpi/piping_costs.py
from ..pipelines.pipes import Pipe
from ..pipelines.network import PipelineNetwork
from ..units import Length

from typing import Dict, Any, Union

class PipeCostModel:
    """
    A simple model for calculating piping system costs based on diameter, material,
    and length. Costs are in dollars per meter.
    """
    def __init__(self, cost_data: Dict[str, Dict[str, float]]):
        self._data = cost_data

    @classmethod
    def default_steel_model(cls):
        """Returns a predefined cost model for carbon steel pipes."""
        default_costs = {
            "CS": {
                "2": 50.0,
                "4": 75.0,
                "6": 120.0,
                "8": 180.0,
                "10": 250.0,
                "12": 350.0,
            }
        }
        return cls(default_costs)

    def get_pipe_cost(self, nominal_diameter: Union[str, float, int], material: str) -> float:
        """Retrieves the cost per meter for a given pipe size and material."""
        dia_str = str(int(nominal_diameter))
        return self._data.get(material, {}).get(dia_str, 0.0)

    def calculate_network_cost(self, network: PipelineNetwork) -> float:
        """Calculates the total cost of all pipes in a given network."""
        total_cost = 0.0
        pipes = network.get_all_pipes()
        for pipe in pipes:
            if pipe.nominal_diameter:
                cost_per_m = self.get_pipe_cost(pipe.nominal_diameter.to('in').value, pipe.material)
                total_cost += cost_per_m * pipe.length.to('m').value
        return total_cost
