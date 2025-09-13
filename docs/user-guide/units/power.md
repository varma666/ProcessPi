# **Class: `Power`**

The `Power` class is a subclass of `Variable` designed to represent the rate at which work is done or energy is transferred. It ensures accurate calculations by storing all values internally in its base SI unit, Watts (W).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Watts (W) |
| :---- | :---- | :---- |
| Watts | W | 1 |
| kilowatts | kW | 103 |
| megawatts | MW | 106 |
| mechanical horsepower | hp | 745.7 |
| British Thermal Units per hour | BTU/h | 0.29307107 |

## **Class Reference**

**`class Power(value, units='W')`**

A class for handling power measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the power. Must be a non-negative number.  
* `units` : `str`, default=`'W'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative or units is not a valid `unit`.

**Examples:**
```py
# Create a Power object of 1000 Watts  
>>> p1 = Power(1000)

# Create a Power object of 1 kilowatt  
>>> p2 = Power(1, "kW")

# Create a Power object of 1.34 horsepower  
>>> p4 = Power(1.34, "hp")
```

## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the power, **always in Watts** (W). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Power` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Power`  
  A new `Power` object with the same `value`, represented in the target `unit`.

**Raises:**

* **`ValueError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a power of 1000 W  
>>> power_W = Power(1000)

# Convert to kilowatts  
>>> power_kW = power_W.to("kW")

>>> print(power_kW)  
1.0 kW
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the power, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation of the object.
