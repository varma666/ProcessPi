# **Pressure Class**

The Pressure class is a subclass of Variable designed to represent a force per unit area. It ensures accurate calculations by storing all values internally in its base SI unit, Pascals (Pa).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Pascals (Pa) |
| :---- | :---- | :---- |
| Pascals | Pa | 1 |
| kilopascals | kPa | 103 |
| megapascals | MPa | 106 |
| bar | bar | 105 |
| atmospheres | atm | 101325 |
| pounds per square inch | psi | 6894.76 |
| millimeters of mercury | mmHg | 133.322 |
| torr | torr | 133.322 |

## **Class Reference**

### **class Pressure(value, units='Pa')**

A class for handling pressure measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the pressure. Must be a non-negative number.  
* units : str, default='Pa'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a Pressure object of 1 atmosphere  
\>\>\> p1 \= Pressure(1, "atm")

\# Create a Pressure object of 101325 Pascals  
\>\>\> p2 \= Pressure(101325, "Pa")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the pressure as provided during initialization. This is inherited from the Variable base class. |
| **.units** | str | The string representation of the variable's units, as provided during initialization. Inherited from the Variable base class. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Pressure object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Pressure  
  A new Pressure object with the same value, represented in the target unit.

**Examples:**

\# Initialize a pressure of 1 atm  
\>\>\> atm\_pressure \= Pressure(1, "atm")

\# Convert to psi  
\>\>\> psi\_pressure \= atm\_pressure.to("psi")

\>\>\> print(psi\_pressure)  
14.695949 psi

#### **to\_base()**

Converts the pressure to the base SI unit, Pascals (Pa), and returns the numeric value.

**Returns:**

* float  
  The value of the pressure in Pascals (Pa).

#### **from\_base(base\_value, target\_units)**

Creates a new Pressure object from a given base unit value.

**Parameters:**

* base\_value : float  
  The value in the base unit (Pa).  
* target\_units : str  
  The units for the new object.

**Returns:**

* Pressure  
  A new Pressure object with the converted value.

**Raises:**

* **TypeError** : If target\_units is not a valid unit.

### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the pressure, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging, showing the internal values.