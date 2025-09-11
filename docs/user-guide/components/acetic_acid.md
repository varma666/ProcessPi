# **Class: `AceticAcid`**

### **Description**

The `AceticAcid` class represents the properties and constants for Acetic Acid (CH<sub>3</sub>​COOH).

This class provides a comprehensive set of physical and thermodynamic properties for Acetic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library.

### **Properties**

* **`name`** (string): The common name of the compound.  
* **`formula`** (string): The chemical formula (CH<sub>3</sub>​COOH).  
* **`molecular_weight`** (float): The molar mass in g/mol.  

### **Methods**

The properties of the `AceticAcid` class are calculated using the following methods, which are inherited from the base `Component` class.

* **`phase()`**: Detects the phase of the substance (`"gas"` or `"liquid"`) by comparing the system pressure to the calculated vapor pressure. The rule is: `"gas"` if **P \< P<sub>vap</sub>,​** otherwise `"liquid"`.  
* **`density()`**:  
  * **Gas Phase**: Calculates density using the Ideal Gas Law:
    
    ![equation](https://latex.codecogs.com/svg.latex?\rho=\frac{R_{universal}\cdot%20T\cdot%20P}{MW_{kg/mol}})
    
  * **Liquid Phase**: Calculates density using the DIPPR correlation:  
    ρ=B(1+(1−Tc​T​)n)A​⋅MWg/mol​

      
* **`specific_heat()`**: Calculates specific heat capacity (Cp​) as a polynomial function of temperature:  
  Cp​=i=0∑4​Ci​⋅Ti⋅MWg/mol​

    
* **`viscosity()`**:  
  * Liquid Phase: Calculates viscosity (μ) using the DIPPR correlation:  
    ln(μ)=A+TB​+Cln(T)+DTE

      
  * **Gas Phase**: Calculates viscosity using Sutherland's Law.  
* **`thermal_conductivity()`**: Calculates thermal conductivity (k) as a polynomial function of temperature:  
  k=i=0∑4​Ci​⋅Ti

    
* **`vapor_pressure()`**: Calculates vapor pressure (Pvap​) using the Antoine-style equation:  
  ln(Pvap​)=A+TB​+Cln(T)+DTE

   
* **`enthalpy()`**: Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature (Tr​=Tc​T​):  
  ΔHvap​=A⋅(1−Tr​)B+C(1−Tr​)+D(1−Tr​)2+E(1−Tr​)3⋅MWg/mol​

  
