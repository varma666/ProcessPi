# **ThermalResistance Class**

The ThermalResistance class is a subclass of Variable designed to represent a material's resistance to heat flow. It simplifies calculations by internally storing all values in its base SI unit, Kelvin per Watt (K/W).

## **Supported Units**

The following units are supported for initialization and conversion. Note that some units, like degrees Celsius per Watt (^\\\\circ C/W), are numerically equivalent to the base SI unit.

| Unit | Symbol | Conversion Factor to Kelvin per Watt (K/W) |
| :---- | :---- | :---- |
| Kelvin per Watt | K/W | 1 |
| Celsius per Watt | C/W | 1 |
| hour-foot²-degree Fahrenheit per British Thermal Unit | hrft2F/BTU | 0.1761 |
| meter²-Kelvin per Watt | m2K/W | 1 |

## **Class Reference**

### **class ThermalResistance(value, units='K/W')**

A class for handling thermal resistance measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the thermal resistance. Must be a positive number.  
* units : str, default='K/W'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is not a positive number.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a ThermalResistance object for a value of 0.5 K/W  
\>\>\> r1 \= ThermalResistance(0.5, "K/W")

\# Create a ThermalResistance object of 2 C/W (numerically equivalent to 2 K/W)  
\>\>\> r2 \= ThermalResistance(2, "C/W")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the thermal resistance, **always in Kelvin per Watt** (K/W). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** ThermalResistance object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* ThermalResistance  
  A new ThermalResistance object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a thermal resistance of 2 K/W  
\>\>\> r\_K \= ThermalResistance(2)

\# Convert to hrft2F/BTU  
\>\>\> r\_BTU \= r\_K.to("hrft2F/BTU")

\>\>\> print(r\_BTU)  
11.353457 hrft2F/BTU

#### **Arithmetic Operations**

The ThermalResistance class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two ThermalResistance objects. The result is a new ThermalResistance object in the base unit (K/W).  
* \_\_eq\_\_(self, other)  
  Compares two ThermalResistance objects for equality based on their internal base unit values.

**Examples:**

\# Create two ThermalResistance objects  
\>\>\> r1 \= ThermalResistance(10, "K/W")  
\>\>\> r2 \= ThermalResistance(5, "C/W")

\# Add them together  
\>\>\> total\_r \= r1 \+ r2

\>\>\> print(total\_r)  
15.0 K/W

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the thermal resistance, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.