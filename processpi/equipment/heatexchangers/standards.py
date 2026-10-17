from __future__ import annotations



from typing import Optional, Tuple

import logging

import math



logger = logging.getLogger("processpi.hx.standards")



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



    return DEFAULT_VELOCITY_RANGE



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



logger = logging.getLogger("processpi.hx.standards")

# Starting tube size when the user fixes neither OD nor length.
PREFERRED_TUBE_OD = 0.019      # 19 mm (3/4 in)
PREFERRED_TUBE_LENGTH = 3.0    # m



def _select_preferred_tube_configuration(area_required, hot, cold):
    """Tube count and passes for the preferred 19 mm x 3 m tube.

    The selection used when the user fixes no geometry: only the tube count
    and passes vary, so the design loop sees the same tube size on every U
    iteration and converges.
    """
    best = None
    best_score = float("inf")

    hot_v_min, hot_v_max = get_velocity_range(hot["component"])
    target_velocity = 0.5 * (hot_v_min + hot_v_max)
    shell_v_min, shell_v_max = 0.3, 1.0

    # ---- FIXED INITIAL SELECTION ----
    preferred_od = PREFERRED_TUBE_OD
    preferred_length = PREFERRED_TUBE_LENGTH

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

                # ---- ESTIMATE SHELL DIAMETER (pitch-based bundle relation) ----
                pitch = 1.25 * tube_od
                bundle_dia = pitch * math.sqrt(max(tube_count, 1))
                shell_dia = bundle_dia + 0.05  # clearance ~50 mm

                L_D_ratio = tube_length / max(shell_dia, 1e-6)

                # ---- L/D CONSTRAINT ----
                if L_D_ratio < 5:
                    Nt_max = tube_count - 1
                    continue
                elif L_D_ratio > 10:
                    Nt_min = tube_count + 1
                    continue

                # ---- SHELL-SIDE VELOCITY CONSTRAINT ----
                shell_flow_area = (math.pi / 4) * max(shell_dia**2 - bundle_dia**2, 1e-12)
                shell_velocity = (cold["m_dot"] / max(cold["density"], 1e-12)) / max(shell_flow_area, 1e-12)

                if shell_velocity < shell_v_min:
                    Nt_max = tube_count - 1
                    continue
                elif shell_velocity > shell_v_max:
                    Nt_min = tube_count + 1
                    continue

                # ---- VELOCITY CALCULATION ----
                flow_per_density = (hot["m_dot"] / max(hot["density"], 1e-12))
                base_tube_area = math.pi * tube_id**2 / 4
                min_passes, max_passes = 1, 8
                passes = 2  # initial assumption
                velocity = None

                while True:
                    flow_area = (tube_count / max(passes, 1)) * base_tube_area
                    trial_velocity = flow_per_density / max(flow_area, 1e-12)

                    if hot_v_min <= trial_velocity <= hot_v_max:
                        velocity = trial_velocity
                        break

                    if trial_velocity < hot_v_min:
                        if passes < max_passes:
                            passes += 1
                            continue
                        Nt_max = tube_count - 1
                        break

                    if trial_velocity > hot_v_max:
                        if passes > min_passes:
                            passes -= 1
                            continue
                        Nt_min = tube_count + 1
                        break

                if velocity is None:
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
                        "shell_velocity": shell_velocity,
                        "velocity_range": (hot_v_min, hot_v_max),
                        "score": score,
                    }

                if total_area < area_required:
                    Nt_min = tube_count + 1
                else:
                    Nt_max = tube_count - 1

    return best


