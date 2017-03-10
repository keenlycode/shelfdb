import unittest, shelfdb, shutil, dbm, shelve, uuid
from functools import reduce
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
        user_from_db = self.db.shelf('user').get(user['_id'])
        self.assertIsInstance(user_from_db, shelf.Entry)
        self.assertEqual(user, user_from_db.copy())

    def test_first(self):
        user = self.user_list[0]
        user_from_db = self.db.shelf('user')\
            .first(lambda u: u['name'] == user['name'])
        self.assertIsInstance(user_from_db, shelf.Entry)
        self.assertEqual(user, user_from_db.copy())

    def test_filter(self):
        user = self.user_list[0]
        chain_query = self.db.shelf('user')\
            .filter(lambda u: u['name'] == user['name'])
        self.assertIsInstance(chain_query, shelf.ChainQuery)
        user_from_db = next(chain_query)
        self.assertEqual(user, user_from_db.copy())

    def test_map(self):
        def map_test(user):
            user['map_test'] = 'test'
            return user
        users = self.db.shelf('user').map(map_test)
        for user in users:
            self.assertEqual(user['map_test'], 'test')

    def test_reduce(self):
        count_by_reduce = self.db.shelf('user').reduce(lambda x, y: x + 1, 0)
        self.assertEqual(len(self.user_list), count_by_reduce)

    def test_slice(self):
        users = self.db.shelf('user').slice(0,2)
        count_by_reduce = users.reduce(lambda x, y: x + 1, 0)
        self.assertEqual(len(self.user_list[0:2]), count_by_reduce)

    def test_sort(self):
        users_sort_by_name = self.db.shelf('user').sort(lambda user: user['name'])
        prev_user = next(users_sort_by_name)
        for user in users_sort_by_name:
            self.assertTrue(prev_user['name'] < user['name'])
            prev_user = user

    def test_update(self):
        users = self.db.shelf('user')
        users.update({'update_test': 'test'})
        for user in users:
            self.assertEqual(user['update_test'], 'test')

    def test_replace(self):
        user = self.user_list[0]
        user = self.db.shelf('user')\
            .first(lambda u: u['name'] == user['name'])
        id_ = user['_id']
        new_user = {'name': 'Aug'}
        self.db.shelf('user').get(id_).replace(new_user)
        user = self.db.shelf('user').get(id_)
        del user['_id']
        self.assertEqual(user.copy(), new_user)

    def test_delete(self):
        user = self.user_list[0]
        user = self.db.shelf('user')\
            .first(lambda u: u['name'] == user['name'])
        user.delete()
        user = self.db.shelf('user')\
            .first(lambda u: u['name'] == user['name'])
        self.assertIsNone(user)


    def tearDown(self):
        self.db.close()
        shutil.rmtree('test_data')
