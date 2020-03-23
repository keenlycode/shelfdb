import asyncio
import dill
import re
import sys
import argparse
import os
import uvloop
import shelfdb


class QueryHandler():
    """Handler for incoming query requests from shelfquery client.
    It will extract python pickle dict queries (by dill), run process on
    server side, then return result back to client.

    Format of incoming chain queries (in python object)
        [
            '<shelf name>',
            {'<method>': <arg>},
            '<method_with_no_arg>',
            ...
        ]
    methods `<arg>` can be anything which can be pickle by dill.
    See `run()` to learn how it extracts chain query into method call.
    """

    def __init__(self, db, shelf, queries):
        self.chain_query = db.shelf(shelf)
        self.queries = queries

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

    def insert(self, data):
        self.chain_query = self.chain_query.insert(data)
        return self

    def map(self, fn):
        self.chain_query = self.chain_query.map(fn)
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
            if isinstance(query, dict):
                q = query.popitem()
                self = self.__getattribute__(q[0])(q[1])
            else:
                self = self.__getattribute__(query)()

        if isinstance(self.chain_query, shelfdb.shelf.Shelf):
            return [(item.id, item.copy()) for item in self.chain_query]
        elif isinstance(self.chain_query, shelfdb.shelf.Item):
            return (self.chain_query.id, self.chain_query.copy())
        else:
            return self.chain_query


class ShelfServer:
    def __init__(self, host='127.0.0.1', port=17000, db_name='db'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.shelfdb = shelfdb.open(db_name)

    async def handler(self, reader, writer):
        queries = await reader.read(-1)
        try:
            queries = dill.loads(queries)
            shelf = queries.pop(0)
            result = QueryHandler(self.shelfdb, shelf, queries).run()
            result = dill.dumps(result)
        except:
            result = dill.dumps(sys.exc_info()[1])
            writer.write(result)
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            raise

        writer.write(result)
        writer.write_eof()
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run(self):
        # tcp-echo-server-using-streams
        # https: // docs.python.org/3.8/library/asyncio-stream.html
        server = await asyncio.start_server(self.handler, self.host, self.port)
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        print('Database :', self.db_name)
        print('pid :', os.getpid())
        async with server:
            await server.serve_forever()


def main():
    arg = argparse.ArgumentParser(description='ShelfDB Asyncio Server')
    arg.add_argument(
        '--host', nargs='?', type=str, default='127.0.0.1', help='server host')
    arg.add_argument(
        '--port', nargs='?', type=int, default=17000, help='server port')
    arg.add_argument(
        '--db', nargs='?', default='db', help='server database')
    arg = arg.parse_args()
    shelf_server = ShelfServer(arg.host, arg.port, arg.db)

    # Run server until Ctrl+C is pressed
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        shelf_server.shelfdb.close()


if __name__ == '__main__':
    main()
