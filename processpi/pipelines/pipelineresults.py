# processpi/pipelines/pipelineresults.py

from typing import Dict, Any, Union, List
from ..units import Pressure, UnitfulValue


class PipelineResults:
    """
    A class for managing and presenting the results of a pipeline flow
    simulation.

    This class encapsulates the raw dictionary of results from the calculation
    engine and provides methods to format and display them in a clean,
    human-readable manner, including a summary and detailed breakdown.
    """

    def __init__(self, results: Dict[str, Any]):
        """
        Initializes the PipelineResults instance.

        Args:
            results (Dict[str, Any]): The dictionary containing all
                                      calculation results from the engine.
        """
        self.results: Dict[str, Any] = results

    def __bool__(self) -> bool:
        """
        Allows the object to be evaluated as a boolean, returning True if
        there are any results and False otherwise.
        """
        return bool(self.results)

    def summary(self) -> None:
        """
        Prints a clean, human-readable summary of the last simulation run.

        This method organizes the results into logical sections for easy
        interpretation, handling different data types (e.g., plain numbers,
        UnitfulValue objects) gracefully.
        """
        if not self.results:
            print("No results available. The simulation has not been run or failed.")
            return

        print("\n=== Pipeline Summary ===")
        print(f"Network Name: {self.results.get('network_name', 'N/A')}")
        print(f"Simulation Mode: {self.results.get('mode', 'N/A').capitalize()}")

        # -------------------- High-level Network Summary --------------------
        summary_data = self.results.get("summary", {})
        if summary_data:
            print("\n--- Network Performance ---")
            
            # Use a helper function for consistent printing of UnitfulValue objects
            def print_unitful(label: str, unitful_value: Optional[UnitfulValue], precision: int):
                if unitful_value is not None:
                    # Check if the value is a UnitfulValue object or a raw number
                    if hasattr(unitful_value, "value") and hasattr(unitful_value, "unit"):
                        val_str = f"{unitful_value.value:.{precision}f}"
                        unit_str = unitful_value.unit
                        print(f"{label:<25}{val_str} {unit_str}")
                    else:
                        print(f"{label:<25}{unitful_value:.{precision}f}")
                else:
                    print(f"{label:<25}N/A")

            print_unitful("Inlet Flow Rate:", summary_data.get("inlet_flow"), 3)
            print_unitful("Outlet Flow Rate:", summary_data.get("outlet_flow"), 3)
            print_unitful("Total Pressure Drop:", summary_data.get("total_pressure_drop"), 2)
            print_unitful("Total Head Loss:", summary_data.get("total_head_loss"), 2)
            print_unitful("Total Power Required:", summary_data.get("total_power_required"), 2)
            
        # -------------------- Detailed Component Breakdown --------------------
        components_data = self.results.get("components", [])
        if components_data:
            print("\n--- Component Details ---")
            
            for component in components_data:
                comp_type = component.get("type", "N/A")
                comp_name = component.get("name", f"{comp_type.capitalize()}").ljust(15)
                
                if comp_type == "pipe":
                    length = component.get("length")
                    length_str = f"{length.value:.1f} {length.unit}" if hasattr(length, "value") else "N/A"
                    print(f"\n{comp_name} - {comp_type}")
                    print(f"  Length: {length_str:<20}")
                    self._print_component_details(component)
                
                elif comp_type == "fitting":
                    print(f"\n{comp_name} - {comp_type}")
                    print(f"  Quantity: {component.get('quantity', 1):<18}")
                    self._print_component_details(component)
                    
                elif comp_type in ["pump", "vessel", "equipment"]:
                    print(f"\n{comp_name} - {comp_type}")
                    self._print_component_details(component)

        # -------------------- ASCII Schematic --------------------
        schematic_str = self.results.get("schematic")
        if schematic_str:
            print("\n=== Network Schematic ===")
            print(schematic_str)
            
    def _print_component_details(self, component: Dict[str, Any]) -> None:
        """Helper method to print common component details consistently."""
        
        # Helper for a single line print
        def print_detail(label: str, value: Any, precision: int = 2):
            if value is not None:
                if hasattr(value, "value") and hasattr(value, "unit"):
                    val_str = f"{value.value:.{precision}f}"
                    unit_str = value.unit
                    print(f"  {label:<22}{val_str} {unit_str}")
                else:
                    print(f"  {label:<22}{value}")

        print_detail("Pressure Drop:", component.get("pressure_drop"))
        print_detail("Velocity:", component.get("velocity"))
        print_detail("Reynolds Number:", component.get("reynolds_number"), 0)
        print_detail("Friction Factor:", component.get("friction_factor"), 4)
        print_detail("Head Loss:", component.get("head_loss"))
        print_detail("Power:", component.get("power"))

    def to_dict(self) -> Dict[str, Any]:
        """Returns the raw results dictionary for programmatic access."""
        return self.results
