import requests, dill, copy, asyncio, json
from urllib.parse import urljoin


def connect(addr='127.0.0.1', port=17000):
    return DB(addr, port)

class DB():
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def shelf(self, shelf_name):
        return ShelfQuery(copy.copy(self), shelf_name)


class ShelfQuery():
    def __init__(self, db, shelf):
        self.db = db
        self.shelf = shelf
        self.queries = []

    def get(self, id_):
        return ChainQuery(self, {'get': id_})

    def first(self, filter_):
        return ChainQuery(self, {'first': filter_})

    def filter(self, filter_):
        return ChainQuery(self, {'filter': filter_})

    def map(self, map_):
        return ChainQuery(self, {'map': map_})

    def slice(self, start, stop, step=None):
        return ChainQuery(self, {'slice': [start, stop, step]})

    def sort(self, key=lambda entry: entry['_id'], reverse=False):
        return ChainQuery(self, {'sort': [key, reverse]})

    def update(self, patch):
        return ChainQuery(self, {'update': patch})

    def insert(self, entry):
        return ChainQuery(self, {'insert': entry})

    def put(self, id_, entry):
        return ChainQuery(self, {'put': (id_, entry)})

    def replace(self, entry):
        return ChainQuery(self, {'replace': entry})

    def delete(self):
        return ChainQuery(self, 'delete')

    def run(self):
        return asyncio.get_event_loop().run_until_complete(
            asyncio.ensure_future(self.run_async())
        )

    async def run_async(self):
        queries = self.queries.copy()
        queries.insert(0, self.shelf)
        queries = dill.dumps(queries)
        reader, writer = await asyncio.open_connection(
            self.db.addr,
            self.db.port,)
        writer.write(queries)
        writer.write_eof()
        result = await reader.read(-1)
        result = json.loads(result.decode())
        writer.close()
        return result

class ChainQuery(ShelfQuery):
    def __init__(self, chain_query, query):
        self.db = chain_query.db
        self.shelf = chain_query.shelf
        self.queries = chain_query.queries.copy()
        self.queries.append(query)
