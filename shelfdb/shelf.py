"""Module to handle file api for shelfdb."""

import shelve
import os
import uuid
from datetime import datetime
from itertools import islice
from functools import reduce
from collections import UserDict
from collections.abc import ItemsView


class DB:
    """Database class to manage `shelves.open()`"""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._shelf = {}

    def shelf(self, shelf_name: str) -> 'ShelfQuery':
        """
        :param `shelf_name (str)`: 
        :io: create shelf file named `shelf_name` to store entries if needed.
        """
        if (shelf_name not in self._shelf or
                isinstance(
                    self._shelf[shelf_name]._shelf.dict,
                    shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.path, shelf_name))
            self._shelf[shelf_name] = Shelf(shelf, shelf.items)
        return self._shelf[shelf_name]

    def close(self):
        """Close all shelf files."""
        for k in self._shelf:
            self._shelf[k]._shelf.close()


# class Iterator:
#     def __init__(self, iterator):
#         self._iterator = iterator

#     def __iter__(self):
#         return self._iterator

#     def map


class Shelf:
    def __init__(self, shelf: 'shelve.open()', iterator_function):
        self._shelf = shelf
        self._iterator_function = iterator_function

    def __iter__(self):
        """Iterator for items"""
        return iter(self._iterator_function())

    @staticmethod
    def _get_datetime_from_uuid(_id):
        return datetime.fromtimestamp(
            (uuid.UUID(_id).time - 0x01b21dd213814000)*100/1e9)

    def get(self, id_: 'str(uuid.uuid1())'):
        return Item(self._shelf, id_, self._shelf[id_])

    def insert(self, data):
        uuid1 = uuid.uuid1()
        uuid1 = str(uuid1)
        assert isinstance(data, dict)
        self._shelf[uuid1] = data
        return uuid1

    def map(self, func):
        return map(func, self)

    def reduce(self, func, initializer=None):
        if initializer is None:
            return reduce(func, self)
        return reduce(func, self, initializer)

    def put(self, uuid1, data):
        """Put entry with specified ID"""
        uuid1 = uuid.UUID(uuid1)
        assert uuid1.version == 1
        assert isinstance(data, dict)
        self._shelf[str(uuid1)] = data

    def first(self, _filter=lambda item: True):
        for item in self:
            if _filter(item[1]):
                return Item(self._shelf, item[0], item[1])

    def filter(self, _filter=lambda item: True):
        return Shelf(self._shelf, lambda: (item for item in self if _filter(item[1])))

    def update(self, data):
        if callable(data):
            data = data(self._shelf)
        assert isinstance(data, dict)
        for item in self:
            item[1].update(data)
            self._shelf[item[0]] = item[1]

    def replace(self, data):
        if callable(data):
            data = data(self._shelf)
        assert isinstance(data, dict)
        for item in self:
            self._shelf[item[0]] = data

    def slice(self, start, stop, step=None):
        return Shelf(self._shelf, lambda: islice(self, start, stop, step))

    def sort(self, key=lambda item: Shelf._get_datetime_from_uuid(item[0]), reverse=False):
        return Shelf(self._shelf, lambda: iter(sorted(self, key=key, reverse=reverse)))

    def delete(self):
        """Delete queried entries"""
        for item in self._shelf.items():
            del self._shelf[item[0]]

    
# class Items(Shelf):

#     def __init__(self, shelf, items):
#         self._shelf = shelf
#         self._items = items

#     def __iter__(self):
#         return self._items

#     def __next__(self):
#         return next(self._items)


class Item(UserDict):
    """Entry API"""

    def __init__(self, shelf, _id, data):
        self._shelf = shelf
        self.id = _id
        self.data = data

    @property
    def datetime(self):
        """
        Entry's timestamp from uuid1.
        Formular from stackoverflow.com : https://bit.ly/2EtH05b
        """
        try:
            return self._datetime
        except AttributeError:
            self._datetime = datetime.fromtimestamp(
                (uuid.UUID(self.id).time - 0x01b21dd213814000)*100/1e9)
            return self._datetime

    def update(self, data):
        if callable(data):
            data = data(self.data)
        assert isinstance(data, dict)
        self.data.update(data)
        self._save()

    def replace(self, data):
        if callable(data):
            data = data(self.data)
        assert isinstance(data, dict)
        self.data = data
        self._save()

    def _save(self):
        self._shelf[self.id] = self.data

    def delete(self):
        """Delete this entry"""
        del self._shelf[self.id]


