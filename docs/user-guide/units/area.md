# **`Area` Class**

The `Area` class is a subclass of `Variable` designed to represent a two-dimensional quantity with unit-aware capabilities. It ensures accurate calculations by storing all values internally in its base SI unit, square meters (m<sup>2</sup>).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Square Meters (m<sup>2</sup>) |
| :---- | :---- | :---- |
| square meters | m2 | 1 |
| square centimeters | cm2 | 0.0001 |
| square millimeters | mm2 | 0.000001 |
| square kilometers | km2 | 1,000,000 |
| square inches | in2 | 0.00064516 |
| square feet | ft2 | 0.092903 |
| square yards | yd2 | 0.836127 |
| acres | acre | 4046.86 |
| hectares | ha | 10000 |

## **Class Reference**

### **`class Area(value, units='m2')`**

A class for handling area measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the area. Must be a non-negative number.  
* `units` : `str`, default=`'m2'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If `units` is not a valid unit.

**Examples:**
```py
# Create an Area object of 100 square centimeters  
>>> a1 = Area(100, "cm2")

# Create an Area object of 0.5 square meters  
>>> a2 = Area(0.5, "m2")
```

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the area, **always in square meters** (m2). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

### **Methods**

#### **`to(target_unit)`**

Returns a **new** `Area` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Area`  
  A new `Area` object with the same `value`, represented in the target `units`.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize an area of 100 square meters  
>>> house_area_m2 = Area(100)

# Convert to square feet  
>>> house_area_ft2 = house_area_m2.to("ft2")

>>> print(house_area_ft2)  
1076.391 ft2
```

#### **Arithmetic Operations**

The `Area` class supports addition (`+`) and comparison (`==`).

* `__add__(self, other)`  
  Adds two Area objects. The result is a new Area object with the unit of the first operand.  
* `__eq__(self, other)`  
  Compares two Area objects for equality based on their internal meter values.

**Examples:**

```py
# Create two Area objects  
>>> area1 = Area(1, "m2")  
>>> area2 = Area(500, "cm2")

# Add them together  
>>> total_area = area1 + area2

>>> print(total_area)  
1.05 m2
```
#### **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the area, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation of the object.
