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
        _id = uuid.UUID(value)
        unittest.TestCase().assertEqual(_id.version, 1)


class Note(Model):
    _id = Field().uuid1()
    title = Field().required().type(str)
    datetime = Field().default(datetime.utcnow)


class TestShelfServer(unittest.TestCase):
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
                cls.db.shelf('note').entry(lambda entry: entry).run()
                break
            except ConnectionRefusedError:
                if i >= 10:
                    raise TimeoutError
                i += 1
        for note in test_notes:
            _id = cls.db.shelf('note').insert(note).run()
            note['_id'] = _id
            cls.test_notes.append(note)

    def test_iterator(self):
        notes = self.db.shelf('note').run()
        self.assertEqual(len(notes), 3)
        for note in notes:
            Note(note)

    def test_get(self):
        note = self.db.shelf('note').get(self.test_notes[0]['_id']).run()
        Note(note)

    # def test_entry(self):
    #     self.db.shelf('note').first().entry(lambda entry: entry.update({'note': 'test_entry'})).run()
    #     note = self.db.shelf('note').first().run()
    #     print(note)

    @classmethod
    def tearDownClass(cls):
        cls.shelfdb_process.terminate()
        shutil.rmtree(Path('db'))
