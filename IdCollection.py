class IdError(NameError):
    pass

class IdCollection(object):
    def __init__(self):
        self.collection = dict()
    
    def setValue(self, name, value):
        self.collection[name] = value
    
    def getValue(self, name):
        if name in self.collection:
            return self.collection[name]
        else:
            raise IdError, "Unknown id name '%s'" % name
