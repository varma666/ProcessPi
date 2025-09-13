# **Class: `Dimensionless`**

The `Dimensionless` class is a subclass of `Variable` designed to represent quantities that do not have physical units. These are often ratios of other quantities, such as Reynolds number, friction factor, or efficiency. The class provides a foundation for performing arithmetic operations on these numbers while maintaining clarity about their unitless nature.

## **Supported Units**

By definition, dimensionless quantities are unitless. No units are supported for this class.

## **Class Reference**

**`class Dimensionless(value)`**

A class for handling dimensionless quantities. It ensures that the value is a number and provides standard arithmetic operations.

**Parameters:**

* `value` : `float` or `int`  
  The numeric value of the dimensionless quantity.

**Raises:**

* **`TypeError`** : If `value` is not a numeric type (`int` or `float`).

**Examples:**
```py
# Create a Dimensionless object for Reynolds number  
>>> Re = Dimensionless(5000)

# Create a Dimensionless object for friction factor  
>>> f = Dimensionless(0.02)
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `float` | The numeric value of the dimensionless quantity. This is the internal representation. |
| **`.original_value`** | `float` | The numeric value as provided during initialization. |

## **String Representation**

* `__str__(self)`  
  Returns a human-readable string representation of the dimensionless quantity, rounded to six decimal places, followed by (dimensionless).  
* `__repr__(self)`  
  Returns a string representation suitable for developers and debugging, such as 5000 (dimensionless).  
* `__format__(self, format_spec)`  
  Allows for custom string formatting of the numeric value, such as with f-strings.
