"""Small test client for exercising the ShelfDB server API."""

import socket

import dill


class ServerQuery:
    def __init__(self, client, shelf_name: str, queries=None):
        self._client = client
        self._shelf_name = shelf_name
        self._queries = queries or []

    def _clone(self, query):
        return ServerQuery(self._client, self._shelf_name, [*self._queries, query])

    def tx(self, write=False):
        return self._clone({"tx": {"write": write}})

    def count(self):
        return self._clone("count")

    def delete(self):
        return self._clone("delete")

    def edit(self, func):
        return self._clone({"edit": func})

    def first(self, filter_=None):
        return self._clone({"first": filter_})

    def filter(self, filter_=None):
        return self._clone({"filter": filter_})

    def key(self, key):
        return self._clone({"key": key})

    def patch(self, key, data):
        return self._clone({"patch": (key, data)})

    def replace(self, data):
        return self._clone({"replace": data})

    def slice(self, start: int, stop: int, step: int = None):
        return self._clone({"slice": (start, stop, step)})

    def sort(self, key=None, reverse=False):
        return self._clone({"sort": {"key": key, "reverse": reverse}})

    def update(self, data):
        return self._clone({"update": data})

    def run(self):
        payload = dill.dumps([self._shelf_name, *self._queries])
        with socket.create_connection((self._client.host, self._client.port)) as sock:
            sock.sendall(payload)
            sock.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        result = dill.loads(b"".join(chunks))
        if isinstance(result, Exception):
            raise result
        return result


class ServerClient:
    def __init__(self, host="127.0.0.1", port=17000):
        self.host = host
        self.port = port

    def shelf(self, shelf_name: str) -> ServerQuery:
        return ServerQuery(self, shelf_name)
