# **Class: AceticAcid**

### **Description**

The AceticAcid class represents the properties and constants for Acetic Acid (CH3​COOH).

This class provides a comprehensive set of physical and thermodynamic properties for Acetic Acid, which are essential for various process engineering calculations. These properties are stored as class attributes and are available for use by other calculation modules within the ProcessPI library.

### **Properties**

* **name** (string): The common name of the compound.  
* **formula** (string): The chemical formula (CH3​COOH).  
* **molecular\_weight** (float): The molar mass in g/mol.  
* **\_critical\_temperature** (Temperature): The critical temperature, above which a substance cannot exist as a liquid, regardless of pressure. Value: 591.95 K.  
* **\_critical\_pressure** (Pressure): The critical pressure, the vapor pressure at the critical temperature. Value: 5.786 MPa.  
* **\_critical\_volume** (Volume): The critical volume per kmole. Value: 0.177 m3.  
* **\_critical\_zc** (float): The critical compressibility factor. Value: 0.208.  
* **\_critical\_acentric\_factor** (float): The acentric factor, a measure of the non-sphericity of the molecule. Value: 0.4665.  
* **\_density\_constants** (list\[float\]): Constants for calculating density as a function of temperature.  
* **\_specific\_heat\_constants** (list\[float\]): Constants for calculating specific heat capacity as a function of temperature.  
* **\_viscosity\_constants** (list\[float\]): Constants for calculating viscosity as a function of temperature.  
* **\_thermal\_conductivity\_constants** (list\[float\]): Constants for calculating thermal conductivity as a function of temperature.  
* **\_vapor\_pressure\_constants** (list\[float\]): Constants for calculating vapor pressure as a function of temperature using the Antoine equation or similar models.  
* **\_enthalpy\_constants** (list\[float\]): Constants for calculating enthalpy as a function of temperature.

### **Methods**

The properties of the AceticAcid class are calculated using the following methods, which are inherited from the base Component class.

* **phase()**: Detects the phase of the substance ("gas" or "liquid") by comparing the system pressure to the calculated vapor pressure. The rule is: "gas" if P\<Pvap​, otherwise "liquid".  
* **density()**:  
  * Gas Phase: Calculates density using the Ideal Gas Law:  
    ρ=Runiversal​⋅TP⋅MWkg/mol​​  
  * Liquid Phase: Calculates density using the DIPPR correlation:  
    ρ=B(1+(1−Tc​T​)n)A​⋅MWg/mol​

    (Note: The constants A, B, Tc​, and n are derived from \_density\_constants).  
* specific\_heat(): Calculates specific heat capacity (Cp​) as a polynomial function of temperature:  
  Cp​=i=0∑4​Ci​⋅Ti⋅MWg/mol​

  (Note: The constants Ci​ are derived from \_specific\_heat\_constants).  
* **viscosity()**:  
  * Liquid Phase: Calculates viscosity (μ) using the DIPPR correlation:  
    ln(μ)=A+TB​+Cln(T)+DTE

    (Note: The constants A,B,C,D,E are derived from \_viscosity\_constants).  
  * **Gas Phase**: Calculates viscosity using Sutherland's Law.  
* thermal\_conductivity(): Calculates thermal conductivity (k) as a polynomial function of temperature:  
  k=i=0∑4​Ci​⋅Ti

  (Note: The constants Ci​ are derived from \_thermal\_conductivity\_constants).  
* vapor\_pressure(): Calculates vapor pressure (Pvap​) using the Antoine-style equation:  
  ln(Pvap​)=A+TB​+Cln(T)+DTE

  (Note: The constants A,B,C,D,E are derived from \_vapor\_pressure\_constants).  
* enthalpy(): Calculates the enthalpy of vaporization (ΔHvap​) using a correlation based on reduced temperature (Tr​=Tc​T​):  
  ΔHvap​=A⋅(1−Tr​)B+C(1−Tr​)+D(1−Tr​)2+E(1−Tr​)3⋅MWg/mol​

  (Note: The constants A,B,C,D,E are derived from \_enthalpy\_constants).