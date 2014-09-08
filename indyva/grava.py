'''
Created on 22/01/2014

:author: Juan Morales
'''
from indyva.names import INamed

GRAVAVERSION = '1.0'

class IDefined(object):
    '''
    An IDefined has a grammar that represents its configuration and state

    It also has the ability to build an instace from a gramar 

     In other to chain the creation of every node of the grammar it is
     useful to register the IDefined like this:

	```
	@register("TypeA")
	class A(IDefined):
	    @classmethod
	    def build(cls, grammar):
	        return A()
	```
    '''

    @property
    def grammar(self):
        raise NotImplementedError('The grammar property has to be implemented')

    @classmethod
    def build(cls, grammar):
        raise NotImplementedError('The build static method has to be implemented')


def register(node_type):
    '''
    This class decorator registers the IDefined's builder in the Root
    object

    :params str node_type: All nodes in a grammar has a type
    attribute. The root object will call the registered builder if the
    type attribute is equal to node_type
    '''
    def inner_decorator(cls):
        Root.register(node_type, cls.build)
        return cls
    return inner_decorator


class Root(IDefined, INamed):

    _builders = {}

    def __init__(self, name, prefix=''):
        INamed.__init__(self, name, prefix=prefix)
        self._nodes = {}

    @classmethod
    def register(cls, node_type, builder):
        cls._builders[node_type] = builder

    def add_dataset(self, dataset):
        self._add_node('datasets', dataset)

    def add_dynamic(self, dynamic):
        self._add_node('dynamics', dynamic)

    @property
    def grammar(self):
        gv = {'_grava_version': GRAVAVERSION}
        for list_name, node_list in self._nodes.items():
            for node in node_list:
                gv.setdefault(list_name,[]).append(node.grammar)
        return gv

    @classmethod
    def build(cls, grammar):
        objects = {}
        for list_name, node_list in grammar.items():
            objects[list_name] = []
            for node in node_list:
                instance = cls._builders[node["type"]](node)
                objects[list_name].append(instance)
        return objects

    def _add_node(self, list_name, node):
        node_list = self._nodes.setdefault(list_name, [])
        node_list.append(node)



if __name__ == '__main__':

    @register("TypeA")
    class A(IDefined):
        @classmethod
        def build(cls, grammar):
            return A()

    instances = Root.build({"datasets":[{"type":"TypeA"}, {"type":"TypeA"}]})
    print instances
