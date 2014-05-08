__author__ = 'Alastair'

import unittest
import os

from config import basedir
from app import app, db
from app.models import Campaign
from app.views import findcamp_byid


class TestFindCampbyId(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRG_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'testCampById.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_findCampByName(self):
        c = Campaign(id='1', creator_id='2', name='test', funnel_ids='2')
        db.session.add(c)
        db.session.commit()
        camp = findcamp_byid('1')

        assert camp.name == c.name

if __name__ == '__main__':
    unittest.main()
