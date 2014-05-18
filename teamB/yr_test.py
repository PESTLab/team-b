__author__ = 'Nick'

__name__ = 'Test'

import unittest

from app import app, views

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

    def test_yr(self):
        assert (views.get_yr() == '14')

    if __name__ == '__main__':
        unittest.main()

