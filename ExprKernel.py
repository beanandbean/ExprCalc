import math, string
import IdObj
import Operators as ops
import IdCollection as idcol

NO_BUF = "no_buffer"
BUF_END = "buffer_end"

ID = "identify"
NUM = "number"
STR_SING = "string_single"
STR_DOUB = "string_double"

class OperatorError(Exception):
    pass

class ExprKernelExit(Exception):
    pass

def _exit():
    raise ExprKernelExit

class ExprKernel(object):
    def __init__(self):
        self.collection = idcol.IdCollection()

        self.collection.setValue("E", math.e)
        self.collection.setValue("PI", math.pi)

        self.collection.setValue("abs", abs)
        self.collection.setValue("cos", math.cos)
        self.collection.setValue("exit", _exit)
        self.collection.setValue("float", float)
        self.collection.setValue("int", int)
        self.collection.setValue("len", len)
        self.collection.setValue("sin", math.sin)
        self.collection.setValue("str", str)
        self.collection.setValue("tan", math.tan)

        IdObj.collection = self.collection
    
    def endBuf(self):
        if self.bufType == ID:
            const = IdObj.IdObj(self.buf)
        elif self.bufType == NUM:
            f = float(self.buf)
            i = int(f)
            if i == f:
                const = i
            else:
                const = f
        elif self.bufType in [STR_SING, STR_DOUB]:
            const = self.buf
        else:
            return
        
        self.queue[-1].right = const
        self.buf = ""
        self.bufType = BUF_END
        self.bufEscaped = False

    def appendOperator(self, op):
        op = op(self.queue[-1].canGiveLeft())

        while op.priority() <= self.queue[-1].priority():
            result = self.queue[-1].operate()
            self.queue = self.queue[:-1]
            self.queue[-1].right = result

        if op.needLeft():
            op.left = self.queue[-1].right
            self.queue[-1].right = ops.none
        self.queue.append(op)

    def evaluate(self, expr):
        self.buf = ""
        self.bufType = NO_BUF
        self.bufEscaped = False

        opBuf = ""

        baseOperator = ops.Operator()
        self.queue = [baseOperator]

        self.collection.setValue("__expr__", expr)

        for char in expr:
            if len(opBuf) > 0:
                if opBuf == "*":
                    if char == "*":
                        op = ops.Exponent
                        continue
                    else:
                        op = ops.Multiply
                if opBuf == "=":
                    if char == "=":
                        op = ops.Equal
                        continue
                    else:
                        op = ops.Assign
                elif opBuf == "!":
                    if char == "=":
                        op = ops.NotEqual
                        continue
                    else:
                        op = ops.Not
                elif opBuf == ">":
                    if char == "=":
                        op = ops.LargerEqual
                        continue
                    else:
                        op = ops.Larger
                elif opBuf == "<":
                    if char == "=":
                        op = ops.SmallerEqual
                        continue
                    else:
                        op = ops.Smaller
                else:
                    raise OperatorError, "Unexpected operator buffer '%s'" % opBuf

                opBuf = ""
                self.appendOperator(op)
                
            if self.bufType == STR_SING:
                if self.bufEscaped:
                    self.bufEscaped = False
                    self.buf += char
                else:
                    if char == "'":
                        self.endBuf()
                    elif char == "\\":
                        self.bufEscaped = True
                    else:
                        self.buf += char
            elif self.bufType == STR_DOUB:
                if self.bufEscaped:
                    self.bufEscaped = False
                    self.buf += char
                else:
                    if char == "\"":
                        self.endBuf()
                    elif char == "\\":
                        self.bufEscaped = True
                    else:
                        self.buf += char
            elif char in string.digits + "." and self.bufType in [NO_BUF, NUM]:
                self.buf += char
                self.bufType = NUM
            elif char in string.letters + string.digits + "_" and self.bufType in [NO_BUF, ID]:
                self.buf += char
                self.bufType = ID
            elif char == "'" and self.bufType == NO_BUF:
                self.bufType = STR_SING
            elif char == "\"" and self.bufType == NO_BUF:
                self.bufType = STR_DOUB
            else:
                self.endBuf()

                if char in string.whitespace:
                    continue

                self.bufType = NO_BUF
                if char == "+":
                    op = ops.Plus
                elif char == "-":
                    op = ops.Minus
                elif char == "/":
                    op = ops.Divide
                elif char == ".":
                    op = ops.Attribute
                elif char == "(":
                    op = ops.OpenBracket
                elif char == ")":
                    op = ops.CloseBracket
                elif char == ",":
                    op = ops.ArgSeparator
                elif char in "*=!><":
                    opBuf = char
                    continue
                else:
                    raise OperatorError, "Unknown operator '%s'" % char

                self.appendOperator(op)

        self.endBuf()
        while self.queue[-1] != baseOperator:
            result = self.queue[-1].operate()
            self.queue = self.queue[:-1]
            self.queue[-1].right = result

        return baseOperator.operate()
                

