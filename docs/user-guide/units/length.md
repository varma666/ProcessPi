# **Class: `Length`**

The `Length` class is a subclass of `Variable` designed to represent a one-dimensional quantity with unit-aware capabilities. It ensures accurate calculations by storing all values internally in its base unit, meters (m).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Meters (m) |
| :---- | :---- | :---- |
| meters | m | 1 |
| centimeters | cm | 0.01 |
| millimeters | mm | 0.001 |
| inches | in | 0.0254 |
| feet | ft | 0.3048 |
| kilometers | km | 1000 |

## **Class Reference**

**`class Length(value, units='m')`**

A class for handling length measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the length. Must be a positive number.  
* `units` : `str`, default=`'m'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative or `units` is not a valid unit.

**Examples:**
```python
# Create a Length object of 30 meters  
>>> length1 = Length(30)

# Create a Length object of 30 inches  
>>> length2 = Length(30, "in")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the length, **always in meters** (m). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Length` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the [supported units]

**Returns:**

* `Length`  
  A new `Length` object with the same value, represented in the target unit.

**Raises:**

* **`ValueError`** : If `target_unit` is not a valid unit.

**Examples:**
```python
# Initialize a length of 5 meters  
>>> distance_m = Length(5)

# Convert to feet  
>>> distance_ft = distance_m.to("ft")

>>> print(distance_ft)  
16.4042 ft
```
**Arithmetic Operations**

The `Length` class supports addition (`+`) and comparison (`==`).

* `__add__(self, other)`  
  Adds two Length objects. The result is a new Length object with the unit of the first operand.  
* `__eq__(self, other)`  
  Compares two Length objects for equality based on their internal meter values.

**Examples:**
```python
# Create two Length objects  
>>> length1 = Length(1, "m")  
>>> length2 = Length(10, "cm")

# Add them together  
>>> total_length = length1 + length2

>>> print(total_length)  
1.1 m
```
**String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the length, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation of the object.
