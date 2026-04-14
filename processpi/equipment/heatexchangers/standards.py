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
