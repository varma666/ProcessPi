# processpi/equipment/heatexchangers/mechanical/double_pipe.py

from typing import Dict, Any

def run(hx, **kwargs) -> Dict[str, Any]:
    """
    Perform mechanical design of a double-pipe heat exchanger.

    Parameters:
        hx : HeatExchanger instance
        **kwargs : optional arguments, e.g., tube diameter, velocity limits

    Returns:
        Dict[str, Any]: Double-pipe exchanger mechanical design parameters
    """

    # -----------------------------
    # Step 1: Fetch basic parameters
    # -----------------------------
    if not hasattr(hx, "_basic_params"):
        raise ValueError(f"{hx.name}: Basic parameters not calculated. Run BasicParameters first.")

    bp = hx._basic_params  # dictionary returned from basic_params.run()

    results: Dict[str, Any] = {}

    # Extract key parameters
    Ch = bp["Ch"]
    Cc = bp["Cc"]
    C_min = bp["C_min"]
    C_max = bp["C_max"]
    Th_in = bp["Th_in"]
    Tc_in = bp["Tc_in"]
    delta_T_max = bp["delta_T_max"]

    # -----------------------------
    # Step 2: Define design inputs / defaults
    # -----------------------------
    tube_diameter = kwargs.get("tube_diameter_m", 0.025)  # meters
    velocity_hot = kwargs.get("velocity_hot_m_s", 1.0)    # m/s
    velocity_cold = kwargs.get("velocity_cold_m_s", 1.0)  # m/s

    # -----------------------------
    # Step 3: Compute flow areas & pipe lengths
    # -----------------------------
    # Placeholder calculations:
    # Flow area = m / (rho * velocity)
    rho_hot = kwargs.get("rho_hot", 1000)  # kg/m3 default for water
    rho_cold = kwargs.get("rho_cold", 1000)

    A_hot = (bp["m_hot"] / rho_hot) / velocity_hot
    A_cold = (bp["m_cold"] / rho_cold) / velocity_cold

    # Equivalent diameters (circular pipes)
    D_hot = (4 * A_hot / 3.1416) ** 0.5
    D_cold = (4 * A_cold / 3.1416) ** 0.5

    # Approximate length using energy balance and assumed U
    if hx.U and hx.area:
        L = hx.area / (3.1416 * tube_diameter)
    else:
        L = None  # unknown until U and area provided

    # -----------------------------
    # Step 4: Package results
    # -----------------------------
    results.update({
        "tube_diameter_m": tube_diameter,
        "D_hot_m": D_hot,
        "D_cold_m": D_cold,
        "tube_length_m": L,
        "flow_area_hot_m2": A_hot,
        "flow_area_cold_m2": A_cold,
        "velocity_hot_m_s": velocity_hot,
        "velocity_cold_m_s": velocity_cold,
    })

    # Optional: merge kwargs overrides
    results.update(kwargs)

    return results

