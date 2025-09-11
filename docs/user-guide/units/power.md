# **Power Class**

The Power class is a subclass of Variable designed to represent the rate at which work is done or energy is transferred. It ensures accurate calculations by storing all values internally in its base SI unit, Watts (W).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Watts (W) |
| :---- | :---- | :---- |
| Watts | W | 1 |
| kilowatts | kW | 103 |
| megawatts | MW | 106 |
| mechanical horsepower | hp | 745.7 |
| British Thermal Units per hour | BTU/h | 0.29307107 |

## **Class Reference**

### **class Power(value, units='W')**

A class for handling power measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the power. Must be a non-negative number.  
* units : str, default='W'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative or units is not a valid unit.

**Examples:**

\# Create a Power object of 1000 Watts  
\>\>\> p1 \= Power(1000)

\# Create a Power object of 1 kilowatt  
\>\>\> p2 \= Power(1, "kW")

\# Create a Power object of 1.34 horsepower  
\>\>\> p4 \= Power(1.34, "hp")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the power, **always in Watts** (W). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Power object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Power  
  A new Power object with the same value, represented in the target unit.

**Raises:**

* **ValueError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a power of 1000 W  
\>\>\> power\_W \= Power(1000)

\# Convert to kilowatts  
\>\>\> power\_kW \= power\_W.to("kW")

\>\>\> print(power\_kW)  
1.0 kW

#### **Arithmetic Operations**

The Power class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two Power objects. The result is a new Power object in the unit of the first operand.  
* \_\_eq\_\_(self, other)  
  Compares two Power objects for equality based on their internal base unit values.

**Examples:**

\# Create two Power objects  
\>\>\> p1 \= Power(1, "kW")  
\>\>\> p2 \= Power(500, "W")

\# Add them together  
\>\>\> total\_power \= p1 \+ p2

\>\>\> print(total\_power)  
1.5 kW

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the power, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns an unambiguous string representation of the object.