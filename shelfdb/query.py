import requests, dill

class Query():
    def __init__(self, server='http://127.0.0.1:17000/user/'):
        self._server = server
        self._queries = []

    def get(self, id_):
        self._queries.append({'get': id_})

    def first(self, filter_):
        self._queries.append({'first': filter_})

    def filter(self, filter_):
        self._queries.append({'filter': filter_})

    def map(self, map_):
        self._queries.append({'map', map_})

    def slice(self, start, stop, step=None):
        self._queries.append({'slice': (start,stop,step)})

    def sort(self, key=lambda entry: entry['_id'], reverse=False):
        self._queries.append({'sort': (key, reverse)})

    def update(self, patch):
        self._queries.append({'update': patch})

    def insert(self, entry):
        self._queries.append({'insert': entry})

    def put(self, id_, entry):
        self._queries.append({'put': (id_, entry)})

    def replace(self, entry):
        self._queries.append({'replace': entry})

    def delete(self):
        self._queries.append({'delete': True})

    def run(self):
        query = dill.dumps(self._queries)
        r = requests.post(self._server, data=query)
        return r.json()
