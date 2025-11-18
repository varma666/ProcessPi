from ...units import *

TYPICAL_U = {
    "water - water": (HeatTransferCoefficient(800, "W/m2K"), HeatTransferCoefficient(1500, "W/m2K")),
    "organicliquid - organicliquid": (HeatTransferCoefficient(100, "W/m2K"), HeatTransferCoefficient(300, "W/m2K")),
    "lightoil - lightoil": (HeatTransferCoefficient(100, "W/m2K"), HeatTransferCoefficient(400, "W/m2K")),
    "heavyoil - heavyoil": (HeatTransferCoefficient(50, "W/m2K"), HeatTransferCoefficient(300, "W/m2K")),
    "reducedcrude - flashedcrude": (HeatTransferCoefficient(35, "W/m2K"), HeatTransferCoefficient(150, "W/m2K")),
    "reduceddea - fouldea": (HeatTransferCoefficient(450, "W/m2K"), HeatTransferCoefficient(650, "W/m2K")),
    "gas - gas": (HeatTransferCoefficient(5, "W/m2K"), HeatTransferCoefficient(35, "W/m2K")),
    "organicliquid - water": (HeatTransferCoefficient(250, "W/m2K"), HeatTransferCoefficient(750, "W/m2K")),
    "lightoil - water": (HeatTransferCoefficient(300, "W/m2K"), HeatTransferCoefficient(900, "W/m2K")),
    "heavyoil - water": (HeatTransferCoefficient(200, "W/m2K"), HeatTransferCoefficient(600, "W/m2K")),
    "reducedcrude - water": (HeatTransferCoefficient(150, "W/m2K"), HeatTransferCoefficient(400, "W/m2K")),
    "reduceddea - water": (HeatTransferCoefficient(600, "W/m2K"), HeatTransferCoefficient(1000, "W/m2K")),
    "gas - water": (HeatTransferCoefficient(20, "W/m2K"), HeatTransferCoefficient(100, "W/m2K")),
    "organicliquid - brine": (HeatTransferCoefficient(200, "W/m2K"), HeatTransferCoefficient(600, "W/m2K")),
    "water - brine": (HeatTransferCoefficient(700, "W/m2K"), HeatTransferCoefficient(1300, "W/m2K")),
    "gas - brine": (HeatTransferCoefficient(15, "W/m2K"), HeatTransferCoefficient(80, "W/m2K")),
    "steam - water": (HeatTransferCoefficient(1000, "W/m2K"), HeatTransferCoefficient(5000, "W/m2K")),
    "steam - organicliquid": (HeatTransferCoefficient(500, "W/m2K"), HeatTransferCoefficient(2000, "W/m2K")),
    "steam - lightoil": (HeatTransferCoefficient(600, "W/m2K"), HeatTransferCoefficient(2500, "W/m2K")),
    "steam - heavyoil": (HeatTransferCoefficient(400, "W/m2K"), HeatTransferCoefficient(1500, "W/m2K")),
    "steam - gas": (HeatTransferCoefficient(50, "W/m2K"), HeatTransferCoefficient(300, "W/m2K")),
    "hotoil - heavoil": (HeatTransferCoefficient(100, "W/m2K"), HeatTransferCoefficient(400, "W/m2K")),
    "hotoil - gas": (HeatTransferCoefficient(20, "W/m2K"), HeatTransferCoefficient(100, "W/m2K")),
    "fluegas - steam": (HeatTransferCoefficient(30, "W/m2K"), HeatTransferCoefficient(150, "W/m2K")),
    "fluegas - hydrocarbonvapor": (HeatTransferCoefficient(10, "W/m2K"), HeatTransferCoefficient(50, "W/m2K")),
    "aqueousvapour - water": (HeatTransferCoefficient(500, "W/m2K"), HeatTransferCoefficient(2000, "W/m2K")),
    "organicvapour - water": (HeatTransferCoefficient(300, "W/m2K"), HeatTransferCoefficient(1500, "W/m2K")),
    "hydrocarbonvapour - water": (HeatTransferCoefficient(200, "W/m2K"), HeatTransferCoefficient(1000, "W/m2K")),
    "aqueousvapour - brine": (HeatTransferCoefficient(400, "W/m2K"), HeatTransferCoefficient(1800, "W/m2K")),
    "organicvapour - brine": (HeatTransferCoefficient(250, "W/m2K"), HeatTransferCoefficient(1200, "W/m2K")),
    "hydrocarbonvapour - brine": (HeatTransferCoefficient(150, "W/m2K"), HeatTransferCoefficient(800, "W/m2K")),
    "steam - aqueousliquid": (HeatTransferCoefficient(800, "W/m2K"), HeatTransferCoefficient(3000, "W/m2K")),
    "steam - organicliquid": (HeatTransferCoefficient(400, "W/m2K"), HeatTransferCoefficient(1500, "W/m2K")),
    "steam - hydrocarbonliquid": (HeatTransferCoefficient(300, "W/m2K"), HeatTransferCoefficient(1200, "W/m2K")),
    "hotoil - hydrocarbonliquid": (HeatTransferCoefficient(80, "W/m2K"), HeatTransferCoefficient(300, "W/m2K")),
    "organicvapour - organicliquid": (HeatTransferCoefficient(300, "W/m2K"), HeatTransferCoefficient(1500, "W/m2K"))
}

