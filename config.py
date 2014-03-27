__author__ = 'Nick'

import os

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

AWS_ACCESS_KEY_ID = 'AKIAIX5Y7RRWI35K2ZQA'
AWS_SECRET_ACCESS_KEY = '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'

GOOGLE_OPENID = 'https://www.google.com/accounts/o8/id'
