# **Class: `AceticAcid`**

## **Description**

The `AceticAcid` class represents the properties and constants for Acetic Acid (CH<sub>3</sub>​COOH).

This class provides a comprehensive set of physical and thermodynamic properties for Acetic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library.

## **Properties**

* **`name`** (string): The common name of the compound.  
* **`formula`** (string): The chemical formula (CH<sub>3</sub>​COOH).  
* **`molecular_weight`** (float): The molar mass in g/mol.

## **Class Reference**

**`class AecticAcid()`**

A class for handling Acetic Acid properties.

**Parameters:**

* `temperature` : `Temperature`, default = `Temperature(35,"C")`
* `pressure` : `Pressure`, default = `Pressure(1,"atm")`
* `density` : `Density`, default = `None`
* `specific_heat` : `SpecificHeat`, default = `None`
* `viscosity` : `Viscosity`, default = `None`  
* `thermal_conductivity` : `ThermalConductivity`, default = `None`
* `vapor_pressure` : `Pressure`, default = `None`  
* `enthalpy` : `HeatOfVaporization`, default = `None` 


## **Methods**

The properties of the `AceticAcid` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the calculated vapor pressure. The rule is: `"gas"` if **P < P<sub>vap</sub>,​** otherwise `"liquid"`.  
* **`density()`**:  
    * **Gas Phase**: Calculates density using the Ideal Gas Law
       
    * **Liquid Phase**: Calculates density using the DIPPR correlation  
      
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature  

    
* **`viscosity()`**:  
    * **Liquid Phase**: Calculates viscosity (μ) using the DIPPR correlation:  
          
    * **Gas Phase**: Calculates viscosity using Sutherland's Law. 

* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature  
  
    
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using the Antoine-style equation  
  
   
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature  
  ​
## **Examples**

**1. Acetone at 35 °C**

```py
# Importing Acetone
>>> from processpi.components import Acetone
# Importing Units
>>> from processpi.units import *
# Creating Acetone at 35 C Temperature
>>> acetone = Acetone(temperature=Temperature(35, "C"))
>>> print(acetone.density().to("kg/m3"))

>>> print(acetone.viscosity().to("Pa·s"))

>>> print(acetone.specific_heat().to("J/kgK"))

>>> print(acetone.thermal_conductivity().to("W/mK"))

>>> print(acetone.vapor_pressure().to("Pa"))

>>> print(acetone.enthalpy().to("J/kg"))

```

**2. Acetone at higher temperature (60 °C) with unit conversion**
```py
# Creating Acetone at 60 C Temperature
>>> acetone_high = Acetone(temperature=Temperature(60, "C"))
>>> print(acetone_high.density().to("lb/ft3"))

>>> print(acetone_high.viscosity().to("cP"))

```

  