def select_tube_configuration(
    area_required,
    hot,
    cold,
    tube_od=None,
    tube_id=None,
    tube_length=None,
    tube_pitch=None,
    tube_layout=None,
    tube_count=None,
    tube_passes=None,
    shell_diameter=None,
    shell_passes=None,
    baffle_spacing=None,
    max_tube_count=10000,
    search_standard_sizes=False,
):
    """
    Select a feasible preliminary shell-and-tube configuration.

    Units:
        area_required: m²
        tube dimensions / shell_diameter / baffle_spacing: m
        mass flow: kg/s
        density: kg/m³
        returned velocities: m/s

    Any supplied geometry value is treated as fixed. Missing values may be
    selected/estimated. With no geometry fixed, the preferred 19 mm x 3 m
    tube is used and only the tube count and passes vary. Otherwise a free
    OD is 19 mm and a free length 3 m, unless search_standard_sizes=True,
    which tries every standard OD and length. This is a preliminary screening model, not a
    TEMA-rated bundle geometry or a substitute for detailed thermal/hydraulic
    and mechanical design.
    """
    import math

    if area_required is None or not math.isfinite(float(area_required)) or float(area_required) <= 0:
        raise ValueError("area_required must be a finite positive value.")
    area_required = float(area_required)

    for stream_name, stream in (("hot", hot), ("cold", cold)):
        if not isinstance(stream, dict):
            raise TypeError(f"{stream_name} must be a dictionary.")
        for key in ("m_dot", "density"):
            if key not in stream:
                raise ValueError(f"{stream_name} stream requires '{key}'.")
            value = float(stream[key])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{stream_name}['{key}'] must be finite and positive.")

    if "component" not in hot:
        raise ValueError("hot stream requires 'component' for velocity-range selection.")

    def positive_optional(name, value):
        if value is None:
            return None
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive value.")
        return value

    tube_od = positive_optional("tube_od", tube_od)
    tube_id = positive_optional("tube_id", tube_id)
    tube_length = positive_optional("tube_length", tube_length)
    tube_pitch = positive_optional("tube_pitch", tube_pitch)
    shell_diameter = positive_optional("shell_diameter", shell_diameter)
    baffle_spacing = positive_optional("baffle_spacing", baffle_spacing)

    if tube_od is not None and tube_id is not None and tube_id >= tube_od:
        raise ValueError("tube_id must be smaller than tube_od.")
    if tube_pitch is not None and tube_od is not None and tube_pitch < tube_od:
        raise ValueError("tube_pitch cannot be smaller than tube_od.")

    if tube_layout is not None:
        tube_layout = str(tube_layout).strip().lower()
        if tube_layout not in {"triangular", "square"}:
            raise ValueError("tube_layout must be 'triangular' or 'square'.")

    if tube_count is not None:
        if isinstance(tube_count, bool) or int(tube_count) != float(tube_count) or int(tube_count) < 1:
            raise ValueError("tube_count must be a positive integer.")
        tube_count = int(tube_count)

    if tube_passes is not None:
        if isinstance(tube_passes, bool) or int(tube_passes) != float(tube_passes) or int(tube_passes) < 1:
            raise ValueError("tube_passes must be a positive integer.")
        tube_passes = int(tube_passes)

    if shell_passes is not None:
        if isinstance(shell_passes, bool) or int(shell_passes) != float(shell_passes) or int(shell_passes) < 1:
            raise ValueError("shell_passes must be a positive integer.")
        shell_passes = int(shell_passes)

    if max_tube_count < 1:
        raise ValueError("max_tube_count must be at least 1.")

    fixed = (tube_od, tube_id, tube_length, tube_pitch, tube_layout, tube_count,
             tube_passes, shell_diameter, shell_passes, baffle_spacing)
    if not search_standard_sizes and all(value is None for value in fixed):
        return _select_preferred_tube_configuration(area_required, hot, cold)

    hot_v_min, hot_v_max = get_velocity_range(hot["component"])
    hot_v_min, hot_v_max = float(hot_v_min), float(hot_v_max)
    if not (0 < hot_v_min <= hot_v_max):
        raise ValueError("get_velocity_range returned an invalid velocity range.")
    target_velocity = 0.5 * (hot_v_min + hot_v_max)

    # If OD is not fixed, use the preferred 19 mm tube, or every standard OD
    # with search_standard_sizes. The design loop calls this on every U
    # iteration, so a free OD that changes between calls stops U converging.
    # If ID is fixed, do not pair it with an OD smaller than the specified ID.
    all_ods = [float(item["od"]) for item in TUBE_DIAMETER_STANDARD]
    if tube_od is not None:
        od_candidates = [tube_od]
    elif search_standard_sizes:
        od_candidates = all_ods
    else:
        od_candidates = [PREFERRED_TUBE_OD]
    if tube_id is not None:
        od_candidates = [od for od in od_candidates if od > tube_id]
        if not od_candidates and tube_od is None:
            od_candidates = [od for od in all_ods if od > tube_id]

    # Arbitrary lengths are supported when supplied. Otherwise the preferred
    # 3 m length, or every standard length with search_standard_sizes.
    if tube_length is not None:
        length_candidates = [tube_length]
    elif search_standard_sizes:
        length_candidates = [float(item["length"]) for item in TUBE_LENGTH_STANDARD]
    else:
        length_candidates = [PREFERRED_TUBE_LENGTH]

    layout_candidates = [tube_layout] if tube_layout is not None else [
        "triangular", "square"
    ]

    best = None
    best_score = float("inf")
    failures = []

    for od in od_candidates:
        # A supplied ID is retained exactly. Otherwise derive ID from the
        # matching standard wall thickness, or use a documented fallback.
        if tube_id is not None:
            ids = [tube_id]
        else:
            matching = [
                item for item in TUBE_DIAMETER_STANDARD
                if math.isclose(float(item["od"]), od, rel_tol=0.0, abs_tol=1e-9)
            ]
            if matching:
                ids = [od - 2.0 * float(matching[0]["thickness"])]
            else:
                # Non-standard user OD without an ID: assume 10% OD wall
                # thickness as an estimate; caller should supply ID for design.
                ids = [0.8 * od]

        for inner_diameter in ids:
            if not (0 < inner_diameter < od):
                continue

            for length in length_candidates:
                if length <= 0:
                    continue

                area_per_tube = math.pi * od * length
                min_count = tube_count if tube_count is not None else max(
                    1, int(math.ceil(area_required / area_per_tube))
                )
                max_count = tube_count if tube_count is not None else min(
                    max_tube_count,
                    max(min_count + 200, int(math.ceil(area_required / area_per_tube * 2.0)) + 20),
                )

                for layout in layout_candidates:
                    for count in range(min_count, max_count + 1):
                        total_area = count * area_per_tube

                        # A fixed tube count is a hard constraint. Otherwise
                        # a candidate must provide at least the required area.
                        if tube_count is not None and total_area + 1e-12 < area_required:
                            continue
                        if tube_count is None and total_area + 1e-12 < area_required:
                            continue

                        pitch = tube_pitch if tube_pitch is not None else 1.25 * od
                        if pitch < od:
                            continue

                        # Approximate bundle diameter. This is a screening
                        # correlation and does not replace TEMA tube-count data.
                        layout_factor = 0.90 if layout == "triangular" else 1.00
                        bundle_dia = pitch * math.sqrt(count / layout_factor)

                        estimated_shell_dia = bundle_dia + 0.05
                        actual_shell_dia = (
                            shell_diameter
                            if shell_diameter is not None
                            else estimated_shell_dia
                        )

                        if actual_shell_dia <= bundle_dia:
                            failures.append("specified shell diameter is too small for estimated bundle")
                            continue

                        ld_ratio = length / actual_shell_dia

                        # Keep the prior model's preferred L/D range as a
                        # scoring preference, not a reason to alter fixed inputs.
                        ld_penalty = 0.0
                        if ld_ratio < 5.0:
                            ld_penalty = (5.0 - ld_ratio) * 0.25
                        elif ld_ratio > 10.0:
                            ld_penalty = (ld_ratio - 10.0) * 0.25

                        # Approximate free area in the annular gap. Real shell-
                        # side crossflow area requires baffle/window geometry.
                        shell_flow_area = (math.pi / 4.0) * max(
                            actual_shell_dia**2 - bundle_dia**2, 1e-12
                        )
                        shell_volumetric_flow = float(cold["m_dot"]) / float(cold["density"])
                        shell_velocity = shell_volumetric_flow / shell_flow_area

                        tube_flow_volumetric = float(hot["m_dot"]) / float(hot["density"])
                        single_tube_flow_area = math.pi * inner_diameter**2 / 4.0

                        pass_candidates = [tube_passes] if tube_passes is not None else range(1, 9)
                        feasible_passes = []
                        for passes in pass_candidates:
                            parallel_tubes = count / passes
                            flow_area = parallel_tubes * single_tube_flow_area
                            velocity = tube_flow_volumetric / max(flow_area, 1e-12)
                            if hot_v_min <= velocity <= hot_v_max:
                                feasible_passes.append((passes, velocity))

                        if not feasible_passes:
                            # If velocity is outside the recommended band,
                            # keep the candidate as a penalized fallback only
                            # when passes were explicitly fixed.
                            if tube_passes is not None:
                                passes = tube_passes
                                velocity = tube_flow_volumetric / max(
                                    (count / passes) * single_tube_flow_area, 1e-12
                                )
                                velocity_penalty = min(
                                    abs(velocity - hot_v_min),
                                    abs(velocity - hot_v_max),
                                )
                            else:
                                continue
                        else:
                            passes, velocity = min(
                                feasible_passes,
                                key=lambda item: abs(item[1] - target_velocity),
                            )
                            velocity_penalty = abs(velocity - target_velocity)

                        # If baffle spacing was not specified, use a common
                        # preliminary estimate of 0.5 * shell diameter.
                        selected_baffle_spacing = (
                            baffle_spacing if baffle_spacing is not None
                            else 0.5 * actual_shell_dia
                        )

                        # Score prioritizes area oversizing and tube velocity,
                        # with a soft L/D preference. Fixed dimensions are never
                        # changed to improve the score.
                        area_penalty = (total_area - area_required) / area_required
                        score = (
                            2.0 * area_penalty
                            + velocity_penalty / max(target_velocity, 1e-12)
                            + ld_penalty
                        )

                        candidate = {
                            "tube_od": od,
                            "tube_id": inner_diameter,
                            "tube_length": length,
                            "tube_pitch": pitch,
                            "tube_layout": layout,
                            "tube_count": count,
                            "passes": passes,
                            "tube_passes": passes,
                            "shell_passes": shell_passes if shell_passes is not None else 1,
                            "velocity": velocity,
                            "area": total_area,
                            "shell_diameter": actual_shell_dia,
                            "bundle_diameter_estimate": bundle_dia,
                            "L/D": ld_ratio,
                            "shell_velocity_estimate": shell_velocity,
                            "baffle_spacing": selected_baffle_spacing,
                            "velocity_range": (hot_v_min, hot_v_max),
                            "score": score,
                            "fixed_inputs": {
                                "tube_od": tube_od is not None,
                                "tube_id": tube_id is not None,
                                "tube_length": tube_length is not None,
                                "tube_pitch": tube_pitch is not None,
                                "tube_layout": tube_layout is not None,
                                "tube_count": tube_count is not None,
                                "tube_passes": tube_passes is not None,
                                "shell_diameter": shell_diameter is not None,
                                "shell_passes": shell_passes is not None,
                                "baffle_spacing": baffle_spacing is not None,
                            },
                        }

                        if score < best_score:
                            best_score = score
                            best = candidate

                        # When count is not fixed, area penalty is monotonic
                        # in count; once the area is adequate, larger counts
                        # generally increase cost. Continue enough to explore
                        # velocity-feasible options.

    if best is None:
        details = "; ".join(dict.fromkeys(failures))
        message = (
            "No feasible preliminary tube configuration found for the supplied "
            "constraints. Check area, dimensions, flow rates, density, and "
            "velocity limits."
        )
        if details:
            message += " Details: " + details
        logger.warning(message)
        return None

    logger.debug("Best tube configuration: %s", best)
    return best


