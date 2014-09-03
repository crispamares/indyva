from indyva.epubsub.abc_publisher import IPublisher, pub_result
from indyva.epubsub.bus import Bus
from indyva.names import INamed
from indyva.grava import IDefined

class SharedObject(INamed, IPublisher, IDefined):
    '''
    A SharedObject (SOs) is a base class for flexible containers that might
    contain application state, be shared between process or described
    with a grammar.

    The flexibility of this objects comes at a price. Usually the
    reusability of modules depending on shared objects is compromised
    since SOs don't have any schema or limitation in form.

    Use them if other datasets like Tables are not flexible enough or
    are overkill.

    Also, take a look to the dynamics and use them instead if can find
    something that feet your needs.
    '''
    def __init__(self, name, topics=None, prefix=''):
        INamed.__init__(self, name, prefix=prefix)

        self._sos = {}

        default_topics = ['change', 'attach', 'detach']
        topics = default_topics if topics is None else default_topics.append(topics)
        bus = Bus(prefix= '{0}{1}:'.format(prefix, self.name))
        IPublisher.__init__(self, bus, topics)

    @property
    def grammar(self):
        gv = dict(name = self.name)
        if self._sos:
            gv.update(dict(sos = {so.oid : so.grammar for so in self._sos.values}))
        return gv

    def _retransmit_change(self, topic, msg):
        msg['original_topic'] = topic
        self._bus.publish('change', msg)

    @pub_result('attach')
    def attach_so(self, so):
        
        self._sos[so.oid] = so
        so.subscribe('change', self._retransmit_change)
        return so

    @pub_result('detach')
    def detach_so(self, so):
        so = self._sos.pop(so)
        so.unsubscribe('change', self._retransmit_change)
        return so

