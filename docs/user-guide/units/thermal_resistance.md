# **`ThermalResistance` Class**

The `ThermalResistance` class is a subclass of `Variable` designed to represent a material's resistance to heat flow. It simplifies calculations by internally storing all values in its base SI unit, Kelvin per Watt (K/W).

## **Supported Units**

The following units are supported for initialization and conversion. Note that some units, like degrees Celsius per Watt (K/W), are numerically equivalent to the base SI unit.

| Unit | `str` | Conversion Factor to Kelvin per Watt (K/W) |
| :---- | :---- | :---- |
| Kelvin per Watt | K/W | 1 |
| Celsius per Watt | C/W | 1 |
| hour-foot²-degree Fahrenheit per British Thermal Unit | hft2F/BTU | 0.1761 |
| meter²-Kelvin per Watt | m2K/W | 1 |

## **Class Reference**

**`class ThermalResistance(value, units='K/W')`**

A class for handling thermal resistance measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the thermal resistance. Must be a positive number.  
* `units` : `str`, default=`'K/W'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is not a positive number.  
* **`TypeError`** : If units is not a valid `unit`.

**Examples:**
```py
# Create a ThermalResistance object for a value of 0.5 K/W  
>>> r1 = ThermalResistance(0.5, "K/W")

# Create a ThermalResistance object of 2 C/W (numerically equivalent to 2 K/W)  
>>> r2 = ThermalResistance(2, "C/W")
```

## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the thermal resistance, **always in Kelvin per Watt** (K/W). This is the internal representation used for all calculations. |
| **`.original\value`** | `float` | The numeric value as provided during initialization. |
| **`.original\unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `ThermalResistance` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `ThermalResistance`  
  A new `ThermalResistance` object with the same `value`, represented in the target `unit`.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid `unit`.

**Examples:**
```py
# Initialize a thermal resistance of 2 K/W  
>>> r_K = ThermalResistance(2)

# Convert to hrft2F/BTU  
>>> r_BTU = r_K.to("hrft2F/BTU")

>>> print(r_BTU)  
11.353457 hrft2F/BTU
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the thermal resistance, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