def tube_length_select(tube_length, ld, fixed=False):
    """
    Return tube_length unchanged when fixed=True. Otherwise retain the legacy
    standard-length recommendation behaviour.
    """
    if tube_length is None:
        raise ValueError("tube_length cannot be None.")

    current_length = float(tube_length)
    if current_length <= 0 or not math.isfinite(current_length):
        raise ValueError("tube_length must be a finite positive value.")

    if fixed:
        return current_length

    std_lengths = sorted(float(item["length"]) for item in TUBE_LENGTH_STANDARD)

    if ld > 10:
        lower = [length for length in std_lengths if length <= current_length]
        return max(lower) if lower else min(std_lengths)

    if ld < 5:
        higher = [length for length in std_lengths if length >= current_length]
        return min(higher) if higher else max(std_lengths)

    return current_length


# -------------------------------

# Industrial standards databases

# -------------------------------

STANDARD_TUBE_COUNT_TABLES = {

    "triangular": {

        0.75: {"0.9375_pitch": {8: {1: 37, 2: 30, 4: 24, 6: 20, 8: 18}, 10: {1: 61, 2: 50, 4: 40, 6: 34, 8: 30}, 12: {1: 91, 2: 76, 4: 62, 6: 52, 8: 46}}},

        1.0: {"1.25_pitch": {10: {1: 37, 2: 30, 4: 24, 6: 20, 8: 18}, 12: {1: 55, 2: 44, 4: 36, 6: 30, 8: 26}, 16: {1: 97, 2: 80, 4: 64, 6: 54, 8: 46}}},

        1.25: {"1.5625_pitch": {14: {1: 37, 2: 30, 4: 24, 6: 20, 8: 18}, 18: {1: 61, 2: 50, 4: 40, 6: 34, 8: 30}, 24: {1: 127, 2: 104, 4: 84, 6: 70, 8: 60}}},

        1.5: {"1.875_pitch": {18: {1: 37, 2: 30, 4: 24, 6: 20, 8: 18}, 24: {1: 73, 2: 58, 4: 46, 6: 40, 8: 34}, 30: {1: 127, 2: 102, 4: 82, 6: 70, 8: 60}}},

    },

    "square": {

        0.75: {"1.0_pitch": {8: {1: 31, 2: 24, 4: 20, 6: 18, 8: 16}, 10: {1: 49, 2: 40, 4: 32, 6: 28, 8: 24}, 12: {1: 71, 2: 58, 4: 48, 6: 40, 8: 34}}},

        1.0: {"1.25_pitch": {10: {1: 31, 2: 24, 4: 20, 6: 18, 8: 16}, 12: {1: 45, 2: 36, 4: 30, 6: 26, 8: 22}, 16: {1: 79, 2: 64, 4: 52, 6: 44, 8: 38}}},

        1.25: {"1.5625_pitch": {14: {1: 31, 2: 24, 4: 20, 6: 18, 8: 16}, 18: {1: 49, 2: 40, 4: 32, 6: 28, 8: 24}, 24: {1: 105, 2: 84, 4: 68, 6: 58, 8: 50}}},

        1.5: {"1.875_pitch": {18: {1: 31, 2: 24, 4: 20, 6: 18, 8: 16}, 24: {1: 59, 2: 46, 4: 38, 6: 32, 8: 28}, 30: {1: 105, 2: 84, 4: 68, 6: 58, 8: 50}}},

    },

}



