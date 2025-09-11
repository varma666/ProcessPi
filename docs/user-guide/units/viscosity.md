# **Viscosity Class**

The Viscosity class is a subclass of Variable designed to represent a quantity of viscosity. It uniquely handles **two different types of viscosity**: dynamic and kinematic. The class automatically determines the viscosity type based on the provided units and performs conversions only within that type.

## **Supported Units**

The class distinguishes between two sets of units for dynamic and kinematic viscosity.

### **Dynamic Viscosity Units**

The base SI unit for dynamic viscosity is Pascal-second (Pacdots).

| Unit | Symbol | Conversion Factor to Pascal-second (Pacdots) |
| :---- | :---- | :---- |
| Pascal-second | Pa·s | 1 |
| milliPascal-second | mPa·s | 10−3 |
| centipoise | cP | 10−3 |
| poise | P | 0.1 |

### **Kinematic Viscosity Units**

The base SI unit for kinematic viscosity is meters-squared per second (m2/s).

| Unit | Symbol | Conversion Factor to meter-squared per second (m2/s) |
| :---- | :---- | :---- |
| meter-squared per second | m2/s | 1 |
| centimeter-squared per second | cm2/s | 10−4 |
| millimeter-squared per second | mm2/s | 10−6 |
| centistoke | cSt | 10−6 |
| stoke | St | 10−4 |

## **Class Reference**

### **class Viscosity(value, units='Pa·s')**

A class for handling viscosity measurements. The type of viscosity (dynamic or kinematic) is determined automatically based on the units argument.

**Parameters:**

* value : float or int  
  The numeric value of the viscosity. Must be a non-negative number.  
* units : str, default='Pa·s'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative or if units is not a valid unit.

**Examples:**

\# Create a Viscosity object for a dynamic viscosity of 1e-3 Pa·s  
\>\>\> v1 \= Viscosity(1e-3, units="Pa·s")

\# Create a Viscosity object for a kinematic viscosity of 1 cSt  
\>\>\> v2 \= Viscosity(1, units="cSt")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the viscosity, always stored in its base SI unit (Pacdots for dynamic, m2/s for kinematic). |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |
| **.viscosity\_type** | str | Indicates the type of viscosity, either "dynamic" or "kinematic". |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Viscosity object converted to the target\_unit. This method can only convert between units of the **same viscosity type** (e.g., dynamic to dynamic). The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be a valid unit for the object's viscosity type.

**Returns:**

* Viscosity  
  A new Viscosity object with the converted value and target unit.

**Raises:**

* **ValueError** : If target\_unit is not a valid unit for the viscosity type.

**Examples:**

\# Initialize a dynamic viscosity of 1 Pa·s  
\>\>\> v\_Pa \= Viscosity(1)

\# Convert to centipoise (cP)  
\>\>\> v\_cP \= v\_Pa.to("cP")

\>\>\> print(v\_cP)  
1000.0 cP (dynamic)

### **Arithmetic Operations**

The Viscosity class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two Viscosity objects. Both objects must be of the same viscosity type. The result is a new Viscosity object in the original units of the first operand.  
* \_\_eq\_\_(self, other)  
  Compares two Viscosity objects for equality. It checks if they are both Viscosity instances, have the same internal value, and the same viscosity type.

**Examples:**

\# Create two dynamic viscosity objects  
\>\>\> v1 \= Viscosity(10, "Pa·s")  
\>\>\> v2 \= Viscosity(5000, "mPa·s")

\# Add them together (5000 mPa·s \= 5 Pa·s)  
\>\>\> total\_v \= v1 \+ v2

\>\>\> print(total\_v)  
15.0 Pa·s (dynamic)

### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the viscosity, rounded to six decimal places, using its original value, unit, and type.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging, showing the original value, unit, and viscosity type.