# -*- coding: utf-8 -*-
'''
Created on 06/06/2013

:author: jmorales
'''

from weakref import WeakValueDictionary
from indyva.core.context import SessionSingleton


class Hub(SessionSingleton):
    '''
    For common uses the :class:`~indyva.epubsub.bus.Bus` is preferred

    The broker of the pubsub system. Handles the subscriptions table.
    Deleted object's destinations are unsubscribed automatically.

    If the destination (a callable) is a method then a weakref of the object
    (the method's owner) is saved in order to know when the object is collected
    by the gc.
    '''

    def __init__(self):
        self._subscriptions = {}
        self._subscribers = WeakValueDictionary()

    def _subscribe(self, topic, destination, only_once=False, group_id=None):
        ''' TODO: publish new subscriptions and new topics through meta topic'''
        oid = None
        topic_destinations = self._subscriptions.setdefault(topic, {})

        subscription_info = {}
        if only_once: subscription_info['only_once'] = True
        if group_id is not None: subscription_info['group_id'] = group_id

        subscriber = getattr(destination, 'im_self', None)
        if subscriber is not None:
            oid = id(subscriber)
            self._subscribers[oid] = subscriber
            subscription_info['subscriber'] = oid
            destination = destination.__name__

        destinations = topic_destinations.setdefault(oid, {})
        destinations[destination] = subscription_info

    def subscribe(self, topic, destination):
        self._subscribe(topic, destination, only_once=False)

    def subscribe_once(self, topic, destination):
        self._subscribe(topic, destination, only_once=True)

    def unsubscribe(self, topic, destination):
        subscriber = getattr(destination, 'im_self', None)
        oid = id(subscriber) if subscriber else None
        destination = destination.__name__ if subscriber else destination
        self._unsubscribe(topic, oid, destination)

    def _unsubscribe(self, topic, oid, destination):
        if oid in self._subscribers:
            self._subscriptions[topic][oid].pop(destination)
        else:
            self._subscriptions[topic].pop(oid)

    def close(self, topic):
        '''Removes all the subscriptions to a topic.
        No error trying to close unexpected topic

        :param str topic:
        '''
        self._subscriptions.pop(topic, None)

    def _unsubscribe_by_group_id(self, group_id):
        oids_to_remove = []
        for topic, oids in self._subscriptions.items():
            for oid, destinations in oids.items():
                if oid is not None and oid not in self._subscribers:
                    oids_to_remove.append(oid)
                    continue
                for destination, subscription_info in destinations.items():
                    if subscription_info.get('group_id', None) == group_id:
                        self._unsubscribe(topic, oid, destination)

        for oid in oids_to_remove:
            self._subscriptions[topic].pop(oid, None)


    def publish(self, topic, msg):
        ''' TODO: publish No one subscribe through meta topic'''
        # if topic != 'r:':   print '*** publish: ', topic, msg
        oids_to_remove = []
        oids = self._subscriptions.get(topic, {})
        for oid, destinations in oids.items():
            if oid is not None and oid not in self._subscribers:
                oids_to_remove.append(oid)
                continue
            for destination, subscription_info in destinations.items():
                # Get the callable in the case of a method destination
                if oid is not None and oid in self._subscribers:
                    callback = getattr(self._subscribers[oid], destination)
                else:
                    callback = destination
                if subscription_info.get('only_once', False):
                    self._unsubscribe(topic, oid, destination)
                self._send_msg(callback, topic, msg)

        for oid in oids_to_remove:
            self._subscriptions[topic].pop(oid, None)

    def _send_msg(self, destination, topic, msg):
        destination(topic, msg)


def instance():
    return Hub.instance()
