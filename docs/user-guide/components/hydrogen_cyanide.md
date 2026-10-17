# **Class: `HydrogenCyanide`**

## **Description**

The `HydrogenCyanide` class represents the properties and constants for Hydrogen Cyanide (HCN).  
It provides physical and thermodynamic properties required in process engineering simulations and calculations.  
All constants are from Perry's Chemical Engineers' Handbook, 8th ed., Section 2 (compound no. 186).

## **Properties**

* **`name`** (string): Hydrogen Cyanide  
* **`formula`** (string): HCN  
* **`molecular_weight`** (float): 27.025 g/mol  

## **Class Reference**

**`class HydrogenCyanide()`**

**Parameters:**  
* `temperature`: `Temperature`, default = `Temperature(25,"C")`  
* `pressure`: `Pressure`, default = `Pressure(1,"atm")`  
* `density`: `Density`, default = `None`  
* `specific_heat`: `SpecificHeat`, default = `None`  
* `viscosity`: `Viscosity`, default = `None`  
* `thermal_conductivity`: `ThermalConductivity`, default = `None`  
* `vapor_pressure`: `Pressure`, default = `None`  
* `enthalpy`: `HeatOfVaporization`, default = `None`  
* `phase`: `str`, default = `None` (`"liquid"` or `"gas"` overrides the vapor-pressure test)  

## **Methods**

The properties of the `HydrogenCyanide` class are calculated using the following methods, inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"liquid"` or `"gas"`) by comparing the system pressure and vapor pressure. (Hydrogen cyanide boils at 298.8 K (25.7 °C) at 1 atm by its Table 2-8 row, so at 25 °C and 1 atm it is a liquid (vapor pressure 98.8 kPa) and at 30 °C a gas.)  
* **`density()`**:  
  * **Liquid Phase**: DIPPR Eq. 105 (Perry's Table 2-32)  
  * **Gas Phase**: Uses the Ideal Gas Law  
* **`specific_heat()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-153)  
  * **Gas Phase**: Ideal-gas heat capacity (Cp), DIPPR Eq. 107 (Perry's Table 2-156)  
* **`viscosity()`**:  
  * **Liquid Phase**: DIPPR Eq. 101 (Perry's Table 2-313)  
  * **Gas Phase**: Uses Sutherland’s Law with the base class's air constants (no gas viscosity data for this component yet)  
* **`thermal_conductivity()`**:  
  * **Liquid Phase**: Polynomial function of temperature (Perry's Table 2-315)  
  * **Gas Phase**: Vapor thermal conductivity (k), DIPPR Eq. 102 (Perry's Table 2-314)  
* **`vapor_pressure()`**: DIPPR Eq. 101 (Perry's Table 2-8).  
* **`enthalpy()`**: Enthalpy of vaporization (ΔHvap), DIPPR Eq. 106 (Perry's Table 2-150).  

## **Examples**

```py
from processpi.components import HydrogenCyanide
from processpi.units import *

hcn = HydrogenCyanide(temperature=Temperature(25, "C"))
print(hcn.phase())
print(hcn.density().to("kg/m3"))
print(hcn.viscosity().to("Pa·s"))
print(hcn.specific_heat().to("J/kgK"))
print(hcn.thermal_conductivity().to("W/mK"))
print(hcn.vapor_pressure().to("Pa"))
print(hcn.enthalpy().to("J/kg"))
```

### Output

```text
liquid
679.540688 kg/m3
0.000183 Pa·s (dynamic)
2628.112043 J/kgK
0.225596 W/mK
98839.880203 Pa
997247.528341 J/kg
```
