# -*- coding: utf-8 -*-
'''
Created on 06/06/2013

:author: jmorales
'''

import uuid

from . import hub

DEFAULT_PREFIX_TOPIC = ""

class Bus(object):
    '''
    Exposes the ``PUB/SUB`` functionality of the
    :class:`~indyva.epubsub.bus.Hub` in a more convenient way

    '''

    def __init__(self, prefix=DEFAULT_PREFIX_TOPIC):
        '''
        :param prefix: This str is the prefix of all the pubsub topics of
         this bus
        '''
        self._prefix = prefix
        self._hub = hub.instance()
        self._bus_id = uuid.uuid4()

    def __del__(self):
        self.clear()

    def subscribe(self, topic, destination):
        self._hub._subscribe(self._prefix + topic, destination, group_id=self._bus_id)

    def subscribe_once(self, topic, destination):
        self._hub._subscribe(self._prefix + topic, destination, only_once=True, group_id=self._bus_id)

    def unsubscribe(self, topic, destination):
        self._hub.unsubscribe(self._prefix + topic, destination)

    def close(self, topic):
        self._hub.close(self._prefix + topic)

    def clear(self):
        self._hub._unsubscribe_by_group_id(self._bus_id)

    def publish(self, topic, msg):
        self._hub.publish(self._prefix + topic, msg)
