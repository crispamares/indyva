'''
Created on Oct 11, 2013

@author: crispamares
'''
from indyva.external import lazy


class Topic(object):
    '''
    Handy methods to build and extract useful information form a topic string
    '''

    def __init__(self, topic_str=None):
        '''
        :param str topic_str: The raw topic
        '''
        self._path = tuple(topic_str.split('.')) if topic_str is not None \
                                                 else tuple

    @property
    def path(self):
        return self._path

    @lazy
    def _str(self):
        return '.'.join(self._path)

    def __str__(self):
        return self._str

    def __repr__(self):
        return 'Toipc ({0})'.format(self._str)
