from __future__ import annotations

from typing import Optional, Tuple


HX_U_STANDARDS = {
    "shell_and_tube": {
        "heat_exchanger": {
            ("water", "water"): (800, 1500),
            ("organic", "organic"): (100, 300),
            ("light_oil", "light_oil"): (100, 400),
            ("heavy_oil", "heavy_oil"): (50, 300),
            ("gas_low_pressure", "gas_low_pressure"): (5, 35),
            ("gas_high_pressure", "gas_high_pressure"): (100, 300),
            ("water","organic"): (250,800),
            
        },
        "cooler": {
            ("organic", "water"): (250, 750),
            ("light_oil", "water"): (350, 700),
            ("heavy_oil", "water"): (60, 300),
            ("gas", "water"): (20, 300),
            ("gas_low_pressure", "water"): (20, 300),
            ("gas_high_pressure", "water"): (100, 300),
        },
        "heater": {
            ("steam", "water"): (1500, 4000),
            ("steam", "organic"): (500, 1000),
            ("steam", "oil"): (300, 900),
        },
        "condenser": {
            ("vapor", "water"): (700, 1500),
            ("water", "water"): (1000, 2000),
            ("water", "organic"): (600,1000),
        },
        "vaporizer": {
            ("steam", "liquid"): (900, 1500),
        },
    }
}


def get_u_range(hx_type: str, service_type: str, hot_type: str, cold_type: str) -> Optional[Tuple[float, float]]:
    data = HX_U_STANDARDS.get(hx_type, {})
    service = data.get(service_type, {})

    key = (hot_type, cold_type)
    if key in service:
        return service[key]

    key_rev = (cold_type, hot_type)
    if key_rev in service:
        return service[key_rev]

    return None

# --- DIN 28184 STANDARD DATA ---
DIN_SHELL_TUBE_STANDARD = [
    {"DN": 150, "tube_passes": 2, "Da": 0.168, "n": 14, "AS": 1.1},
    {"DN": 200, "tube_passes": 2, "Da": 0.219, "n": 26, "AS": 2.0},
    {"DN": 250, "tube_passes": 2, "Da": 0.273, "n": 44, "AS": 3.5},
    {"DN": 300, "tube_passes": 2, "Da": 0.324, "n": 66, "AS": 5.2},
    {"DN": 350, "tube_passes": 2, "Da": 0.355, "n": 76, "AS": 6.0},
    {"DN": 400, "tube_passes": 2, "Da": 0.406, "n": 106, "AS": 8.3},
    {"DN": 500, "tube_passes": 2, "Da": 0.508, "n": 180, "AS": 14.1},
    {"DN": 600, "tube_passes": 2, "Da": 0.600, "n": 258, "AS": 20.3},
    {"DN": 700, "tube_passes": 2, "Da": 0.700, "n": 364, "AS": 28.6},
    {"DN": 800, "tube_passes": 2, "Da": 0.800, "n": 484, "AS": 38.0},
    {"DN": 900, "tube_passes": 2, "Da": 0.900, "n": 622, "AS": 48.9},
    {"DN": 1000, "tube_passes": 2, "Da": 1.000, "n": 776, "AS": 61.0},
]

def select_standard_exchanger(area_required, tube_length, tube_passes,
                              hot_mdot, hot_density,
                              cold_mdot, cold_density,
                              tube_id):

    best = None
    best_score = float("inf")

    for item in DIN_SHELL_TUBE_STANDARD:
        if item["passes"] != tube_passes:
            continue

        # --- Area check ---
        area_available = item["AS"] * tube_length
        if area_available < area_required:
            continue

        tube_count = item["n"]
        shell_diameter = item["Da"]

        # --- Tube velocity ---
        area_per_tube = math.pi * tube_id**2 / 4
        tube_flow_area = tube_count / tube_passes * area_per_tube
        v_tube = (hot_mdot / hot_density) / max(tube_flow_area, 1e-12)

        # --- Shell velocity ---
        shell_area = math.pi * shell_diameter**2 / 4
        v_shell = (cold_mdot / cold_density) / max(shell_area, 1e-12)

        # --- Scoring ---
        # Penalize deviation from target velocities
        score = (
            abs(v_tube - 1.5) * 2 +   # tube importance high
            abs(v_shell - 0.5) * 1.5 +
            (area_available - area_required) / area_required
        )

        if score < best_score:
            best_score = score
            best = item

    return best
