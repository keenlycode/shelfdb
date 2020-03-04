import shutil
import unittest
from multiprocessing import Process
from pathlib import Path
from time import sleep
import uuid
from datetime import datetime
from shelfdb import server
import shelfquery
from dictify import Model, Field as BaseField, define


class Field(BaseField):
    @define.value
    def uuid1(value):
        id = uuid.UUID(value)
        unittest.TestCase().assertEqual(id.version, 1)


class Note(Model):
    title = Field().required().type(str)
    note = Field().type(str)
    datetime = Field().default(datetime.utcnow)


class TestRetrieveData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shelfdb_process = Process(target=server.main, daemon=True)
        cls.shelfdb_process.start()
        cls.db = shelfquery.db()
        cls.notes = []
        for i in range (5):
            cls.notes.append(Note({'title': 'note-' + str(i)}))
        i = 0
        while True:
            sleep(0.1)
            try:
                cls.db.shelf('note').first().run()
                break
            except ConnectionRefusedError:
                if i >= 10:
                    raise TimeoutError
                i += 1
        for note in cls.notes:
            id = cls.db.shelf('note').insert(note.copy()).run()
            note.id = id

    def test_iterator(self):
        notes = self.db.shelf('note').run()
        self.assertEqual(len(notes), len(self.notes))
        for id, note in notes:
            Note(note)

    def test_get(self):
        id, note = self.db.shelf('note').get(self.notes[0].id).run()
        Note(note)

    def test_first(self):
        id, note = self.db.shelf('note').first().run()
        note = Note(note)

    def test_filter(self):
        notes = self.db.shelf('note').filter(lambda note: note['title'] == 'note-1').run()
        self.assertIsInstance(notes, list)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0][1]['title'], 'note-1')

    @classmethod
    def tearDownClass(cls):
        cls.shelfdb_process.terminate()
        shutil.rmtree(Path('db'))


class TestModifyData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shelfdb_process = Process(target=server.main, daemon=True)
        cls.shelfdb_process.start()
        cls.db = shelfquery.db()
        cls.test_notes = []
        test_notes = [
            dict(Note({'title': 'note-1'})),
            dict(Note({'title': 'note-2'})),
            dict(Note({'title': 'note-3'})),
        ]
        i = 0
        while True:
            sleep(0.1)
            try:
                cls.db.shelf('note').first().run()
                break
            except ConnectionRefusedError:
                if i >= 10:
                    raise TimeoutError
                i += 1
        for note in test_notes:
            _id = cls.db.shelf('note').insert(note).run()
            note['_id'] = _id
            cls.test_notes.append(note)

    def test_entry(self):
        self.db.shelf('note').first().update({'title': 'test_entry'}).run()
        id, note = self.db.shelf('note').first().run()
        self.assertEqual(note['title'], 'test_entry')

    @classmethod
    def tearDownClass(cls):
        cls.shelfdb_process.terminate()
        shutil.rmtree(Path('db'))
