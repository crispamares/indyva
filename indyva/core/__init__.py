__all__ = ['names', 'grava', 'kernel', 'Singleton']


class Singleton(object):
    """
    A flexible implementation of the Singleton pattern

    """

    @classmethod
    def instance(cls, *args, **kwargs):
        """
        Returns a global instance.

        :warning: Not ThreadSafe.
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    @classmethod
    def initialized(cls):
        """Returns true if the singleton instance has been created."""
        return hasattr(cls, "_instance")

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
        singleton_cls._instance = self


import grava
import names
import kernel
