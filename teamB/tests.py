__author__ = 'Nick'

import os
import unittest

from config import basedir
from app import app, db, views

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):

    def test_allowed_file(self):
        assert (views.allowed_file('abc.html')) == True
        assert (views.allowed_file('abc.txt')) == False

    if __name__ == '__main__':
        unittest.main()

