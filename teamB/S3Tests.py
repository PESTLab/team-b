__author__ = 'Nick'

import unittest
from app import app, views
from boto.s3.key import Key

class MyTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

    def tearDown(self):
        b = views.connect_to_bucket()
        k = Key(b)
        k.key = 'test.html'
        b.delete_key(k)

    def test_upload_file(self):
        b = views.connect_to_bucket()
        testfile = open('teamB/test.html', "r")
        views.upload_to_bucket(testfile, testfile.name)
        mykey = b.get_key('teamB/test.html')
        assert mykey.name == 'teamB/test.html'

    def test_delete_file(self):
        testfile = open('teamB/test.html', "r")
        views.upload_to_bucket(testfile, testfile.name)
        b = views.connect_to_bucket()
        k = Key(b)
        k.key = 'teamB/test.html'
        b.delete_key(k)
        mykey = b.get_key(testfile.name)
        assert mykey == None


if __name__ == '__main__':
    unittest.main()
