import shelve
import os
import uuid
from datetime import datetime
from itertools import islice
from functools import reduce
from warnings import warn


class DB:
    """Database class to manage `shelves.open()`"""

    def __init__(self, path: str):
        """
        1. Create database object.
        2. Create database directory.

        Parameters
        ----------
        path: str
            Path to database (directory)
        """

        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self._shelf = {}

    def shelf(self, shelf_name: str) -> 'Shelf':
        """
        Create shelf file to store entries.

        Parameters
        ----------
        shelf_name: str
        """
        if (shelf_name not in self._shelf
                or isinstance(
                    self._shelf[shelf_name]._shelf.dict,
                    shelve._ClosedDict)):
            shelf = shelve.open(os.path.join(self.path, shelf_name))
            self._shelf[shelf_name] = Shelf(
                shelf,
                lambda: (Item(item[0], item[1]) for item in shelf.items()))
        return self._shelf[shelf_name]

    def close(self):
        """Close all shelf files."""
        for k in self._shelf:
            self._shelf[k]._shelf.close()


class Shelf:
    def __init__(self, shelf: shelve.DbfilenameShelf, items_iterator_function):
        """
        Parameters
        ----------
        shelf: shelve.DbfilenameShelf
            `shelve.DbfilenameShelf` instace from shelve.open()
        """

        self._shelf = shelf
        self._items_iterator_function = items_iterator_function

    def __iter__(self):
        """Items iterator"""
        return iter(self._items_iterator_function())

    def add(self, item: dict) -> uuid.UUID:
        """Add item to database. Use UUID1 string as ID"""
        
        uuid1 = str(uuid.uuid1())
        assert isinstance(item, dict)
        self._shelf[uuid1] = item
        return uuid1


    def count(self, filter_=None) -> int:
        """Count items using filter function"""

        return reduce(lambda x, y: x + 1, filter(filter_, self), 0)

    def delete(self):
        """Delete entries in chain query"""
        for item in self:
            del self._shelf[item.id]

    def edit(self, func):
        """Edit item using funcion
        
        Parameters
        ----------
        func: function(item: Item) -> dict
            Returned ``dict`` instance will be saved to database
        """

        for item in self:
            data = func(item.copy())
            assert isinstance(data, dict)
            self._shelf[item.id] = data

    def filter(self, filter_=None) -> 'Shelf':
        """Filter items using filter function.

        Parameters
        ----------
        filter_: funciton(item: Item) -> bool
        """

        return Shelf(self._shelf, lambda: filter(filter_, self))

    def first(self, filter_=None) -> 'Item':
        """Get first item matched with filter function.

        Parameters
        ----------
        filter_: function(item: Item) -> bool
        """

        try:
            item = next(filter(filter_, self))
        except StopIteration:
            return None
        return Entry(self._shelf, item.id, self._shelf[item.id])

    def get(self, id: str) -> 'Item':
        """Get item by id"""

        try:
            return Entry(self._shelf, id, self._shelf[id])
        except KeyError:
            return None

    def insert(self, item: dict) -> uuid.UUID:
        """Insert item to database. Use UUID1 string as ID"""
        
        warn('`insert()` is deprecated. Please use `add()`', DeprecationWarning, stacklevel=2)
        uuid1 = str(uuid.uuid1())
        assert isinstance(item, dict)
        self._shelf[uuid1] = item
        return uuid1

    def items(self) -> 'Iterator':
        """Return Iterator instance of the Shelf"""

        return iter(self)

    def map(self, func) -> 'Shelf':
        """Apply ``map()`` on items

        Parameters
        ----------
        func: function(item: Item) -> 'Any'
            Mapping function which can return any instance
            to keep in chain query.
        """

        return Shelf(self._shelf, lambda: map(func, self))

    def patch(self, id_: str, data: dict):
        """Patch entry"""
        assert isinstance(id_, str), 'ID should be ``str`` instance.'
        assert isinstance(data, dict), 'Data should be ``dict`` instance.'
        entry = dict()
        try:
            entry = self._shelf[id_]
        except KeyError:
            pass
        entry.update(data)
        self._shelf[id_] = entry

    def put(self, id_: str, item: dict):
        """Put entry"""

        assert isinstance(id_, str), 'ID should be ``str`` instance.'
        assert isinstance(item, dict), 'Item should be ``dict`` instance.'
        self._shelf[id_] = item

    def reduce(self, func, initializer=None) -> 'Any':
        """Apply ``reduce()`` on items"""

        if initializer is None:
            return reduce(func, self)
        return reduce(func, self, initializer)

    def replace(self, data: dict):
        """Replace entry with data"""

        assert isinstance(data, dict)
        for item in self:
            self._shelf[item.id] = data

    def slice(self, start: int, stop: int, step: int = None) -> 'Shelf':
        """Slice items"""

        return Shelf(self._shelf, lambda: islice(self, start, stop, step))

    def sort(self, key=lambda item: item.timestamp, reverse=False) -> 'Shelf':
        """Sort items"""

        return Shelf(
            self._shelf,
            lambda: sorted(self, key=lambda item: key(item), reverse=reverse))

    def update(self, data: dict):
        """Update entry with data"""

        assert isinstance(data, dict), 'Update data should be dict object'
        for item in self:
            item.update(data)
            self._shelf[item.id] = item


class Item(dict):
    """Item class to read entry from database"""

    def __init__(self, id_, data):
        self.id = id_
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
                (uuid.UUID(self.id).time - 0x01b21dd213814000) * 100 / 1e9)
            return self._timestamp


class Entry(Item):
    """Entry class to write entry to database"""

    def __init__(self, shelf, id, data):
        self._shelf = shelf
        self.id = id
        super().__init__(id, data)

    def delete(self):
        """Delete this entry"""

        del self._shelf[self.id]

    def edit(self, func) -> dict:
        """Edit entry using provided function

        Parameters
        ----------
        func: function(entry) -> dict
            Returned ``dict`` instance will replace the entry.
        """

        data = func(self.copy())
        assert isinstance(data, dict)
        self.replace(data)

    def map(self, func) -> 'Any':
        """map ``func()`` on the entry.

        Parameters
        ----------
        func: function(item: Item) -> 'Any'
            Mapping function which can return any instance as result.
        """

        return func(self)

    def replace(self, data: dict):
        """Replace entry with data"""

        assert isinstance(data, dict)
        self._shelf[self.id] = data

    def update(self, data: dict):
        """Update entry with data"""

        super().update(data)
        self._shelf[self.id] = self.copy()
