# **Class: `HeatFlux`**

The `HeatFlux` class is a subclass of `Variable` designed to represent heat transfer rate per unit area. It ensures accurate calculations by storing all values internally in its base SI unit, Watts per square meter (W/m<sup>2</sup>).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | `str` | Conversion Factor to Watts per Square Meter (W/m<sup>2</sup>) |
| :---- | :---- | :---- |
| Watts per square meter | W/m2 | 1 |
| kilowatts per square meter | kW/m2 | 1000 |
| Watts per square centimeter | W/cm2 | 10000 |
| British Thermal Units per hour per square foot | BTU/hft2 | 3.1546 |
| calories per second per square centimeter | cal/scm2 | 41840 |

## **Class Reference**

**`class HeatFlux(value, units='W/m2')`**

A class for handling heat flux measurements with automatic unit conversion.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the heat flux. Must be a non-negative number.  
* `units` : `st`r, default=`'W/m2'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative.  
* **`TypeError`** : If `units` is not a valid unit.

**Examples:**
```py
# Create a HeatFlux object of 300 W/m²  
>>> q1 = HeatFlux(300)

# Create a HeatFlux object of 0.3 kW/m²  
>>> q2 = HeatFlux(0.3, "kW/m2")
```

## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the heat flux, **always in Watts per square meter** (W/m<sup>2</sup>). This is the internal representation used for all calculations. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |
| **`.original_unit`** | `str` | The unit as provided during initialization. |

## **Methods**

**`to(target_unit)`**

Returns a **new** `HeatFlux` object converted to the `target_unit`. The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* `HeatFlux`  
  A new `HeatFlux` object with the same `value`, represented in the target unit.

**Raises:**

* **`TypeError`** : If `target_unit` is not a valid unit.

**Examples:**
```py
# Initialize a heat flux of 1000 W/m²  
>>> heat_flux_W = HeatFlux(1000)

# Convert to kW/m²  
>>> heat_flux_kW = heat_flux_W.to("kW/m2")

>>> print(heat_flux_kW)  
1.0 kW/m2
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the heat flux, rounded to six decimal places, using its original value and unit.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging.
