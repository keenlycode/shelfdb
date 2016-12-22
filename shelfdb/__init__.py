import asyncio, shelve, os, uuid
from copy import copy
from datetime import datetime

class Shelf(dict):
    def __init__(self, db_dir=None, *args, **kw):
        if db_dir is None:
            db_dir = os.path.join(os.getcwd(), 'db')
        self.dir = db_dir
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        return super().__init__(*args, **kw)

    def __getitem__(self, k):
        if (not k in self or
                isinstance(super().__getitem__(k).shelf.dict, shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.dir, k))
            super().__setitem__(
                k, ShelfQuery(shelf))
        return super().__getitem__(k)

    def get(self, k, *args, **kw):
        return self.__getitem__(k, *args, **kw)

    def close(self):
        for k in self:
            self[k].close()


class ShelfQuery():
    def __init__(self, shelf):
        self._shelf = shelf

    def __iter__(self):
        for k, v in self._shelf.items():
            v.update({"_id": k})
            yield v

    def __getitem__(self, k):
        entry = self._shelf[k]
        entry.update({'_id': k})
        return ChainQuery([entryy])

    def filter(self, fn):
        return ChainQuery(filter(fn, self))

    def update(self, patch):
        for entry in self:
            id_ = entry.pop('_id')
            entry.update(patch)
            self._shelf[id_] = entry

    def insert(self, entry=None):
        # Since id_=str(uuid.uuid1()) in def args will return the same value
        id_ = str(uuid.uuid1())
        self._shelf[id_] = entry
        return id_

    def delete(self):
        for entry in self:
            del self._shelf[entry['_id']]

class ChainQuery(ShelfQuery):
    def __init__(self, results):
        self._results = results

    def __iter__(self):
        for entry in self._results:
            yield entry

    def filter(self, fn):
        return ChainQuery(filter(fn, self))
