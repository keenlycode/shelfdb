"""Large buffered messages use the same framing over TCP and Unix sockets."""

import asyncio

from shelfdb.protocol import encode_response
from shelfdb.protocol.query_result import normalize_query_result
from shelfdb.shelf import Item, MutationResult


def test_large_values_and_query_results_round_trip(transaction_server):
    binary = bytes(range(256)) * 8192  # 2 MiB: one large record.
    records = [Item(f"record-{i}", {"data": b"a" * (384 * 1024)}) for i in range(4)]
    response = {"ok": True, "result": normalize_query_result(records)}
    assert len(encode_response(response)) > 1024 * 1024

    async def run():
        async with transaction_server() as server:
            client = await server.connect()

            async def write():
                async with client.transaction(write=True) as tx:
                    assert await tx.shelf("large_assets").put(
                        "binary", binary
                    ).query() == MutationResult("binary", True)
                    assert await tx.shelf("large_records").put_many(
                        records
                    ).query() == [MutationResult(item.key, True) for item in records]

            await server.result(write())

            async def read():
                async with client.transaction() as tx:
                    assert await tx.shelf("large_assets").key(
                        "binary"
                    ).item().query() == Item("binary", binary)
                    shelf = tx.shelf("large_records")
                    assert await shelf.items().query() == records
                    assert await shelf.slice(1, 3).items().query() == records[1:3]
                    # A small command still works after the large response.
                    assert await shelf.count().query() == 4

            await server.result(read())

    asyncio.run(run())
