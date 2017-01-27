import asyncio, shelfdb, dill, json, re, js2py
from shelfdb.shelf import ChainQuery

class QueryHandler():
    def __init__(self, db, shelf, queries):
        self.chain_query = db.shelf(shelf)
        self.queries = queries

    def get(self, id_):
        self.chain_query = self.chain_query.get(id_)
        return self

    def first(self, filter_):
        self.chain_query = self.chain_query.first(filter_)
        return self

    def filter(self, filter_):
        self.chain_query = self.chain_query.filter(filter_)
        return self

    def map(self, fn):
        self.chain_query = self.chain_query.map(fn, self.chain_query)
        return self

    def slice(self, args):
        """`args` should be [start, stop, step]"""

        self.chain_query = self.chain_query.slice(*args)
        return self

    def sort(self, kw):
        self.chain_query = self.chain_query.sort(**kw)
        return self

    def update(self, patch):
        [entry.update(patch) for entry in self.chain_query]
        return self

    def insert(self, entry):
        self.chain_query = self.chain_query.insert(entry)
        return self

    def put(self, id_, entry):
        self.chain_query = self.chain_query.put(id_, entry)
        return self

    def replace(self, data):
        self.chain_query = self.chain_query.replace(data)
        return self

    def delete(self):
        self.chain_query = self.chain_query.delete()
        return self

    def run(self):
        for query in self.queries:
            if isinstance(query, dict):
                q = query.popitem()
                self = self.__getattribute__(q[0])(q[1])
            else:
                self = self.__getattribute__(query)()
        result = {}
        if isinstance(self.chain_query, shelfdb.shelf.ShelfQuery):
            entries = []
            [entries.append(entry.copy()) for entry in self.chain_query]
            result['result'] = entries
        else:
            result['result'] = self.chain_query

        return result

async def handler(reader, writer):
    queries = await reader.read(-1)
    queries = dill.loads(queries)
    shelf = queries.pop(0)
    result = QueryHandler(db, shelf, queries).run()
    result = dill.dumps(result)
    writer.write(result)
    await writer.drain()
    writer.close()

db = shelfdb.open('db')
loop = asyncio.get_event_loop()
server = asyncio.start_server(handler, '127.0.0.1', 17000, loop=loop)
server = loop.run_until_complete(server)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
db.close()
loop.run_until_complete(server.wait_closed())
loop.close()
