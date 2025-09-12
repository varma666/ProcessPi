# **`Pressure` Class**

The `Pressure` class is a subclass of `Variable` designed to represent a force per unit area. It ensures accurate calculations by storing all values internally in its base SI unit, Pascals (Pa).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Pascals (Pa) |
| :---- | :---- | :---- |
| Pascals | Pa | 1 |
| kilopascals | kPa | 103 |
| megapascals | MPa | 106 |
| bar | bar | 105 |
| atmospheres | atm | 101325 |
| pounds per square inch | psi | 6894.76 |
| millimeters of mercury | mmHg | 133.322 |
| torr | torr | 133.322 |

## **Class Reference**

**`class Pressure(value, units='Pa')`**

A class for handling pressure measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the pressure. Must be a non-negative number.  
* `units` : `str`, default=`'Pa'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If units is not a valid `unit`.

**Examples:**
```py
# Create a Pressure object of 1 atmosphere  
>>> p1 = Pressure(1, "atm")

# Create a Pressure object of 101325 Pascals  
>>> p2 = Pressure(101325, "Pa")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the pressure as provided during initialization. This is inherited from the Variable base class. |
| **`.units`** | `str` | The string representation of the variable's units, as provided during initialization. Inherited from the Variable base class. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Pressure` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `Pressure`  
  A new `Pressure` object with the same `value`, represented in the target `unit`.

**Examples:**
```py
# Initialize a pressure of 1 atm  
>>> atm_pressure = Pressure(1, "atm")

# Convert to psi  
>>> psi_pressure = atm_pressure.to("psi")

>>> print(psi_pressure)  
14.695949 psi
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the pressure, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging, showing the internal values.
