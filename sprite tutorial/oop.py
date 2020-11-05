#object oriented programming

#abstraction: start with a basic superclass and implement it in specialisations
class gameObject:
    def __init__(self):
        self.x = 1
    
    def update(self):
        pass

    def draw(self):
        #not implemented yet
        pass

class specialObject(gameObject):
    def __init__(self):
        #extension
        super().__init__()
        self.y=2

#polymorphism: object can be used in different ways
class Button:
    def __init__(self,text="",graphic=None,clickaction=None):
        if text:
            self.text = text
        if graphic:
            self.graphic = graphic

#encapsulation: data is protected from outside functions
class A:
    def __init__(self,x):
        self.x = x

    #getters and setters
    def get_x(self):
        return self.x
    
    def set_x(self):
        self.x = x

a = specialObject()
print(a.x,a.y)
#big O: maximum complexity
#little o: minimum complexity
# O(n): list searching, o(1)
"""
for i in list:
    if i==target:
        done!
"""
# O(n2): searching array (2D list)

# O(log): binary search
# log(10) = 1
# log(100) = 2
# log(1000) = 3
# log2(2) = 1
# log2(8) = 3
""" [1,2,3,4,5,6,7,8]
[1,2,3,4] [5,6,7,8]

[5,6,7,8]
[5,6] [7,8]

[7,8]
[7] [8]

[7]
found result in 3 trials
every search halves the size of the search space, so algorithm has log2(n) complexity"""
""" 
2**2 = 4
2**3 = 8
therefore it will take either 2 or 3 trials, depending

[1,2,3,4,5,6]
[1,2,3] [4,5,6]

[4,5,6]
[4,5] [6]

[4,5]
[4] [5]

[4]
found result in 3 trials
every search halves the size of the search space, so algorithm has log2(n) complexity"""

# O(n!), intractible
# 4! = 4*3*2*1
#tensorflow
