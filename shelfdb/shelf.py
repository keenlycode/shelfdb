"""Module to handle file api for shelfdb."""

import shelve
import os
import uuid
from datetime import datetime
from itertools import islice
from functools import reduce
import inspect


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
    def __init__(self, shelf: 'shelve.open()', items_iterator_function):
        self._shelf = shelf
        self._items_iterator_function = items_iterator_function

    def __iter__(self):
        """Iterator for items"""
        return iter(self._items_iterator_function())

    def items_generator(self):
        for item in self:
            yield item

    def delete(self):
        """Delete queried entries"""
        for item in self:
            del self._shelf[item[0]]

    def filter(self, filter_=lambda item: True):
        param = inspect.signature(filter_).parameters
        param = len(param)
        iterator_function = None
        if param == 1:
            iterator_function = lambda: (item for item in self if filter_(item[1]))
        elif param == 2:
            iterator_function = lambda: (item for item in self if filter_(item[0], item[1]))
        return Shelf(self._shelf, iterator_function)

    def first(self, filter_=lambda item: True):
        param = inspect.signature(filter_).parameters
        param = len(param)
        if param == 1:
            for item in self:
                if filter_(item[1]):
                    return Entry(self._shelf, item[0])
        elif param == 2:
            for item in self:
                if filter_(item[0], item[1]):
                    return Entry(self._shelf, item[0])

    def get(self, id: 'str(uuid.uuid1())'):
        return Entry(self._shelf, id)

    def insert(self, data):
        uuid1 = uuid.uuid1()
        uuid1 = str(uuid1)
        assert isinstance(data, dict)
        self._shelf[uuid1] = data
        return uuid1

    def map(self, func):
        return MapReduce(map(func, self))

    def put(self, uuid1, data):
        """Put entry with specified ID"""
        uuid1 = uuid.UUID(uuid1)
        assert uuid1.version == 1
        assert isinstance(data, dict)
        self._shelf[str(uuid1)] = data

    def replace(self, data):
        if isinstance(data, dict):
            for item in self:
                self._shelf[item[0]] = data
        elif callable(data):
            generator = self.items_generator()
            item = next(generator)
            data_to_replace = data(item[0], item[1])
            assert isinstance(data_to_replace, dict)
            self._shelf[item[0]] = data_to_replace
            for item in generator:
                self._shelf[item[0]] = data(item[0], item[1])

    def slice(self, start, stop, step=None):
        return Shelf(self._shelf, lambda: islice(self, start, stop, step))

    def sort(self, func=lambda id, item: id, reverse=False):
        return Shelf(self._shelf,
            lambda: iter(
                sorted(self,
                    key=lambda item: func(item[0], item[1]),
                    reverse=reverse)))

    def update(self, data):
        if isinstance(data, dict):
            for item in self:
                item[1].update(data)
                self._shelf[item[0]] = item[1]
        elif callable(data):
            for item in self:
                item[1].update(data(item[0], item[1]))
                self._shelf[item[0]] = item[1]


class Entry(dict):
    """Entry API"""

    def __init__(self, shelf, id):
        self._shelf = shelf
        self.id = id
        super().__init__(shelf[id])

    def delete(self):
        """Delete this entry"""
        del self._shelf[self.id]

    def replace(self, data):
        if callable(data):
            data = data(self)
        self.clear()
        super().update(data)
        self._shelf[self.id] = self.copy()

    def update(self, data):
        if callable(data):
            data = data(self)
        super().update(data)
        self._shelf[self.id] = self.copy()


class MapReduce:
    def __init__(self, map_obj):
        self.map_obj = map_obj

    def __iter__(self):
        return iter(self.map_obj)

    def reduce(self, func, initializer=None):
        if initializer is None:
            return reduce(func, self.map_obj)
        return reduce(func, self.map_obj, initializer)
