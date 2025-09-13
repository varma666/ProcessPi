# **Class: `StringUnit`**

The `StringUnit` class is a subclass of `Variable` designed to represent quantities that are categorical or string-based, rather than numeric. Examples include a material's phase, a flow type, or a component's status. It provides a simple way to handle these non-numeric values within a consistent framework.

## **Supported Units**

By definition, this class does not have physical units. The category attribute is used to provide context for the string value.

## **Class Reference**

**`class StringUnit(value, category='string')`**

A class for handling string-based quantities.

**Parameters:**

* `value` : `str`  
  The string value of the quantity.  
* `category` : `str`, default=`'string'`  
  The descriptive category for the quantity (e.g., 'flow_type', 'phase_state').

**Raises:**

* **`TypeError`** : If `value` is not a `string`.

**Examples:**
```py
# Create a StringUnit object for a flow type  
>>> flow = StringUnit("Laminar", "flow_type")

# Create a StringUnit object for a phase state  
>>> phase = StringUnit("Gas", "phase_state")
```
## **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **`.value`** | `str` | The string value of the quantity. |
| **`.original_value`** | `str` | The value as provided during initialization. Identical to .value. |
| **`.category`** | `str` | The category name for the string value. |

## **String Representation**

* `__repr__(self)`  
  Returns a string representation of the object in the format "`{value} ({category})`", which is also used for the `__str__` method.
