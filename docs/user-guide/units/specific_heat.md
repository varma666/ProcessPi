# **`SpecificHeat` Class**

The `SpecificHeat` class is a subclass of `Variable` designed to represent the amount of energy required to raise the temperature of a unit mass of a substance by one degree. It stores all values internally in its base unit, kilojoules per kilogram-Kelvin (kJ/kg.K).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Kilojoules per Kilogram-Kelvin (kJ/kg.K) |
| :---- | :---- | :---- |
| kilojoules per kilogram-Kelvin | kJ/kgK | 1 |
| Joules per kilogram-Kelvin | J/kgK | 0.001 |
| calories per gram-Kelvin | cal/gK | 4.1868 |
| British Thermal Units per pound-degree Fahrenheit | BTU/lbF | 9.7423 |
| kilocalories per kilogram-Kelvin | kcal/kgK | 4.1868 |

## **Class Reference**

**`class SpecificHeat(value, units='kJ/kgK')`**

A class for handling specific heat capacity measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the specific heat. Must be a non-negative number.  
* `units` : `str`, default=`'kJ/kgK'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If units is not a valid `unit`.

**Examples:**
```py
# Create a SpecificHeat object of 4.186 kJ/kgK  
>>> cp1 = SpecificHeat(4.186, "kJ/kgK")

# Create a SpecificHeat object of 1.0 cal/gK  
>>> cp2 = SpecificHeat(1.0, "cal/gK")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the specific heat, **always in kilojoules per kilogram-Kelvin** (kJ/kg.K). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `SpecificHeat` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `SpecificHeat`  
  A new `SpecificHeat` object with the same `value`, represented in the target `unit`.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a specific heat of 4.186 kJ/kgK  
>>> water_cp = SpecificHeat(4.186, "kJ/kgK")

# Convert to BTU/lbF  
>>> water_cp_btu = water_cp.to("BTU/lbF")

>>> print(water_cp_btu)  
1.79159 BTU/lbF
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the specific heat, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
