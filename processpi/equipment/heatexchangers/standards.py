from __future__ import annotations

from typing import Optional, Tuple
import math
from processpi.pipelines.standards import RECOMMENDED_VELOCITIES

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
            ("water", "light_oil"): (200, 600),
            ("water", "heavy_oil"): (100, 350),
            ("water", "gas_low_pressure"): (100, 350),
            ("water", "gas_high_pressure"): (200, 500),
            ("organic", "light_oil"): (120, 350),
            ("organic", "heavy_oil"): (80, 280),
            ("organic", "gas_low_pressure"): (40, 180),
            ("organic", "gas_high_pressure"): (120, 300),
            ("light_oil", "heavy_oil"): (80, 220),
            ("light_oil", "gas_low_pressure"): (30, 140),
            ("light_oil", "gas_high_pressure"): (100, 250),
            ("heavy_oil", "gas_low_pressure"): (15, 90),
            ("heavy_oil", "gas_high_pressure"): (60, 200),
            
        },
        "cooler": {
            ("organic", "water"): (250, 750),
            ("light_oil", "water"): (350, 700),
            ("heavy_oil", "water"): (60, 300),
            ("gas", "water"): (20, 300),
            ("gas_low_pressure", "water"): (20, 300),
            ("gas_high_pressure", "water"): (100, 300),
            ("water", "water"): (900, 1800),
            ("organic", "organic"): (120, 320),
            ("light_oil", "organic"): (150, 400),
            ("heavy_oil", "organic"): (80, 250),
            ("gas_low_pressure", "organic"): (25, 200),
            ("gas_high_pressure", "organic"): (120, 350),
            ("gas_low_pressure", "light_oil"): (20, 160),
            ("gas_high_pressure", "light_oil"): (90, 280),
        },
        "heater": {
            ("steam", "water"): (1500, 4000),
            ("steam", "organic"): (500, 1000),
            ("steam", "oil"): (300, 900),
            ("steam", "light_oil"): (350, 950),
            ("steam", "heavy_oil"): (220, 700),
            ("hot_oil", "water"): (250, 650),
            ("hot_oil", "organic"): (180, 450),
        },
        "condenser": {
            ("vapor", "water"): (700, 1500),
            ("water", "water"): (1000, 2000),
            ("water", "organic"): (600,1000),
            ("vapor", "organic"): (350, 900),
            ("vapor", "light_oil"): (250, 750),
            ("vapor", "heavy_oil"): (120, 450),
            ("steam", "water"): (1500, 3500),
            ("steam", "organic"): (700, 1800),
        },
        "vaporizer": {
            ("steam", "liquid"): (900, 1500),
            ("steam", "water"): (1200, 3000),
            ("steam", "organic"): (600, 1400),
            ("steam", "light_oil"): (500, 1100),
            ("hot_oil", "organic"): (250, 700),
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


def get_velocity_range(component):
    hx_type = getattr(component, "hx_type", None)

    if hx_type and hx_type in RECOMMENDED_VELOCITIES:
        return RECOMMENDED_VELOCITIES[hx_type]

    name = getattr(component, "name", "").lower()
    if name in RECOMMENDED_VELOCITIES:
        return RECOMMENDED_VELOCITIES[name]

    return (0.8, 2.5)

TUBE_LENGTH_STANDARD = [
    {"length": 0.5, "area": 10},
    {"length": 1.0, "area": 20},
    {"length": 2.5, "area": 40},
    {"length": 3.0, "area": 60},
    {"length": 4.0, "area": 80},
    {"length": 5.0, "area": 100},
    {"length": 6.0, "area": 120},
]

TUBE_DIAMETER_STANDARD = [
    {"od": 0.012, "thickness": 0.001},
    {"od": 0.016, "thickness": 0.0012},
    {"od": 0.019, "thickness": 0.0015},
    {"od": 0.025, "thickness": 0.002},
    {"od": 0.032, "thickness": 0.0026},
    {"od": 0.038, "thickness": 0.003},
]


import math

def select_tube_configuration(area_required, hot, cold):
    best = None
    best_score = float("inf")

    hot_v_min, hot_v_max = get_velocity_range(hot["component"])
    target_velocity = 0.5 * (hot_v_min + hot_v_max)

    # ---- FIXED INITIAL SELECTION ----
    preferred_od = 0.019   # 19 mm
    preferred_length = 3.0 # 3 m

    for tube in TUBE_DIAMETER_STANDARD:
        tube_od = tube["od"]

        # prioritize 19 mm but still allow fallback
        if abs(tube_od - preferred_od) > 1e-6:
            continue

        tube_id = tube_od - 2 * tube["thickness"]

        for length_data in TUBE_LENGTH_STANDARD:
            tube_length = length_data["length"]

            # prioritize 3 m but still allow fallback
            if abs(tube_length - preferred_length) > 1e-6:
                continue

            area_per_tube = math.pi * tube_od * tube_length

            # ---- BINARY SEARCH ON TUBE COUNT ----
            Nt_min = max(1, int(area_required / area_per_tube * 0.5))
            Nt_max = int(area_required / area_per_tube * 2) + 10

            while Nt_min <= Nt_max:
                tube_count = (Nt_min + Nt_max) // 2

                total_area = tube_count * area_per_tube

                # ---- ESTIMATE SHELL DIAMETER (simplified Kern relation) ----
                pitch = 1.25 * tube_od
                bundle_dia = tube_od * (tube_count / 0.785) ** 0.5  # rough triangular layout
                shell_dia = bundle_dia + 0.05  # clearance ~50 mm

                L_D_ratio = tube_length / max(shell_dia, 1e-6)

                # ---- L/D CONSTRAINT ----
                if L_D_ratio < 5:
                    Nt_max = tube_count - 1
                    continue
                elif L_D_ratio > 10:
                    Nt_min = tube_count + 1
                    continue

                # ---- VELOCITY CALCULATION ----
                passes = 2  # initial assumption

                flow_area = (tube_count / passes) * (math.pi * tube_id**2 / 4)
                velocity = (hot["m_dot"] / hot["density"]) / max(flow_area, 1e-12)

                # ---- VELOCITY CHECK ----
                if velocity < hot_v_min:
                    passes = max(1, passes - 1)
                    Nt_max = tube_count - 1
                    continue

                elif velocity > hot_v_max:
                    passes += 1
                    Nt_min = tube_count + 1
                    continue

                # ---- SCORING ----
                area_penalty = abs((total_area - area_required) / max(area_required, 1e-12))
                velocity_penalty = abs(velocity - target_velocity)

                score = area_penalty * 2 + velocity_penalty

                if score < best_score:
                    best_score = score
                    best = {
                        "tube_od": tube_od,
                        "tube_id": tube_id,
                        "tube_length": tube_length,
                        "tube_count": tube_count,
                        "passes": passes,
                        "velocity": velocity,
                        "area": total_area,
                        "shell_diameter": shell_dia,
                        "L/D": L_D_ratio,
                        "velocity_range": (hot_v_min, hot_v_max),
                        "score": score,
                    }

                break  # valid solution found, exit binary search

    return best
