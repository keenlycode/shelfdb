import asyncio, shelve, os, collections
from uuid import uuid4

class DB:
    def __init__(self, db_dir=None, *args, **kw):
        if db_dir is None:
            db_dir = os.path.join(os.getcwd(), 'db')
        self.dir = db_dir
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        self.shelf = Shelf(self.dir)
        super().__init__(*args, **kw)

class Shelf(dict):
    def __init__(self, db_dir, *args, **kw):
        self.dir = db_dir

    def __getitem__(self, k):
        if (not k in self or
                isinstance(super().__getitem__(k).dict, shelve._ClosedDict)):
            super().__setitem__(
                k, FileShelf(os.path.join(self.dir, k)))
        return super().__getitem__(k)

    def get(self, k, *args, **kw):
        return self.__getitem__(k, *args, **kw)


class FileShelf(shelve.DbfilenameShelf):
    def __init__(self, filename, *args, **kw):
        self._filename = filename
        return super().__init__(filename, *args, **kw)

    def __setitem__(self, id_, obj, *args, **kw):
        if not isinstance(obj, dict):
            raise ValueError('Value must be `dict` instance')
        super().__setitem__(id_, obj, *args, *kw)

    def all(self):
        for key in self:
            obj = self.get(key)
            yield obj

    def insert(self, obj=None, id_=None):
        # Since id_=str(uuid4()) in def args will return the same value
        if id_ is None:
            id_ = str(uuid4())
        self[id_] = obj

    def get(self, id_):
        obj = self[id_]
        obj.update({'_id': id_})
        return obj

    def update(self, id_, data):
        obj = self[id_]
        obj.update(data)
        self[id_] = obj

    def replace(self, id_, data):
        self[id_] = data

    def filter(self, fn):
        result = filter(fn, self.all())
        while True:
            try:
                yield next(result)
            except KeyError:
                pass

    def delete(self):
        for k in self.keys():
            del self[k]
        self.close()
        os.remove(self._filename)
