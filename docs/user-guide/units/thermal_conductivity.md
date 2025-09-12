# **`ThermalConductivity` Class**

The `ThermalConductivity` class is a subclass of `Variable` designed to represent a material's ability to conduct heat. It ensures accurate calculations by storing all values internally in its base SI unit, Watts per meter-Kelvin (W/m.K).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary formula-based conversions to and from the base unit.

| Unit | `str` | Conversion Factor to Watts per Meter-Kelvin (W/m.K) |
| :---- | :---- | :---- |
| Watts per meter-Kelvin | W/mK | 1 |
| kilowatts per meter-Kelvin | kW/mK | 1000 |
| calories per second-centimeter-degree Celsius | cal/scmC | 418.4 |
| British Thermal Units per hour-foot-degree Fahrenheit | BTU/hftF | 1.730735 |

## **Class Reference**

**`class ThermalConductivity(value, units='W/mK')`**

A class for handling thermal conductivity measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the thermal conductivity. Must be a non-negative number.  
* `units` : `str`, default=`'W/mK'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If units is not a valid `unit`.

**Examples:**
```py
# Create a ThermalConductivity object for a value of 0.5 W/mK  
>>> k1 = ThermalConductivity(0.5, "W/mK")

# Create a ThermalConductivity object of 1 kW/mK  
>>> k2 = ThermalConductivity(1, "kW/mK")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the thermal conductivity, **always in Watts per meter-Kelvin** (W/m.K). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

### **Methods**

**`to(target_unit)`**

Returns a **new** `ThermalConductivity` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `ThermalConductivity`  
  A new `ThermalConductivity` object with the same `value`, represented in the target `unit`.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a thermal conductivity of 0.5 W/mK  
>>> k_W = ThermalConductivity(0.5)

# Convert to BTU/hftF  
>>> k_BTU = k_W.to("BTU/hftF")

>>> print(k_BTU)  
0.289356 BTU/hftF
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the thermal conductivity, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
