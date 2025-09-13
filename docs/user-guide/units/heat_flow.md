# **Class: `HeatFlow`**

The `HeatFlow` class is a subclass of `Variable` designed to represent the total heat transfer rate. It ensures accurate calculations by storing all values internally in its base SI unit, Watts (W).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Watts (W) |
| :---- | :---- | :---- |
| Watts | W | 1 |
| kilowatts | kW | 1000 |
| megawatts | MW | 106 |
| British Thermal Units per hour | BTU/h | 0.293071 |
| calories per second | cal/s | 4.184 |
| kilocalories per hour | kcal/h | 1.163 |

## **Class Reference**

**`class HeatFlow(value, units='W')`**

A class for handling heat flow measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the heat flow. Must be a non-negative number.  
* `units` : `str`, default=`'W'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeErro`r** : If `units` is not a valid unit.

**Examples:**
```py
# Create a HeatFlow object of 5000 Watts  
>>> Q1 = HeatFlow(5000, "W")

# Create a HeatFlow object of 5 kilowatts  
>>> Q2 = HeatFlow(5, "kW")
```

## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the heat flow, **always in Watts** (W). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit`)**

Returns a **new** `HeatFlow` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The `unit` to convert to. Must be one of the supported units.

**Returns:**

* `HeatFlow`  
  A new `HeatFlow` object with the same `value`, represented in the target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a heat flow of 5000 Watts  
>>> heat_flow_W = HeatFlow(5000)

# Convert to kilowatts  
>>> heat_flow_kW = heat_flow_W.to("kW")

>>> print(heat_flow_kW)  
5.0 kW
```

## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the heat flow, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
