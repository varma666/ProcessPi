# **HeatTransferCoefficient Class**

The HeatTransferCoefficient class is a subclass of Variable designed to represent the heat transfer rate per unit area per unit temperature difference. It ensures accurate calculations by storing all values internally in its base SI unit, Watts per square meter-Kelvin (W/m2cdotK).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Watts per Square Meter-Kelvin (W/m2cdotK) |
| :---- | :---- | :---- |
| Watts per square meter-Kelvin | W/m2K | 1 |
| kilowatts per square meter-Kelvin | kW/m2K | 1000 |
| calories per second per square centimeter-degree Celsius | cal/scm2C | 41840 |
| British Thermal Units per hour per square foot-degree Fahrenheit | BTU/hft2F | 5.678263 |

## **Class Reference**

### **class HeatTransferCoefficient(value, units='W/m2K')**

A class for handling heat transfer coefficient measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the heat transfer coefficient. Must be a non-negative number.  
* units : str, default='W/m2K'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a HeatTransferCoefficient object of 200 W/m²K  
\>\>\> h1 \= HeatTransferCoefficient(200)

\# Create a HeatTransferCoefficient object of 0.2 kW/m²K  
\>\>\> h2 \= HeatTransferCoefficient(0.2, "kW/m2K")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the heat transfer coefficient, **always in Watts per square meter-Kelvin** (W/m2cdotK). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** HeatTransferCoefficient object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* HeatTransferCoefficient  
  A new HeatTransferCoefficient object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a heat transfer coefficient of 500 W/m²K  
\>\>\> h\_W \= HeatTransferCoefficient(500)

\# Convert to BTU/hft²F  
\>\>\> h\_BTU \= h\_W.to("BTU/hft2F")

\>\>\> print(h\_BTU)  
88.058309 BTU/hft2F

#### **Arithmetic Operations**

The HeatTransferCoefficient class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two HeatTransferCoefficient objects. The result is a new HeatTransferCoefficient object in the base unit (W/m2cdotK).  
* \_\_eq\_\_(self, other)  
  Compares two HeatTransferCoefficient objects for equality based on their internal base unit values.

**Examples:**

\# Create two HeatTransferCoefficient objects  
\>\>\> h1 \= HeatTransferCoefficient(100, "W/m2K")  
\>\>\> h2 \= HeatTransferCoefficient(0.1, "kW/m2K")

\# Add them together  
\>\>\> total\_h \= h1 \+ h2

\>\>\> print(total\_h)  
200.0 W/m2K

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the heat transfer coefficient, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.