# **ThermalConductivity Class**

The ThermalConductivity class is a subclass of Variable designed to represent a material's ability to conduct heat. It ensures accurate calculations by storing all values internally in its base SI unit, Watts per meter-Kelvin (W/mcdotK).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary formula-based conversions to and from the base unit.

| Unit | Symbol | Conversion Factor to Watts per Meter-Kelvin (W/mcdotK) |
| :---- | :---- | :---- |
| Watts per meter-Kelvin | W/mK | 1 |
| kilowatts per meter-Kelvin | kW/mK | 1000 |
| calories per second-centimeter-degree Celsius | cal/scmC | 418.4 |
| British Thermal Units per hour-foot-degree Fahrenheit | BTU/hftF | 1.730735 |

## **Class Reference**

### **class ThermalConductivity(value, units='W/mK')**

A class for handling thermal conductivity measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the thermal conductivity. Must be a non-negative number.  
* units : str, default='W/mK'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a ThermalConductivity object for a value of 0.5 W/mK  
\>\>\> k1 \= ThermalConductivity(0.5, "W/mK")

\# Create a ThermalConductivity object of 1 kW/mK  
\>\>\> k2 \= ThermalConductivity(1, "kW/mK")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the thermal conductivity, **always in Watts per meter-Kelvin** (W/mcdotK). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** ThermalConductivity object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* ThermalConductivity  
  A new ThermalConductivity object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a thermal conductivity of 0.5 W/mK  
\>\>\> k\_W \= ThermalConductivity(0.5)

\# Convert to BTU/hftF  
\>\>\> k\_BTU \= k\_W.to("BTU/hftF")

\>\>\> print(k\_BTU)  
0.289356 BTU/hftF

#### **Arithmetic Operations**

The ThermalConductivity class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two ThermalConductivity objects. The result is a new ThermalConductivity object in the base unit (W/mcdotK).  
* \_\_eq\_\_(self, other)  
  Compares two ThermalConductivity objects for equality based on their internal base unit values.

**Examples:**

\# Create two ThermalConductivity objects  
\>\>\> k1 \= ThermalConductivity(10, "W/mK")  
\>\>\> k2 \= ThermalConductivity(0.01, "kW/mK")

\# Add them together  
\>\>\> total\_k \= k1 \+ k2

\>\>\> print(total\_k)  
20.0 W/mK

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the thermal conductivity, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.