# **Mass Class**

The Mass class is a subclass of Variable designed to represent a quantity of mass. It ensures accurate calculations by storing all values internally in its base SI unit, kilograms (kg).

## **Supported Units**

The following units are supported for initialization and conversion.

| Unit | Symbol | Conversion Factor to Kilograms (kg) |
| :---- | :---- | :---- |
| kilograms | kg | 1 |
| grams | g | 0.001 |
| milligrams | mg | 0.000001 |
| ton | ton | 1000 |
| pounds | lb | 0.453592 |
| ounces | oz | 0.0283495 |
| metric tons | mt | 1000 |
| micrograms | ug | 10−9 |

## **Class Reference**

### **class Mass(value, units='kg')**

A class for handling mass measurements with automatic unit conversion.

**Parameters:**

* value : float or int  
  The numeric value of the mass. Must be a non-negative number.  
* units : str, default='kg'  
  The unit of the provided value. Must be one of the supported units.

**Raises:**

* **ValueError** : If value is negative.  
* **TypeError** : If units is not a valid unit.

**Examples:**

\# Create a Mass object of 500 grams  
\>\>\> m1 \= Mass(500, "g")

\# Create a Mass object of 2 kilograms  
\>\>\> m2 \= Mass(2, "kg")

### **Properties**

| Property | Type | Description |
| :---- | :---- | :---- |
| **.value** | float | The numeric value of the mass, **always in kilograms** (kg). This is the internal representation used for all calculations. |
| **.original\_value** | float | The numeric value as provided during initialization. |
| **.original\_unit** | str | The unit as provided during initialization. |

### **Methods**

#### **to(target\_unit)**

Returns a **new** Mass object converted to the target\_unit. The original object remains unchanged.

**Parameters:**

* target\_unit : str  
  The unit to convert to. Must be one of the supported units.

**Returns:**

* Mass  
  A new Mass object with the same value, represented in the target unit.

**Raises:**

* **TypeError** : If target\_unit is not a valid unit.

**Examples:**

\# Initialize a mass of 500 grams  
\>\>\> mass\_g \= Mass(500, "g")

\# Convert to pounds  
\>\>\> mass\_lb \= mass\_g.to("lb")

\>\>\> print(mass\_lb)  
1.102312 lb

#### **Arithmetic Operations**

The Mass class supports addition (+) and comparison (==).

* \_\_add\_\_(self, other)  
  Adds two Mass objects. The result is a new Mass object in the base unit (kg).  
* \_\_eq\_\_(self, other)  
  Compares two Mass objects for equality based on their internal base unit values.

**Examples:**

\# Create two Mass objects  
\>\>\> m1 \= Mass(1, "kg")  
\>\>\> m2 \= Mass(500, "g")

\# Add them together  
\>\>\> total\_mass \= m1 \+ m2

\>\>\> print(total\_mass)  
1.5 kg

#### **String Representation**

* \_\_str\_\_(self)  
  Returns a human-readable string representation of the mass, rounded to six decimal places, using its original value and unit.  
* \_\_repr\_\_(self)  
  Returns an unambiguous string representation of the object.