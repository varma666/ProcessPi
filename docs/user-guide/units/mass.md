# **Class: `Mass`**

The `Mass` class is a subclass of `Variable` designed to represent a quantity of mass. It ensures accurate calculations by storing all values internally in its base SI unit, kilograms (kg).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Kilograms (kg) |
| :---- | :---- | :---- |
| kilograms | kg | 1 |
| grams | g | 0.001 |
| milligrams | mg | 0.000001 |
| ton | ton | 1000 |
| pounds | lb | 0.453592 |
| ounces | oz | 0.0283495 |
| metric tons | mt | 1000 |
| micrograms | ug | 10−9 |

## **Class Reference**

**`class Mass(value, units='kg')`**

A class for handling mass measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the mass. Must be a non-negative number.  
* `units` : `str`, default=`'kg'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If units is not a valid `unit`.

**Examples:**
```py
# Create a Mass object of 500 grams  
>>> m1 = Mass(500, "g")

# Create a Mass object of 2 kilograms  
>>> m2 = Mass(2, "kg")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the mass, **always in kilograms** (kg). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target\_unit)`**

Returns a **new** `Mass` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Mass`  
  A new `Mass` object with the same `value`, represented in the target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid `unit`.

**Examples:**
```py
# Initialize a mass of 500 grams  
>>> mass_g = Mass(500, "g")

# Convert to pounds  
>>> mass_lb = mass_g.to("lb")

>>> print(mass_lb)  
1.102312 lb
```
## **String Representation**

* `__str__(self)` 
  Returns a human-readable string representation of the mass, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation of the object.
