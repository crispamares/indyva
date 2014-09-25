# coding: utf-8
'''
The indyva context is a class that holds meta information about
the current ongoing work, like the `Session` or in the future some
knowledge about the users or the connections status.

A context is gonna be passed to any RPC call as a named attribute
`_context`. The dispatcher chain has a middleware step called
`context_handling` that will process the context information, so the
context is gonna be transparent to services and probably to any other
class inside indyva.
'''

from indyva.core import Singleton


class Context(Singleton):

    def __init__(self):

        self._open_sessions = {}
        self._active_session = None

        self.add_session(Session('default'), as_active=True)

    def add_session(self, session, as_active=False):
        self._open_sessions[session.session_id] = session
        if as_active:
            self.activate_session(session.session_id)

    def has_session(self, session_id):
        return session_id in self._open_sessions

    def get_session(self, session_id):
        return self._open_sessions[session_id]

    @property
    def active_session(self):
        return self._active_session

    def activate_session(self, session_id):
        self._active_session = self.get_session(session_id)



class Session(object):

    def __init__(self, session_id):
        """
        Holds all the Session dependent objects

        Might has the following `SessionSingleton`s:

        - Front
        - NameAuthority
        - Hub
        - Showcase

        :param str session_id: The identifier aka `sid` of the session
        """
        self.session_id = session_id
        self.root = None


class SessionSingleton(object):
    """
    A flexible implementation of the Singleton pattern

    """

    @classmethod
    def instance(cls, *args, **kwargs):
        """
        Returns a global instance.

        :warning: Not ThreadSafe.
        """
        session = Context.instance().active_session
        class_name = cls.__name__
        if not hasattr(session, class_name):
            setattr(session, class_name, cls(*args, **kwargs))
        return getattr(session, class_name)

    @classmethod
    def initialized(cls):
        """Returns true if the singleton instance has been created."""
        session = Context.instance().active_session
        class_name = cls.__name__
        return hasattr(session, class_name)

    def install(self):
        """
        Installs this object as the singleton instance.

        This is normally not necessary as `instance()` will create an
        instance on demand, but you may want to call `install` to use
        a custom subclass of any subclass of `Singleton`. You just
        need to define a class attribute `_singleton_cls` with the
        `Singleton` class that the subclasses want to be attached to.
        """
        cls = self.__class__
        singleton_cls = cls if not hasattr(cls, "_singleton_cls") else cls._singleton_cls
        assert not singleton_cls.initialized()

        session = Context.instance().active_session
        class_name = singleton_cls.__name__
        setattr(session, class_name, self)
