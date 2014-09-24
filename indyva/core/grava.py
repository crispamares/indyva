'''
Created on 22/01/2014

:author: Juan Morales
'''
from indyva.core.names import INamed
from logbook import debug

GRAVAVERSION = '1.0'


class GrammarException(Exception):
    pass


class IDefined(object):
    '''
    An IDefined has a grammar that represents its configuration and state

    It also has the ability to build an instace from a grammar

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
    def build(cls, grammar, objects=None):
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

    def add_condition(self, condition):
        self._add_node('conditions', condition)

    @property
    def grammar(self):
        gv = {'_grava_version': GRAVAVERSION}
        for list_name, node_list in self._nodes.items():
            for node in node_list:
                gv.setdefault(list_name,[]).append(node.grammar)
        return gv

    @classmethod
    def build(cls, grammar, objects=None):

        nodes = cls._flat_grammar(grammar)
        dirty_nodes = []
        objects = {} if objects is None else objects
        build_objects = {}

        any_progress = True

        while any_progress:
            any_progress = False
            while nodes:
                node = nodes.pop(0)
                try:
                    debug('building:\t{0}\t{1}', node["type"], node["name"])
                    all_objects = dict(build_objects.items() + objects.items())
                    instance = cls._builders[node["type"]](node, all_objects)
                    build_objects[instance.name] = instance
                    any_progress = True
                except KeyError:
                    dirty_nodes.append(node)
                    debug('dirty:\t{0}\t{1}', node["type"], node["name"])

            if not any_progress:
                raise GrammarException("Imposible to build nodes:", dirty_nodes)
            if dirty_nodes:
                nodes = dirty_nodes
                dirty_nodes = []
            else:
                return build_objects



    def _add_node(self, list_name, node):
        node_list = self._nodes.setdefault(list_name, [])
        node_list.append(node)

    @staticmethod
    def _flat_grammar(grammar):
        gv = []
        for list_name, node_list in grammar.items():
            if isinstance(node_list, list):
                gv.extend(node_list)
        return gv


if __name__ == '__main__':

    @register("TypeA")
    class A(IDefined):
        @classmethod
        def build(cls, grammar, objects=None):
            return A()

    instances = Root.build({"datasets":[{"type":"TypeA"}, {"type":"TypeA"}]})
    print instances
