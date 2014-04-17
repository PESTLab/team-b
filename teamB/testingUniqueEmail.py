__author__ = 'Alastair'

import unittest
import os

from config import basedir
from app import app, db
from app.models import User


class TestingUniqueEmail(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'testUserEmail.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_unique_email(self):
        u = User(id= '1', nickname = 'ali', email='ali@test.com', role='webdev', rights='admin')
        db.session.add(u)
        db.session.commit()
        email = User.make_unique_email('ali@test.com')
        assert email != 'ali@test.com'
        u = User(id='2', nickname='ali2', email=email)
        db.session.add(u)
        db.session.commit()
        email2 = User.make_unique_email('ali2@test.com')
        assert email2 != 'ali@test.com'
        assert email2 != email

if __name__ == '__main__':
    unittest.main()





