# **Class: `HeatTransferCoefficient`**

The `HeatTransferCoefficient` class is a subclass of `Variable` designed to represent the heat transfer rate per unit area per unit temperature difference. It ensures accurate calculations by storing all values internally in its base SI unit, Watts per square meter-Kelvin (W/m<sup>2</sup>.K).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Watts per Square Meter-Kelvin (W/m<sup>2</sup>.K) |
| :---- | :---- | :---- |
| Watts per square meter-Kelvin | W/m2K | 1 |
| kilowatts per square meter-Kelvin | kW/m2K | 1000 |
| calories per second per square centimeter-degree Celsius | cal/scm2C | 41840 |
| British Thermal Units per hour per square foot-degree Fahrenheit | BTU/hft2F | 5.678263 |

## **Class Reference**

**`class HeatTransferCoefficient(value, units='W/m2K')`**

A class for handling heat transfer coefficient measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the heat transfer coefficient. Must be a non-negative number.  
* `units` : `str`, default=`'W/m2K'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If `units` is not a valid unit.

**Examples:**
```py
# Create a HeatTransferCoefficient object of 200 W/m²K  
>>> h1 = HeatTransferCoefficient(200)

# Create a HeatTransferCoefficient object of 0.2 kW/m²K  
>>> h2 = HeatTransferCoefficient(0.2, "kW/m2K")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the heat transfer coefficient, **always in Watts per square meter-Kelvin** (W/m<sup>2</sup>.K). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `HeatTransferCoefficient` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `HeatTransferCoefficient`  
  A new `HeatTransferCoefficient` object with the same `value`, represented in the target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a heat transfer coefficient of 500 W/m²K  
>>> h_W = HeatTransferCoefficient(500)

# Convert to BTU/hft²F  
>>> h_BTU = h_W.to("BTU/hft2F")

>>> print(h_BTU)  
88.058309 BTU/hft2F
```


## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the heat transfer coefficient, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
