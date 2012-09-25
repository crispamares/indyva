
import weakref
import exceptions
import threading   # for lock

class RecursionError(exceptions.RuntimeError):
    pass

class _subscription(object):
    """A subscription is returned as a result of subscribing to an 
       observable. When the subscription object is finalized, the 
       subscription is cancelled.  This class is used to facilitate 
       subscription cancellation."""

    def __init__(self, subscriber, observed):
        self.subscriber = subscriber
        self.observed = weakref.ref(observed)

    def __del__(self):
        obsrvd = self.observed()
        if (self.subscriber and obsrvd):
            obsrvd._cancel(self.subscriber)


class _obwan(object):
    '''Half-hidden class.  Only 'observable should construct these.
    Calls to subscribe, cancel get invoked through the observable.
    _obwan objects reside in class instances containing observables.'''

    def __init__(self):
        self.subscribers = []
        self._value = None
        self._changeLock = threading.Lock()
        
    def __call__(self):
        """returns the current value, the one last set"""
        return self._value

    def _notifySubscribers(self, value):
        for (f,exceptionHdlr) in self._callbacks():
            try:
                f(value)
            except Exception, ex:
                if exceptionHdlr and not exceptionHdlr(ex): 
                    raise            # reraise if not handled

    def setvalu(self, value):
        """Notify the subcribers only when the value changes."""
        if self._value != value:
            if self._changeLock.acquire(0):     # non-blocking
                self._value = value
                try:
                    self._notifySubscribers(value)
                finally:
                    self._changeLock.release()
            else:
                raise RecursionError("Attempted recursion into observable's set method.")

    def subscribe(self, obsv, exceptionInfo = None):
        observer = obsv.setvalu if isinstance(obsv, _obwan) else obsv
        ob_info =(observer, exceptionInfo)
        self.subscribers.append(ob_info)
        return _subscription(ob_info, self)

    def _callbacks(self):
        scribers = []
        scribers.extend(self.subscribers)
        return scribers

    def _cancel(self, wref):
        self.subscribers.remove(wref)


class Observable(object):
    """An observable implemented as a descriptor. Subscribe to an observable 
    via calling  xxx.observable.subscribe(callback)"""
    def __init__(self, nam):
        self.xname = "__"+nam
        self.obwan = _obwan

    def __set__(self,inst, value ):
        """set gets the instances associated variable and calls 
        its setvalu method, which notifies subribers"""
        if inst and not hasattr(inst, self.xname):
            setattr(inst, self.xname, self.obwan())
        ow = getattr(inst, self.xname)
        ow.setvalu(value)

    def __get__(self, inst, klass):
        """get gets the instances associated variable returns it"""
        if inst and not hasattr(inst, self.xname):
            setattr(inst, self.xname, self.obwan())
        return getattr(inst, self.xname)


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