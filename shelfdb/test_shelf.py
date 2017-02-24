import unittest, shelfdb, shutil, dbm, shelve, uuid
from shelfdb import shelf

class DB(unittest.TestCase):
    def setUp(self):
        self.db = shelfdb.open('test_data/db')
        self.assertIsInstance(self.db, shelfdb.shelf.DB)

    def test_shelf(self):
        self.assertIsInstance(self.db.shelf('user'), shelfdb.shelf.ShelfQuery)

    def test_shelf_open_close(self):
        self.db.shelf('user')
        try:
            dbm.open('test_data/db/user')
        except dbm.gnu.error as e:
            self.assertEqual(e.errno, 11)
        self.db.close()
        self.assertIsInstance(self.db._shelf['user']._shelf.dict,
            shelve._ClosedDict)

    def tearDown(self):
        shutil.rmtree('test_data')

class ShelfQuery(unittest.TestCase):
    def setUp(self):
        self.db = shelfdb.open('test_data/db')
        self.user_list = [
            {'name': 'Jan'},
            {'name': 'Feb'},
            {'name': 'Mar'},
        ]
        for user in self.user_list:
            user['_id'] = self.db.shelf('user').insert(user)
            # Check if _id is a valid uuid1
            id_ = uuid.UUID(user['_id'], version=1)
            self.assertEqual(user['_id'].replace('-', ''), id_.hex)

    def test_get(self):
        user = self.user_list[0]
        self.assertIsInstance(
            self.db.shelf('user').get(user['_id']), shelf.Entry)

    def test_first(self):
        user = self.user_list[0]
        self.assertIsInstance(
            self.db.shelf('user').first(lambda u: u['name'] == user['name']),
            shelf.Entry
        )

    def tearDown(self):
        self.db.close()
        shutil.rmtree('test_data')
