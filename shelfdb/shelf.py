"""Module to handle file api for shelfdb.
"""

import shelve, os, uuid
from datetime import datetime
from itertools import islice
from collections import deque
from functools import reduce


def db(path):
    """Open database, return DB object.

    Args:
        path (string): path for database.
    Return:
        ``DB`` object.
    """
    return DB(path)


class DB():
    """Class to handle shelves in database"""

    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._shelf = {}

    def shelf(self, shelf_name):
        """Get ``ShelfQuery`` object. create shelf file named ``shelf_name``
        to store entries if needed.
        """
        if (not shelf_name in self._shelf or
                isinstance(self._shelf[shelf_name]._shelf.dict, shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.path, shelf_name))
            self._shelf[shelf_name] = ShelfQuery(shelf)
        return self._shelf[shelf_name]

    def close(self):
        """Close all shelf files"""
        for k in self._shelf:
            self._shelf[k]._shelf.close()


class ShelfQuery():
    def __init__(self, shelf):
        self._shelf = shelf

    def __iter__(self):
        """Iterator for entries"""
        return map(self._get_entry, self._shelf.items())

    def _get_entry(self, items):
        """Just to be used in `def __iter__(self)`
        to map with `items()` iterator.
        """
        return Entry(self._shelf, items[0], items[1])

    def __getitem__(self, id_):
        entry = self._shelf[id_]
        return Entry(self._shelf, id_, entry)

    def get(self, id_):
        """Get an entry by ID."""
        return self.__getitem__(id_)

    def first(self, filter_):
        """Get the first entry matched by ``filter_`` and exit iteration."""
        try:
            return next(filter(filter_, self))
        except StopIteration:
            return None

    def filter(self, filter_):
        """Get entries matched by ``filter_``."""
        return ChainQuery(filter(filter_, self))

    def map(self, fn):
        """Apply map function on queried entries, return iterator."""
        return ChainQuery(map(fn, self))

    def reduce(self, fn, initializer=None):
        """Apply reduce function on queried entries"""
        return reduce(fn, self, initializer)

    def run(self):
        """Iterate through ChainQuery and keep results in a list"""
        return [obj for obj in self if obj is not None]

    def slice(self, start, stop, step=None):
        """Slice queried entries."""
        return ChainQuery(islice(self, start, stop, step))

    def sort(self, key=lambda entry: entry.ts, reverse=False):
        """Sort queried entries."""
        return ChainQuery(iter(sorted(self, key=key, reverse=reverse)))

    def insert(self, entry):
        """Insert an entry. Automatic generate **uuid1** as entry's ID."""

        # Must generate uuid1 here, since id_=str(uuid.uuid1()) in def args
        # will return the same value all the times after first call.
        id_ = str(uuid.uuid1())
        if isinstance(entry, dict):
            self._shelf[id_] = entry
            return id_
        else:
            raise Exception('Entry is not a dict object')

    def update(self, patch):
        """Update queried entries with ``patch``"""
        [entry.update(patch) for entry in self]

    def replace(self, data):
        """Replace queried entries with ``data``"""
        [entry.replace(data) for entry in self]

    def delete(self):
        """Delete queried entries"""
        [entry.delete() for entry in self]


class ChainQuery(ShelfQuery):
    """Subclass of ShelfQuery to store query result.
    The propose of ChainQuery object is to keep ShelfQuery object state
    unmodified for future use.
    """

    def __init__(self, results):
        self._results = results

    def __iter__(self):
        return self._results

    def __next__(self):
        return next(self._results)


class Entry(dict):
    """Class for Entry object which contains API to deal with shelf."""

    # To have `entry` as an argument is by design to be more efficient
    # when call by `ShelfQuery._get_entry()`. Since entry data will be pull out
    # from the shelf anyway before leave `__init__()`, then lets put this duty to
    # the caller.
    def __init__(self, shelf, id_, entry):
        self._shelf = shelf
        self._id = id_
        super().__init__(entry)
        super().__setitem__('_id', id_)

    @property
    def ts(self):
        """Entry's timestamp from uuid1. Got the formular from stack overflow.
        http://stackoverflow.com/questions/3795554/extract-the-time-from-a-uuid-v1-in-python
        """
        try:
            return self._ts
        except AttributeError:
            self._ts = datetime.fromtimestamp(
                (uuid.UUID(self._id).time - 0x01b21dd213814000)*100/1e9
            )
            return self._ts

    def update(self, patch):
        """Update the entry with `patch`."""
        super().update(patch)
        self._save()

    def replace(self, entry):
        """Replace the entry."""
        if type(entry) is not dict:
            raise Exception('entry to replace must be a dict object')
        entry['_id'] = self._id
        self.clear()
        self.update(entry)

    def _save(self):
        entry = self.copy() # store only dict data.
        self._shelf[self._id] = entry

    def delete(self):
        del self._shelf[self._id]
