import sys
import Operators as ops
import ExprKernel as kernel

ek = kernel.ExprKernel()

while True:
    try:
        sys.stderr.write(">>> ")
        expr = raw_input()
        output = ek.evaluate(expr)
        if output != None and output != ops.none:
            print "%s" % str(output)
    except kernel.ExprKernelExit:
        break
    except:
        sys.excepthook(*sys.exc_info())
