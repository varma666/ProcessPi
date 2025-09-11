# **Velocity Class**

The Velocity class is a subclass of Variable designed to represent a quantity of velocity. It handles automatic unit conversion by storing all internal values in the base SI unit, meters per second (m/s).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary conversions to and from the base unit.

| Unit | Symbol | Conversion Factor to Meters per Second (m/s) |
| :---- | :---- | :---- |
| meters per second | m/s | 1 |
| kilometers per hour | km/h | 1/3.6 |
| centimeters per second | cm/s | 0.01 |
| feet per second | ft/s | 0.3048 |
| miles per hour | mph | 0.44704 |

## **Class Reference**

### **class Velocity(value, units='m/s')**

A class for handling velocity measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the velocity.  
* units : str, default='m/s'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If units is not a valid unit.

**Examples:**

\# Create a Velocity object for a value of 25 m/s  
\>\>\> v1 \= Velocity(25, "m/s")

\# Create a Velocity object for 100 km/h  
\>\>\> v2 \= Velocity(100, "km/h")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the velocity, **always in meters per second** (m/s). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Velocity object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Velocity  
  A new Velocity object with the same value, represented in the target unit.

**Raises:**

* **ValueError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a velocity of 25 m/s  
\>\>\> v\_ms \= Velocity(25)

\# Convert to km/h  
\>\>\> v\_kmh \= v\_ms.to("km/h")

\>\>\> print(v\_kmh)  
90.0 km/h

### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the velocity, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.