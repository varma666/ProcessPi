# **VolumetricFlowRate Class**

The VolumetricFlowRate class is a subclass of Variable that represents the volume of fluid passing a point per unit of time. The base SI unit for volumetric flow rate is cubic meters per second (m3/s).

## **Supported Units**

The following units are supported for initialization and conversion. The class automatically converts all internal values to the base unit (m3/s).

| Unit | Symbol | Conversion Factor to Cubic Meters per Second (m3/s) |
| :---- | :---- | :---- |
| cubic meter per second | m3/s | 1 |
| cubic meter per hour | m3/h | frac13600 |
| liter per second | L/s | frac11000 |
| liter per minute | L/min | frac160000 |
| liter per hour | L/h | frac13600000 |
| cubic foot per second | ft3/s | 0.0283168 |
| cubic foot per minute | ft3/min | frac0.028316860 |
| cubic foot per hour | ft3/h | frac0.02831683600 |
| US gallon per minute | gal/min | frac0.0037854160 |
| US gallon per hour | gal/h | frac0.003785413600 |

## **Class Reference**

### **class VolumetricFlowRate(value, units='m3/s')**

A class for handling volumetric flow rate measurements.

**Parameters:**

* value : float or int  
  The numeric value of the flow rate. Must be a non-negative number.  
* units : str, default='m3/s'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a VolumetricFlowRate object for 2 m3/h  
\>\>\> v1 \= VolumetricFlowRate(2, "m3/h")

\# Create a VolumetricFlowRate object for 500 L/min  
\>\>\> v2 \= VolumetricFlowRate(500, "L/min")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the flow rate, **always in cubic meters per second** (m3/s). |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** VolumetricFlowRate object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* VolumetricFlowRate  
  A new VolumetricFlowRate object with the converted value and target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a flow rate of 100 L/s  
\>\>\> flow\_L \= VolumetricFlowRate(100, "L/s")

\# Convert to cubic meters per hour  
\>\>\> flow\_m3h \= flow\_L.to("m3/h")

\>\>\> print(flow\_m3h)  
360.0 m3/h

### **Arithmetic Operations**

The VolumetricFlowRate class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two VolumetricFlowRate objects. The result is a new VolumetricFlowRate object in cubic meters per second. The original objects remain unchanged.  
* \_\_eq\_\_(self, other)  
  Compares two VolumetricFlowRate objects for equality. It checks if they are both VolumetricFlowRate instances and have the same internal value.

**Examples:**

\# Create two flow rate objects  
\>\>\> v1 \= VolumetricFlowRate(10, "L/s")  
\>\>\> v2 \= VolumetricFlowRate(10, "L/min")

\# Add them together (10 L/s \= 600 L/min)  
\>\>\> total\_v \= v1 \+ v2

\>\>\> print(total\_v)  
0.010167 m3/s

### **Class Methods**

#### **from\_mass\_flow(cls, mass\_flow: "MassFlowRate", density: "Density")**

A class method that converts a MassFlowRate and Density into a VolumetricFlowRate. The conversion formula is:

Qvol​=ρm˙​

where Q\_vol is volumetric flow rate, dotm is mass flow rate, and rho is density.  
**Parameters:**

* mass\_flow : MassFlowRate  
  An instance of the MassFlowRate class.  
* density : Density  
  An instance of the Density class.

**Returns:**

* VolumetricFlowRate  
  A new VolumetricFlowRate object with the calculated value in the base unit (m3/s).

**Example:**

\# Assuming MassFlowRate and Density classes are available  
\>\>\> m\_dot \= MassFlowRate(100, "kg/s")  
\>\>\> rho \= Density(1000, "kg/m3")

\>\>\> q\_vol \= VolumetricFlowRate.from\_mass\_flow(m\_dot, rho)

\>\>\> print(q\_vol)  
0.1 m3/s  
