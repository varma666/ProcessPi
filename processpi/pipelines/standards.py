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
RECOMMENDED_VELOCITIES = {
    # ---- Generalized Categories ----
    "organic_liquids": (1.0, 2.0),
    "inorganic_liquids": (1.0, 2.5),
    "oils": (0.5, 1.5),
    "gases": (10.0, 20.0),
    "vapours": (15.0, 30.0),

    # ---- Specific Chemicals ----
    "water": (1.0, 2.5),
    "acetic_acid": (1.0, 2.0),
    "acetone": (1.0, 2.0),
    "acrylic_acid": (1.0, 2.0),
    "air": (10.0, 20.0),
    "ammonia": (8.0, 15.0),
    "benzene": (1.0, 2.0),
    "benzoic_acid": (1.0, 2.0),
    "bromine": (0.8, 1.5),
    "butane": (10.0, 18.0),
    "carbon_dioxide": (8.0, 15.0),
    "carbon_monoxide": (8.0, 15.0),
    "carbon_tetrachloride": (0.8, 1.5),
    "chlorine": (5.0, 10.0),
    "chlorobenzene": (1.0, 2.0),
    "chloroform": (0.8, 1.5),
    "chloromethane": (8.0, 15.0),
    "cyanogen": (8.0, 15.0),
    "cyclohexane": (1.0, 2.0),
    "ethane": (10.0, 20.0),
    "ethanol": (1.0, 2.0),
    "ethyl_acetate": (1.0, 2.0),
    "ethylene": (10.0, 20.0),
    "fluorine": (5.0, 10.0),
    "fluorobenzene": (1.0, 2.0),
    "formic_acid": (1.0, 2.0),
    "helium_4": (20.0, 40.0),
    "hydrogen_chloride": (8.0, 15.0),
    "hydrogen_cyanide": (8.0, 15.0),
    "hydrogen_sulfide": (8.0, 15.0),
    "methane": (10.0, 20.0),
    "methanol": (1.0, 2.0),
    "neon": (15.0, 30.0),
    "nitrogen": (10.0, 20.0),
    "nitrous_oxide": (8.0, 15.0),
    "nitric_oxide": (8.0, 15.0),
    "oxygen": (10.0, 20.0),
    "ozone": (8.0, 15.0),
    "phenol": (1.0, 2.0),
    "propane": (10.0, 18.0),
    "propionic_acid": (1.0, 2.0),
    "styrene": (1.0, 2.0),
    "sulfur_dioxide": (8.0, 15.0),
    "toluene": (1.0, 2.0),
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
# 🔹 Pump Efficiencies
# --------------------------
PUMP_EFFICIENCIES = {
    "centrifugal_single_stage": 0.70,     # Typical 65-75%
    "centrifugal_multistage": 0.80,       # Typical 75-85%
    "vertical_turbine": 0.82,             # Typical 80-85%
    "gear_pump": 0.75,                    # Typical 70-80%
    "screw_pump": 0.80,                   # Typical 75-85%
    "diaphragm_pump": 0.60,               # Typical 50-65%
    "peristaltic_pump": 0.55,             # Typical 50-60%
    "progressive_cavity_pump": 0.75,      # Typical 70-80%
    "reciprocating_piston_pump": 0.85,    # Typical 80-90%
    "axial_flow_pump": 0.75,              # Typical 70-80%
    "mixed_flow_pump": 0.78,              # Typical 75-80%
    "magnetic_drive_pump": 0.65,          # Typical 60-70%
    "regenerative_turbine_pump": 0.55,    # Typical 50-60%
    "jet_pump": 0.35,                     # Typical 30-40%
    "hand_pump": 0.20,                    # Very low efficiency
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
    Returns recommended velocity (m/s) for a given chemical or general service.

    Args:
        service (str): Chemical name or general category (lowercase, underscores for spaces)

    Returns:
        float or tuple: Recommended velocity (m/s) as single value or range.
    """
    key = service.strip().lower().replace(" ", "_")
    return RECOMMENDED_VELOCITIES.get(key, None)

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
