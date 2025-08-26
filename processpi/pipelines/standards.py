# processpi/pipelines/standards.py

from typing import Dict, Tuple, Optional, Union, List, Any
from ..units import Diameter, Length, UnitfulValue

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
        "XS": (Length(15.1, "mm"), Diameter(273.1, "mm"), Diameter(273.1 - 2 *
