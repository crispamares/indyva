# -*- coding: utf-8 -*-
'''
Created on 17/07/2013

@author: jmorales
'''
FRONTPREFIX = 'r'

class Front(object):
    '''
    This class centralizes the access to the provided services
    
    The Front replies to requests. A request is a dict with:
      - 'rpc' : str of the form 'r.name_of_service.name_of_method'
      - 'args' : list like in *args or dict like in **kwargs
    '''

    def __init__(self):
        self._services = {}
        self.register('_builtin', BuiltinService())
        
    def register(self, name, service):
        if self._services.has_key(name):
            raise ValueError('There is a service registered with the same name: {0}'.format(name) )
        self._services[name] = service
        return '{0}.{1}'.format(FRONTPREFIX, name)
    
    def unregister(self, name):
        self._services.pop(name)
        return True
        
    def call(self, request):
        service_name = request['service']
        service = self._services[service_name]
        if isinstance(request['args'], dict):
            response = service.__getattribute__(request['rpc'])(**request['args'])
        else:
            response = service.__getattribute__(request['rpc'])(*request['args'])
        return response
    
    def __getattr__(self, name):
        return self._services[name]
    
def _singleton():
    front = Front()
    while True:
        yield front
        
__singleton = _singleton()
def get_instance():
    return __singleton.next()    
    
    
class IService(object):
    '''An IService is automatically registered when initialized. Use this as a 
    base class for developing Services'''
    def __init__(self, name):
        front = get_instance()
        front.register(name, self)

class BuiltinService(object):
    def echo(self, a):
        return a
    
    