STANDARD_EXCHANGER_TUBES = {

    0.5: {20: {"wall_in": 0.035, "id_in": 0.43}, 18: {"wall_in": 0.049, "id_in": 0.402}, 16: {"wall_in": 0.065, "id_in": 0.37}, 14: {"wall_in": 0.083, "id_in": 0.334}, 12: {"wall_in": 0.109, "id_in": 0.282}},

    0.75: {20: {"wall_in": 0.035, "id_in": 0.68}, 18: {"wall_in": 0.049, "id_in": 0.652}, 16: {"wall_in": 0.065, "id_in": 0.62}, 14: {"wall_in": 0.083, "id_in": 0.584}, 12: {"wall_in": 0.109, "id_in": 0.532}},

    1.0: {20: {"wall_in": 0.035, "id_in": 0.93}, 18: {"wall_in": 0.049, "id_in": 0.902}, 16: {"wall_in": 0.065, "id_in": 0.87}, 14: {"wall_in": 0.083, "id_in": 0.834}, 12: {"wall_in": 0.109, "id_in": 0.782}},

    1.25: {20: {"wall_in": 0.035, "id_in": 1.18}, 18: {"wall_in": 0.049, "id_in": 1.152}, 16: {"wall_in": 0.065, "id_in": 1.12}, 14: {"wall_in": 0.083, "id_in": 1.084}, 12: {"wall_in": 0.109, "id_in": 1.032}},

    1.5: {20: {"wall_in": 0.035, "id_in": 1.43}, 18: {"wall_in": 0.049, "id_in": 1.402}, 16: {"wall_in": 0.065, "id_in": 1.37}, 14: {"wall_in": 0.083, "id_in": 1.334}, 12: {"wall_in": 0.109, "id_in": 1.282}},

}



