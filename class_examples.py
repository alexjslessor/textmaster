class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width

    def perimeter(self):
        return 2 * self.length + 2 * self.width

# Here we declare that the Square class inherits from the Rectangle class
class Square(Rectangle):
    def __init__(self, length):
        super().__init__()
# square = Square(4)
# df = square.area()
# print(df)



'''
Learning Python 5th Edition
'''
class Person:
    # __init__ is instance constructor
    def __init__(self, name, job=None, pay=0):
        self.name = name
        self.job = job
        self.pay = pay

    def lastName(self):
        return self.name.split()[-1]

    def giveRaise(self, percent):
        self.pay = int(self.pay * (1 + percent))
    # Overloads print() to give cutomized output.
    def __repr__(self):#pg 879/1594
        return '[Person: %s, %s]' % (self.name, self.pay)

# class Manager(Person):

# #Dont do this: use inheritance: pg 881/1594
# #    def giveRaise(self, percent, bonus=.10):
# #        self.pay = int(self.pay * (1 + percent + bonus))# Bad: cut and paste

#     def giveRaise(self, percent, bonus=.10):
#         Person.giveRaise(self, percent + bonus)

class Manager(Person):#887/1594
    
    def __init__(self, name, pay):
        Person.__init__(self, name, 'mgr', pay)
    
    def giveRaise(self, percent, bonus=.10):
        Person.giveRaise(self, percent + bonus)


'''
pg: 873/1594
This means if we ever decide to import the class in this file in order to use it somewhere else (and we will soon in this chapter), we’ll see the output of its test code every time the file is imported. 
Although we could split the test code off into a separate file, it’s often more convenient to code tests in the same file as the items to be tested. 
It would be better to arrange to run the test statements at the bottom only when the file is run for testing, not when the file is imported. 
That’s exactly what the module __name__ check is designed for/
Allows us to test in file but not have this code executed when we import into other script!!
'''
if __name__ == "__main__":# THIS IS FOR TESTING
    # Test the class
    bob = Person('Bob Smith')
    sue = Person('Sue Jones', job='dev', pay=100000) # Runs __init__ automatically
    
    # Fetch attached attributes
    print(bob.name, bob.pay)
    print(sue.name, sue.pay, sue.job)

    print(bob.name.split()[-1])
    #Give sue 10% raise
    sue.pay *= 1.10
    print('%.2f' % sue.pay)
    #pg 876/1594
    print(sue.name, sue.pay)
    print(bob.lastName(), sue.lastName())
    # Use the new methods
    sue.giveRaise(.10)
    print(sue.pay)
    print(sue)
    #pg:883/1594
    tom = Manager('Tom Jones', 50000)
    tom.giveRaise(.10)
    print(tom.lastName())
    print(tom.job)


'''
Specifically, we can make use of what are probably the second most commonly
used operator overloading methods in Python, after __init__ : the __repr__ method
we’ll deploy here, and its __str__ twin introduced in the preceding chapter.
These methods are run automatically every time an instance is converted to its print
string. Because that’s what printing an object does, the net transitive effect is that
printing an object displays whatever is returned by the object’s __str__ or __repr__
method, if the object either defines one itself or inherits one from a superclass. Double-
underscored names are inherited just like any other.

Technically, __str__ is preferred by print and str , and __repr__ is used as a fallback for these roles and in all other contexts. Although the two can be used to implement
'''

'''
Inheritance
When we make a Manager, we pass in a name, and an optional job and pay as before—because Manager had no __init__ constructor,
it inherits that in Person . Here’s the new version’s output:
'''
'''
- Instance creation—filling out instance attributes
- Behavior methods—encapsulating logic in a class’s methods
- Operator overloading—providing behavior for built-in operations like printing
- Customizing behavior—redefining methods in subclasses to specialize them
- Customizing constructors—adding initialization logic to superclass steps
- Most of these concepts are based upon just three simple ideas: the inheritance search
'''

