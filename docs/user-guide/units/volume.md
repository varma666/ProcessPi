# **Volume Class**

The Volume class is a subclass of Variable designed to represent a quantity of volume. It handles automatic unit conversion by storing all internal values in the base SI unit, cubic meters (m3).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary conversions to and from the base unit.

| Unit | Symbol | Conversion Factor to Cubic Meters (m3) |
| :---- | :---- | :---- |
| cubic meter | m3 | 1 |
| liter | L | 0.001 |
| milliliter | mL | 10−6 |
| cubic centimeter | cm3 | 10−6 |
| cubic foot | ft3 | 0.0283168 |
| cubic inch | in3 | 1.63871times10−5 |
| US gallon | gal | 0.00378541 |
| oil barrel | bbl | 0.158987 |

## **Class Reference**

### **class Volume(value, units='m3')**

A class for handling volume measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the volume. Must be a non-negative number.  
* units : str, default='m3'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a Volume object for 100 liters  
\>\>\> v1 \= Volume(100, "L")

\# Create a Volume object for 1 cubic meter  
\>\>\> v2 \= Volume(1, "m3")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the volume, **always in cubic meters** (m3). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Volume object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Volume  
  A new Volume object with the converted value and target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a volume of 5 gallons  
\>\>\> v\_gal \= Volume(5, "gal")

\# Convert to liters  
\>\>\> v\_L \= v\_gal.to("L")

\>\>\> print(v\_L)  
18.92705 L

### **Arithmetic Operations**

The Volume class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two Volume objects. The result is a new Volume object in cubic meters. The original objects remain unchanged.  
* \_\_eq\_\_(self, other)  
  Compares two Volume objects for equality. It checks if they are both Volume instances and have the same internal value.

**Examples:**

\# Create two volume objects  
\>\>\> v1 \= Volume(10, "L")  
\>\>\> v2 \= Volume(1, "m3")

\# Add them together (1 m3 \= 1000 L)  
\>\>\> total\_v \= v1 \+ v2

\>\>\> print(total\_v)  
1010.0 L

### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the volume, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging, showing the original value and unit.