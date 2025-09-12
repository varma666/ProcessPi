# **`Density` Class**

The `Density` class is a subclass of `Variable` designed to represent the mass per unit volume of a substance. It ensures accurate calculations by storing all values internally in its base SI unit, kilograms per cubic meter (kg/m<sup>3</sup>).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Kilograms per Cubic Meter (kg/m<sup>3</sup>) |
| :---- | :---- | :---- |
| kilograms per cubic meter | kg/m3 | 1 |
| grams per cubic centimeter | g/cm3 | 1000 |
| grams per milliliter | g/mL | 1000 |
| pounds per cubic foot | lb/ft3 | 16.0185 |
| pounds per cubic inch | lb/in3 | 27679.9 |

## **Class Reference**

**`class Density(value, units='kg/m3')`**

A class for handling density measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the density. Must be a non-negative number.  
* `units` : `str`, default=`'kg/m3'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative or `units` is not a valid unit.

**Examples:**
```py
# Create a Density object of 1000 kg/m^3 (the density of water)  
>>> d1 = Density(1000)

# Create a Density object of 1 g/cm^3  
>>> d2 = Density(1, "g/cm3")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the density, **always in kilograms per cubic meter** (kg/m3). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Density` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Density`  
  A new `Density` object with the same value, represented in the target unit.

**Raises:**

* **`ValueError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a density of 1000 kg/m^3  
>>> water_density_kg = Density(1000)

# Convert to g/cm^3  
>>> water_density_g = water_density_kg.to("g/cm3")

>>> print(water_density_g)  
1.0 g/cm3
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the density, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation of the object.
