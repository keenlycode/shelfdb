import asyncio, shelve, os, uuid
from copy import copy
from datetime import datetime
from itertools import islice


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
                isinstance(super().__getitem__(k)._shelf.dict, shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.dir, k))
            super().__setitem__(
                k, ShelfQuery(shelf))
        return super().__getitem__(k)

    def get(self, k):
        return self.__getitem__(k)

    def close(self):
        for k in self:
            self[k].close()


class ShelfQuery():
    def __init__(self, shelf):
        self._shelf = shelf

    def __iter__(self):
        def _add_id(item):
            item[1].update({"_id": item[0]})
            return item[1]
        return map(_add_id, self._shelf.items())

    def __getitem__(self, k):
        entry = self._shelf[k]
        entry.update({'_id': k})
        return entry

    def first(self, filter_):
        try:
            return next(filter(filter_, self))
        except StopIteration:
            return []

    def filter(self, filter_):
        return ChainQuery(filter(filter_, self))

    def slice(self, start, stop, step=None):
        return ChainQuery(islice(self, start, stop))

    def sort(self, key=lambda entry: entry['_id'], reverse=False):
        return ChainQuery(sorted(self, key=key, reverse=reverse))

    def update(self, patch):
        def _update(entry, patch):
            id_ = entry.pop('_id')
            entry.update(patch)
            self._shelf[id_] = entry
        [_update(entry, patch) for entry in self]

    def insert(self, entry):
        # Since id_=str(uuid.uuid1()) in def args will return the same value
        id_ = str(uuid.uuid1())
        self._shelf[id_] = entry
        return id_

    def put(self, id_, entry):
        self._shelf[id_] = entry

    def delete(self):
        for entry in self:
            del self._shelf[entry['_id']]

class ChainQuery(ShelfQuery):
    def __init__(self, results):
        self._results = results

    def __iter__(self):
        return self._results
