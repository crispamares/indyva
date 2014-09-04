'''
Created on 22/01/2014

:author: Juan Morales
'''
from indyva.names import INamed


class IDefined(object):
    '''
    An IDefined has a grammar that represents its configuration and state
    '''

    @property
    def grammar(self):
        raise NotImplementedError('The grammar property has to be implemented')

    @staticmethod
    def build(cls, grammar):
        raise NotImplementedError('The build static method has to be implemented')


class Root(IDefined, INamed):

    def __init__(self, name, prefix=''):
        INamed.__init__(self, name, prefix=prefix)

        self._builders = {}
        self._nodes = {}

    def register(self, key, builder):
        self._builders[key] = builder

    def add_node(self, name, node):
        self._nodes[name] = node

    @property
    def grammar(self):
        gv = {}
        for name, node in self._nodes.items:
            gv[name] = node.grammar
        return gv

    @staticmethod
    def build(cls, grammar):
        pass
