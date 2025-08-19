# processpi/pipelines/selection.py

"""
Pipeline Material Selection Module

This module provides logic for selecting appropriate
pipeline materials based on design conditions such as
temperature, pressure, and corrosion requirements.

Uses data from materials.py
"""

from typing import Dict, Any, List
from .materials import MATERIAL_PROPERTIES


class MaterialSelector:
    """
    Class for selecting suitable pipeline materials.
    """

    def __init__(self, design_temp: float, design_pressure: float, corrosive: bool = False):
        """
        Initialize material selector with design parameters.

        Args:
            design_temp (float): Design temperature in °C.
            design_pressure (float): Design pressure in bar.
            corrosive (bool): Whether the fluid is corrosive.
        """
        self.design_temp = design_temp
        self.design_pressure = design_pressure
        self.corrosive = corrosive

    def filter_materials(self) -> List[str]:
        """
        Filter materials that can withstand design conditions.

        Returns:
            list: Suitable material codes.
        """
        suitable = []
        for material, props in MATERIAL_PROPERTIES.items():
            max_temp = props.get("max_temp", 0)
            allowable_stress = props.get("allowable_stress", 0)

            # Simple selection logic
            if self.design_temp <= max_temp:
                # Convert MPa stress to bar (1 MPa = 10 bar approx)
                if self.design_pressure <= allowable_stress * 10:
                    if self.corrosive:
                        if "SS" in material or material in ["HDPE", "CPVC"]:
                            suitable.append(material)
                    else:
                        suitable.append(material)
        return suitable

    def recommend_material(self) -> Dict[str, Any]:
        """
        Recommend the most suitable material based on design conditions.

        Returns:
            dict: Recommended material data.
        """
        suitable = self.filter_materials()

        if not suitable:
            return {"message": "No suitable material found for given conditions."}

        # Prefer stainless steel in corrosive service
        if self.corrosive:
            for pref in ["SS316", "SS304", "HDPE", "CPVC"]:
                if pref in suitable:
                    return {"material": pref, **MATERIAL_PROPERTIES[pref]}

        # Otherwise pick carbon steel first if allowed
        if "CS" in suitable:
            return {"material": "CS", **MATERIAL_PROPERTIES["CS"]}

        # Fallback: return the first suitable option
        mat = suitable[0]
        return {"material": mat, **MATERIAL_PROPERTIES[mat]}


# Example usage
if __name__ == "__main__":
    selector = MaterialSelector(design_temp=150, design_pressure=15, corrosive=True)
    recommendation = selector.recommend_material()
    print("Recommended Material:", recommendation)
