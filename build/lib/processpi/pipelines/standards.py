# processpi/pipelines/standards.py

from typing import Dict, Tuple, Optional, Union, List, Any
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
- Utility functions for data retrieval
- Economic parameters for cost estimation
"""

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
# Updated to a list of Diameter objects
STANDARD_SIZES: List[Diameter] = [
    Diameter(0.125, "in"), Diameter(0.25, "in"), Diameter(0.375, "in"), Diameter(0.5, "in"),
    Diameter(0.75, "in"), Diameter(1, "in"), Diameter(1.25, "in"), Diameter(1.5, "in"),
    Diameter(2, "in"), Diameter(2.5, "in"), Diameter(3, "in"), Diameter(3.5, "in"),
    Diameter(4, "in"), Diameter(5, "in"), Diameter(6, "in"), Diameter(8, "in"),
    Diameter(10, "in"), Diameter(12, "in"), Diameter(14, "in"), Diameter(16, "in"),
    Diameter(18, "in"), Diameter(20, "in"), Diameter(22, "in"), Diameter(24, "in"),
    Diameter(26, "in"), Diameter(28, "in"), Diameter(30, "in"), Diameter(32, "in"),
    Diameter(34, "in"), Diameter(36, "in"), Diameter(38, "in"), Diameter(40, "in"),
    Diameter(42, "in"), Diameter(44, "in"), Diameter(46, "in"), Diameter(48, "in"),
]

# --------------------------
# 🔹 Pipe Size Database (OD and wall thickness)
# --------------------------
# Nominal Pipe Size (in) -> (outside diameter mm, {schedule: wall thickness mm})
#
# Carbon and alloy steel schedules (S5 ... S160, STD, XS, XXS) are Table 1 of
# ASME B36.10M-2015. Stainless schedules (5S, 10S, 40S, 80S) are Table 1 of
# ASME B36.19M-2004 (R2015) and are listed separately because 10S for NPS 14
# through 22, 40S for NPS 12, and 80S for NPS 10 and 12 are NOT the same as the
# matching B36.10M schedule. Both standards tabulate these values in
# millimetres, so nothing here is a conversion from inches.
#
# Outside diameters are the B36.10M SI values; B36.19M rounds two of them
# differently (NPS 10: 273.1 mm, NPS 12: 323.9 mm).
_PIPE_DIMENSIONS_MM: Dict[float, Tuple[float, Dict[str, float]]] = {
    0.125: (10.3, {  # NPS 1/8
        "S10": 1.24, "10S": 1.24, "S30": 1.45, "S40": 1.73, "40S": 1.73,
        "STD": 1.73, "S80": 2.41, "80S": 2.41, "XS": 2.41,
    }),
    0.25: (13.7, {  # NPS 1/4
        "S10": 1.65, "10S": 1.65, "S30": 1.85, "S40": 2.24, "40S": 2.24,
        "STD": 2.24, "S80": 3.02, "80S": 3.02, "XS": 3.02,
    }),
    0.375: (17.1, {  # NPS 3/8
        "S10": 1.65, "10S": 1.65, "S30": 1.85, "S40": 2.31, "40S": 2.31,
        "STD": 2.31, "S80": 3.2, "80S": 3.2, "XS": 3.2,
    }),
    0.5: (21.3, {  # NPS 1/2
        "S5": 1.65, "5S": 1.65, "S10": 2.11, "10S": 2.11, "S30": 2.41,
        "S40": 2.77, "40S": 2.77, "STD": 2.77, "S80": 3.73, "80S": 3.73,
        "XS": 3.73, "S160": 4.78, "XXS": 7.47,
    }),
    0.75: (26.7, {  # NPS 3/4
        "S5": 1.65, "5S": 1.65, "S10": 2.11, "10S": 2.11, "S30": 2.41,
        "S40": 2.87, "40S": 2.87, "STD": 2.87, "S80": 3.91, "80S": 3.91,
        "XS": 3.91, "S160": 5.56, "XXS": 7.82,
    }),
    1: (33.4, {  # NPS 1
        "S5": 1.65, "5S": 1.65, "S10": 2.77, "10S": 2.77, "S30": 2.9,
        "S40": 3.38, "40S": 3.38, "STD": 3.38, "S80": 4.55, "80S": 4.55,
        "XS": 4.55, "S160": 6.35, "XXS": 9.09,
    }),
    1.25: (42.2, {  # NPS 1 1/4
        "S5": 1.65, "5S": 1.65, "S10": 2.77, "10S": 2.77, "S30": 2.97,
        "S40": 3.56, "40S": 3.56, "STD": 3.56, "S80": 4.85, "80S": 4.85,
        "XS": 4.85, "S160": 6.35, "XXS": 9.7,
    }),
    1.5: (48.3, {  # NPS 1 1/2
        "S5": 1.65, "5S": 1.65, "S10": 2.77, "10S": 2.77, "S30": 3.18,
        "S40": 3.68, "40S": 3.68, "STD": 3.68, "S80": 5.08, "80S": 5.08,
        "XS": 5.08, "S160": 7.14, "XXS": 10.15,
    }),
    2: (60.3, {  # NPS 2
        "S5": 1.65, "5S": 1.65, "S10": 2.77, "10S": 2.77, "S30": 3.18,
        "S40": 3.91, "40S": 3.91, "STD": 3.91, "S80": 5.54, "80S": 5.54,
        "XS": 5.54, "S160": 8.74, "XXS": 11.07,
    }),
    2.5: (73, {  # NPS 2 1/2
        "S5": 2.11, "5S": 2.11, "S10": 3.05, "10S": 3.05, "S30": 4.78,
        "S40": 5.16, "40S": 5.16, "STD": 5.16, "S80": 7.01, "80S": 7.01,
        "XS": 7.01, "S160": 9.53, "XXS": 14.02,
    }),
    3: (88.9, {  # NPS 3
        "S5": 2.11, "5S": 2.11, "S10": 3.05, "10S": 3.05, "S30": 4.78,
        "S40": 5.49, "40S": 5.49, "STD": 5.49, "S80": 7.62, "80S": 7.62,
        "XS": 7.62, "S160": 11.13, "XXS": 15.24,
    }),
    3.5: (101.6, {  # NPS 3 1/2
        "S5": 2.11, "5S": 2.11, "S10": 3.05, "10S": 3.05, "S30": 4.78,
        "S40": 5.74, "40S": 5.74, "STD": 5.74, "S80": 8.08, "80S": 8.08,
        "XS": 8.08,
    }),
    4: (114.3, {  # NPS 4
        "S5": 2.11, "5S": 2.11, "S10": 3.05, "10S": 3.05, "S30": 4.78,
        "S40": 6.02, "40S": 6.02, "STD": 6.02, "S80": 8.56, "80S": 8.56,
        "XS": 8.56, "S120": 11.13, "S160": 13.49, "XXS": 17.12,
    }),
    5: (141.3, {  # NPS 5
        "S5": 2.77, "5S": 2.77, "S10": 3.4, "10S": 3.4, "S40": 6.55,
        "40S": 6.55, "STD": 6.55, "S80": 9.53, "80S": 9.53, "XS": 9.53,
        "S120": 12.7, "S160": 15.88, "XXS": 19.05,
    }),
    6: (168.3, {  # NPS 6
        "S5": 2.77, "5S": 2.77, "S10": 3.4, "10S": 3.4, "S40": 7.11,
        "40S": 7.11, "STD": 7.11, "S80": 10.97, "80S": 10.97, "XS": 10.97,
        "S120": 14.27, "S160": 18.26, "XXS": 21.95,
    }),
    8: (219.1, {  # NPS 8
        "S5": 2.77, "5S": 2.77, "S10": 3.76, "10S": 3.76, "S20": 6.35,
        "S30": 7.04, "S40": 8.18, "40S": 8.18, "STD": 8.18, "S60": 10.31,
        "S80": 12.7, "80S": 12.7, "XS": 12.7, "S100": 15.09, "S120": 18.26,
        "S140": 20.62, "S160": 23.01, "XXS": 22.23,
    }),
    10: (273, {  # NPS 10
        "S5": 3.4, "5S": 3.4, "S10": 4.19, "10S": 4.19, "S20": 6.35,
        "S30": 7.8, "S40": 9.27, "40S": 9.27, "STD": 9.27, "S60": 12.7,
        "S80": 15.09, "80S": 12.7, "XS": 12.7, "S100": 18.26, "S120": 21.44,
        "S140": 25.4, "S160": 28.58, "XXS": 25.4,
    }),
    12: (323.8, {  # NPS 12
        "S5": 3.96, "5S": 3.96, "S10": 4.57, "10S": 4.57, "S20": 6.35,
        "S30": 8.38, "S40": 10.31, "40S": 9.53, "STD": 9.53, "S60": 14.27,
        "S80": 17.48, "80S": 12.7, "XS": 12.7, "S100": 21.44, "S120": 25.4,
        "S140": 28.58, "S160": 33.32, "XXS": 25.4,
    }),
    14: (355.6, {  # NPS 14
        "S5": 3.96, "5S": 3.96, "S10": 6.35, "10S": 4.78, "S20": 7.92,
        "S30": 9.53, "S40": 11.13, "40S": 9.53, "STD": 9.53, "S60": 15.09,
        "S80": 19.05, "80S": 12.7, "XS": 12.7, "S100": 23.83, "S120": 27.79,
        "S140": 31.75, "S160": 35.71,
    }),
    16: (406.4, {  # NPS 16
        "S5": 4.19, "5S": 4.19, "S10": 6.35, "10S": 4.78, "S20": 7.92,
        "S30": 9.53, "S40": 12.7, "40S": 9.53, "STD": 9.53, "S60": 16.66,
        "S80": 21.44, "80S": 12.7, "XS": 12.7, "S100": 26.19, "S120": 30.96,
        "S140": 36.53, "S160": 40.49,
    }),
    18: (457, {  # NPS 18
        "S5": 4.19, "5S": 4.19, "S10": 6.35, "10S": 4.78, "S20": 7.92,
        "S30": 11.13, "S40": 14.27, "40S": 9.53, "STD": 9.53, "S60": 19.05,
        "S80": 23.83, "80S": 12.7, "XS": 12.7, "S100": 29.36, "S120": 34.93,
        "S140": 39.67, "S160": 45.24,
    }),
    20: (508, {  # NPS 20
        "S5": 4.78, "5S": 4.78, "S10": 6.35, "10S": 5.54, "S20": 9.53,
        "S30": 12.7, "S40": 15.09, "40S": 9.53, "STD": 9.53, "S60": 20.62,
        "S80": 26.19, "80S": 12.7, "XS": 12.7, "S100": 32.54, "S120": 38.1,
        "S140": 44.45, "S160": 50.01,
    }),
    22: (559, {  # NPS 22
        "S5": 4.78, "5S": 4.78, "S10": 6.35, "10S": 5.54, "S20": 9.53,
        "S30": 12.7, "STD": 9.53, "S60": 22.23, "S80": 28.58, "XS": 12.7,
        "S100": 34.93, "S120": 41.28, "S140": 47.63, "S160": 53.98,
    }),
    24: (610, {  # NPS 24
        "S5": 5.54, "5S": 5.54, "S10": 6.35, "10S": 6.35, "S20": 9.53,
        "S30": 14.27, "S40": 17.48, "40S": 9.53, "STD": 9.53, "S60": 24.61,
        "S80": 30.96, "80S": 12.7, "XS": 12.7, "S100": 38.89, "S120": 46.02,
        "S140": 52.37, "S160": 59.54,
    }),
    26: (660, {  # NPS 26
        "S10": 7.92, "S20": 12.7, "STD": 9.53, "XS": 12.7,
    }),
    28: (711, {  # NPS 28
        "S10": 7.92, "S20": 12.7, "S30": 15.88, "STD": 9.53, "XS": 12.7,
    }),
    30: (762, {  # NPS 30
        "S5": 6.35, "5S": 6.35, "S10": 7.92, "10S": 7.92, "S20": 12.7,
        "S30": 15.88, "STD": 9.53, "XS": 12.7,
    }),
    32: (813, {  # NPS 32
        "S10": 7.92, "S20": 12.7, "S30": 15.88, "S40": 17.48, "STD": 9.53,
        "XS": 12.7,
    }),
    34: (864, {  # NPS 34
        "S10": 7.92, "S20": 12.7, "S30": 15.88, "S40": 17.48, "STD": 9.53,
        "XS": 12.7,
    }),
    36: (914, {  # NPS 36
        "S10": 7.92, "S20": 12.7, "S30": 15.88, "S40": 19.05, "STD": 9.53,
        "XS": 12.7,
    }),
    38: (965, {  # NPS 38
        "STD": 9.53, "XS": 12.7,
    }),
    40: (1016, {  # NPS 40
        "STD": 9.53, "XS": 12.7,
    }),
    42: (1067, {  # NPS 42
        "STD": 9.53, "XS": 12.7,
    }),
    44: (1118, {  # NPS 44
        "STD": 9.53, "XS": 12.7,
    }),
    46: (1168, {  # NPS 46
        "STD": 9.53, "XS": 12.7,
    }),
    48: (1219, {  # NPS 48
        "STD": 9.53, "XS": 12.7,
    }),
}

# Nominal Diameter -> { Schedule -> (Wall Thickness, OD, ID) }
PIPE_SCHEDULES: Dict[Diameter, Dict[str, Tuple[Length, Diameter, Diameter]]] = {
    Diameter(nps, "in"): {
        schedule: (
            Length(thickness, "mm"),
            Diameter(od, "mm"),
            Diameter(od - 2 * thickness, "mm"),
        )
        for schedule, thickness in schedules.items()
    }
    for nps, (od, schedules) in _PIPE_DIMENSIONS_MM.items()
}


def _check_pipe_schedule_table() -> None:
    """
    Guards the two ways this table has gone wrong before: a thickness copied
    into the neighbouring schedule column, and a bore that cannot exist.

    Raises:
        ValueError: If a nominal size has a non-increasing wall thickness across
            the schedule sequence, or a wall thickness at or beyond the radius.
    """
    sequence = ("S5", "S10", "S20", "S30", "S40", "S60", "S80",
                "S100", "S120", "S140", "S160")
    for nps, (od, schedules) in _PIPE_DIMENSIONS_MM.items():
        listed = [(s, schedules[s]) for s in sequence if s in schedules]
        for (lower, t_lower), (upper, t_upper) in zip(listed, listed[1:]):
            if t_upper <= t_lower:
                raise ValueError(
                    f"NPS {nps}: wall thickness does not increase from {lower} "
                    f"({t_lower} mm) to {upper} ({t_upper} mm)"
                )
        for schedule, thickness in schedules.items():
            if od - 2 * thickness <= 0:
                raise ValueError(
                    f"NPS {nps} schedule {schedule}: wall thickness {thickness} "
                    f"mm leaves no bore in a {od} mm outside diameter"
                )


_check_pipe_schedule_table()

# --------------------------
# 🔹 Recommended Fluid Velocities (m/s)
# --------------------------
RECOMMENDED_VELOCITIES = {
    "organic_liquid": (1.8, 2.0),
    "inorganic_liquid": (1.2, 1.8),
    "oil": (1.8, 2.0),
    "gas": (15.0, 30.0),
    "vapour": (15.0, 30.0),
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
# 🔹 Equivalent Lengths & K Factors
# --------------------------
EQUIVALENT_LENGTHS = {
    "gate_valve": 8, "globe_valve": 340, "angle_valve": 55, "ball_valve": 3,
    "plug_valve_straightway": 18, "plug_valve_3_way_through_flow": 30,
    "plug_valve_branch_flow": 90, "swing_check_valve": 100, "lift_check_valve": 600,
    "standard_elbow_90_deg": 30, "standard_elbow_45_deg": 16, "long_radius_90_deg": 16,
    "standard_tee_through_flow": 20, "standard_tee_through_branch": 60,
    "miter_bends_alpha_0": 2, "miter_bends_alpha_30": 8, "miter_bends_alpha_60": 25,
    "miter_bends_alpha_90": 60
}

K_FACTORS = {
    "gate_valve": 0.15, "globe_valve": 10.0, "angle_valve": 5.0, "ball_valve": 0.05,
    "plug_valve_straightway": 0.4, "plug_valve_3_way_through_flow": 0.6,
    "plug_valve_branch_flow": 1.8, "swing_check_valve": 2.0, "lift_check_valve": 10.0,
    "standard_elbow_90_deg": 0.9, "standard_elbow_45_deg": 0.4, "long_radius_90_deg": 0.9,
    "standard_tee_through_flow": 0.6, "standard_tee_through_branch": 1.8,
    "miter_bends_alpha_0": 0.04, "miter_bends_alpha_30": 0.16, "miter_bends_alpha_60": 0.5,
    "miter_bends_alpha_90": 1.2, "sudden_contraction": 0.42, "sudden_expansion": 1.0,
    "entrance_sharp": 0.5, "entrance_rounded": 0.04, "exit": 1.0,
}

# --------------------------
# 🔹 Pump Efficiencies
# --------------------------
PUMP_EFFICIENCIES = {
    "centrifugal_single_stage": 0.70,
    "centrifugal_multistage": 0.80,
    "vertical_turbine": 0.82,
    "gear_pump": 0.75,
    "screw_pump": 0.80,
    "diaphragm_pump": 0.60,
    "peristaltic_pump": 0.55,
    "progressive_cavity_pump": 0.75,
    "reciprocating_piston_pump": 0.85,
    "axial_flow_pump": 0.75,
    "mixed_flow_pump": 0.78,
    "magnetic_drive_pump": 0.65,
    "regenerative_turbine_pump": 0.55,
    "jet_pump": 0.35,
    "hand_pump": 0.20,
}

# --------------------------
# 🔹 Cost Data
# --------------------------
# These are representative, for a real application they would come from a database
# or a more complex function based on material, pressure rating, etc.
# Cost per unit mass of pipe material (e.g., USD per kg)
PIPE_MATERIAL_COST_KG: Dict[str, float] = {
    "CS": 1.5,
    "SS": 4.0,
    "PVC": 1.0,
    "Copper": 10.0,
}
# Cost per joint (e.g., for welding)
INSTALLATION_COST_PER_JOINT: Dict[str, float] = {
    "CS": 50.0,
    "SS": 80.0,
    "PVC": 20.0,
    "Copper": 60.0,
}
# Pump cost based on power (e.g., USD/kW)
PUMP_COST_PER_POWER: Dict[str, float] = {
    "centrifugal": 400.0,
    "positive_displacement": 600.0,
    "other": 500.0,
}

# --------------------------
# 🔹 Utility Functions
# --------------------------
def get_internal_diameter(
    nominal_diameter: Diameter, schedule: str = "STD"
) -> Optional[Diameter]:
    """Returns internal diameter for a given nominal diameter and schedule."""
    if nominal_diameter not in PIPE_SCHEDULES:
        return None
    return PIPE_SCHEDULES[nominal_diameter].get(schedule, (None, None, None))[2]

def get_thickness(nominal_diameter: Diameter, schedule: str = "STD") -> Optional[Length]:
    """Returns wall thickness for a given nominal diameter and schedule."""
    if nominal_diameter not in PIPE_SCHEDULES:
        return None
    return PIPE_SCHEDULES[nominal_diameter].get(schedule, (None, None, None))[0]

def get_roughness(material: str) -> Variable:
    """Returns roughness for given material. Defaults if not found."""
    roughness_mm = ROUGHNESS.get(material, ROUGHNESS["Other"])
    return Variable(roughness_mm, "mm")

def get_recommended_velocity(service: str) -> Optional[Union[float, Tuple[float, float]]]:
    """
    Returns recommended velocity (m/s) for a given chemical or general service.
    """
    key = service.strip().lower().replace(" ", "_")
    return RECOMMENDED_VELOCITIES.get(key, None)

def get_nearest_diameter(calculated_diameter: Diameter) -> Diameter:
    """
    Returns the nearest standard nominal diameter for a given calculated diameter.
    """
    nearest = min(STANDARD_SIZES, key=lambda x: abs(x.value - calculated_diameter.value))
    return nearest

def get_standard_pipe_data(
    nominal_diameter: Diameter, schedule: str = "STD"
) -> Dict[str, Union[Length, Diameter, None]]:
    """
    Returns a dictionary of standard pipe properties for a given nominal size and schedule.
    """
    data = PIPE_SCHEDULES.get(nominal_diameter, {}).get(schedule, (None, None, None))
    return {
        "nominal_diameter": nominal_diameter,
        "wall_thickness": data[0],
        "outer_diameter": data[1],
        "internal_diameter": data[2],
    }

def get_k_factor(fitting_type: str) -> float:
    """
    Retrieve the standard K-factor (loss coefficient) for a given fitting type.
    """
    return K_FACTORS.get(fitting_type.lower(), 0.0)

def list_available_pipe_diameters() -> List[Diameter]:
    """
    Returns a list of all available standard nominal pipe diameters.
    """
    return STANDARD_SIZES

def get_next_standard_nominal(diameter_m: float) -> Optional[Tuple[Diameter, dict]]:
    """
    Finds the next standard nominal size >= given diameter (inner diameter basis).
    If no larger diameter is found, returns the largest available.
    """
    target_mm = diameter_m
    last_candidate = None
    for nominal, schedules in PIPE_SCHEDULES.items():
        if "STD" in schedules:
            _, _, id_mm = schedules["STD"]
            last_candidate = (nominal, schedules["STD"])
            if id_mm.value >= target_mm:
                return nominal, schedules["STD"]
    
    # If no larger size was found, return the largest one
    return last_candidate

def get_previous_standard_nominal(nominal_diameter: Diameter) -> Optional[Diameter]:
    """
    Finds the previous standard nominal size in the sorted list.
    """
    try:
        idx = STANDARD_SIZES.index(nominal_diameter)
        if idx > 0:
            return STANDARD_SIZES[idx - 1]
    except ValueError:
        pass
    return None

def get_next_next_standard_nominal(nominal_diameter: Diameter) -> Optional[Diameter]:
    """
    Finds the next-next standard nominal size in the sorted list.
    """
    try:
        idx = STANDARD_SIZES.index(nominal_diameter)
        if idx < len(STANDARD_SIZES) - 1:
            return STANDARD_SIZES[idx + 1]
    except ValueError:
        pass
    return None

def get_standard_diameters_list() -> List[Diameter]:
    """Returns a sorted list of standard nominal diameters."""
    return sorted(list(PIPE_SCHEDULES.keys()), key=lambda d: d.value)


from typing import Optional

def get_equivalent_length(fitting_type: str) -> Optional[float]:
    """
    Return the equivalent length multiplier (Le/D) for a fitting type.
    """
    return EQUIVALENT_LENGTHS.get(fitting_type.lower())


def get_k_factor(
    fitting_type: str,
    reynolds_number: Optional[float] = None,
    relative_roughness: Optional[float] = None,
    diameter: Optional[float] = None,
) -> Optional[float]:
    """
    Return the K-factor (resistance coefficient) for a fitting type.
    Includes logic for Reynolds number-dependent fittings.
    
    Args:
        fitting_type: The type of fitting.
        reynolds_number: Reynolds number of the flow (for fittings where K depends on Re).
        relative_roughness: Pipe roughness divided by diameter (not always used).
        diameter: Pipe internal diameter in meters.

    Returns:
        The K-factor as a float, or None if not found.
    """
    
    # 1. Look up a simple K-factor from the K_FACTORS dictionary
    k_factor_value = K_FACTORS.get(fitting_type.lower())
    
    if k_factor_value is not None:
        return k_factor_value

    # 2. Fallback to calculating K from equivalent length
    le_d_ratio = EQUIVALENT_LENGTHS.get(fitting_type.lower())
    if le_d_ratio is not None and reynolds_number is not None and relative_roughness is not None:
        # This part assumes you have a ColebrookWhite function or similar
        # to calculate the friction factor 'f'
        f = ColebrookWhite(reynolds_number, relative_roughness).calculate()
        return f * le_d_ratio
    
    # Return None if no method yields a value
    return None

def get_nominal_dia_from_internal_dia(internal_diameter: Diameter, schedule: str = "STD") -> Optional[Diameter]:
    """
    Finds the nominal diameter of a pipe given its internal diameter and schedule.

    This function performs a reverse lookup in the PIPE_SCHEDULES data. It iterates
    through all nominal diameters and calculates the corresponding internal diameter
    for a given schedule. It returns the first nominal diameter that matches the
    input internal diameter.

    Args:
        internal_diameter (Diameter): The internal diameter of the pipe.
        schedule (str): The pipe schedule (e.g., "STD", "40", "80").

    Returns:
        Optional[Diameter]: The nominal diameter, or None if no match is found.
    """
    # Use a small tolerance for floating-point comparisons
    TOLERANCE = 1e-6 

    # Iterate through each nominal diameter in the standards data
    for nom_dia, schedules in PIPE_SCHEDULES.items():
        # Check if the requested schedule exists for the current nominal diameter
        if schedule in schedules:
            # The internal diameter is the third value in the tuple
            data = schedules[schedule]
            if data[2] is not None:
                calculated_internal_dia = data[2]
                
                # Convert both diameters to a base unit (meters) for comparison
                if abs(internal_diameter.to('m').value - calculated_internal_dia.to('m').value) < TOLERANCE:
                    # Match found! Return the nominal diameter.
                    return nom_dia

    # No matching nominal diameter was found for the given internal diameter and schedule
    return None