__author__ = 'Nick'

import unittest
import os

from config import basedir
from app import app, db
from app.models import LandingPage
from app import views


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRG_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'testgetallfiles.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_findLandPageByName(self):
        l1 = LandingPage(id='1', uploader_id='2', page_name='test1', page_type='download', visibility='Visibile', product='testp', variants='', test_pos='', test_id='')
        l2 = LandingPage(id='2', uploader_id='2', page_name='test2', page_type='download', visibility='Visibile', product='testp', variants='', test_pos='', test_id='')
        l3 = LandingPage(id='3', uploader_id='2', page_name='test3', page_type='download', visibility='Visibile', product='testp', variants='', test_pos='', test_id='')
        l4 = LandingPage(id='4', uploader_id='2', page_name='test4', page_type='download', visibility='Visibile', product='testp', variants='', test_pos='', test_id='')
        l5 = LandingPage(id='5', uploader_id='2', page_name='test5', page_type='download', visibility='Visibile', product='testp', variants='', test_pos='', test_id='')

        db.session.add(l1)
        db.session.add(l2)
        db.session.add(l3)
        db.session.add(l4)
        db.session.add(l5)
        db.session.commit()
        mylist = views.get_allfiles()

        assert len(mylist) == 5

if __name__ == '__main__':
    unittest.main()
