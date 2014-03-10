__author__ = 'Nick'

import os

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from flask_login import LoginManager
from config import basedir

UPLOAD_FOLDER = os.path.join(basedir, 'uploadfolder')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html'])

app = Flask(__name__)

app.config.from_object('config')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import views, models