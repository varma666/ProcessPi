# **`Temperature` Class**

The `Temperature` class is a subclass of `Variable` designed to represent a temperature quantity. It ensures accurate conversions and calculations by storing all values internally in its base SI unit, Kelvin (K).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary formula-based conversions to and from the base unit.

| Unit | `str` | Conversion Formula to Kelvin (K) |
| :---- | :---- | :---- |
| Kelvin | K | T_K=T_K |
| Celsius | C | T_K=T_C+273.15 |
| Fahrenheit | F | T_K=(T_F−32)times5/9+273.15 |

## **Class Reference**

**`class Temperature(value, units='K')`**

A class for handling temperature measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the temperature.  
* `units` : `str`, default=`'K'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If units is not a valid unit.

**Examples:**
```py
# Create a Temperature object of 100°C  
>>> t1 = Temperature(100, "C")

# Create a Temperature object of 373.15 K  
>>> t2 = Temperature(373.15)
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the temperature, **always in Kelvin** (K). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Temperature` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Temperature`  
  A new `Temperature` object with the same `value`, represented in the target `unit`.

**Raises:**

* **`ValueError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a temperature of 25°C  
>>> temp_C = Temperature(25, "C")

# Convert to Fahrenheit  
>>> temp_F = temp_C.to("F")

>>> print(temp_F)  
77.0 F
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the temperature, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
