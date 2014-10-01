# -*- coding: utf-8 -*-
'''

:author: jmorales
'''

from functools import partial

from indyva.core.names import INamed
from indyva.core.grava import Root
from indyva.facade.showcase import Case, Showcase


class GrammarService(INamed):
    '''
    This class let clients create
    '''

    def __init__(self, name='GrammarSrv'):
        '''
        :param name: The unique name of the service
        '''
        self._roots = Case().tag(name).tag(Root.__name__)
        INamed.__init__(self, name)

    def register_in(self, dispatcher):
        dispatcher.add_method(self.new_root)
        dispatcher.add_method(self.expose_root)
        dispatcher.add_method(self.del_root)
        dispatcher.add_method(self.build)
        dispatcher.add_method(partial(self._proxy_instanciator, 'add_dataset'), 'add_dataset')
        dispatcher.add_method(partial(self._proxy_instanciator, 'add_dynamic'), 'add_dynamic')
        dispatcher.add_method(partial(self._proxy_instanciator, 'add_condition'), 'add_condition')
        dispatcher.add_method(partial(self._proxy_property, 'grammar'), 'grammar')

    def build(self, grammar, objects=None):
        showcase = Showcase.instance()
        if objects:
            objects = {o:showcase.get(o) for o in objects}
        instances = Root.build(grammar, objects)
        print '////', instances
        for name, instance in instances.items():
            case = showcase.get_case(instance.__class__.__name__)
            case[name] = instance
        return instances.values()

    def _proxy(self, method, root_oid, *args, **kwargs):
        root = self._roots[root_oid]
        result = root.__getattribute__(method)(*args, **kwargs)
        return result

    def _proxy_property(self, method, root_oid):
        root = self._roots[root_oid]
        result = root.__getattribute__(method)
        return result

    def _proxy_instanciator(self, method, root_oid, object_or_objects):
        showcase = Showcase.instance()
        names = object_or_objects if isinstance(object_or_objects, list) else [object_or_objects]
        objects = [showcase.get(n) for n in names]
        return self._proxy(method, root_oid, objects)

    def new_root(self, name, prefix=''):
        '''
        :param str name: The name is ussed as identifier
        :param str prefix: Prepended to the name creates the oid
        '''
        new_root = Root(name, prefix=prefix)
        self._roots[new_root.oid] = new_root
        return new_root

    def expose_root(self, root):
        self._roots[root.oid] = root
        return root

    def del_root(self, oid):
        self._roots.pop(oid)
