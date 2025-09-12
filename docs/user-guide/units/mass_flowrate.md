# **`MassFlowRate` Class**

The `MassFlowRate` class is a subclass of `Variable` designed to represent the mass of a substance passing per unit of time. It ensures accurate calculations by storing all values internally in its base SI unit, kilograms per second (kg/s).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Kilograms per Second (kg/s) |
| :---- | :---- | :---- |
| kilograms per second | kg/s | 1 |
| kilograms per hour | kg/h | 1/3600 |
| grams per second | g/s | 0.001 |
| grams per minute | g/min | 0.001/60 |
| grams per hour | g/h | 0.001/3600 |
| pounds per second | lb/s | 0.453592 |
| pounds per minute | lb/min | 0.453592/60 |
| pounds per hour | lb/h | 0.453592/3600 |
| kilograms per day | kg/day | 1/86400 |
| tons per day | t/day | 0.0115740741 |

## **Class Reference**

**`class MassFlowRate(value, units='kg/s')`**

A class for handling mass flow rate measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the mass flow rate. Must be a non-negative number.  
* `units` : `str`, default=`'kg/s'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If units is not a valid `unit`.

**Examples:**
```py
# Create a MassFlowRate object of 100 kg/h  
>>> mfr1 = MassFlowRate(100, "kg/h")

# Create a MassFlowRate object of 0.5 lb/s  
>>> mfr2 = MassFlowRate(0.5, "lb/s")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the mass flow rate, **always in kilograms per second** (kg/s). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `MassFlowRate` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `MassFlowRate`  
  A new `MassFlowRate` object with the same `value`, represented in the target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a mass flow rate of 100 kg/h  
>>> flow_kg_h = MassFlowRate(100, "kg/h")

# Convert to kg/s  
>>> flow_kg_s = flow_kg_h.to("kg/s")

>>> print(flow_kg_s)  
0.027778 kg/s
```

## **String Representation**

* `__str__(self)` 
  Returns a human-readable string representation of the mass flow rate, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
