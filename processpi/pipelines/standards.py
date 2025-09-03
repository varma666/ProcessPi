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
    Diameter(0.25,"in"), Diameter(0.5,"in"), Diameter(0.75,"in"), Diameter(1,"in"),
    Diameter(1.5,"in"), Diameter(2,"in"), Diameter(2.5,"in"), Diameter(3,"in"),
    Diameter(3.5,"in"), Diameter(4,"in"), Diameter(5,"in"), Diameter(6,"in"),
    Diameter(8,"in"), Diameter(10,"in"), Diameter(12,"in"), Diameter(14,"in"),
    Diameter(16,"in"), Diameter(18,"in"), Diameter(20,"in"), Diameter(22,"in"),
    Diameter(24,"in"), Diameter(26,"in"), Diameter(28,"in"), Diameter(30,"in"),
    Diameter(32,"in"), Diameter(34,"in"), Diameter(36,"in"), Diameter(50,"in")
]

# --------------------------
# 🔹 Pipe Size Database (OD and ID)
# Nominal Diameter (in) -> { Schedule -> (Wall Thickness mm, OD mm, ID mm) }
# --------------------------
# The pipe schedule database has been updated to include the OD explicitly
PIPE_SCHEDULES: Dict[Diameter, Dict[str, Tuple[Length, Diameter, Diameter]]] = {
    Diameter(0.125, "in"): {
        "5S": (Length(1.2, "mm"), Diameter(10.29, "mm"), Diameter(10.29 - 2 * 1.2, "mm")),
        "STD": (Length(1.73, "mm"), Diameter(10.29, "mm"), Diameter(10.29 - 2 * 1.73, "mm")),
        "XS": (Length(2.41, "mm"), Diameter(10.29, "mm"), Diameter(10.29 - 2 * 2.41, "mm")),
        "80S": (Length(2.41, "mm"), Diameter(10.29, "mm"), Diameter(10.29 - 2 * 2.41, "mm")),
    },
    # ... (rest of the database entries for other diameters)
    # The full database from the user's prompt is a bit too long to include here,
    # but the structure is shown above and should be replicated for all diameters.
    # The key change is adding the outer diameter (OD) to the tuple.
    Diameter(0.25, "in"): {
        "5S": (Length(1.7, "mm"), Diameter(13.72, "mm"), Diameter(13.72 - 2 * 1.7, "mm")),
        "STD": (Length(2.24, "mm"), Diameter(13.72, "mm"), Diameter(13.72 - 2 * 2.24, "mm")),
        "XS": (Length(3.02, "mm"), Diameter(13.72, "mm"), Diameter(13.72 - 2 * 3.02, "mm")),
        "80S": (Length(3.02, "mm"), Diameter(13.72, "mm"), Diameter(13.72 - 2 * 3.02, "mm")),
    },
    Diameter(0.375, "in"): {
        "5S": (Length(1.7, "mm"), Diameter(17.15, "mm"), Diameter(17.15 - 2 * 1.7, "mm")),
        "STD": (Length(2.31, "mm"), Diameter(17.15, "mm"), Diameter(17.15 - 2 * 2.31, "mm")),
        "XS": (Length(3.2, "mm"), Diameter(17.15, "mm"), Diameter(17.15 - 2 * 3.2, "mm")),
        "80S": (Length(3.2, "mm"), Diameter(17.15, "mm"), Diameter(17.15 - 2 * 3.2, "mm")),
    },
    Diameter(0.5, "in"): {
        "STD": (Length(2.8, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 2.8, "mm")),
        "5S": (Length(1.7, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 1.7, "mm")),
        "10S": (Length(2.1, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 2.1, "mm")),
        "S40": (Length(2.77, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 2.77, "mm")),
        "XS": (Length(3.73, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 3.73, "mm")),
        "80S": (Length(3.73, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 3.73, "mm")),
        "S120": (Length(4.78, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 4.78, "mm")),
        "XXS": (Length(7.47, "mm"), Diameter(21.34, "mm"), Diameter(21.34 - 2 * 7.47, "mm")),
    },
    Diameter(0.75, "in"): {
        "STD": (Length(2.9, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 2.9, "mm")),
        "5S": (Length(1.7, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 1.7, "mm")),
        "10S": (Length(2.1, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 2.1, "mm")),
        "S40": (Length(2.87, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 2.87, "mm")),
        "XS": (Length(3.91, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 3.91, "mm")),
        "80S": (Length(3.91, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 3.91, "mm")),
        "S120": (Length(5.56, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 5.56, "mm")),
        "XXS": (Length(7.82, "mm"), Diameter(26.67, "mm"), Diameter(26.67 - 2 * 7.82, "mm")),
    },
    Diameter(1.0, "in"): {
        "STD": (Length(3.4, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 3.4, "mm")),
        "5S": (Length(1.7, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 1.7, "mm")),
        "10S": (Length(2.8, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 2.8, "mm")),
        "S40": (Length(3.38, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 3.38, "mm")),
        "XS": (Length(4.55, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 4.55, "mm")),
        "80S": (Length(4.55, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 4.55, "mm")),
        "S120": (Length(6.35, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 6.35, "mm")),
        "XXS": (Length(9.09, "mm"), Diameter(33.4, "mm"), Diameter(33.4 - 2 * 9.09, "mm")),
    },
    Diameter(1.25, "in"): {
        "STD": (Length(3.6, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 3.6, "mm")),
        "5S": (Length(1.7, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 1.7, "mm")),
        "10S": (Length(2.8, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 2.8, "mm")),
        "S40": (Length(3.56, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 3.56, "mm")),
        "XS": (Length(4.85, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 4.85, "mm")),
        "80S": (Length(4.85, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 4.85, "mm")),
        "S120": (Length(6.35, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 6.35, "mm")),
        "XXS": (Length(9.7, "mm"), Diameter(42.16, "mm"), Diameter(42.16 - 2 * 9.7, "mm")),
    },
    Diameter(1.5, "in"): {
        "STD": (Length(3.7, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 3.7, "mm")),
        "5S": (Length(1.7, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 1.7, "mm")),
        "10S": (Length(2.8, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 2.8, "mm")),
        "S40": (Length(3.68, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 3.68, "mm")),
        "XS": (Length(5.08, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 5.08, "mm")),
        "80S": (Length(5.08, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 5.08, "mm")),
        "S120": (Length(7.14, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 7.14, "mm")),
        "XXS": (Length(10.2, "mm"), Diameter(48.26, "mm"), Diameter(48.26 - 2 * 10.2, "mm")),
    },
    Diameter(2.0, "in"): {
        "STD": (Length(3.9, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 3.9, "mm")),
        "5S": (Length(1.7, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 1.7, "mm")),
        "10S": (Length(2.8, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 2.8, "mm")),
        "S40": (Length(3.91, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 3.91, "mm")),
        "XS": (Length(5.54, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 5.54, "mm")),
        "80S": (Length(5.54, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 5.54, "mm")),
        "S120": (Length(9.74, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 9.74, "mm")),
        "XXS": (Length(11.1, "mm"), Diameter(60.33, "mm"), Diameter(60.33 - 2 * 11.1, "mm")),
    },
    Diameter(2.5, "in"): {
        "STD": (Length(5.2, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 5.2, "mm")),
        "5S": (Length(2.1, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 2.1, "mm")),
        "10S": (Length(3.1, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 3.1, "mm")),
        "S40": (Length(5.16, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 5.16, "mm")),
        "XS": (Length(7.01, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 7.01, "mm")),
        "80S": (Length(7.01, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 7.01, "mm")),
        "S120": (Length(9.53, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 9.53, "mm")),
        "XXS": (Length(14, "mm"), Diameter(73.03, "mm"), Diameter(73.03 - 2 * 14, "mm")),
    },
    Diameter(3.0, "in"): {
        "STD": (Length(5.5, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 5.5, "mm")),
        "5S": (Length(2.1, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 2.1, "mm")),
        "10S": (Length(3.1, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 3.1, "mm")),
        "S40": (Length(5.49, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 5.49, "mm")),
        "XS": (Length(7.62, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 7.62, "mm")),
        "80S": (Length(7.62, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 7.62, "mm")),
        "S120": (Length(11.1, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 11.1, "mm")),
        "XXS": (Length(15.2, "mm"), Diameter(88.9, "mm"), Diameter(88.9 - 2 * 15.2, "mm")),
    },
    Diameter(3.5, "in"): {
        "STD": (Length(5.7, "mm"), Diameter(101.6, "mm"), Diameter(101.6 - 2 * 5.7, "mm")),
        "5S": (Length(2.1, "mm"), Diameter(101.6, "mm"), Diameter(101.6 - 2 * 2.1, "mm")),
        "10S": (Length(3.1, "mm"), Diameter(101.6, "mm"), Diameter(101.6 - 2 * 3.1, "mm")),
        "S40": (Length(5.74, "mm"), Diameter(101.6, "mm"), Diameter(101.6 - 2 * 5.74, "mm")),
        "XS": (Length(8.08, "mm"), Diameter(101.6, "mm"), Diameter(101.6 - 2 * 8.08, "mm")),
        "80S": (Length(8.08, "mm"), Diameter(101.6, "mm"), Diameter(101.6 - 2 * 8.08, "mm")),
    },
    Diameter(4.0, "in"): {
        "STD": (Length(6, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 6, "mm")),
        "5S": (Length(2.1, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 2.1, "mm")),
        "10S": (Length(3.1, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 3.1, "mm")),
        "S40": (Length(6.02, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 6.02, "mm")),
        "XS": (Length(8.56, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 8.56, "mm")),
        "80S": (Length(8.56, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 8.56, "mm")),
        "S100": (Length(11.1, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 11.1, "mm")),
        "S120": (Length(13.5, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 13.5, "mm")),
        "S160": (Length(17.1, "mm"), Diameter(114.3, "mm"), Diameter(114.3 - 2 * 17.1, "mm")),
    },
    Diameter(5.0, "in"): {
        "STD": (Length(6.6, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 6.6, "mm")),
        "5S": (Length(2.8, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 2.8, "mm")),
        "10S": (Length(3.4, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 3.4, "mm")),
        "S40": (Length(6.55, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 6.55, "mm")),
        "XS": (Length(9.53, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 9.53, "mm")),
        "80S": (Length(9.53, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 9.53, "mm")),
        "S100": (Length(12.7, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 12.7, "mm")),
        "S120": (Length(15.9, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 15.9, "mm")),
        "S160": (Length(19.1, "mm"), Diameter(141.3, "mm"), Diameter(141.3 - 2 * 19.1, "mm")),
    },
    Diameter(6.0, "in"): {
        "STD": (Length(7.1, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 7.1, "mm")),
        "5S": (Length(2.8, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 2.8, "mm")),
        "10S": (Length(3.4, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 3.4, "mm")),
        "S40": (Length(7.11, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 7.11, "mm")),
        "XS": (Length(10.97, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 10.97, "mm")),
        "80S": (Length(11, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 11, "mm")),
        "S100": (Length(14.3, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 14.3, "mm")),
        "S120": (Length(18.3, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 18.3, "mm")),
        "S160": (Length(22, "mm"), Diameter(168.3, "mm"), Diameter(168.3 - 2 * 22, "mm")),
    },
    Diameter(8.0, "in"): {
        "STD": (Length(8.2, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 8.2, "mm")),
        "5S": (Length(2.8, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 2.8, "mm")),
        "10S": (Length(3.8, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 3.8, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 6.4, "mm")),
        "S20": (Length(8.18, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 8.18, "mm")),
        "S40": (Length(10.3, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 10.3, "mm")),
        "S60": (Length(12.7, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 12.7, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 12.7, "mm")),
        "S100": (Length(15.1, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 15.1, "mm")),
        "S120": (Length(19.3, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 19.3, "mm")),
        "S140": (Length(20.6, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 20.6, "mm")),
        "S160": (Length(23, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 23, "mm")),
        "XXS": (Length(22.2, "mm"), Diameter(219.1, "mm"), Diameter(219.1 - 2 * 22.2, "mm")),
    },
    Diameter(10.0, "in"): {
        "STD": (Length(9.3, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 9.3, "mm")),
        "5S": (Length(3.4, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 3.4, "mm")),
        "10S": (Length(4.2, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 4.2, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 6.4, "mm")),
        "S20": (Length(9.27, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 9.27, "mm")),
        "S40": (Length(12.7, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 12.7, "mm")),
        "S60": (Length(12.7, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 12.7, "mm")),
        "XS": (Length(15.1, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 15.1, "mm")),
        "80S": (Length(15.1, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 15.1, "mm")),
        "S120": (Length(19.3, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 19.3, "mm")),
        "S140": (Length(21.4, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 21.4, "mm")),
        "S160": (Length(25.4, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 25.4, "mm")),
        "XXS": (Length(28.6, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 * 28.6, "mm")),
    },
    Diameter(12.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 9.5, "mm")),
        "5S": (Length(4, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 4, "mm")),
        "10S": (Length(4.6, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 4.6, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 6.4, "mm")),
        "S20": (Length(10.3, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 10.3, "mm")),
        "S40": (Length(14.3, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 14.3, "mm")),
        "S60": (Length(12.7, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 12.7, "mm")),
        "XS": (Length(17.5, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 17.5, "mm")),
        "80S": (Length(17.5, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 17.5, "mm")),
        "S120": (Length(21.4, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 21.4, "mm")),
        "S140": (Length(25.4, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 25.4, "mm")),
        "S160": (Length(28.6, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 28.6, "mm")),
        "XXS": (Length(33.3, "mm"), Diameter(323.9, "mm"), Diameter(323.9 - 2 * 33.3, "mm")),
    },
    Diameter(14.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 9.5, "mm")),
        "5S": (Length(4, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 4, "mm")),
        "10S": (Length(4.8, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 4.8, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 6.4, "mm")),
        "S20": (Length(7.9, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 7.9, "mm")),
        "S40": (Length(11.1, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 11.1, "mm")),
        "S60": (Length(15.1, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 15.1, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 12.7, "mm")),
        "S100": (Length(19.1, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 19.1, "mm")),
        "S120": (Length(23.8, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 23.8, "mm")),
        "S140": (Length(27.8, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 27.8, "mm")),
        "S160": (Length(31.8, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 31.8, "mm")),
        "XXS": (Length(35.7, "mm"), Diameter(355.6, "mm"), Diameter(355.6 - 2 * 35.7, "mm")),
    },
    Diameter(16.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 9.5, "mm")),
        "5S": (Length(4.2, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 4.2, "mm")),
        "10S": (Length(4.8, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 4.8, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 6.4, "mm")),
        "S20": (Length(7.9, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 7.9, "mm")),
        "S40": (Length(12.7, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 12.7, "mm")),
        "S60": (Length(16.7, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 16.7, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 12.7, "mm")),
        "S100": (Length(21.4, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 21.4, "mm")),
        "S120": (Length(26.2, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 26.2, "mm")),
        "S140": (Length(31, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 31, "mm")),
        "S160": (Length(36.5, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 36.5, "mm")),
        "XXS": (Length(40.5, "mm"), Diameter(406.4, "mm"), Diameter(406.4 - 2 * 40.5, "mm")),
    },
    Diameter(18.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 9.5, "mm")),
        "5S": (Length(4.2, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 4.2, "mm")),
        "10S": (Length(4.8, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 4.8, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 6.4, "mm")),
        "S20": (Length(7.9, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 7.9, "mm")),
        "S40": (Length(14.3, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 14.3, "mm")),
        "S60": (Length(19.1, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 19.1, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 12.7, "mm")),
        "S100": (Length(23.8, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 23.8, "mm")),
        "S120": (Length(29.4, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 29.4, "mm")),
        "S140": (Length(34.9, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 34.9, "mm")),
        "S160": (Length(39.7, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 39.7, "mm")),
        "XXS": (Length(45.2, "mm"), Diameter(457.2, "mm"), Diameter(457.2 - 2 * 45.2, "mm")),
    },
    Diameter(20.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 9.5, "mm")),
        "5S": (Length(4.8, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 4.8, "mm")),
        "10S": (Length(5.5, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 5.5, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 6.4, "mm")),
        "S20": (Length(9.5, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 9.5, "mm")),
        "S40": (Length(15.1, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 15.1, "mm")),
        "S60": (Length(20.6, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 20.6, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 12.7, "mm")),
        "S100": (Length(26.2, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 26.2, "mm")),
        "S120": (Length(32.5, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 32.5, "mm")),
        "S140": (Length(38.1, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 38.1, "mm")),
        "S160": (Length(44.5, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 44.5, "mm")),
        "XXS": (Length(50, "mm"), Diameter(508, "mm"), Diameter(508 - 2 * 50, "mm")),
    },
    Diameter(22.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 9.5, "mm")),
        "5S": (Length(4.8, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 4.8, "mm")),
        "10S": (Length(5.5, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 5.5, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 6.4, "mm")),
        "S20": (Length(9.5, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 9.5, "mm")),
        "S60": (Length(22.2, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 22.2, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 12.7, "mm")),
        "S100": (Length(28.6, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 28.6, "mm")),
        "S120": (Length(34.9, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 34.9, "mm")),
        "S140": (Length(41.3, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 41.3, "mm")),
        "S160": (Length(47.6, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 47.6, "mm")),
        "XXS": (Length(54, "mm"), Diameter(558.8, "mm"), Diameter(558.8 - 2 * 54, "mm")),
    },
    Diameter(24.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 9.5, "mm")),
        "5S": (Length(5.5, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 5.5, "mm")),
        "10S": (Length(6.4, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 6.4, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 6.4, "mm")),
        "S20": (Length(9.5, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 9.5, "mm")),
        "S40": (Length(17.5, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 17.5, "mm")),
        "S60": (Length(24.6, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 24.6, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 12.7, "mm")),
        "S100": (Length(31, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 31, "mm")),
        "S120": (Length(38.9, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 38.9, "mm")),
        "S140": (Length(46, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 46, "mm")),
        "S160": (Length(52.4, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 52.4, "mm")),
        "XXS": (Length(59.5, "mm"), Diameter(609.6, "mm"), Diameter(609.6 - 2 * 59.5, "mm")),
    },
    Diameter(26.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(660.4, "mm"), Diameter(660.4 - 2 * 9.5, "mm")),
        "S10": (Length(7.9, "mm"), Diameter(660.4, "mm"), Diameter(660.4 - 2 * 7.9, "mm")),
        "S20": (Length(13, "mm"), Diameter(660.4, "mm"), Diameter(660.4 - 2 * 13, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(660.4, "mm"), Diameter(660.4 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(660.4, "mm"), Diameter(660.4 - 2 * 12.7, "mm")),
    },
    Diameter(28.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(711.2, "mm"), Diameter(711.2 - 2 * 9.5, "mm")),
        "S10": (Length(7.9, "mm"), Diameter(711.2, "mm"), Diameter(711.2 - 2 * 7.9, "mm")),
        "S20": (Length(13, "mm"), Diameter(711.2, "mm"), Diameter(711.2 - 2 * 13, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(711.2, "mm"), Diameter(711.2 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(711.2, "mm"), Diameter(711.2 - 2 * 12.7, "mm")),
    },
    Diameter(30.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 9.5, "mm")),
        "5S": (Length(6.4, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 6.4, "mm")),
        "10S": (Length(7.9, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 7.9, "mm")),
        "S10": (Length(7.9, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 7.9, "mm")),
        "S20": (Length(13, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 13, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(762, "mm"), Diameter(762 - 2 * 12.7, "mm")),
    },
    Diameter(32.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(812.8, "mm"), Diameter(812.8 - 2 * 9.5, "mm")),
        "S10": (Length(7.9, "mm"), Diameter(812.8, "mm"), Diameter(812.8 - 2 * 7.9, "mm")),
        "S20": (Length(13, "mm"), Diameter(812.8, "mm"), Diameter(812.8 - 2 * 13, "mm")),
        "S40": (Length(17.5, "mm"), Diameter(812.8, "mm"), Diameter(812.8 - 2 * 17.5, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(812.8, "mm"), Diameter(812.8 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(812.8, "mm"), Diameter(812.8 - 2 * 12.7, "mm")),
    },
    Diameter(34.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(863.6, "mm"), Diameter(863.6 - 2 * 9.5, "mm")),
        "S10": (Length(7.9, "mm"), Diameter(863.6, "mm"), Diameter(863.6 - 2 * 7.9, "mm")),
        "S20": (Length(13, "mm"), Diameter(863.6, "mm"), Diameter(863.6 - 2 * 13, "mm")),
        "S40": (Length(17.5, "mm"), Diameter(863.6, "mm"), Diameter(863.6 - 2 * 17.5, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(863.6, "mm"), Diameter(863.6 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(863.6, "mm"), Diameter(863.6 - 2 * 12.7, "mm")),
    },
    Diameter(36.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(914.4, "mm"), Diameter(914.4 - 2 * 9.5, "mm")),
        "S10": (Length(7.9, "mm"), Diameter(914.4, "mm"), Diameter(914.4 - 2 * 7.9, "mm")),
        "S20": (Length(13, "mm"), Diameter(914.4, "mm"), Diameter(914.4 - 2 * 13, "mm")),
        "S40": (Length(19.1, "mm"), Diameter(914.4, "mm"), Diameter(914.4 - 2 * 19.1, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(914.4, "mm"), Diameter(914.4 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(914.4, "mm"), Diameter(914.4 - 2 * 12.7, "mm")),
    },
    Diameter(50.0, "in"): {
        "STD": (Length(9.5, "mm"), Diameter(1270.0, "mm"), Diameter(1270.0 - 2 * 9.5, "mm")),
        "5S": (Length(4.8, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 4.8, "mm")),
        "10S": (Length(5.5, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 5.5, "mm")),
        "S10": (Length(6.4, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 6.4, "mm")),
        "S20": (Length(9.5, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 9.5, "mm")),
        "S40": (Length(15.1, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 15.1, "mm")),
        "S60": (Length(20.6, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 20.6, "mm")),
        "XS": (Length(12.7, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 12.7, "mm")),
        "80S": (Length(12.7, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 12.7, "mm")),
        "S100": (Length(26.2, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 26.2, "mm")),
        "S120": (Length(32.5, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 32.5, "mm")),
        "S140": (Length(38.1, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 38.1, "mm")),
        "S160": (Length(44.5, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 44.5, "mm")),
        "XXS": (Length(50, "mm"), Diameter(1270, "mm"), Diameter(1270 - 2 * 50, "mm")),
    }
}

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