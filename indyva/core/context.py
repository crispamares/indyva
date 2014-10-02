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
        self._active_session_queue = []

        self.stacking = False

        self.add_session(Session('_default'), as_active=True)

    def open(self, context_info):
        if context_info is not None:
            session_name = context_info['session']
            if self.active_session.name != session_name:
                self.activate_session(session_name)
                self.stacking = True
        return self


    def close(self):
        if self.stacking:
            self.pop_active_session()
            self.stacking = False

    def add_session(self, session, as_active=False):
        self._open_sessions[session.name] = session
        if as_active:
            self.activate_session(session.name)

    def has_session(self, name):
        return name in self._open_sessions

    def get_session(self, name):
        return self._open_sessions[name]

    def remove_session(self, name):
        if name in self._active_session_queue[:-1]:
            raise ValueError("The session '{}' can't be removed because is currently in use"
                             .format(name))
        self._open_sessions.pop(name)

    @property
    def active_session(self):
        return self._active_session_queue[-1]

    def activate_session(self, name):
        self._active_session_queue.append(self.get_session(name))

    def activate_default(self):
        self._active_session_queue.append(self.get_session('_default'))

    def pop_active_session(self):
        self._active_session_queue.pop()

    def __str__(self):
        return "  - Active Session: {}\n  - Open Sessions: {}".format(self.active_session,
                                                                      self._open_sessions)



class Session(object):

    def __init__(self, name):
        """
        Holds all the Session dependent objects

        Might has the following `SessionSingleton`s:

        - Front
        - NameAuthority
        - Hub
        - Showcase

        :param str name: The identifier of the session
        """
        self.name = name
        self.root = None

    def __str__(self):
        return "{} @ {}".format(self.name, id(self))


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
