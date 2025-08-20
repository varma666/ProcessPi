# processpi/pipelines/standards.py
from ..units import *

"""
Pipeline Standards Module
-------------------------
Contains standard reference data for process pipelines:
- Pipe nominal sizes
- Schedules and wall thickness
- Internal diameter lookup
- Material roughness values
- Recommended fluid velocities
"""

from typing import Dict, Tuple, Optional, Union, List

# --------------------------
# 🔹 Roughness (mm)
# --------------------------
ROUGHNESS: Dict[str, float] = {
    "CS": 0.045,        # Carbon Steel
    "SS": 0.015,        # Stainless Steel
    "PVC": 0.0015,      # Polyvinyl Chloride
    "Copper": 0.0015,
    "Concrete": 0.3,
    "Glass": 0.001,
    "Other": 0.05,      # Default
}

# --------------------------
# 🔹 Pipe Standard Sizes (in)
# --------------------------

STANDARD_SIZES = [Diameter(0.25,"in"),
                  Diameter(0.5,"in"),
                  Diameter(0.75,"in"),
                  Diameter(1,"in"),
                  Diameter(1.5,"in"),
                  Diameter(2,"in"),
                  Diameter(2.5,"in"),
                  Diameter(3,"in"),
                  Diameter(4,"in"),
                  Diameter(5,"in"),
                  Diameter(6,"in"),
                  Diameter(8,"in"),
                  Diameter(10,"in"),
                  Diameter(12,"in"),
                  Diameter(14,"in"),
                  Diameter(15,"in"),
                  Diameter(20,"in"),
                  Diameter(25,"in"),
                  Diameter(30,"in"),
                  Diameter(35,"in"),
                  Diameter(40,"in"),
                  Diameter(45,"in"),
                  Diameter(50,"in")]

# --------------------------
# 🔹 Pipe Size Database
# Nominal Diameter (mm) → { Schedule → (Wall Thickness mm, ID mm) }
# --------------------------
PIPE_SCHEDULES: Dict[int, Dict[str, Tuple[float, float]]] = {
    25: {   # 1" pipe
        "40": (3.38, 21.3),   # (thickness, ID)
        "80": (4.55, 20.2),
    },
    50: {   # 2" pipe
        "40": (3.91, 52.5),
        "80": (5.54, 50.3),
    },
    100: {  # 4" pipe
        "40": (6.02, 102.3),
        "80": (8.56, 97.2),
    },
    150: {  # 6" pipe
        "40": (7.11, 154.1),
        "80": (10.97, 146.3),
    },
    200: {  # 8" pipe
        "40": (8.18, 202.7),
        "80": (12.70, 193.7),
    },
    # 🔹 Extend as required (up to 48” or DN1200)
}

# --------------------------
# 🔹 Recommended Fluid Velocities (m/s)
# --------------------------
RECOMMENDED_VELOCITIES: Dict[str, Union[Tuple[float, float], float]] = {
    "Water - Pump suction": (0.3, 1.5),
    "Water - Pump discharge": (2.0, 3.0),
    "Water - Average service": (1.0, 2.5),

    "Steam - 0 to 2 atm g, saturated": (20, 30),
    "Steam - 2 to 10 atm g, saturated": (30, 50),
    "Steam - Superheated <10 atm g": (20, 50),
    "Steam - Superheated >10 atm g": (30, 75),

    "Vacuum lines": (100, 125),

    "Air - 0 to 2 atm g": 20,
    "Air - >2 atm g or above": 30,

    "Ammonia - Liquid": 1.8,
    "Ammonia - Gas": 30,

    "Organic liquids and oils": (1.8, 2.0),
    "Natural gas": (25, 35),

    "Chlorine - Liquid": 1.5,
    "Chlorine - Gas": (10, 25),

    "Hydrochloric acid - Liquid": 1.5,
    "Hydrochloric acid - Gas": 10,

    "Inorganic liquids": (1.2, 1.8),
    "Inorganic gases and vapours": (15, 30),
}
# --------------------------
# 🔹 Equivalent Lengths Equivalent Length / Diameter
# --------------------------

EQUIVALENT_LENGTHS = {
    "gate_valve_open": (7, 10),          # fully open
    "gate_valve_3_4_closed": (800, 1100),
    "gate_valve_half_closed": (190, 290),
    "globe_valve_open": (330, 480),
    "angle_valve_open": (165, 220),
    "plug_valve_open": 18,
    "elbow_90_standard": 30,
    "elbow_45_long": 5.8,
    "elbow_45_short": 8.0,
    "return_bend_medium": (39, 56),
    "coupling_union": 0,                 # negligible
    "tee_straight": 22,
}
# --------------------------
# 🔹 Utility Functions
# --------------------------
def get_internal_diameter(
    nominal_diameter: int, schedule: str
) -> Optional[float]:
    """Returns internal diameter for a given nominal diameter and schedule."""
    if nominal_diameter not in PIPE_SCHEDULES:
        return None
    return PIPE_SCHEDULES[nominal_diameter].get(schedule, (None, None))[1]


def get_thickness(
    nominal_diameter: int, schedule: str
) -> Optional[float]:
    """Returns wall thickness for a given nominal diameter and schedule."""
    if nominal_diameter not in PIPE_SCHEDULES:
        return None
    return PIPE_SCHEDULES[nominal_diameter].get(schedule, (None, None))[0]


def get_roughness(material: str) -> float:
    """Returns roughness for given material. Defaults if not found."""
    return ROUGHNESS.get(material, ROUGHNESS["Other"])


def get_recommended_velocity(service: str) -> Optional[Union[float, Tuple[float, float]]]:
    """
    Returns recommended velocity (m/s) for a given service type.
    Can be a single value or a range (tuple).
    """
    return RECOMMENDED_VELOCITIES.get(service, None)

def get_nearest_diameter(calculated_diameter: Diameter) -> Diameter:
    """
    Returns the nearest standard diameter for a given calculated diameter.
    if calculated_diameter not in STANDARD_SIZES:
        return calculated_diameter

    """
    
    # Find the nearest standard diameter
    nearest = min(STANDARD_SIZES, key=lambda x: abs(x.value - calculated_diameter.value))
    #print(f"Nearest standard diameter for {calculated_diameter.value} mm is {nearest.value} mm")
    #print(type(nearest))
    return nearest
