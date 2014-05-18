__author__ = 'Nick'

__name__ = 'Test'

import unittest

from app import app, views

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

    def test_no_testcode(self):
        assert (views.get_testcode('notest', '14-011', '1') == '14-011-1')

    def test_1_testcode(self):
        assert (views.get_testcode('14-015-10', '14-011', '1') == '14-015-10_14-011-1')

    def test_2_testcode(self):
        assert (views.get_testcode('14-015-10_14-011-1', '14-019', '2') == '14-015-10_14-011-1_14-019-2')

    if __name__ == '__main__':
        unittest.main()

