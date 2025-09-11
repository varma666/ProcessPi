# **Length Class**

The Length class is a specialized Variable that represents a one-dimensional quantity. It is designed for clear, unit-aware calculations and conversions. All Length values are stored internally in the standard SI unit of **meters (**m**)**, which serves as the base unit for all conversions.

## **Supported Units**

The Length class supports the following units. You can initialize a Length object with any of these units, and convert to any of them.

| Unit | Symbol | Conversion to Meters (m) |
| :---- | :---- | :---- |
| meters | m | 1 |
| centimeters | cm | 0.01 |
| millimeters | mm | 0.001 |
| inches | in | 0.0254 |
| feet | ft | 0.3048 |
| kilometers | km | 1000 |

## **Initialization**

You create a Length object by providing a numeric value and an optional unit. If no unit is specified, the value is assumed to be in meters.

\# Create a Length object of 30 meters  
length1 \= Length(30)

\# Create a Length object of 30 inches  
length2 \= Length(30, "in")

The constructor will raise a ValueError if the value is negative or if the specified unit is not supported.

## **The .to() Method**

The .to() method is the primary function for converting a Length object to a different unit. It returns a **new** Length object with the same value, but represented in the target unit. The original object remains unchanged.

### **Syntax**

length\_object.to(target\_unit)

### **Example**

To convert a length from meters to feet:

\# Initialize a length of 5 meters  
distance\_m \= Length(5)

\# Convert to feet  
distance\_ft \= distance\_m.to("ft")

\# Print the converted value  
print(distance\_ft) \# Output: 16.4042 ft

The method ensures a clean separation of concerns, leaving the original object in its initial state while providing the flexibility to work with different units.

## **Arithmetic Operations**

The Length class supports addition and comparison (==). When adding two Length objects, the result is a new Length object with the same unit as the first object.

\# Create two Length objects  
length1 \= Length(1, "m")  
length2 \= Length(10, "cm")

\# Add them together  
total\_length \= length1 \+ length2

\# The result is automatically in the same unit as the first operand  
print(total\_length) \# Output: 1.1 m

## **String Representation**

Printing a Length object (print(obj)) or getting its string representation (str(obj)) will display the value in its original unit, rounded to six decimal places for clarity.