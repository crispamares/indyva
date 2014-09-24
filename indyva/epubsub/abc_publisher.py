'''
Created on Jun 26, 2013

@author: crispamares
'''

from abc import ABCMeta
from functools import wraps

'''@@var TESTDESCRIPTION: If True every subscription is asserted to be
the list of topics'''
TESTSUBSCRIPTION = True




def pub_result(topic):
    '''Decorator that publish the result of the decorated function as the msg
    of the given topic.

    The message is a dict {origin : The id of the publisher,
                           topic: The topic of the publication
                           result: The result of the decorated function}

    This decorator also adds a kw argument 'pub_options' to the interface of
    the decorated function. This argument is a dict that configures how the
    result is emitted.
    * Configurable options:
       - silent: if pub_options['silent'] == True then no msg will be emitted
    '''
    def wrap(func):
        @wraps(func)
        def publisher(self, *args, **kwargs):
            pub_options = kwargs.pop('pub_options', {})

            result = func (self, *args, **kwargs)
            msg = {'origin':self.publisher_id, 'topic':topic, 'result': result}

            if not pub_options.get('silent', False):
                self._bus.publish(topic, msg)
            return result

        return publisher
    return wrap



class IPublisher(object):
    '''
    This class is useful for publishers that want to provide
    an easy way to subscribe to its own topics.

    Hides the bus and hub classes for the subscribers
    '''

    __metaclass__ = ABCMeta

    def __init__(self, bus, topics=None):
        '''
        :param epubsub.bus.Bus bus: The bus to publish thought
        :param list topics: A list of possible topics to use
        '''
        self._bus = bus
        self._topics = topics if topics is not None else []

    def subscribe(self, topic, destination):
        if TESTSUBSCRIPTION:
            assert topic in self._topics
        self._bus.subscribe(topic, destination)

    def subscribe_once(self, topic, destination):
        if TESTSUBSCRIPTION:
            assert topic in self._topics
        self._bus.subscribe_once(topic, destination)

    def unsubscribe(self, topic, destination):
        if TESTSUBSCRIPTION:
            assert topic in self._topics
        self._bus.unsubscribe(topic, destination)

    @property
    def publisher_id(self):
        '''
        This property is used in the pub_result decorator. The publisher_id
        will identify the publisher.

        The id will be the oid attribute of the instance or '' if not
        name exists.
        '''
        return self.oid if hasattr(self, 'name') else ''
