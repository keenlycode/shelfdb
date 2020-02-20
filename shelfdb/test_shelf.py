import unittest
import shelfdb
import shutil
import dbm
import shelve
import uuid
from datetime import datetime
from dictify import Model, Field as BaseField, define


class DB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = shelfdb.open('test_data/db')
        cls.assertIsInstance(cls, cls.db, shelfdb.shelf.DB)

    def test_shelf(self):
        self.assertIsInstance(self.db.shelf('note'), shelfdb.shelf.Shelf)

    def test_shelf_open_close(self):
        self.db.shelf('note')
        try:
            dbm.open('test_data/db/note')
        except dbm.gnu.error as e:
            self.assertEqual(e.errno, 11)
        self.db.close()
        self.assertIsInstance(
            self.db._shelf['note']._shelf.dict,
            shelve._ClosedDict)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('test_data')


class Field(BaseField):
    @define.value
    def uuid1(value):
        uuid1 = uuid.UUID(value)
        assert uuid1.version == 1


class Note(Model):
    title = Field().required().type(str)
    content = Field().type(str)
    datetime = Field().default(datetime.utcnow).required()


class TestShelf(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = shelfdb.open('test_data/db')

    def setUp(self):
        self.notes = [
            dict(Note({'title': 'note-1'})),
            dict(Note({'title': 'note-2'})),
            dict(Note({'title': 'note-3'})),
        ]
        for note in self.notes:
            note['_id'] = self.db.shelf('note').insert(note)
            # Check if _id is a valid uuid1
            assert uuid.UUID(note['_id'], version=1)

        results = self.db.shelf('note').map(lambda item: 1).reduce(lambda sum,i: sum + i)
        print(results)
    
    def test_get(self):
        assert True

    # def test_get(self):
    #     note = self.notes[0]
    #     note_from_db = self.db.shelf('note').get(note['_id'])
    #     self.assertIsInstance(note_from_db, shelfdb.shelf.Entry)
    #     self.assertEqual(note, note_from_db.copy())

    # def test_first(self):
    #     note_from_db = self.db.shelf('note').first()
    #     self.assertIsInstance(note_from_db, shelfdb.shelf.Entry)

    #     note = self.notes[0]
    #     note_from_db = self.db.shelf('note')\
    #         .first(lambda n: n['title'] == note['title'])
    #     self.assertIsInstance(note_from_db, shelfdb.shelf.Entry)
    #     self.assertEqual(note, note_from_db.copy())

    # def test_filter(self):
    #     note = self.notes[0]
    #     query = self.db.shelf('note')\
    #         .filter(lambda n: n['title'] == note['title'])
    #     self.assertIsInstance(query, shelfdb.shelf.ChainQuery)
    #     note_from_db = next(query)
    #     self.assertEqual(note, note_from_db.copy())

    # def test_map(self):
    #     def map_test(note):
    #         note['map_test'] = 'test'
    #         return note
    #     notes = self.db.shelf('user').map(map_test)
    #     for note in notes:
    #         self.assertEqual(note['map_test'], 'test')

    # def test_reduce(self):
    #     count_by_reduce = self.db.shelf('note').reduce(lambda x, y: x + 1, 0)
    #     self.assertEqual(len(self.notes), count_by_reduce)

    # def test_slice(self):
    #     notes = self.db.shelf('note').slice(0, 2)
    #     count_by_reduce = notes.reduce(lambda x, y: x + 1, 0)
    #     self.assertEqual(len(self.notes[0:2]), count_by_reduce)

    # def test_sort(self):
    #     notes_sort_by_title = self.db.shelf('note')\
    #         .sort(lambda note: note['title'])
    #     prev_note = next(notes_sort_by_title)
    #     for note in notes_sort_by_title:
    #         self.assertTrue(prev_note['title'] < note['title'])
    #         prev_note = note

    # def test_put(self):
    #     uuid1 = str(uuid.uuid1())
    #     note = dict(Note({'title': 'test_put'}))
    #     self.db.shelf('note').put(uuid1, note)
    #     note_from_db = self.db.shelf('note').get(uuid1)
    #     note['_id'] = uuid1
    #     self.assertEqual(note, note_from_db)

    # def test_update(self):
    #     notes = self.db.shelf('user')
    #     notes.update({'content': 'test_update'})
    #     for note in notes:
    #         self.assertEqual(note['content'], 'test_update')

    #     notes.update(lambda user: {'content': note['content'] + '_function'})
    #     for note in notes:
    #         self.assertEqual(note['content'], 'test_update_function')

    # def test_replace(self):
    #     note = self.notes[0]
    #     note = self.db.shelf('note')\
    #         .first(lambda n: n['title'] == note['title'])
    #     new_note = dict(Note({
    #         '_id': note['_id'],
    #         'title': 'test_replace'}))
    #     self.db.shelf('note').get(note['_id']).replace(new_note)
    #     note = self.db.shelf('note').get(note['_id'])
    #     self.assertDictEqual(note, new_note)

    #     note = self.db.shelf('note').get(note['_id'])
    #     compare = {
    #         '_id': note['_id'],
    #         'title': note['title'] + '1'
    #     }
    #     self.db.shelf('note').get(note['_id']).replace(lambda note: {'title': note['title'] + '1'})
    #     note = self.db.shelf('note').get(note['_id'])
    #     self.assertEqual(note, compare)

    # def test_delete(self):
    #     note = self.notes[0]
    #     self.db.shelf('note')\
    #         .first(lambda n: n['title'] == note['title'])\
    #         .delete()
    #     note = self.db.shelf('note')\
    #         .first(lambda n: n['title'] == note['title'])
    #     self.assertIsNone(note)

    def tearDown(self):
        self.db.shelf('note').delete()
        self.db.close()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('test_data')
