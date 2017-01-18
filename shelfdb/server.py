from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
import shelfdb, os, dill

db_dir = os.path.join(os.getcwd(), 'db')
shelf = shelfdb.open(db_dir)

class Query(RequestHandler):
    def post(self, shelf_):
        queries = dill.loads(self.request.body)
        chain_query = shelf[shelf_]
        for query in queries:
            query = query.popitem()
            chain_query = chain_query.__getattribute__(query[0])(query[1])
        if chain_query is not None:
            entries = []
            for entry in chain_query:
                entries.append(entry)
            return self.write({'entries': entries})


app = Application([
    (r'/([a-zA-Z0-9-_]*)/', Query)
], debug=True)

if __name__ == '__main__':
    app.listen(17000)
    IOLoop.current().start()
