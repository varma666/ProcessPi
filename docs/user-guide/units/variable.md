# **Variable Class**

The Variable class is a generic base class for physical quantities. It provides a foundation for handling a value and its associated units, and defines common methods for comparison and arithmetic operations. This class is designed to be subclassed; specific physical types (like Length or Area) must implement the necessary unit conversion logic.

## **Class Reference**

### **class Variable(value: float, units: str)**

A generic physical variable with a numeric value and string-based units. It provides a base for all unit-aware quantity classes.

**Parameters:**

* value : float or int  
  The numeric value of the variable.  
* units : str  
  The string representation of the variable's units.

**Examples:**

\# Create a generic variable  
\>\>\> my\_var \= Variable(10, "unit")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the variable. |
| **.units** | str | The string representation of the variable's units. |

### **Methods**

#### **Arithmetic Operations**

The Variable class supports addition (+) and subtraction (-) for instances of the same subclass. These operations are performed on the base unit values, ensuring correct results regardless of the original units.

* \_\_add\_\_(self, other)  
  Adds two variables of the same subclass.  
  Raises: TypeError if other is not an instance of the same subclass.  
* \_\_sub\_\_(self, other)  
  Subtracts two variables of the same subclass.  
  Raises: TypeError if other is not an instance of the same subclass.

#### **Comparison Operations**

All comparison operations (==, \!=, \<, \>, \<=, \>=) are defined for instances of the same subclass. They work by comparing the objects' internal base unit values.

* \_\_eq\_\_(self, other)  
  Compares two variables for equality.  
* \_\_ne\_\_(self, other)  
  Compares two variables for inequality.  
* \_\_lt\_\_(self, other), \_\_le\_\_(self, other), \_\_gt\_\_(self, other), \_\_ge\_\_(self, other)  
  Standard less-than, less-than-or-equal-to, greater-than, and greater-than-or-equal-to comparisons.

#### **Formatting & Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the variable in the format: "{value} {units}".  
* \_\_repr\_\_(self)  
  Returns an unambiguous string representation suitable for developers, like "\<Variable: 10 unit\>".  
* \_\_format\_\_(self, format\_spec)  
  Allows for custom string formatting of the numeric value, such as with f-strings.  
* \_\_hash\_\_(self)  
  Enables Variable objects to be used in sets or as dictionary keys by providing a hash based on the class name and the base unit value.

#### **Abstract Methods**

The following methods are abstract and **must be overridden by subclasses** to handle specific unit conversions. Attempting to call these methods on the Variable base class will result in a NotImplementedError.

* to(self, target\_units: str)  
  Converts the variable to a specified target\_units.  
* to\_base(self)  
  Converts the variable's value to its base unit.  
* from\_base(self, base\_value: float, target\_units: str)  
  Creates a new instance from a given base unit value.