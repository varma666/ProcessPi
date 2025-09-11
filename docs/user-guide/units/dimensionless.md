# **Dimensionless Class**

The Dimensionless class is a subclass of Variable designed to represent quantities that do not have physical units. These are often ratios of other quantities, such as Reynolds number, friction factor, or efficiency. The class provides a foundation for performing arithmetic operations on these numbers while maintaining clarity about their unitless nature.

## **Supported Units**

By definition, dimensionless quantities are unitless. No units are supported for this class.

## **Class Reference**

### **class Dimensionless(value)**

A class for handling dimensionless quantities. It ensures that the value is a number and provides standard arithmetic operations.

**Parameters:**

* value : float or int  
  The numeric value of the dimensionless quantity.

**Raises:**

* **TypeError** : If value is not a numeric type (int or float).

**Examples:**

\# Create a Dimensionless object for Reynolds number  
\>\>\> Re \= Dimensionless(5000)

\# Create a Dimensionless object for friction factor  
\>\>\> f \= Dimensionless(0.02)

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the dimensionless quantity. This is the internal representation. |
| **.original\_value** | float | The numeric value as provided during initialization. |

### **Methods**

#### **to(target\_unit=None)**

For dimensionless quantities, unit conversion is not applicable. This method is provided for interface consistency with other Variable subclasses. It returns a new Dimensionless object with the same value.

**Parameters:**

* target\_unit : None  
  This parameter is ignored for this class.

**Returns:**

* Dimensionless  
  A new Dimensionless object with the same value.

**Examples:**

\# The to() method simply returns a copy  
\>\>\> Re \= Dimensionless(5000)  
\>\>\> Re\_copy \= Re.to()

\>\>\> print(Re \== Re\_copy)  
True

#### **Arithmetic Operations**

The Dimensionless class supports addition (+) and multiplication (\*) with other Dimensionless objects or standard numeric types.

* \_\_add\_\_(self, other)  
  Adds two Dimensionless objects. The result is a new Dimensionless object.  
  Raises: TypeError if other is not a Dimensionless instance.  
* \_\_mul\_\_(self, other)  
  Multiplies a Dimensionless object by another Dimensionless object or a standard numeric type (int, float).  
  Raises: TypeError if other is an unsupported type.  
* \_\_eq\_\_(self, other)  
  Compares two Dimensionless objects for equality based on their values.

**Examples:**

\# Addition with another dimensionless quantity  
\>\>\> d1 \= Dimensionless(0.5)  
\>\>\> d2 \= Dimensionless(1.5)  
\>\>\> d\_total \= d1 \+ d2  
\>\>\> print(d\_total)  
2.0 (dimensionless)

\# Multiplication with a numeric type  
\>\>\> Re \= Dimensionless(5000)  
\>\>\> Re\_doubled \= Re \* 2  
\>\>\> print(Re\_doubled)  
10000.0 (dimensionless)

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the dimensionless quantity, rounded to six decimal places, followed by (dimensionless).  
* \_\_repr\_\_(self)  
  Returns a string representation suitable for developers and debugging, such as 5000 (dimensionless).  
* \_\_format\_\_(self, format\_spec)  
  Allows for custom string formatting of the numeric value, such as with f-strings.