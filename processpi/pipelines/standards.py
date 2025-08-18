# processpi/pipelines/standards.py

"""
Pipeline Standards Module
-------------------------
Contains standard reference data for process pipelines:
- Pipe nominal sizes
- Schedules and wall thickness
- Internal diameter lookup
- Material roughness values
"""

from typing import Dict, Tuple, Optional

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
# 🔹 Utility Functions
# --------------------------
def get_internal_diameter(
    nominal_diameter: int, schedule: str
) -> Optional[float]:
    """
    Returns internal diameter for a given nominal diameter and schedule.
    """
    if nominal_diameter not in PIPE_SCHEDULES:
        return None
    return PIPE_SCHEDULES[nominal_diameter].get(schedule, (None, None))[1]


def get_thickness(
    nominal_diameter: int, schedule: str
) -> Optional[float]:
    """
    Returns wall thickness for a given nominal diameter and schedule.
    """
    if nominal_diameter not in PIPE_SCHEDULES:
        return None
    return PIPE_SCHEDULES[nominal_diameter].get(schedule, (None, None))[0]


def get_roughness(material: str) -> float:
    """
    Returns roughness for given material. Defaults if not found.
    """
    return ROUGHNESS.get(material, ROUGHNESS["Other"])
