import collections
import IdObj

class NoneObj(object):
    def __repr__(self):
        return "NONE"

    def __str__(self):
        return "NONE"

class ListObj(list):
    pass

none = NoneObj()

class Operator(object):
    op = "?"
    
    def __init__(self, canHaveLeft = False):
        self.left = none
        self.right = none

    def __repr__(self):
        return "Op'%s' <%s, %s>" % (self.op, str(self.left), str(self.right))

    def __str__(self):
        return "Op'%s' <%s, %s>" % (self.op, str(self.left), str(self.right))

    def priority(self):
        return 0

    def needLeft(self):
        return False

    def vLeft(self):
        return IdObj.value(self.left)
        
    def vRight(self):
        return IdObj.value(self.right)

    def operate(self):
        return self.vRight()

    def canGiveLeft(self):
        return self.right != none

assignPriority = 10

class Assign(Operator):
    op = "="

    def __init__(self, canHaveLeft = False):
        global assignPriority
        
        Operator.__init__(self)
        self._priority = assignPriority
        assignPriority += 1

    def priority(self):
        return self._priority

    def needLeft(self):
        return True

    def operate(self):
        assignPriority = 10

        self.left.setValue(self.vRight())

        return self.vRight()

class Attribute(Operator):
    op = "."
    
    def priority(self):
        return 5000

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft().__getattribute__(self.right.name)

singlePriority = 1000

class Not(Operator):
    op = "!"

    def __init__(self, canHaveLeft = False):
        global singlePriority
        
        Operator.__init__(self)
        self._priority = singlePriority
        singlePriority += 1
    
    def priority(self):
        return self._priority

    def needLeft(self):
        return False

    def operate(self):
        singlePriority = 1000
        return not self.vRight()

class Plus(Operator):
    op = "+"
    
    def __init__(self, canHaveLeft = False):
        global singlePriority
        
        Operator.__init__(self)
        self._needLeft = canHaveLeft
        if canHaveLeft:
            self._priority = 100
        else:
            self._priority = singlePriority
            singlePriority += 1
    
    def priority(self):
        return self._priority

    def needLeft(self):
        return self._needLeft

    def operate(self):
        if self._needLeft:
            return self.vLeft() + self.vRight()
        else:
            singlePriority = 1000
            return self.vRight()

class Minus(Operator):
    op = "-"
    
    def __init__(self, canHaveLeft = False):
        global singlePriority
        
        Operator.__init__(self)
        self._needLeft = canHaveLeft
        if canHaveLeft:
            self._priority = 100
        else:
            self._priority = singlePriority
            singlePriority += 1

    def priority(self):
        return self._priority

    def needLeft(self):
        return self._needLeft

    def operate(self):
        if self._needLeft:
            return self.vLeft() - self.vRight()
        else:
            singlePriority = 1000
            return -self.vRight()

class Multiply(Operator):
    op = "*"
    
    def priority(self):
        return 200

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() * self.vRight()

class Divide(Operator):
    op = "/"
    
    def priority(self):
        return 200

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() / self.vRight()

class Exponent(Operator):
    op = "**"

    def priority(self):
        return 300

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() ** self.vRight()

class Equal(Operator):
    op = "=="

    def priority(self):
        return 70

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() == self.vRight()

class NotEqual(Operator):
    op = "!="

    def priority(self):
        return 70

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() != self.vRight()

class Larger(Operator):
    op = ">"

    def priority(self):
        return 80

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() > self.vRight()

class LargerEqual(Operator):
    op = ">="

    def priority(self):
        return 80

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() >= self.vRight()

class Smaller(Operator):
    op = "<"

    def priority(self):
        return 80

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() < self.vRight()

class SmallerEqual(Operator):
    op = "<="

    def priority(self):
        return 80

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft() <= self.vRight()

openBracketOperated = False

class OpenBracket(Operator):
    op = "("
    
    def __init__(self, canHaveLeft = False):
        Operator.__init__(self)

        self.placing = True

        if canHaveLeft:
            self._runFunc = True
            self._priority = 4000
        else:
            self._runFunc = False
            self._priority = 10000
    
    def priority(self):
        if self.placing:
            self.placing = self._runFunc and self.left == none
            return self._priority
        else:
            return -100

    def needLeft(self):
        return self._runFunc

    def operate(self):
        global openBracketOperated
        
        openBracketOperated = True
        if self._runFunc:
            if self.vRight() == none:
                return self.vLeft()()
            elif self.vRight().__class__ == ListObj:
                return self.vLeft()(*self.vRight())
            else:
                return self.vLeft()(self.vRight())
        else:
            return self.vRight()

class CloseBracket(Operator):
    op = ")"
    
    def __init__(self, canHaveLeft = False):
        Operator.__init__(self)

        self._priority = -110
    
    def priority(self):
        global openBracketOperated

        if openBracketOperated:
            openBracketOperated = False
            self._priority = 10001
        return self._priority

    def needLeft(self):
        return True

    def operate(self):
        return self.vLeft()

    def canGiveLeft(self):
        return True

class ArgSeparator(Operator):
    op = ","

    def priority(self):
        return -90

    def needLeft(self):
        return True

    def operate(self):
        result = ListObj()
        if self.vLeft() != none:
            if self.vLeft().__class__ == ListObj:
                result.extend(self.vLeft())
            else:
                result.append(self.vLeft())
        if self.vRight() != none:
            result.append(self.vRight())

        return result
