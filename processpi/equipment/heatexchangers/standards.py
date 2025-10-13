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


