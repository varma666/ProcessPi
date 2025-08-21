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
PIPE_SCHEDULES: Dict[Diameter, Dict[str, Tuple[Length, Diameter]]] = {
    Diameter(0.25,"in"): {  # 1/4"
        "40": (Length(2.77,"mm"), Diameter(6.35,"mm")),
        "80": (Length(3.02,"mm"), Diameter(5.49,"mm")),
    },
    Diameter(0.5,"in"): {  # 1/2"
        "40": (Length(2.77,"mm"), Diameter(15.8,"mm")),
        "80": (Length(3.73,"mm"), Diameter(13.8,"mm")),
    },
    Diameter(0.75,"in"): {  # 3/4"
        "40": (Length(2.87,"mm"), Diameter(20.9,"mm")),
        "80": (Length(3.91,"mm"), Diameter(18.8,"mm")),
    },
    Diameter(1,"in"): {  # 1"
        "40": (Length(3.38,"mm"), Diameter(26.6,"mm")),
        "80": (Length(4.55,"mm"), Diameter(24.3,"mm")),
    },
    Diameter(1.5,"in"): {  # 1-1/2"
        "40": (Length(3.68,"mm"), Diameter(40.9,"mm")),
        "80": (Length(5.08,"mm"), Diameter(37.5,"mm")),
    },
    Diameter(2,"in"): {  # 2"
        "40": (Length(3.91,"mm"), Diameter(52.5,"mm")),
        "80": (Length(5.54,"mm"), Diameter(49.3,"mm")),
    },
    Diameter(2.5,"in"): {  # 2-1/2"
        "40": (Length(5.16,"mm"), Diameter(62.7,"mm")),
        "80": (Length(7.01,"mm"), Diameter(59.5,"mm")),
    },
    Diameter(3,"in"): {  # 3"
        "40": (Length(5.49,"mm"), Diameter(77.9,"mm")),
        "80": (Length(7.62,"mm"), Diameter(73.7,"mm")),
    },
    Diameter(4,"in"): {  # 4"
        "40": (Length(6.02,"mm"), Diameter(102.3,"mm")),
        "80": (Length(8.56,"mm"), Diameter(97.2,"mm")),
    },
    Diameter(5,"in"): {  # 5"
        "40": (Length(6.55,"mm"), Diameter(127.3,"mm")),
        "80": (Length(9.53,"mm"), Diameter(121.9,"mm")),
    },
    Diameter(6,"in"): {  # 6"
        "40": (Length(7.11,"mm"), Diameter(154.1,"mm")),
        "80": (Length(10.97,"mm"), Diameter(146.3,"mm")),
    },
    Diameter(8,"in"): {  # 8"
        "40": (Length(8.18,"mm"), Diameter(202.7,"mm")),
        "80": (Length(12.70,"mm"), Diameter(193.7,"mm")),
    },
    Diameter(10,"in"): {  # 10"
        "40": (Length(9.27,"mm"), Diameter(254.5,"mm")),
        "80": (Length(15.09,"mm"), Diameter(242.8,"mm")),
    },
    Diameter(12,"in"): {  # 12"
        "40": (Length(10.31,"mm"), Diameter(303.2,"mm")),
        "80": (Length(17.48,"mm"), Diameter(289.1,"mm")),
    },
    Diameter(14,"in"): {  # 14"
        "40": (Length(11.13,"mm"), Diameter(333.4,"mm")),
        "80": (Length(19.05,"mm"), Diameter(318.5,"mm")),
    },
    Diameter(15,"in"): {  # 15"
        "40": (Length(11.91,"mm"), Diameter(359.1,"mm")),
        "80": (Length(19.05,"mm"), Diameter(338.9,"mm")),
    },
    Diameter(20,"in"): {  # 20"
        "40": (Length(12.70,"mm"), Diameter(508.0,"mm")),
        "80": (Length(23.01,"mm"), Diameter(482.6,"mm")),
    },
    Diameter(25,"in"): {  # 25"
        "40": (Length(15.88,"mm"), Diameter(635.0,"mm")),
        "80": (Length(24.61,"mm"), Diameter(584.2,"mm")),
    },
    Diameter(30,"in"): {  # 30"
        "40": (Length(15.88,"mm"), Diameter(762.0,"mm")),
        "80": (Length(27.78,"mm"), Diameter(730.0,"mm")),
    },
    Diameter(35,"in"): {  # 35"
        "40": (Length(19.05,"mm"), Diameter(889.0,"mm")),
        "80": (Length(28.58,"mm"), Diameter(850.0,"mm")),
    },
    Diameter(40,"in"): {  # 40"
        "40": (Length(19.05,"mm"), Diameter(1016.0,"mm")),
        "80": (Length(31.75,"mm"), Diameter(965.0,"mm")),
    },
    Diameter(45,"in"): {  # 45"
        "40": (Length(19.05,"mm"), Diameter(1143.0,"mm")),
        "80": (Length(31.75,"mm"), Diameter(1092.0,"mm")),
    },
    Diameter(50,"in"): {  # 50"
        "40": (Length(19.05,"mm"), Diameter(1270.0,"mm")),
        "80": (Length(31.75,"mm"), Diameter(1219.0,"mm")),
    },
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
# 🔹 K Factors
# --------------------------

K_FACTORS = {
    "gate_valve_open": 0.15,            # fully open
    "gate_valve_3_4_closed": 17.0,
    "gate_valve_half_closed": 9.5,
    "globe_valve_open": 10.0,
    "angle_valve_open": 5.0,
    "plug_valve_open": 0.4,
    "elbow_90_standard": 0.9,
    "elbow_45_long": 0.35,
    "elbow_45_short": 0.4,
    "return_bend_medium": 2.2,
    "coupling_union": 0.08,
    "tee_straight": 0.6,
    "tee_branch": 1.8,                  # flow through branch
    "sudden_contraction": 0.42,
    "sudden_expansion": 1.0,            # (1 - (d/D)^2)^2, here avg
    "entrance_sharp": 0.5,
    "entrance_rounded": 0.04,
    "exit": 1.0,
}

# --------------------------
# 🔹 Utility Functions
# --------------------------
def get_internal_diameter(
    nominal_diameter: Diameter, schedule: str
):
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