def get_typical_U(fluid1, fluid2):
    """
    Get typical heat transfer coefficient range for a given pair of fluids.

    Parameters:
    fluid1 (str): Name of the first fluid.
    fluid2 (str): Name of the second fluid.

    Returns:
    tuple: A tuple containing the minimum and maximum typical heat transfer coefficients as HeatTransferCoefficient objects.

    Raises:
    ValueError: If no typical values are found for the given fluid pair.
    """
    key = f"{fluid1.lower()} - {fluid2.lower()}"
    reverse_key = f"{fluid2.lower()} - {fluid1.lower()}"
    
    if key in TYPICAL_U:
        return TYPICAL_U[key]
    elif reverse_key in TYPICAL_U:
        return TYPICAL_U[reverse_key]
    else:
        raise ValueError(f"No typical heat transfer coefficient values found for the fluid pair: {fluid1} and {fluid2}.")


# Typical thermal conductivity values for metals used in heat exchangers
# Values in W/m.K (typical range at/near room temperature)
TYPICAL_K_METALS = {
    "copper (electrolytic)": (ThermalConductivity(350, "W/mK"), ThermalConductivity(390, "W/mK")),  # very high
    "aluminum 6061": (ThermalConductivity(150, "W/mK"), ThermalConductivity(170, "W/mK")),       # typical 6061-T6 ~152-167
    "aluminum (general)": (ThermalConductivity(200, "W/mK"), ThermalConductivity(240, "W/mK")),   # high-conductivity Al alloys
    "brass": (ThermalConductivity(100, "W/mK"), ThermalConductivity(130, "W/mK")),
    "bronze": (ThermalConductivity(50, "W/mK"), ThermalConductivity(80, "W/mK")),
    "carbon steel / plain steel": (ThermalConductivity(35, "W/mK"), ThermalConductivity(60, "W/mK")), 
    "stainless steel 304": (ThermalConductivity(14, "W/mK"), ThermalConductivity(17, "W/mK")),    # 304 typical ~16 W/mK
    "stainless steel 316": (ThermalConductivity(13, "W/mK"), ThermalConductivity(16, "W/mK")),
    "nickel (commercially pure)": (ThermalConductivity(60, "W/mK"), ThermalConductivity(90, "W/mK")),
    "inconel 625": (ThermalConductivity(9.0, "W/mK"), ThermalConductivity(13.0, "W/mK")),         # low, increases with T
    "hastelloy (C-276)": (ThermalConductivity(10.0, "W/mK"), ThermalConductivity(14.0, "W/mK")),
    "titanium (Grade 2)": (ThermalConductivity(15.0, "W/mK"), ThermalConductivity(21.0, "W/mK")),
    "monel": (ThermalConductivity(20.0, "W/mK"), ThermalConductivity(40.0, "W/mK")),
    "nickel-chromium (nichrome)": (ThermalConductivity(11.0, "W/mK"), ThermalConductivity(20.0, "W/mK")),
    # add other alloys / special materials as needed...
}

def get_typical_k(metal_name: str):
    """
    Return typical (low, high) ThermalConductivity tuple for a metal/alloy.
    Accepts case-insensitive lookups; raises ValueError if missing.
    """
    key = metal_name.lower().strip()
    # simple normalization: allow short forms like "cu" -> "copper (electrolytic)"
    aliases = {
        "cu": "copper (electrolytic)",
        "copper": "copper (electrolytic)",
        "al6061": "aluminum 6061",
        "al": "aluminum (general)",
        "ss304": "stainless steel 304",
        "ss316": "stainless steel 316",
        "carbon steel": "carbon steel / plain steel",
        "cs" : "carbon steel / plain steel",
        "inconel625": "inconel 625",
        "hastelloy c276": "hastelloy (C-276)",
        "hastelloy" : "hastelloy (C-276)",
        "ti grade 2": "titanium (Grade 2)",
        "ti" : "titanium (Grade 2)",
    }
    if key in TYPICAL_K_METALS:
        return TYPICAL_K_METALS[key]
    if key in aliases and aliases[key] in TYPICAL_K_METALS:
        return TYPICAL_K_METALS[aliases[key]]
    # try fuzzy match: exact word in keys
    for k in TYPICAL_K_METALS.keys():
        if key in k:
            return TYPICAL_K_METALS[k]
    raise ValueError(f"No typical thermal conductivity entry for '{metal_name}'")

