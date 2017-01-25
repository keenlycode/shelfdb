import asyncio, shelfdb, dill, json, re, js2py

db = shelfdb.open('db')

async def connection(reader, writer):
    queries = await reader.read(-1)
    queries = dill.loads(queries)
    shelf = queries.pop(0)
    chain_query = db.shelf(shelf)

    for query in queries:
        if isinstance(query, dict):
            q = query.popitem()
            chain_query = chain_query.__getattribute__(q[0])(q[1])
        else:
            chain_query = chain_query.__getattribute__(query)()

    result = {}
    if isinstance(chain_query, shelfdb.shelf.ShelfQuery):
        entries = []
        [entries.append(entry) for entry in chain_query]
        result['result'] = entries
    else:
        result['result'] = chain_query

    result = json.dumps(result).encode()
    writer.write(result)
    await writer.drain()
    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(connection, '127.0.0.1', 17000, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
