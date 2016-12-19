from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from shelfdb import Shelf
import json

shelf = Shelf()

class ShelfId(RequestHandler):
    def get(self, name=None, id_=None):
        return self.write(shelf[name][id_])

    def put(self, name=None, id_=None):
        entry = json.loads(self.request.body.decode())
        shelf[name][id_] = entry
        return self.write('hello')

    def delete(self, name=None, id_=None):
        del shelf[name][id_]
        return self.write('ok')

class Shelf(RequestHandler):
    def get(self, name=None):
        result = {
            "count": str(len(shelf[name])),
        }
        return self.write(result)

    def post(self, name=None):
        entry = json.loads(self.request.body.decode())
        result = shelf[name].insert(entry)
        return self.write(result)

    def delete(self, name=None):
        shelf[name].clear()


setting = {"debug": True}

app = Application([
    (r'/shelf/(\w*)/$', Shelf),
    (r'/shelf/(\w*)/(.*)', ShelfId),
], **setting)

if __name__ == '__main__':
    app.listen(5001)
    IOLoop.current().start()
