import weakref

class Change(object):
    def __init__(self, name, type, object, old_value):
        '''
        @param name: String, the name of the property changed
        @param type: String, ['new' | 'updated' |'deleted' | 'reconfigured']
        @param object: Object, the object that notifies the change  Done with weakref
        @param old_value: Object, the value before the change
        '''
        self.__refs = weakref.WeakValueDictionary()
        
        self.__refs['name'] = name
        self.__refs['type'] = type
        self.__refs['object'] = object
        self.__refs['old_value'] = old_value

    def get_name(self):
        return self.__refs['name']
    def get_type(self):
        return self.__refs['type']
    def get_object(self):
        return self.__refs['object']
    def get_old_value(self):
        return self.__refs['old_value']
    def set_name(self, value):
        self.__refs['name'] = value
    def set_type(self, value):
        self.__refs['type'] = value
    def set_object(self, value):
        self.__refs['object'] = value
    def set_old_value(self, value):
        self.__refs['old_value'] = value

    name = property(get_name, set_name, doc="String, the name of the property changed")
    type = property(get_type, set_type, doc= "String, ['new' | 'updated' |'deleted' | 'reconfigured']")
    object = property(get_object, set_object, doc= "object: Object, the object that notifies the change")
    old_value = property(get_old_value, set_old_value, doc= "Object, the value before the change")
        

class Subscription(object):
    def __init__(self, channel):
        self._channel = channel
        self._callbacks = []
        self._connected = False
    @property
    def channel(self):
        return self._channel
    
    def on_event(self, callback):
        if self._connected:
            self._callbacks.append(callback)
        else:
            raise Exception('This subscription is already disconnected')
        
    def unsubscribe(self):
        Notifier.unsubscribe(self)
    
class Notifier(object):
    __channels = {}
    
    @classmethod
    def subscribe(cls, channel):
        subscription = Subscription(channel)
        subscription._connected = True
        cls.__channels.get(channel, []).append(subscription)
        return subscription

    @classmethod
    def unsubscribe(cls, subscription):
        cls.__channels[subscription.channel].remove(subscription)
        subscription._connected = False
        
    @classmethod
    def publish(cls, channel, message):
        subscriptions = cls.__channels.get(channel, [])
        for subscription in subscriptions:
            for callback in subscription._callbacks:
                cls._send(callback,message, channel)  
        return len(subscriptions)
        
    @classmethod
    def _send(cls, callback, message, channel):
        '''This method should be reimplemented in other to use other message system
        This implementation is Synchronous but ideally will be Asynchronous
        '''
        callback(message, channel)  
        
class Reactive( type ):
    def __new__( cls, name, bases, classdict ):

        def notifySetAttr( func ):
            ''' to be applied exclusively on __setattr__ '''
            def wrapper( *args, **kwargs ):
                instance, attr, new_value = args[0], args[1], args[2]
                old_value = None
                if hasattr( instance, attr ):
                    old_value = getattr( instance, attr )
                ret = func( *args, **kwargs )
                # TODO: Implement deleted and reconfigured
                if not old_value:
                    instance.notify( attr, 'new', old_value )
                elif old_value != new_value:
                    instance.notify( attr, "updated", old_value )
                return ret
            return wrapper

        def notify( self, attribute, type, old_value ):
            ''' notify the change '''
            Notifier.publish(self.channel+'/'+attribute, Change(attribute, type, self, old_value))

        ## add new functions to class dict
        classdict['notify'] = notify
        classdict['channel'] = 'common'
        aType = type.__new__( cls, name, bases, classdict )
        ## decorate setattr to trace down every update of value
        aType.__setattr__ = notifySetAttr( aType.__setattr__ )
        return aType 
