# **Class: `HeatOfVaporization`**

The `HeatOfVaporization` class is a subclass of `Variable` designed to represent the heat required to change a unit mass of a substance from liquid to gas at a given pressure. It ensures accurate calculations by storing all values internally in its base SI unit, Joules per kilogram (J/kg).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Joules per Kilogram (J/kg) |
| :---- | :---- | :---- |
| Joules per kilogram | J/kg | 1 |
| kilojoules per kilogram | kJ/kg | 103 |
| megajoules per kilogram | MJ/kg | 106 |
| calories per gram | cal/g | 4184 |
| British Thermal Units per pound | BTU/lb | 2326 |

## **Class Reference**

**`class HeatOfVaporization(value, units='J/kg')`**

A class for handling heat of vaporization measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the heat of vaporization. Must be a non-negative number.  
* `units` : `st`r, default=`'J/kg'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative or `units` is not a valid unit.

**Examples:**
```py
# Create a HeatOfVaporization object of 2.257 MJ/kg  
>>> hv1 = HeatOfVaporization(2257000)

# Create a HeatOfVaporization object of 540 cal/g  
>>> hv2 = HeatOfVaporization(540, "cal/g")
```

## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the heat of vaporization, **always in Joules per kilogram** (J/kg). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `HeatOfVaporization` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `HeatOfVaporization`  
  A new `HeatOfVaporization` object with the same `value`, represented in the target `unit`.

**Raises:**

* **`ValueErro`r** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a heat of vaporization of 2257000 J/kg  
>>> water_hv = HeatOfVaporization(2257000, "J/kg")

# Convert to cal/g  
>>> water_hv_cal = water_hv.to("cal/g")

>>> print(water_hv_cal)  
540.057352 cal/g
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the heat of vaporization, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns an unambiguous string representation suitable for developers and debugging.
