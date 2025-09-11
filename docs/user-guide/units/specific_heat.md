# **SpecificHeat Class**

The SpecificHeat class is a subclass of Variable designed to represent the amount of energy required to raise the temperature of a unit mass of a substance by one degree. It stores all values internally in its base unit, kilojoules per kilogram-Kelvin (kJ/kgcdotK).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Kilojoules per Kilogram-Kelvin (kJ/kgcdotK) |
| :---- | :---- | :---- |
| kilojoules per kilogram-Kelvin | kJ/kgK | 1 |
| Joules per kilogram-Kelvin | J/kgK | 0.001 |
| calories per gram-Kelvin | cal/gK | 4.1868 |
| British Thermal Units per pound-degree Fahrenheit | BTU/lbF | 9.7423 |
| kilocalories per kilogram-Kelvin | kcal/kgK | 4.1868 |

## **Class Reference**

### **class SpecificHeat(value, units='kJ/kgK')**

A class for handling specific heat capacity measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the specific heat. Must be a non-negative number.  
* units : str, default='kJ/kgK'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a SpecificHeat object of 4.186 kJ/kgK  
\>\>\> cp1 \= SpecificHeat(4.186, "kJ/kgK")

\# Create a SpecificHeat object of 1.0 cal/gK  
\>\>\> cp2 \= SpecificHeat(1.0, "cal/gK")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the specific heat, **always in kilojoules per kilogram-Kelvin** (kJ/kgcdotK). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** SpecificHeat object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* SpecificHeat  
  A new SpecificHeat object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a specific heat of 4.186 kJ/kgK  
\>\>\> water\_cp \= SpecificHeat(4.186, "kJ/kgK")

\# Convert to BTU/lbF  
\>\>\> water\_cp\_btu \= water\_cp.to("BTU/lbF")

\>\>\> print(water\_cp\_btu)  
1.79159 BTU/lbF

#### **Arithmetic Operations**

The SpecificHeat class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two SpecificHeat objects. The result is a new SpecificHeat object in the base unit (kJ/kgcdotK).  
* \_\_eq\_\_(self, other)  
  Compares two SpecificHeat objects for equality based on their internal base unit values.

**Examples:**

\# Create two SpecificHeat objects  
\>\>\> cp1 \= SpecificHeat(1, "kJ/kgK")  
\>\>\> cp2 \= SpecificHeat(1, "kJ/kgK")

\# Add them together  
\>\>\> total\_cp \= cp1 \+ cp2

\>\>\> print(total\_cp)  
2.0 kJ/kgK

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the specific heat, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.