STANDARD_PIPE_TABLES = {

    0.125: {40: {"od_in": 0.405, "id_in": 0.269}, 80: {"od_in": 0.405, "id_in": 0.215}},

    0.5: {20: {"od_in": 0.84, "id_in": 0.622}, 40: {"od_in": 0.84, "id_in": 0.622}, 80: {"od_in": 0.84, "id_in": 0.546}},

    1.0: {20: {"od_in": 1.315, "id_in": 1.049}, 40: {"od_in": 1.315, "id_in": 1.049}, 80: {"od_in": 1.315, "id_in": 0.957}},

    2.0: {20: {"od_in": 2.375, "id_in": 2.067}, 40: {"od_in": 2.375, "id_in": 2.067}, 80: {"od_in": 2.375, "id_in": 1.939}},

    4.0: {20: {"od_in": 4.5, "id_in": 4.154}, 40: {"od_in": 4.5, "id_in": 4.026}, 80: {"od_in": 4.5, "id_in": 3.826}},

    6.0: {20: {"od_in": 6.625, "id_in": 6.357}, 40: {"od_in": 6.625, "id_in": 6.065}, 80: {"od_in": 6.625, "id_in": 5.761}},

    8.0: {20: {"od_in": 8.625, "id_in": 8.329}, 40: {"od_in": 8.625, "id_in": 7.981}, 80: {"od_in": 8.625, "id_in": 7.625}},

    10.0: {20: {"od_in": 10.75, "id_in": 10.42}, 40: {"od_in": 10.75, "id_in": 10.02}, 80: {"od_in": 10.75, "id_in": 9.564}},

    12.0: {20: {"od_in": 12.75, "id_in": 12.39}, 40: {"od_in": 12.75, "id_in": 11.938}, 80: {"od_in": 12.75, "id_in": 11.376}},

    16.0: {20: {"od_in": 16.0, "id_in": 15.25}, 40: {"od_in": 16.0, "id_in": 15.0}, 80: {"od_in": 16.0, "id_in": 14.5}},

    24.0: {20: {"od_in": 24.0, "id_in": 23.25}, 40: {"od_in": 24.0, "id_in": 23.0}, 80: {"od_in": 24.0, "id_in": 22.5}},

}



