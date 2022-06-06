import asyncio
import dill
import re  # to be used by client
from datetime import datetime  # to be used by client
import argparse
import os
import sys
import shelfdb


class QueryHandler():
    """Class to handle incoming query requests from shelfquery client.
    It will extract python pickle dict queries (by dill), run process on
    server side, then return result back to client.

    Format of incoming chain queries (Python ``list`` instance)
        [
            '<shelf name>',
            {'<method>': <arg>},
            '<method_with_no_arg>',
            ...
        ]
    methods `<arg>` can be anything which can be pickle by dill.
    See `QueryHandler.run()` to learn how it extracts chain query
    into method call.

    Methods in QueryHandler are used to map arguments sent from client
    to methods in ``shelfdb.shelf.Shelf``.
    """

    def __init__(self, db, shelf, queries):
        self.chain_query = db.shelf(shelf)
        self.queries = queries

    def add(self, data):
        self.chain_query = self.chain_query.add(data)
        return self

    def count(self):
        self.chain_query = self.chain_query.count()
        return self

    def delete(self):
        self.chain_query = self.chain_query.delete()
        return self

    def edit(self, func):
        self.chain_query = self.chain_query.edit(func)
        return self

    def first(self, filter_):
        self.chain_query = self.chain_query.first(filter_)
        return self

    def filter(self, filter_):
        self.chain_query = self.chain_query.filter(filter_)
        return self

    def get(self, id_):
        self.chain_query = self.chain_query.get(id_)
        return self

    # Deprecated
    def insert(self, data):
        self.chain_query = self.chain_query.insert(data)
        return self

    def map(self, fn):
        self.chain_query = self.chain_query.map(fn)
        return self

    def patch(self, args):
        self.chain_query = self.chain_query.patch(*args)
        return self

    def put(self, args):
        self.chain_query = self.chain_query.put(*args)
        return self

    def reduce(self, fn):
        self.chain_query = self.chain_query.reduce(fn)
        return self

    def replace(self, data):
        self.chain_query = self.chain_query.replace(data)
        return self

    def slice(self, args):
        """`args` should be [start, stop, step]"""
        self.chain_query = self.chain_query.slice(*args)
        return self

    def sort(self, kw):
        # Remove sort key from `kw` if it hasn't been sent from client
        if kw['key'] is None:
            del kw['key']
        self.chain_query = self.chain_query.sort(**kw)
        return self

    def update(self, data):
        self.chain_query = self.chain_query.update(data)
        return self

    def run(self):
        # Extract function call from request into chain query.
        for query in self.queries:
            if isinstance(query, dict):  # method with arguments
                q = query.popitem()
                self = self.__getattribute__(q[0])(q[1])
            else:  # method with no arguments
                self = self.__getattribute__(query)()

        if isinstance(self.chain_query, shelfdb.shelf.Shelf):
            return [(item.id, item.copy()) for item in self.chain_query]
        elif isinstance(self.chain_query, shelfdb.shelf.Item):
            return (self.chain_query.id, self.chain_query.copy())
        else:
            return self.chain_query


class ShelfServer:
    """ShelfDB asyncio server

    Follow and modify code from:
    https://docs.python.org/3.8/library/asyncio-stream.html
    """

    def __init__(self, host='127.0.0.1', port=17000, db_name='db'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.shelfdb = shelfdb.open(db_name)

    async def handler(self, reader, writer):
        queries = await reader.read(-1)  # Read until EOF
        try:
            queries = dill.loads(queries)
            shelf = queries.pop(0)
            result = QueryHandler(self.shelfdb, shelf, queries).run()
            result = dill.dumps(result)
            writer.write(result)
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as error:
            result = dill.dumps(error)
            writer.write(result)
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        print('Database :', self.db_name)
        print('pid :', os.getpid())
        async with server:
            await server.serve_forever()


def main():
    arg = argparse.ArgumentParser(description='ShelfDB Asyncio Server')
    arg.add_argument(
        '--host', nargs='?', type=str, default='127.0.0.1',
        help="server host ip. (default: '127.0.0.1')")
    arg.add_argument(
        '--port', nargs='?', type=int, default=17000,
        help="server port. (default: 17000)")
    arg.add_argument(
        '--db', nargs='?', default='db',
        help="server database directory. (default: 'db')")
    arg = arg.parse_args()
    shelf_server = ShelfServer(arg.host, arg.port, arg.db)

    if sys.platform.startswith('linux'):
        import uvloop
        uvloop.install()

    # Run server until Ctrl+C is pressed
    try:
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        shelf_server.shelfdb.close()


if __name__ == '__main__':
    main()
