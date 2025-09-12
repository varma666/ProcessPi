# **`VolumetricFlowRate` Class**

The `VolumetricFlowRate` class is a subclass of `Variable` that represents the volume of fluid passing a point per unit of time. The base SI unit for volumetric flow rate is cubic meters per second (m<sup>3</sup>/s).

## **Supported Units**

The following units are supported for initialization and conversion. The class automatically converts all internal values to the base unit (m3/s).

| Unit | `str` | Conversion Factor to Cubic Meters per Second (m<sup>3</sup>/s) |
| :---- | :---- | :---- |
| cubic meter per second | m3/s | 1 |
| cubic meter per hour | m3/h | 13600 |
| liter per second | L/s | 11000 |
| liter per minute | L/min | 160000 |
| liter per hour | L/h | 13600000 |
| cubic foot per second | ft3/s | 0.0283168 |
| cubic foot per minute | ft3/min |0.028316860 |
| cubic foot per hour | ft3/h | 0.02831683600 |
| US gallon per minute | gal/min | 0.0037854160 |
| US gallon per hour | gal/h | 0.003785413600 |

## **Class Reference**

**`class VolumetricFlowRate(value, units='m3/s')`**

A class for handling volumetric flow rate measurements.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the flow rate. Must be a non-negative number.  
* `units` : `str`, default=`'m3/s'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If `units` is not a valid unit.

**Examples:**
```py
# Create a VolumetricFlowRate object for 2 m3/h  
>>> v1 = VolumetricFlowRate(2, "m3/h")

# Create a VolumetricFlowRate object for 500 L/min  
>>> v2 = VolumetricFlowRate(500, "L/min")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the flow rate, **always in cubic meters per second** (m<sup>3</sup>/s). |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `VolumetricFlowRate` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `VolumetricFlowRate`  
  A new `VolumetricFlowRate` object with the converted value and target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a flow rate of 100 L/s  
>>> flow_L = VolumetricFlowRate(100, "L/s")

# Convert to cubic meters per hour  
>>> flow_m3h = flow_L.to("m3/h")

>>> print(flow\_m3h)  
360.0 m3/h
```
## **Class Methods**

**`from_mass_flow(cls, mass_flow: "MassFlowRate", density: "Density")`**

A class method that converts a  `MassFlowRate` and `Density` into a `VolumetricFlowRate`. The conversion formula is:

Q<sub>vol</sub>​=ρm˙​

where `Q<sub>vol</sub> is volumetric flow rate, m is mass flow rate, and ρ is density.  
**Parameters:**

* `mass_flow` : `MassFlowRate`  
  An instance of the `MassFlowRate` class.  
* `density` : `Density`  
  An instance of the `Density` class.

**Returns:**

* `VolumetricFlowRate`  
  A new `VolumetricFlowRate` object with the calculated `value` in the base unit (m3/s).

**Example:**
```py
# Assuming MassFlowRate and Density classes are available  
>>> m_dot = MassFlowRate(100, "kg/s")  
>>> rho = Density(1000, "kg/m3")

>>> q_vol = VolumetricFlowRate.from_mass_flow(m_dot, rho)

>>> print(q_vol)  
0.1 m3/s  
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the viscosity, rounded to six decimal places, using its original value, unit, and type.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging, showing the original value, unit, and viscosity type.
