'''
Created on Jul 19, 2013

:author: Juan Morales
'''

from functools import partial

from indyva.core.names import INamed
from indyva.facade.showcase import Case
from indyva.dataset.shared_object import SharedObject, VersionError


class SharedObjectService(INamed):
    '''
    This class provide a facade for managing SharedObjects
    '''

    def __init__(self, name='SharedObjectSrv'):
        '''
        @param name: The unique name of the service
        '''
        self._shared_objects = Case().tag(name).tag(SharedObject.__name__)
        INamed.__init__(self, name)

    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_shared_object)
        dispatcher.add_method(self.expose_shared_object)
        dispatcher.add_method(self.del_shared_object)
        dispatcher.add_method(self.clear)
        dispatcher.add_method(self.push)
        # SharedObject properties
        dispatcher.add_method(partial(self._proxy_property, 'name'), 'name')
        dispatcher.add_method(partial(self._proxy_property, 'grammar'), 'grammar')
        # SharedObject methods
        dispatcher.add_method(partial(self._proxy, 'pull'), 'pull')

    def _proxy(self, method, shared_object_oid, *args, **kwargs):
        shared_object = self._shared_objects[shared_object_oid]
        result = shared_object.__getattribute__(method)(*args, **kwargs)
        return result

    def _proxy_property(self, method, shared_object_oid):
        shared_object = self._shared_objects[shared_object_oid]
        result = shared_object.__getattribute__(method)
        return result

    def push(self, oid, data, version):
        '''
        :param oid: The SharedObject oid
        :param data: list or dict. The updated data.
        :param version: This should be the returned by pull or push methods.

        :returns: tuple(conflict_ocurred, new_version)
                 conflict_ocurred: True if provided version is older than current
                                   False otherwise
                 new_version: The version generated after the modification.
                              Becomes the current one.
        '''
        shared_object = self._shared_objects[oid]
        conflict = False
        try:
            new_version = shared_object.push(data, version)
        except VersionError:
            conflict = True
            new_version = None

        return (conflict, new_version)

    def new_shared_object(self, name, data, prefix=''):
        '''
        :param str name: If a name is not provided, an uuid is generated
        :param data: A dict or list
        :param str prefix: Prepended to the name creates the oid
        '''
        new_shared_object = SharedObject(name, data, prefix=prefix)
        self._shared_objects[new_shared_object.oid] = new_shared_object
        return new_shared_object

    def expose_shared_object(self, shared_object):
        self._shared_objects[shared_object.oid] = shared_object
        return shared_object

    def del_shared_object(self, oid):
        self._shared_objects.pop(oid)

    def clear(self):
        self._shared_objects.clear()

    def __getattr__(self, method):
        if method in ['name', 'grammar']:
            return partial(self._proxy_property, method)
        else:
            return partial(self._proxy, method)
