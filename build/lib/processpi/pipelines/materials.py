# processpi/pipelines/materials.py

"""
Pipeline Materials Specifications and Properties

This module contains physical and mechanical properties of
pipeline materials commonly used in process industries.

All values are representative and may vary depending on
standards (ASME, ASTM, ISO) and manufacturer data.
"""

from typing import Dict, Any


# Dictionary of material properties
MATERIAL_PROPERTIES: Dict[str, Dict[str, Any]] = {
    "CS": {  # Carbon Steel
        "density": 7850,               # kg/m³
        "thermal_conductivity": 54,    # W/m·K
        "roughness": 0.045,            # mm
        "max_temp": 425,               # °C (approximate)
        "allowable_stress": 138,       # MPa
        "notes": "Standard carbon steel pipes, widely used in process piping."
    },
    "SS304": {  # Stainless Steel 304
        "density": 8000,               
        "thermal_conductivity": 16.2,
        "roughness": 0.015,
        "max_temp": 870,
        "allowable_stress": 137,
        "notes": "Good corrosion resistance, general chemical service."
    },
    "SS316": {  # Stainless Steel 316
        "density": 8000,
        "thermal_conductivity": 16.3,
        "roughness": 0.015,
        "max_temp": 925,
        "allowable_stress": 137,
        "notes": "Better corrosion resistance than SS304, widely used in chemical plants."
    },
    "PVC": {  # Polyvinyl Chloride
        "density": 1380,
        "thermal_conductivity": 0.19,
        "roughness": 0.0015,
        "max_temp": 60,
        "allowable_stress": 13.8,
        "notes": "Lightweight, used in water and low-pressure service."
    },
    "CPVC": {  # Chlorinated Polyvinyl Chloride
        "density": 1500,
        "thermal_conductivity": 0.14,
        "roughness": 0.0015,
        "max_temp": 90,
        "allowable_stress": 17,
        "notes": "Higher temperature resistance than PVC."
    },
    "HDPE": {  # High Density Polyethylene
        "density": 950,
        "thermal_conductivity": 0.42,
        "roughness": 0.007,
        "max_temp": 60,
        "allowable_stress": 5,
        "notes": "Corrosion resistant, flexible, low-pressure applications."
    },
    "Copper": {
        "density": 8960,
        "thermal_conductivity": 401,
        "roughness": 0.0015,
        "max_temp": 200,
        "allowable_stress": 70,
        "notes": "Excellent thermal conductivity, used in heat exchangers."
    }
}


def get_material_property(material: str, prop: str) -> Any:
    """
    Get a specific property of a pipeline material.
    
    Args:
        material (str): Material code (e.g., 'CS', 'SS316', 'PVC').
        prop (str): Property name (e.g., 'density', 'roughness').

    Returns:
        Any: Property value if found, else None.
    """
    return MATERIAL_PROPERTIES.get(material, {}).get(prop)


def get_material_data(material: str) -> Dict[str, Any]:
    """
    Get all properties for a given pipeline material.
    
    Args:
        material (str): Material code.
    
    Returns:
        dict: Dictionary of material properties.
    """
    return MATERIAL_PROPERTIES.get(material, {})