class ShelfQuery:
    """Database query API. Return either ChainQuery or Entry object."""

    def __init__(self, shelf: 'shelve.open()'):
        self._shelf = shelf

    def __iter__(self):
        """Iterator for entries"""
        return map(
            lambda item: Entry(self._shelf, item[0], item[1]),
            self._shelf.items())

    def __getitem__(self, id_: 'str(uuid.uuid1())'):
        return Entry(self._shelf, id_, self._shelf[id_])

    def get(self, id_: 'str(uuid.uuid1())') -> 'Entry':
        """Get an entry by ID."""
        return self.__getitem__(id_)

    def first(self, filter_: 'function' = None) -> 'Entry':
        '''
        Get the first entry matched by `filter_` then stop iteration.
        params:
            filter_ (function): Filter function or lambda which get
            Entry object as an argument. Must return **True** or **False**.
            If return **True**, return Entry object and stop Iteration.

        Return:
            ``Entry`` object.

        Example::
            shelfquery.first(lambda entry: entry['name'] == 'admin')
        '''
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

    def map(self, func):
        """Apply map function on ``ChainQuery``.

        Args:
            ``fn`` (function): Function to apply by map, receive Entry object
            as an argument. Can return anything which will be kept in
            ChainQuery result.

        Return:
            ``ChainQuery`` of result from map function.
        """
        return ChainQuery(map(func, self))

    def reduce(self, func, initializer=None):
        """Apply reduce function on ``ChainQuery``.

        See: https://docs.python.org/3/library/functools.html#functools.reduce
        """
        if initializer is None:
            return reduce(func, self)
        return reduce(func, self, initializer)

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
        if not isinstance(entry, dict):
            raise Exception('Entry is not a dict object')
        entry.pop('_id', None)
        self._shelf[id_] = entry
        return id_

    def put(self, uuid1, entry):
        """Put entry with specified ID"""
        uuid1 = uuid.UUID(uuid1)
        if uuid1.version != 1:
            raise Exception('ID is not UUID1')
        if not isinstance(entry, dict):
            raise Exception('Entry is not a dict object')
        entry.pop('_id', None)
        self._shelf[str(uuid1)] = entry

    def update(self, patch):
        """Update queried entries with ``patch``"""
        if isinstance(patch, dict):
            patch.pop('_id', None)
            [entry._update_dict(patch) for entry in self]
        elif callable(patch):
            [entry._update_fn(patch) for entry in self]
        else:
            raise '`patch` is not an instance of `dict` or `function`'

    def replace(self, obj):
        """Replace queried entries with ``data``"""
        if isinstance(obj, dict):
            obj.pop('_id', None)
            [entry._replace_dict(obj) for entry in self]
        elif callable(obj):
            [entry._replace_fn(obj) for entry in self]
        else:
            raise '`patch` is not an instance of `dict` or `function`'

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


# class Entry(dict):
#     """Entry API"""

#     # To have `entry` as an argument is by design to be more efficient
#     # when call by `ShelfQuery._get_entry()`. Since entry data will be pull out
#     # from the shelf anyway before leave `__init__()`, then lets put this duty to
#     # the caller.
#     def __init__(self, shelf, id_, entry):
#         self._shelf = shelf
#         self._id = id_
#         super().__init__(entry)
#         super().__setitem__('_id', id_)

#     @property
#     def ts(self):
#         """Entry's timestamp from uuid1. Use formular from stack overflow.

#         See in stackoverflow.com : https://bit.ly/2EtH05b
#         """
#         try:
#             return self._ts
#         except AttributeError:
#             self._ts = datetime.fromtimestamp(
#                 (uuid.UUID(self._id).time - 0x01b21dd213814000)*100/1e9
#             )
#             return self._ts

#     def _update_dict(self, patch):
#         super().update(patch)
#         self._save()

#     def _update_fn(self, patch):
#         patch = patch(self.copy())
#         assert isinstance(patch, dict)
#         patch.pop('_id', None)
#         super().update(patch)
#         self._save()

#     def _replace_dict(self, patch):
#         super().clear()
#         super().update(patch)
#         self._save()

#     def _replace_fn(self, patch):
#         patch = patch(self.copy())
#         assert isinstance(patch, dict)
#         patch.pop('_id', None)
#         super().clear()
#         super().update(patch)
#         self._save()

#     def update(self, patch):
#         """Update this entry with ``patch``.

#         Args:
#             ``patch`` (dict): Data to update.
#         """
#         if isinstance(patch, dict):
#             return self._update_dict(patch)
#         if callable(patch):
#             return self._update_fn(patch)
#         raise '`patch` is not an instance of `dict` for `function`'

#     def replace(self, obj):
#         """Replace this entry with ``obj``

#         Args:
#             ``obj`` (dict, function): Object to replace.
#         """
#         if isinstance(obj, dict):
#             return self._replace_dict(obj)
#         if callable(obj):
#             return self._replace_fn(obj)
#         raise '`obj` is not an instance of `dict` for `function`'

#     def _save(self):
#         self._shelf[self._id] = self.copy() # store only dict data.

#     def delete(self):
#         """Delete this entry"""
#         del self._shelf[self._id]
