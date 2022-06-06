import unittest
import shelfdb
import shutil
import dbm
import shelve
import uuid
from datetime import datetime
from dictify import Model, Field
from shelfdb.shelf import Item, Entry


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


class Note(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)


class TestShelf(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = shelfdb.open('test_data/db')

    def setUp(self):
        self.notes = []
        for i in range(10):
            self.notes.append(Note({'title': 'note-' + str(i)}))
        for note in self.notes:
            note.id = self.db.shelf('note').add(note.copy())

    def test_iteration(self):
        i = 0
        for note in self.db.shelf('note'):
            i += 1
        self.assertEqual(len(self.notes), i)

    def test_add(self):
        note = Note({'title': 'new note'})
        note.id = self.db.shelf('note').add(note.copy())
        self.assertDictEqual(note, self.db.shelf('note').get(note.id))

    def test_count(self):
        self.assertEqual(len(self.notes), self.db.shelf('note').count())

        count = self.db.shelf('note').count(
            lambda note: note['title'] == 'note-1')
        self.assertEqual(count, 1)

    def test_delete(self):
        self.db.shelf('note').delete()
        notes = list(self.db.shelf('note'))
        self.assertEqual(notes, [])

    def test_edit(self):
        note = self.notes[0]
        note = self.db.shelf('note')\
            .first(lambda n: n['title'] == note['title'])

        def _update_title(note):
            note['title'] = 'test_edit'
            return note

        self.db.shelf('note').get(note.id).edit(_update_title)
        note = self.db.shelf('note').get(note.id)
        self.assertEqual(note['title'], 'test_edit')

    def test_filter(self):
        note = self.notes[0]
        query = self.db.shelf('note')\
            .filter(lambda n: n['title'] == note['title'])
        self.assertIsInstance(query, shelfdb.shelf.Shelf)
        note_from_db = next(query.items())
        self.assertEqual(note, note_from_db)

    def test_first(self):
        note_from_db = self.db.shelf('note').first()
        self.assertIsInstance(note_from_db, shelfdb.shelf.Item)

        note = self.notes[0]
        note_from_db = self.db.shelf('note')\
            .first(lambda n: n['title'] == note['title'])
        self.assertIsInstance(note_from_db, shelfdb.shelf.Item)
        self.assertEqual(note, note_from_db)

    def test_get(self):
        note = self.notes[0]
        note_from_db = self.db.shelf('note').get(note.id)
        self.assertIsInstance(note_from_db, Item)
        self.assertEqual(note, note_from_db)

    def test_insert(self):
        note = Note({'title': 'inserted note'})
        note.id = self.db.shelf('note').insert(note.copy())
        self.assertDictEqual(note, self.db.shelf('note').get(note.id))

    def test_items(self):
        i = 0
        notes = self.db.shelf('note').items()
        for note in notes:
            i += 1
        self.assertEqual(i, len(self.notes))

    def test_map(self):
        def map_test(note):
            note['map_test'] = 'test'
            return note
        notes = self.db.shelf('user').map(map_test)
        for note in notes:
            self.assertEqual(note['map_test'], 'test')

    def test_patch(self):
        uuid1 = str(uuid.uuid1())
        note = dict(Note({'title': 'test_patch'}))
        self.db.shelf('note').patch(uuid1, note)
        patch = {'content': 'patched content'}
        self.db.shelf('note').patch(uuid1, patch)
        note.update(patch)
        note_from_db = self.db.shelf('note').get(uuid1)
        self.assertEqual(note, note_from_db)

    def test_put(self):
        uuid1 = str(uuid.uuid1())
        note = dict(Note({'title': 'test_put'}))
        self.db.shelf('note').put(uuid1, note)
        note_from_db = self.db.shelf('note').get(uuid1)
        self.assertEqual(note, note_from_db)

    def test_reduce(self):
        count_by_reduce = self.db.shelf('note').reduce(lambda x, y: x + 1, 0)
        self.assertEqual(len(self.notes), count_by_reduce)

    def test_replace(self):
        note = self.notes[0]
        note = self.db.shelf('note')\
            .first(lambda n: n['title'] == note['title'])
        new_note = dict(Note({
            'title': 'test_replace'}))
        self.db.shelf('note').get(note.id).replace(new_note)
        note = self.db.shelf('note').get(note.id)
        self.assertDictEqual(note, new_note)

    def test_slice(self):
        notes = self.db.shelf('note').slice(0, 2)
        self.assertEqual(len(self.notes[0:2]), notes.count())

    def test_sort(self):
        notes_sort_by_title = self.db.shelf('note')\
            .sort(lambda note: note['title']).items()
        prev_note = next(notes_sort_by_title)
        for note in notes_sort_by_title:
            self.assertTrue(prev_note['title'] < note['title'])
            prev_note = note

    def test_update(self):
        notes = self.db.shelf('user')
        notes.update({'content': 'test_update'})
        for note in notes:
            self.assertEqual(note['content'], 'test_update')

    def tearDown(self):
        self.db.shelf('note').delete()
        self.db.close()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('test_data')


class TestItem(unittest.TestCase):

    def setUp(self):
        self.id = str(uuid.uuid1())
        self.data = {'item': 1}
        self.item = Item(id_=self.id, data=self.data)

    def test_init(self):
        self.assertEqual(self.id, self.item.id)
        self.assertDictEqual(self.data, self.item)
    
    def test_timestamp(self):
        self.assertIsInstance(self.item.timestamp, datetime)


class TestEntry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = shelfdb.open('test_data/db')

    def setUp(self):
        self.note = Note({'title': 'entry'})
        self.db.shelf('note').add(self.note.copy())

    def note_from_db(self):
        return self.db.shelf('note').first()

    def test_init(self):
        self.assertDictEqual(self.note_from_db(), self.note)

    def test_edit(self):
        def edit(note):
            note['title'] = 'edit'
            return note

        self.note_from_db().edit(edit)
        self.assertDictEqual(self.note_from_db(), {'title': 'edit'})
        
    def test_replace(self):
        note = Note({'title': 'replace'}).copy()
        self.note_from_db().replace(note)
        self.assertDictEqual(note, self.note_from_db())

    def test_update(self):
        data = {'content': 'update'}
        self.note.update(data)
        self.note_from_db().update(data)
        self.assertDictEqual(self.note, self.note_from_db())

    def tearDown(self):
        self.db.shelf('note').delete()
        self.db.close()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('test_data')
