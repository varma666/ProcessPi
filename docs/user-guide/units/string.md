# **StringUnit Class**

The StringUnit class is a subclass of Variable designed to represent quantities that are categorical or string-based, rather than numeric. Examples include a material's phase, a flow type, or a component's status. It provides a simple way to handle these non-numeric values within a consistent framework.

## **Supported Units**

By definition, this class does not have physical units. The category attribute is used to provide context for the string value.

## **Class Reference**

### **class StringUnit(value, category='string')**

A class for handling string-based quantities.

**Parameters:**

* value : str  
  The string value of the quantity.  
* category : str, default='string'  
  The descriptive category for the quantity (e.g., 'flow\_type', 'phase\_state').

**Raises:**

* **TypeError** : If value is not a string.

**Examples:**

\# Create a StringUnit object for a flow type  
\>\>\> flow \= StringUnit("Laminar", "flow\_type")

\# Create a StringUnit object for a phase state  
\>\>\> phase \= StringUnit("Gas", "phase\_state")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | str | The string value of the quantity. |
| **.original\_value** | str | The value as provided during initialization. Identical to .value. |
| **.category** | str | The category name for the string value. |

### **Methods**

#### **to(target\_unit=None)**

For string-based quantities, unit conversion is not applicable. This method is provided for interface consistency with other Variable subclasses. It returns a new StringUnit object with the same value and category.

**Parameters:**

* target\_unit : None  
  This parameter is ignored for this class.

**Returns:**

* StringUnit  
  A new StringUnit object with the same value.

**Examples:**

\# The to() method simply returns a copy  
\>\>\> flow \= StringUnit("Laminar")  
\>\>\> flow\_copy \= flow.to()

\>\>\> print(flow \== flow\_copy)  
True

#### **Comparison Operations**

The StringUnit class supports equality (==) comparison.

* \_\_eq\_\_(self, other)  
  Compares two StringUnit objects for equality based on their string values.

#### **String Representation**

* \_\_repr\_\_(self)  
  Returns a string representation of the object in the format "{value} ({category})", which is also used for the \_\_str\_\_ method.