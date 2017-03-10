"""Module to handle file api for shelfdb."""

import shelve, os, uuid
from datetime import datetime
from itertools import islice
from collections import deque
from functools import reduce


class DB():
    """Database class to manage shelves"""

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
            self._shelf[shelf_name] = ShelfQuery(self, shelf)
        return self._shelf[shelf_name]

    def close(self):
        """Close all shelf files."""
        for k in self._shelf:
            self._shelf[k]._shelf.close()


class ShelfQuery():
    """Database query API. Return either ChainQuery or Entry object."""
    def __init__(self, db, shelf):
        self._db = db
        self._shelf = shelf

    def __iter__(self):
        """Iterator for entries"""
        return map(self._get_entry, self._shelf.items())

    def _get_entry(self, items):
        """To be used in `def __iter__(self)`"""
        return Entry(self._shelf, items[0], items[1])

    def __getitem__(self, id_):
        entry = self._shelf[id_]
        return Entry(self._shelf, id_, entry)

    def get(self, id_):
        """Get an entry by ID.

        Args:
            ``id_`` (string): uuid1 string for the entry.

        Return:
            ``Entry`` object.
        """
        return self.__getitem__(id_)

    def first(self, filter_):
        """Get the first entry matched by ``filter_`` then stop iteration.

        Args:
            ``filter_`` (function): Filter function or lambda which get
            Entry object as an argument. Must return **True** or **False**.
            If return **True**, return Entry object and stop Iteration.

        Return:
            ``Entry`` object.

        Example::

            shelfquery.first(lambda entry: entry['name'] == 'admin')
        """
        try:
            return next(filter(filter_, self))
        except StopIteration:
            return None

    def filter(self, filter_):
        """Get entries matched by ``filter_``.

        Args:
            ``filter_`` (function): Filter function or lambda which get
            Entry object as an argument. Must return **True** or **False**.
            If return **True**, the entry will be kept in ChainQuery result.

        Return:
            ``ChainQuery`` object.
        """
        return ChainQuery(filter(filter_, self))

    def map(self, fn):
        """Apply map function on ``ChainQuery``.

        Args:
            ``fn`` (function): Function to apply by map, receive Entry object as an
            argument. Can return anything which will be kept in ChainQuery result.

        Return:
            ``ChainQuery`` of result from map function.
        """
        return ChainQuery(map(fn, self))

    def reduce(self, fn, initializer=None):
        """Apply reduce function on ``ChainQuery``.

        See: https://docs.python.org/3/library/functools.html#functools.reduce
        """
        if initializer is None:
            return reduce(fn, self)
        else:
            return reduce(fn, self, initializer)

    def run(self):
        """Iterate through ``ChainQuery`` and return results in a ``list``"""
        return [obj for obj in self if obj is not None]

    def slice(self, start, stop, step=None):
        """Slice ``ChainQuery`` by applied ``islice`` function.

        See: https://docs.python.org/3/library/itertools.html#itertools.islice
        """
        return ChainQuery(islice(self, start, stop, step))

    def sort(self, key=lambda entry: entry.ts, reverse=False):
        """Sort ``ChainQuery`` by ``key``.

        Args:
            ``key`` (function): function or lambda which return sort key.

            ``reverse`` (bool): if **True**, reverse the order.

        Return:
            ChainQuery object.
        """
        return ChainQuery(iter(sorted(self, key=key, reverse=reverse)))

    def insert(self, entry):
        """Insert an entry. Automatic generate **uuid1** as entry's ID.

        Args:
            ``entry`` (dict): Entry to be inserted.

        Return:
            ``string``: Entry's UUID.
        """

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
    """Entry API"""

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
        """Entry's timestamp from uuid1. Use formular from stack overflow.

        See: http://stackoverflow.com/questions/3795554/extract-the-time-from-a-uuid-v1-in-python
        """
        try:
            return self._ts
        except AttributeError:
            self._ts = datetime.fromtimestamp(
                (uuid.UUID(self._id).time - 0x01b21dd213814000)*100/1e9
            )
            return self._ts

    def update(self, patch):
        """Update this entry with ``patch``.

        Args:
            ``patch`` (dict): Data to update.
        """
        super().update(patch)
        self._save()

    def replace(self, entry):
        """Replace this entry with ``entry``

        Args:
            ``entry`` (dict): Entry data to replace.
        """
        if type(entry) is not dict:
            raise Exception('entry to replace must be a dict object')
        entry = entry.copy()
        entry['_id'] = self._id
        self.clear()
        self.update(entry)

    def _save(self):
        entry = self.copy() # store only dict data.
        self._shelf[self._id] = entry

    def delete(self):
        """Delete this entry"""
        del self._shelf[self._id]
