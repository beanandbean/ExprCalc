collection = None

class IdObj(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ID'%s'" % self.name

    def __str__(self):
        return "ID'%s'" % self.name
    
    def getValue(self):
        return collection.getValue(self.name)

    def setValue(self, value):
        collection.setValue(self.name, value)

def value(obj):
    if obj.__class__ == IdObj:
        return obj.getValue()
    else:
        return obj
