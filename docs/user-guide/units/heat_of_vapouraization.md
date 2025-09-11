# **HeatOfVaporization Class**

The HeatOfVaporization class is a subclass of Variable designed to represent the heat required to change a unit mass of a substance from liquid to gas at a given pressure. It ensures accurate calculations by storing all values internally in its base SI unit, Joules per kilogram (J/kg).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Joules per Kilogram (J/kg) |
| :---- | :---- | :---- |
| Joules per kilogram | J/kg | 1 |
| kilojoules per kilogram | kJ/kg | 103 |
| megajoules per kilogram | MJ/kg | 106 |
| calories per gram | cal/g | 4184 |
| British Thermal Units per pound | BTU/lb | 2326 |

## **Class Reference**

### **class HeatOfVaporization(value, units='J/kg')**

A class for handling heat of vaporization measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the heat of vaporization. Must be a non-negative number.  
* units : str, default='J/kg'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative or units is not a valid unit.

**Examples:**

\# Create a HeatOfVaporization object of 2.257 MJ/kg  
\>\>\> hv1 \= HeatOfVaporization(2257000)

\# Create a HeatOfVaporization object of 540 cal/g  
\>\>\> hv2 \= HeatOfVaporization(540, "cal/g")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the heat of vaporization, **always in Joules per kilogram** (J/kg). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** HeatOfVaporization object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* HeatOfVaporization  
  A new HeatOfVaporization object with the same value, represented in the target unit.

**Raises:**

* **ValueError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a heat of vaporization of 2257000 J/kg  
\>\>\> water\_hv \= HeatOfVaporization(2257000, "J/kg")

\# Convert to cal/g  
\>\>\> water\_hv\_cal \= water\_hv.to("cal/g")

\>\>\> print(water\_hv\_cal)  
540.057352 cal/g

#### **Arithmetic Operations**

The HeatOfVaporization class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two HeatOfVaporization objects. The result is a new HeatOfVaporization object with the unit of the first operand.  
* \_\_eq\_\_(self, other)  
  Compares two HeatOfVaporization objects for equality based on their internal base unit values.

**Examples:**

\# Create two HeatOfVaporization objects  
\>\>\> hv1 \= HeatOfVaporization(100, "kJ/kg")  
\>\>\> hv2 \= HeatOfVaporization(20, "kJ/kg")

\# Add them together  
\>\>\> total\_hv \= hv1 \+ hv2

\>\>\> print(total\_hv)  
120.0 kJ/kg

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the heat of vaporization, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns an unambiguous string representation suitable for developers and debugging.