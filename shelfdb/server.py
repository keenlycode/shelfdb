import asyncio, shelfdb, dill, re, sys, json, argparse
from shelfdb.shelf import ChainQuery


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

    def get(self, id_):
        self.chain_query = self.chain_query.get(id_)
        return self

    def first(self, filter_):
        self.chain_query = self.chain_query.first(filter_)
        return self

    def entry(self, fn):
        self.chain_query = fn(self.chain_query)
        return self

    def filter(self, filter_):
        self.chain_query = self.chain_query.filter(filter_)
        return self

    def map(self, fn):
        self.chain_query = self.chain_query.map(fn)
        return self

    def reduce(self, fn):
        self.chain_query = self.chain_query.reduce(fn)
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

    def update(self, patch):
        self.chain_query = self.chain_query.update(patch)
        return self

    def insert(self, entry):
        self.chain_query = self.chain_query.insert(entry)
        return self

    def replace(self, data):
        self.chain_query = self.chain_query.replace(data)
        return self

    def delete(self):
        self.chain_query = self.chain_query.delete()
        return self

    def run(self):
        # Extract function call from request into chain query.
        for query in self.queries:
            if isinstance(query, dict):
                q = query.popitem()
                self = self.__getattribute__(q[0])(q[1])
            else:
                self = self.__getattribute__(query)()

        if isinstance(self.chain_query, shelfdb.shelf.ShelfQuery):
            entries = []
            # Keep only dict value from entry.copy() into entries
            [entries.append(entry.copy()) for entry in self.chain_query]
            return entries
        elif isinstance(self.chain_query, shelfdb.shelf.Entry):
            return self.chain_query.copy()
        else:
            return self.chain_query

async def handler(reader, writer):
    queries = await reader.read(-1)
    try:
        queries = dill.loads(queries)
        shelf = queries.pop(0)
        result = QueryHandler(db, shelf, queries).run()
        result = dill.dumps(result)
    except:
        print("Unexpected error:", sys.exc_info()[1])
        result = dill.dumps(sys.exc_info()[1])
        writer.write(result)
        await writer.drain()
        writer.close()
        raise
    writer.write(result)
    await writer.drain()
    writer.close()

def main():
    global args
    global db
    args = argparse.ArgumentParser(description='ShelfDB Asyncio Server')
    args.add_argument('--host', nargs='?', type=str, default='0.0.0.0',
        help='server host')
    args.add_argument('--port', nargs='?', type=int, default=17000,
        help='server port')
    args.add_argument('--db', nargs='?', default='db',
        help='server database')

    args = args.parse_args()
    db = shelfdb.open(args.db)

    loop = asyncio.get_event_loop()
    server = asyncio.start_server(handler, args.host, args.port, loop=loop)
    server = loop.run_until_complete(server)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    print('Database : ' + args.db)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    db.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    main()
