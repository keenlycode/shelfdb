import asyncio, shelve, os, collections
import uuid
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
                isinstance(super().__getitem__(k).dict, shelve._ClosedDict)):
            super().__setitem__(
                k, FileShelf(os.path.join(self.dir, k)))
        return super().__getitem__(k)

    def get(self, k, *args, **kw):
        return self.__getitem__(k, *args, **kw)

    def close(self):
        for k in self:
            self[k].close()


class FileShelf(shelve.DbfilenameShelf):
    def __init__(self, file, *args, **kw):
        self._file = file
        return super().__init__(file, *args, **kw)

    def __setitem__(self, id_, entry):
        if not isinstance(entry, dict):
            raise ValueError('Value must be `dict` instance')
        super().__setitem__(id_, entry)

    def __getitem__(self, id_):
        return Entry(self, id_, super().__getitem__(id_))

    def all(self):
        for id_ in self:
            yield self[id_]

    def insert(self, entry=None):
        # Since id_=str(uuid.uuid1()) in def args will return the same value
        id_ = str(uuid.uuid1())
        self[id_] = entry
        return id_

    def delete(self):
        for k in self.keys():
            del self[k]
        self.close()
        os.remove(self._filename)

class Entry(dict):
    def __init__(self, shelf, id_, entry):
        super().__init__(entry)
        super().__setitem__('_id', id_)
        self._shelf = shelf

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._write_entry()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._write_entry()

    @property
    def timestamp(self):
        try:
            return self._timestamp
        except AttributeError:
            self._timestamp = datetime.fromtimestamp(
                (uuid.UUID(self['_id']).time - 0x01b21dd213814000)*100/1e9)
            return self._timestamp

    def _write_entry(self):
        entry = self.copy()
        id_ = entry.pop('_id')
        self._shelf[id_] = entry

    def update(self, data):
        super().update(data)
        self._write_entry()

    def clear(self):
        del self._shelf[self['_id']]
        super().clear()
