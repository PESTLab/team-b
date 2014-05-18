__author__ = 'Nick'

__name__ = 'Test'

import unittest

from app import app, views

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

    def test_seqno_001(self):
        assert (views.get_seq_no(1) == '001')

    def test_seqno_011(self):
        assert (views.get_seq_no(11) == '011')

    def test_seqno_111(self):
        assert (views.get_seq_no(111) == '111')

    if __name__ == '__main__':
        unittest.main()

