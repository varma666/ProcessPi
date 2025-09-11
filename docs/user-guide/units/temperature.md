# **Temperature Class**

The Temperature class is a subclass of Variable designed to represent a temperature quantity. It ensures accurate conversions and calculations by storing all values internally in its base SI unit, Kelvin (K).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary formula-based conversions to and from the base unit.

| Unit | Symbol | Conversion Formula to Kelvin (K) |
| :---- | :---- | :---- |
| Kelvin | K | T\_K=T\_K |
| Celsius | C | T\_K=T\_C+273.15 |
| Fahrenheit | F | T\_K=(T\_F−32)times5/9+273.15 |

## **Class Reference**

### **class Temperature(value, units='K')**

A class for handling temperature measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the temperature.  
* units : str, default='K'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If units is not a valid unit.

**Examples:**

\# Create a Temperature object of 100°C  
\>\>\> t1 \= Temperature(100, "C")

\# Create a Temperature object of 373.15 K  
\>\>\> t2 \= Temperature(373.15)

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the temperature, **always in Kelvin** (K). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Temperature object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Temperature  
  A new Temperature object with the same value, represented in the target unit.

**Raises:**

* **ValueError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a temperature of 25°C  
\>\>\> temp\_C \= Temperature(25, "C")

\# Convert to Fahrenheit  
\>\>\> temp\_F \= temp\_C.to("F")

\>\>\> print(temp\_F)  
77.0 F

#### **Arithmetic Operations**

The Temperature class handles addition and subtraction differently from other quantities due to the physical nature of temperature scales.

* \_\_add\_\_(self, other)  
  Raises a TypeError. Direct addition of two temperatures is not supported as it is not physically meaningful.  
* \_\_sub\_\_(self, other)  
  Subtracts a Temperature object from another. The result is a numeric value representing the temperature difference in Kelvin.  
  Raises: TypeError if other is not a Temperature instance.  
* \_\_eq\_\_(self, other)  
  Compares two Temperature objects for equality based on their internal Kelvin values.

**Examples:**

\# Create two Temperature objects  
\>\>\> t1 \= Temperature(20, "C")  
\>\>\> t2 \= Temperature(10, "C")

\# Subtract them to get the temperature difference  
\>\>\> diff \= t1 \- t2

\>\>\> print(f"{diff} K")  
10.0 K

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the temperature, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.