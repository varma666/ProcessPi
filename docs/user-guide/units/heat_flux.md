# **HeatFlux Class**

The HeatFlux class is a subclass of Variable designed to represent heat transfer rate per unit area. It ensures accurate calculations by storing all values internally in its base SI unit, Watts per square meter (W/m2).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Watts per Square Meter (W/m2) |
| :---- | :---- | :---- |
| Watts per square meter | W/m2 | 1 |
| kilowatts per square meter | kW/m2 | 1000 |
| Watts per square centimeter | W/cm2 | 10000 |
| British Thermal Units per hour per square foot | BTU/hft2 | 3.1546 |
| calories per second per square centimeter | cal/scm2 | 41840 |

## **Class Reference**

### **class HeatFlux(value, units='W/m2')**

A class for handling heat flux measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the heat flux. Must be a non-negative number.  
* units : str, default='W/m2'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a HeatFlux object of 300 W/m²  
\>\>\> q1 \= HeatFlux(300)

\# Create a HeatFlux object of 0.3 kW/m²  
\>\>\> q2 \= HeatFlux(0.3, "kW/m2")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the heat flux, **always in Watts per square meter** (W/m2). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** HeatFlux object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* HeatFlux  
  A new HeatFlux object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a heat flux of 1000 W/m²  
\>\>\> heat\_flux\_W \= HeatFlux(1000)

\# Convert to kW/m²  
\>\>\> heat\_flux\_kW \= heat\_flux\_W.to("kW/m2")

\>\>\> print(heat\_flux\_kW)  
1.0 kW/m2

#### **Arithmetic Operations**

The HeatFlux class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two HeatFlux objects. The result is a new HeatFlux object in the base unit (W/m2).  
* \_\_eq\_\_(self, other)  
  Compares two HeatFlux objects for equality based on their internal base unit values.

**Examples:**

\# Create two HeatFlux objects  
\>\>\> q1 \= HeatFlux(100, "W/m2")  
\>\>\> q2 \= HeatFlux(0.01, "W/cm2")

\# Add them together  
\>\>\> total\_heat\_flux \= q1 \+ q2

\>\>\> print(total\_heat\_flux)  
200.0 W/m2

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the heat flux, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging.