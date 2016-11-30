import asyncio, shelve, os, collections
from uuid import uuid4

class DB:
    def __init__(self, db_dir=None, *args, **kw):
        if db_dir is None:
            db_dir = os.path.join(os.getcwd(), 'db')
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        self.shelf = Shelf(self.db_dir)
        super().__init__(*args, **kw)

class Shelf(dict):
    def __init__(self, db_dir, *args, **kw):
        self._dir = db_dir

    def __getitem__(self, k):
        if (not k in self or
                isinstance(super().__getitem__(k).dict, shelve._ClosedDict)):
            super().__setitem__(
                k, FileShelf(os.path.join(self._dir, k)))
        return super().__getitem__(k)

    def get(self, k, *args, **kw):
        return self.__getitem__(k, *args, **kw)


class FileShelf(shelve.DbfilenameShelf):
    def __init__(self, filename, *args, **kw):
        self._filename = filename
        return super().__init__(filename, *args, **kw)

    def __setitem__(self, id_, obj):
        if not isinstance(obj, dict):
            raise ValueError('Value must be `dict` instance')
        super().__setitem__(id_, obj)

    def all(self, *args, **kw):
        for item in self:
            result = self[item]
            result.update({'_id': item})
            yield result

    def insert(self, obj=None, id_=None):
        # Since id_=str(uuid4()) in def args will return the same value
        if id_ is None:
            id_ = str(uuid4())
        self[id_] = obj

    def get(self, k, *args, **kw):
        result = super().__getitem__(k)
        result.update({'_id': k})
        return result

    def filter(self, fn):
        result = filter(fn, self.all())
        while True:
            try:
                yield next(result)
            except KeyError:
                pass

    def delete(self, *args, **kw):
        for k in self.keys():
            del self[k]
        self.close()
        os.remove(self._filename)
