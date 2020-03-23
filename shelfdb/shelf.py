"""Module to handle file api for shelfdb."""

import shelve
import os
import uuid
from datetime import datetime
from itertools import islice
from functools import reduce


class DB:
    """Database class to manage `shelves.open()`"""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._shelf = {}

    def shelf(self, shelf_name: str) -> 'Shelf':
        """
        :param `shelf_name (str)`:
        :io: create shelf file named `shelf_name` to store entries if needed.
        """
        if (shelf_name not in self._shelf or
                isinstance(
                    self._shelf[shelf_name]._shelf.dict,
                    shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.path, shelf_name))
            self._shelf[shelf_name] = Shelf(
                shelf,
                lambda: (Item(item[0], item[1]) for item in shelf.items())
            )
        return self._shelf[shelf_name]

    def close(self):
        """Close all shelf files."""
        for k in self._shelf:
            self._shelf[k]._shelf.close()


class Shelf:
    def __init__(self, shelf: 'shelve.open()', items_iterator_function):
        self._shelf = shelf
        self._items_iterator_function = items_iterator_function

    def __iter__(self):
        """Iterator for items"""
        return iter(self._items_iterator_function())

    def count(self, filter_=None):
        return reduce(lambda x, y: x+1, filter(filter_, self), 0)

    def delete(self):
        """Delete queried entries"""
        for item in self:
            del self._shelf[item.id]

    def edit(self, func):
        for item in self:
            data = func(item.copy())
            assert isinstance(data, dict)
            self._shelf[item.id] = data

    def filter(self, filter_=None):
        return Shelf(self._shelf, lambda: filter(filter_, self))

    def first(self, filter_=None):
        try:
            item = next(filter(filter_, self))
        except StopIteration:
            return None
        return Entry(self._shelf, item.id, self._shelf[item.id])

    def get(self, id: 'str(uuid.uuid1())'):
        try:
            return Entry(self._shelf, id, self._shelf[id])
        except KeyError:
            return None

    def insert(self, data):
        uuid1 = str(uuid.uuid1())
        assert isinstance(data, dict)
        self._shelf[uuid1] = data
        return uuid1

    def items(self):
        for item in self:
            yield item

    def map(self, func):
        return Shelf(self._shelf, lambda: map(func, self))

    def reduce(self, func, initializer=None):
        if initializer is None:
            return reduce(func, self)
        return reduce(func, self, initializer)

    def put(self, id, data):
        """Put entry with specified ID"""
        assert isinstance(data, dict)
        self._shelf[str(id)] = data

    def replace(self, obj):
        if isinstance(obj, dict):
            for item in self:
                self._shelf[item.id] = obj

    def slice(self, start, stop, step=None):
        return Shelf(self._shelf, lambda: islice(self, start, stop, step))

    def sort(self, key=lambda item: item.timestamp, reverse=False):
        return Shelf(
            self._shelf,
            lambda: sorted(self, key=lambda item: key(item), reverse=reverse))

    def update(self, data):
        assert isinstance(data, dict), 'Update data should be dict object'
        for item in self:
            item.update(data)
            self._shelf[item.id] = item


class Item(dict):
    def __init__(self, id, data):
        self.id = id
        super().__init__(data)

    @property
    def timestamp(self):
        """Entry's timestamp from uuid1. Use formular from stack overflow.
        See in stackoverflow.com : https://bit.ly/2EtH05b
        """
        try:
            return self._timestamp
        except AttributeError:
            self._timestamp = datetime.fromtimestamp(
                (uuid.UUID(self.id).time - 0x01b21dd213814000)*100/1e9)
            return self._timestamp


class Entry(Item):
    def __init__(self, shelf, id, data):
        self._shelf = shelf
        self.id = id
        super().__init__(id, data)

    def delete(self):
        """Delete this entry"""
        del self._shelf[self.id]

    def edit(self, func):
        data = func(self.copy())
        self.replace(data)

    def replace(self, data):
        assert isinstance(data, dict)
        self._shelf[self.id] = data

    def update(self, data):
        super().update(data)
        self._shelf[self.id] = self.copy()
