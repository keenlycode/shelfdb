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


class Shelf:
    def __init__(self, shelf: 'shelve.open()', items_function):
        self._shelf = shelf
        self._items_function = items_function

    def __iter__(self):
        """Iterator for items"""
        return iter(self._items_function())

    @staticmethod
    def _get_datetime_from_uuid(_id):
        return datetime.fromtimestamp(
            (uuid.UUID(_id).time - 0x01b21dd213814000)*100/1e9)

    def delete(self):
        """Delete queried entries"""
        for item in self._shelf.items():
            del self._shelf[item[0]]

    def filter(self, filter_=lambda item: True):
        return Shelf(self._shelf,
                     lambda: (item for item in self if filter_(item[1])))

    def first(self, filter_=lambda item: True):
        for item in self:
            if filter_(item[1]):
                return Item(self._shelf, item[0], item[1])

    def format(self, format):
        return Shelf(self._shelf, lambda: (format(id, item) for id, item in self))

    def get(self, id_: 'str(uuid.uuid1())'):
        return Item(self._shelf, id_, self._shelf[id_])

    def insert(self, data):
        uuid1 = uuid.uuid1()
        uuid1 = str(uuid1)
        assert isinstance(data, dict)
        self._shelf[uuid1] = data
        return uuid1

    def map(self, func):
        return Map(map(func, self))

    def put(self, uuid1, data):
        """Put entry with specified ID"""
        uuid1 = uuid.UUID(uuid1)
        assert uuid1.version == 1
        assert isinstance(data, dict)
        self._shelf[str(uuid1)] = data

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

    def update(self, data):
        if callable(data):
            data = data(self._shelf)
        assert isinstance(data, dict)
        for item in self:
            item[1].update(data)
            self._shelf[item[0]] = item[1]


class Item(UserDict):
    """Entry API"""

    def __init__(self, shelf, id_, data):
        self._shelf = shelf
        self.id = id_
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

    def _save(self):
        self._shelf[self.id] = self.data

    def delete(self):
        """Delete this entry"""
        del self._shelf[self.id]

    def replace(self, data):
        if callable(data):
            data = data(self.data)
        assert isinstance(data, dict)
        self.data = data
        self._save()

    def update(self, data):
        if callable(data):
            data = data(self.data)
        assert isinstance(data, dict)
        self.data.update(data)
        self._save()


class Map:
    def __init__(self, map_iterator):
        self._map_iterator = map_iterator

    def __iter__(self):
        return self._map_iterator

    def reduce(self, func, initializer=None):
        if initializer is None:
            return reduce(func, self)
        return reduce(func, self, initializer)
