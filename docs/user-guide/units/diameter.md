# **Diameter Class**

The Diameter class is a subclass of Variable designed to represent the length of a diameter. It ensures accurate calculations by storing all values internally in its base SI unit, meters (m).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Meters (m) |
| :---- | :---- | :---- |
| meters | m | 1 |
| centimeters | cm | 0.01 |
| millimeters | mm | 0.001 |
| inches | in | 0.0254 |
| feet | ft | 0.3048 |

## **Class Reference**

### **class Diameter(value, units='m')**

A class for handling diameter measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the diameter. Must be a non-negative number.  
* units : str, default='m'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a Diameter object of 10 meters  
\>\>\> d1 \= Diameter(10)

\# Create a Diameter object of 12 inches  
\>\>\> d2 \= Diameter(12, "in")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the diameter, **always in meters** (m). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Diameter object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Diameter  
  A new Diameter object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a diameter of 5 meters  
\>\>\> pipe\_diameter\_m \= Diameter(5)

\# Convert to feet  
\>\>\> pipe\_diameter\_ft \= pipe\_diameter\_m.to("ft")

\>\>\> print(pipe\_diameter\_ft)  
16.4042 ft

#### **to\_base()**

Returns the internal numeric value of the diameter in its base SI unit, meters (m).

**Returns:**

* float  
  The value of the diameter in meters.

#### **Arithmetic Operations**

The Diameter class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two Diameter objects. The result is a new Diameter object with the unit of the first operand.  
* \_\_eq\_\_(self, other)  
  Compares two Diameter objects for equality based on their internal meter values.

**Examples:**

\# Create two Diameter objects  
\>\>\> d1 \= Diameter(1, "m")  
\>\>\> d2 \= Diameter(10, "cm")

\# Add them together  
\>\>\> total\_diameter \= d1 \+ d2

\>\>\> print(total\_diameter)  
1.1 m

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the diameter, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns an unambiguous string representation of the object, suitable for debugging.