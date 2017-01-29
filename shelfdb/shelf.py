import shelve, os, uuid, json, re
from datetime import datetime
from itertools import islice
from collections import deque


def open(dir_):
    return DB(dir_)


class DB():
    def __init__(self, dir_=os.path.join(os.getcwd(), 'db')):
        self.dir = dir_
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        self._shelf = {}

    def shelf(self, shelf_name):
        if (not shelf_name in self._shelf or
                isinstance(self._shelf[shelf_name]._shelf.dict, shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.dir, shelf_name))
            self._shelf[shelf_name] = ShelfQuery(shelf)
        return self._shelf[shelf_name]

    def close(self):
        for k in self._shelf:
            self[k]._shelf.close()


class ShelfQuery():
    def __init__(self, shelf):
        self._shelf = shelf

    def __iter__(self):
        return map(self._get_entry, self._shelf.items())

    def __getitem__(self, id_):
        entry = self._shelf[id_]
        return Entry(self._shelf, id_, entry)

    def _get_entry(self, item):
        return Entry(self._shelf, item[0], item[1])

    def get(self, id_):
        return self.__getitem__(id_)

    def first(self, filter_):
        try:
            return next(filter(filter_, self))
        except StopIteration:
            return None

    def filter(self, filter_):
        return ChainQuery(filter(filter_, self))

    def map(self, fn):
        return ChainQuery(map(fn, self))

    def apply(self, fn):
        deque(map(fn, self), 0)
        return

    def slice(self, start, stop, step=None):
        return ChainQuery(islice(self, start, stop, step))

    def sort(self, key=lambda entry: entry.ts, reverse=False):
        return ChainQuery(iter(sorted(self, key=key, reverse=reverse)))

    def insert(self, entry):
        # Since id_=str(uuid.uuid1()) in def args will return the same value
        id_ = str(uuid.uuid1())
        if isinstance(entry, dict):
            self._shelf[id_] = entry
            return id_
        else:
            raise Exception('Entry is not a dict object')

    def update(self, patch):
        [entry.update(patch) for entry in self]

    def replace(self, data):
        [entry.replace(data) for entry in self]

    def delete(self):
        [entry.delete() for entry in self]


class ChainQuery(ShelfQuery):
    def __init__(self, results):
        self._results = results

    def __iter__(self):
        return self._results


class Entry(dict):
    def __init__(self, shelf, id_, entry):
        self._shelf = shelf
        self._id = id_
        super().__init__(entry)
        super().__setitem__('_id', id_)

    @property
    def ts(self):
        """Entry timestamp from uuid1"""
        try:
            return self._ts
        except AttributeError:
            self._ts = datetime.fromtimestamp(
                (uuid.UUID(self._id).time - 0x01b21dd213814000)*100/1e9
            )
            return self._ts

    def update(self, patch):
        super().update(patch)
        self._save()

    def replace(self, entry):
        entry = entry.copy() # Make sure not to replace itself.
        entry['_id'] = self._id
        self.clear()
        self.update(entry)

    def _save(self):
        entry = self.copy()
        self._shelf[self._id] = entry

    def delete(self):
        del self._shelf[self._id]
