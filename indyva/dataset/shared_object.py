from indyva.epubsub.abc_publisher import IPublisher, pub_result
from indyva.epubsub.bus import Bus
from indyva.core.names import INamed
from indyva.core.grava import IDefined, register

from copy import copy


class VersionError(Exception):
    '''
    This Exception is raised when there is a modification
    conflict. Prevents silent data races.
    '''


@register("shared_object")
class SharedObject(INamed, IPublisher, IDefined):
    '''
    A SharedObject (SOs) is a flexible container for application state.

    * All changes are published under a "change" topic.
    * It can be described with a grammar.
    * It is designed to be shared between processes.

    Version Control
    ---------------

    It does not provide any high level API for modification, instead
    the contained data is pulled by clients, modified and pushed back
    again. The push method can fail if the SO had been modified in
    between pull and push.

    To support this conflict-aware behavior the SO maintains a simple
    version control. The contained data is pulled coupled with a
    version tag, then the client might modify the data and eventually
    the client might pushes the modified data back along with the
    given version tag. This push process can fail if the pushed
    version tag is older than the internal version. Every modification
    generates a new version.

    When to use them
    ----------------

    They are designed to contain small amount of data. A SO has one
    collection inside, either a dictionary or a list. No other
    data types are allowed.

    The flexibility of this objects comes at a price. Usually the
    reusability of modules depending on shared objects is compromised
    since SOs don't have any schema or limitation in form.

    Use them if other datasets like Tables are not flexible enough or
    are overkill.

    Also, take a look to the dynamics and use them instead if can find
    something that feet your needs.

    '''
    def __init__(self, name, data, topics=None, prefix=''):
        INamed.__init__(self, name, prefix=prefix)

        self._check_data(data)

        self._data = data
        self._version = 1

        default_topics = ['change']
        topics = default_topics if topics is None else default_topics.append(topics)
        bus = Bus(prefix='{0}{1}:'.format(prefix, self.name))
        IPublisher.__init__(self, bus, topics)

    def pull(self):
        '''
        Returns the inner state of the SharedObject and the current
        version. You should keep the version tag because is needed for
        pushing back the changes.

        :returns: (data, version)
        '''
        return (copy(self._data), copy(self._version))

    @pub_result('change')
    def push(self, data, version):
        '''
        Modify the inner state of the SharedObject. Will fail if detects
        conflicts with the version tag.

        :raises `VersionError`: When the provided version is older than the current

        :param data: list or dict. The updated data.
        :param version: This should be the returned by pull or push methods.

        :returns: (data, version)
                  The version generated after the modification.
                  Becomes the current one.
        '''
        self._check_data(data)
        if version < self._version:
            raise VersionError("Version confict ocurred in SharedObject '{0}'"
                               .format(self.name))

        self._data = data
        self._version += 1

        return (copy(self._data), copy(self._version))

    @property
    def grammar(self):
        gv = {"type":"shared_object",
              "name":self.name,
              "data":self._data}
        return gv


    @classmethod
    def build(cls, grammar, objects=None):
        self = cls(name=grammar['name'],
                   data=grammar['data'])
        return self


    def _check_data(self, data):
        if not isinstance(data, (dict, list)):
            raise ValueError("SharedObject only support dict or list data types:\n"
                             + "\t {0} provided".format(data))
