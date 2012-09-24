

class cached_property(object):
    '''A read-only @property that is only evaluated once. The value is cached
    on the object itself rather than the function or class; this should prevent
    memory leakage.'''
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result

        
    
class observable_property(property):
    def __init__(self, *args):
        property.__init__(self, *args)
    
    def __get__(self, obj, cls):
        return self.fget(obj)
    
    def __set__(self, obj, value):
        if value != self.fget(obj):
            self.fset(obj, value)
            for callback in obj.callbacks:
                callback()



class ReactiveVariable(object):
    def __init__(self, obj, name, value=None):
        self.name = name
        obj._values = obj.__dict__.get('_values', {})
        obj._values[name] = value
        obj._callbacks = obj.__dict__.get('_callbacks', {})
        obj._callbacks[name] = []

    def __get__(self, obj, cls):
        return obj._values[self.name]
    
    def __set__(self, obj, value):
        if value != obj._values[self.name]:
            obj._values[self.name] = value
            for callback in obj._callbacks[self.name]:
                callback()


#@derived(cosaA, cosaB, cosaC)
#@property
#def paco():
#    pass