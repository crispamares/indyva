from  collections import namedtuple 

Change = namedtuple("Change", 'name type object old_value')
#class Change(object):
#    def __init__(self, name, type, object, old_value):
#        '''
#        @param name: String, the name of the property changed
#        @param type: String, ['new' | 'updated' |'deleted' | 'reconfigured']
#        @param object: Object, the object that notifies the change  Done with weakref
#        @param old_value: Object, the value before the change
#        '''
#        self.name = name
#        self.type = type
#        self.object = object
#        self.old_value = old_value
#        

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
        if cls.__channels.has_key(channel):
            cls.__channels.get(channel, []).append(subscription)
        else:
            cls.__channels[channel] = [subscription]
        return subscription

    @classmethod
    def unsubscribe(cls, subscription):
        cls.__channels[subscription.channel].remove(subscription)
        subscription._connected = False
        
    @classmethod
    def publish(cls, channel, message):
        #print '*** _publish', channel, message
        subscriptions = cls.__channels.get(channel, [])
        for subscription in subscriptions:
            for callback in subscription._callbacks:
                cls._send(callback,message, channel)  
        return len(subscriptions)
    
    @classmethod
    def is_anyone_listening(cls, channel):
        subscriptions = cls.__channels.get(channel, [])
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
                old_value = getattr(instance, attr, None)
                ret = func( *args, **kwargs )

                if (not instance._muted 
                    and Notifier.is_anyone_listening(instance._channel+'/'+attr)):
                    # TODO: Implement deleted and reconfigured    
                    if not old_value:
                        instance.notify( attr, 'new', old_value )
                    elif old_value != new_value:
                        instance.notify( attr, "updated", old_value )
                    
                return ret
            return wrapper

        def notify( self, attribute, type, old_value ):
            ''' notify the change '''
            Notifier.publish(self._channel+'/'+attribute, Change(attribute, type, self, old_value))

        def mute(self, on):
            '''
            An object muted does not notify changes
            @param on:
            '''
            self._muted = on

        ## add new functions to class dict
        classdict['notify'] = notify
        classdict['_channel'] = 'common'
        classdict['_muted'] = False
        aType = type.__new__( cls, name, bases, classdict )
        ## decorate setattr to trace down every update of value
        aType.__setattr__ = notifySetAttr( aType.__setattr__ )
        return aType 