FOULING_FACTOR_DATABASE = {

    "seawater": {"base": 0.00035, "velocity_sensitive": True},

    "brackish_water": {"base": 0.00030, "velocity_sensitive": True},

    "cooling_tower_water": {"base": 0.00025, "velocity_sensitive": True},

    "distilled_water": {"base": 0.00009, "velocity_sensitive": False},

    "treated_water": {"base": 0.00018, "velocity_sensitive": True},

    "river_water": {"base": 0.00035, "velocity_sensitive": True},

    "hydrocarbons": {"base": 0.00020, "velocity_sensitive": True},

    "crude": {"base": 0.00050, "velocity_sensitive": True, "temperature_sensitive": True},

    "steam": {"base": 0.00009, "velocity_sensitive": False},

    "vapor": {"base": 0.00012, "velocity_sensitive": False},

    "reboiler": {"base": 0.00035, "velocity_sensitive": True, "temperature_sensitive": True},

    "condenser": {"base": 0.00018, "velocity_sensitive": False},

    "refinery": {"base": 0.00040, "velocity_sensitive": True},

    "oil": {"base": 0.00030, "velocity_sensitive": True, "temperature_sensitive": True},

}



CORROSION_SEVERITY_DATABASE = {

    "seawater": "high",

    "brackish_water": "high",

    "acid": "high",

    "hydrocarbon": "low-medium",

    "steam_condensate": "low",

    "refinery": "medium-high",

    "treated_water": "medium",

    "crude": "medium-high",

    "amine": "high",
    "inert_gas": "low",

}





DEFAULT_VELOCITY_RANGE = (0.8, 2.5)

RECOMMENDED_VELOCITIES = {"organic_liquid": (1.8, 2.0),"inorganic_liquid": (1.2, 1.8),"oil": (1.8, 2.0),"gas": (15.0, 30.0),"vapor": (15.0, 30.0),"water": (1.0, 2.5),"acetic_acid": (1.0, 2.0),"acetone": (1.0, 2.0),"acrylic_acid": (1.0, 2.0),"air": (10.0, 20.0),"ammonia": (8.0, 15.0),"benzene": (1.0, 2.0),"benzoic_acid": (1.0, 2.0),"bromine": (0.8, 1.5),"butane": (10.0, 18.0),"carbon_dioxide": (8.0, 15.0),"carbon_monoxide": (8.0, 15.0),"carbon_tetrachloride": (0.8, 1.5),"chlorine": (5.0, 10.0),"chlorobenzene": (1.0, 2.0),"chloroform": (0.8, 1.5),"chloromethane": (8.0, 15.0),"cyanogen": (8.0, 15.0),"cyclohexane": (1.0, 2.0),"ethane": (10.0, 20.0),"ethanol": (1.0, 2.0),"ethyl_acetate": (1.0, 2.0),"ethylene": (10.0, 20.0),"fluorine": (5.0, 10.0),"fluorobenzene": (1.0, 2.0),"formic_acid": (1.0, 2.0),"helium_4": (20.0, 40.0),"hydrogen_chloride": (8.0, 15.0),"hydrogen_cyanide": (8.0, 15.0),"hydrogen_sulfide": (8.0, 15.0),"methane": (10.0, 20.0),"methanol": (1.0, 2.0),"neon": (15.0, 30.0),"nitrogen": (10.0, 20.0),"nitrous_oxide": (8.0, 15.0),"nitric_oxide": (8.0, 15.0),"oxygen": (10.0, 20.0),"ozone": (8.0, 15.0),"phenol": (1.0, 2.0),"propane": (10.0, 18.0),"propionic_acid": (1.0, 2.0),"styrene": (1.0, 2.0),"sulfur_dioxide": (8.0, 15.0),"toluene": (1.0, 2.0)}

