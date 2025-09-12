# **`Diameter` Class**

The `Diameter` class is a subclass of `Variable` designed to represent the length of a diameter. It ensures accurate calculations by storing all values internally in its base SI unit, meters (m).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Meters (m) |
| :---- | :---- | :---- |
| meters | m | 1 |
| centimeters | cm | 0.01 |
| millimeters | mm | 0.001 |
| inches | in | 0.0254 |
| feet | ft | 0.3048 |

## **Class Reference**

**`class Diameter(value, units='m')`**

A class for handling diameter measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the diameter. Must be a non-negative number.  
* `units` : `str`, default=`'m'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`ypeError`** : If `units` is not a valid unit.

**Examples:**
```py
# Create a Diameter object of 10 meters  
>>> d1 = Diameter(10)

# Create a Diameter object of 12 inches  
>>> d2 = Diameter(12, "in")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the diameter, **always in meters** (m). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Diameter` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Diameter`  
  A new `Diameter` object with the same `value`, represented in the target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a diameter of 5 meters  
>>> pipe_diameter_m = Diameter(5)

# Convert to feet  
>>> pipe_diameter_ft = pipe_diameter_m.to("ft")

>>> print(pipe_diameter_ft)  
16.4042 ft
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the diameter, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation of the object, suitable for debugging.
