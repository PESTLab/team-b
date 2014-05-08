__author__ = 'Alastair'

import unittest
import os

from config import basedir
from app import app, db
from app.models import Funnel
from app.views import findfunnel_byid


class TestFindFunnelbyId(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRG_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'testFunnelById.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_findFunnelById(self):
        f = Funnel(id='1', campaign_id='1', name='testing', product='testp', content_ids='2')
        db.session.add(f)
        db.session.commit()
        funnel = findfunnel_byid('1')

        assert funnel.name == f.name

if __name__ == '__main__':
    unittest.main()