from difflib import get_close_matches



def get_fouling_factor(

    fluid_key: str,

    velocity: float | None = None,

    temperature: float | None = None,

    database: dict | None = None,

    debug: bool = True,

) -> float:

    """

    Returns fouling factor based on ProcessPI fouling standards.



    Parameters

    ----------

    fluid_key : str

        Fluid/service lookup key.

        Example:

            "water"

            "treated_water"

            "hydrocarbons"

            "crude"



    velocity : float, optional

        Fluid velocity in m/s.



    temperature : float, optional

        Fluid temperature in °C.



    database : dict, optional

        Fouling factor database.



    debug : bool

        Print debug messages.



    Returns

    -------

    float

        Fouling factor in m2.K/W

    """



    if database is None:

        database = FOULING_FACTOR_DATABASE



    DEFAULT_FOULING = 0.00018



    # ======================================================

    # NORMALIZE KEY

    # ======================================================



    key = (

        fluid_key.lower()

        .strip()

        .replace(" ", "_")

    )



    # ======================================================

    # DIRECT MATCH

    # ======================================================



    if key in database:

        entry = database[key]



    else:



        # ==================================================

        # FUZZY MATCH

        # ==================================================



        matches = get_close_matches(

            key,

            database.keys(),

            n=1,

            cutoff=0.6

        )



        if matches:

            matched_key = matches[0]

            entry = database[matched_key]



            if debug:

                logger.debug(

                    f"[DEBUG] Fouling key '{key}' "

                    f"not found. Using closest match "

                    f"'{matched_key}'"

                )



        else:



            # ==============================================

            # SAFE DEFAULT

            # ==============================================



            if debug:

                logger.debug(

                    f"[DEBUG] Fouling key '{key}' "

                    f"not found. Using default fouling "

                    f"factor = {DEFAULT_FOULING}"

                )



            return DEFAULT_FOULING



    # ======================================================

    # BASE FOULING

    # ======================================================



    fouling = entry["base"]



    if debug:

        logger.debug(f"[DEBUG] Base fouling factor = {fouling}")



    # ======================================================

    # VELOCITY CORRECTION

    # ======================================================



    if entry.get("velocity_sensitive", False):



        if velocity is not None:



            # ----------------------------------------------

            # LOWER VELOCITY → HIGHER FOULING

            # HIGHER VELOCITY → LOWER FOULING

            # ----------------------------------------------



            if velocity < 1.0:

                fouling *= 1.30



                if debug:

                    logger.debug(

                        f"[DEBUG] Low velocity correction "

                        f"applied (v={velocity:.3f} m/s)"

                    )



            elif velocity > 2.5:

                fouling *= 0.85



                if debug:

                    logger.debug(

                        f"[DEBUG] High velocity correction "

                        f"applied (v={velocity:.3f} m/s)"

                    )



    # ======================================================

    # TEMPERATURE CORRECTION

    # ======================================================



    if entry.get("temperature_sensitive", False):



        if temperature is not None:



            # ----------------------------------------------

            # Higher temperature generally increases

            # fouling tendency for oils/crudes

            # ----------------------------------------------



            if temperature > 150:

                fouling *= 1.25



                if debug:

                    logger.debug(

                        f"[DEBUG] High temperature "

                        f"correction applied "

                        f"(T={temperature:.2f} °C)"

                    )



            elif temperature < 50:

                fouling *= 0.95



                if debug:

                    logger.debug(

                        f"[DEBUG] Low temperature "

                        f"correction applied "

                        f"(T={temperature:.2f} °C)"

                    )



    # ======================================================

    # FINAL DEBUG

    # ======================================================



    if debug:

        logger.debug(

            f"[DEBUG] Final fouling factor "

            f"for '{key}' = {fouling}"

        )



    return fouling
