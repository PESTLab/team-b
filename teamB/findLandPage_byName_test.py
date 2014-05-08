__author__ = 'Alastair'

import unittest
import os

from config import basedir
from app import app, db
from app.models import LandingPage
from app.views import findlandpage_byname


class TestFindLandPagebyName(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRG_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'testLandPageByName.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_findLandPageByName(self):
        l = LandingPage(id='1', uploader_id='2', page_name='test', page_type='download', visibility='Visibile', product='testp', variants='', test_pos='', test_id='')
        db.session.add(l)
        db.session.commit()
        landPage = findlandpage_byname('test')

        assert landPage.id == l.id

if __name__ == '__main__':
    unittest.main()
