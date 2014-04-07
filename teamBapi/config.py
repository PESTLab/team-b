__author__ = 'Nick'

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'apidb.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')