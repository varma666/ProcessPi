# **`Viscosity` Class**

The `Viscosity` class is a subclass of `Variable` designed to represent a quantity of viscosity. It uniquely handles **two different types of viscosity**: dynamic and kinematic. The class automatically determines the viscosity type based on the provided units and performs conversions only within that type.

## **Supported Units**

The class distinguishes between two sets of units for dynamic and kinematic viscosity.

### **Dynamic Viscosity Units**

The base SI unit for dynamic viscosity is Pascal-second (P.s).

| Unit | `str` | Conversion Factor to Pascal-second (Pa.s) |
| :---- | :---- | :---- |
| Pascal-second | Pa·s | 1 |
| milliPascal-second | mPa·s | 10−3 |
| centipoise | cP | 10−3 |
| poise | P | 0.1 |

### **Kinematic Viscosity Units**

The base SI unit for kinematic viscosity is meters-squared per second (m<sup>2</sup>/s).

| Unit | `str` | Conversion Factor to meter-squared per second (m<sup>2</sup>/s) |
| :---- | :---- | :---- |
| meter-squared per second | m2/s | 1 |
| centimeter-squared per second | cm2/s | 10−4 |
| millimeter-squared per second | mm2/s | 10−6 |
| centistoke | cSt | 10−6 |
| stoke | St | 10−4 |

## **Class Reference**

**`class Viscosity(value, units='Pa·s')`**

A class for handling viscosity measurements. The type of viscosity (dynamic or kinematic) is determined automatically based on the units argument.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the viscosity. Must be a non-negative number.  
* `units` : `str`, default=`'Pa·s'`  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **`ValueError`** : If `value` is negative or if units is not a valid `unit`.

**Examples:**
```py
# Create a Viscosity object for a dynamic viscosity of 1e-3 Pa·s  
>>> v1 = Viscosity(1e-3, units="Pa·s")

# Create a Viscosity object for a kinematic viscosity of 1 cSt  
>>> v2 = Viscosity(1, units="cSt")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the viscosity, always stored in its base SI unit (Pacdots for dynamic, m2/s for kinematic). |
| **`.original\value`** | `float` | The numeric value as provided during initialization. |
| **`.original\unit`** | `str` | The unit as provided during initialization. |
| **`.viscosity\type`** | `str` | Indicates the type of viscosity, either "dynamic" or "kinematic". |

## **Methods**

**`to(target_unit)`**

Returns a **new** `Viscosity` object converted to the `target_unit`. This method can only convert between units of the **same viscosity type** (e.g., dynamic to dynamic). The original object remains unchanged.

**Parameters:**

* `target_unit` : `str`  
  The unit to convert to. Must be a valid unit for the object's viscosity type.

**Returns:**

* `Viscosity`  
  A new `Viscosity` object with the converted `value` and target `unit`.

**Raises:**

* **`ValueError`** : If `target_unit` is not a valid `unit` for the viscosity type.

**Examples:**
```py
# Initialize a dynamic viscosity of 1 Pa·s  
>>> v_Pa = Viscosity(1)

# Convert to centipoise (cP)  
>>> v_cP = v_Pa.to("cP")

>>> print(v_cP)  
1000.0 cP (dynamic)
```
## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the viscosity, rounded to six decimal places, using its original value, unit, and type.  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging, showing the original value, unit, and viscosity type.
