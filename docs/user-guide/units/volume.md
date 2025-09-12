# **`Volume` Class**

The `Volume` class is a subclass of `Variable` designed to represent a quantity of volume. It handles automatic unit conversion by storing all internal values in the base SI unit, cubic meters (m<sup>3</sup>).

## **Supported Units**

The following units are supported for initialization and conversion. The class handles the necessary conversions to and from the base unit.

| Unit | `str` | Conversion Factor to Cubic Meters (m<sup>3</sup>) |
| :---- | :---- | :---- |
| cubic meter | m3 | 1 |
| liter | L | 0.001 |
| milliliter | mL | 10−6 |
| cubic centimeter | cm3 | 10−6 |
| cubic foot | ft3 | 0.0283168 |
| cubic inch | in3 | 1.63871times10−5 |
| US gallon | gal | 0.00378541 |
| oil barrel | bbl | 0.158987 |

## **Class Reference**

**`class Volume(value, units='m3')`**

A class for handling volume measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the volume. Must be a non-negative number.  
* `units` : `str`, default=`'m3'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If value is negative.  
* **`TypeError`** : If units is not a valid unit.

**Examples:**
```py
# Create a Volume object for 100 liters  
>>> v1 = Volume(100, "L")

# Create a Volume object for 1 cubic meter  
>>> v2 = Volume(1, "m3")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the volume, **always in cubic meters** (m<sup>3</sup>). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Volume` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Volume`  
  A new `Volume` object with the converted `value` and target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a volume of 5 gallons  
>>> v_gal = Volume(5, "gal")

# Convert to liters  
>>> v_L = v_gal.to("L")

>>> print(v_L)  
18.92705 L
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the volume, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging, showing the original value and unit.
