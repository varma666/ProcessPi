# **Area Class**

The Area class is a subclass of Variable designed to represent a two-dimensional quantity with unit-aware capabilities. It ensures accurate calculations by storing all values internally in its base SI unit, square meters (m2).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Square Meters (m2) |
| :---- | :---- | :---- |
| square meters | m2 | 1 |
| square centimeters | cm2 | 0.0001 |
| square millimeters | mm2 | 0.000001 |
| square kilometers | km2 | 1,000,000 |
| square inches | in2 | 0.00064516 |
| square feet | ft2 | 0.092903 |
| square yards | yd2 | 0.836127 |
| acres | acre | 4046.86 |
| hectares | ha | 10000 |

## **Class Reference**

### **class Area(value, units='m2')**

A class for handling area measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the area. Must be a non-negative number.  
* units : str, default='m2'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create an Area object of 100 square centimeters  
\>\>\> a1 \= Area(100, "cm2")

\# Create an Area object of 0.5 square meters  
\>\>\> a2 \= Area(0.5, "m2")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the area, **always in square meters** (m2). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Area object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Area  
  A new Area object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize an area of 100 square meters  
\>\>\> house\_area\_m2 \= Area(100)

\# Convert to square feet  
\>\>\> house\_area\_ft2 \= house\_area\_m2.to("ft2")

\>\>\> print(house\_area\_ft2)  
1076.391 ft2

#### **Arithmetic Operations**

The Area class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two Area objects. The result is a new Area object with the unit of the first operand.  
* \_\_eq\_\_(self, other)  
  Compares two Area objects for equality based on their internal meter values.

**Examples:**

\# Create two Area objects  
\>\>\> area1 \= Area(1, "m2")  
\>\>\> area2 \= Area(500, "cm2")

\# Add them together  
\>\>\> total\_area \= area1 \+ area2

\>\>\> print(total\_area)  
1.05 m2

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the area, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns an unambiguous string representation of the object.