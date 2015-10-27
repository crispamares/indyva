import pymongo


class Connection(object):
    '''Borg pattern in order to have a single MongoClient'''
    __shared_state = dict(mongo_host = 'localhost',
                          mongo_port = 27017,
                          _client = None,
                          _db = 'test'
                          )

    def __init__(self):
        self.__dict__ = self.__shared_state
        if self._client is None:
            self._client = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._client[self._db]

    @db.setter
    def set_db(self, db):
        self._db = db
