import asyncio, shelve, os, collections
from uuid import uuid1

class DB:
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._db_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(self._db_dir):
            os.makedirs(self._db_dir)
        self.shelf = Shelf(self._db_dir)

class Shelf(dict):
    def __init__(self, db_dir, *args, **kw):
        self._db_dir = db_dir

    def __getitem__(self, k, *args, **kw):
        if not k in self:
            super().__setitem__(
                k, FileShelf(os.path.join(self._db_dir, k)))
        return super().__getitem__(k)

    def get(self, k, *args, **kw):
        return self.__getitem__(k, *args, **kw)


class FileShelf(shelve.DbfilenameShelf):
    def __init__(self, filename, *args, **kw):
        self._filename = filename
        return super().__init__(filename, *args, **kw)

    def __iter__(self, *args, **kw):
        for item in super().__iter__(*args, **kw):
            result = self[item]
            result.update({'_id': item})
            yield result

    def insert(self, obj=None, id_=str(uuid1())):
        return super().__setitem__(id_, obj)

    def items(self, *args, **kw):
        return self.__iter__(*args, **kw)

    def get(self, k, *args, **kw):
        result = super().__getitem__(k)
        result.update({'_id': k})
        return result

    def delete(self, *args, **kw):
        self.clear()
        self.close()
        os.remove(self._filename)

db = DB()
