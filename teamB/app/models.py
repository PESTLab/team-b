__author__ = 'Nick'

from app import db, app
import flask.ext.whooshalchemy as whooshalchemy

RIGHT_USER = 0
RIGHT_ADMIN = 1

ROLE_WEBDEV = 0
ROLE_SALESEXEC = 1
ROLE_ADMIN = 2

VISIBILE = 0
HIDDEN = 1

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    
class Page_Type(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(64), unique = True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    creator_id = db.Column(db.SmallInteger)
    name = db.Column(db.String(64), index = True, unique = True)
    funnel_ids = db.Column(db.String(500), default="NONE")

class Funnel(db.Model):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key = True)
    campaign_id = db.Column(db.SmallInteger)
    name = db.Column(db.String(64), index = True, unique = True)
    product = db.Column(db.String(120))
    content_ids = db.Column(db.String(500))

whooshalchemy.whoosh_index(app, Funnel)

class LandingPage(db.Model):
    __searchable__ = ['page_name']
    id = db.Column(db.Integer, primary_key = True)
    uploader_id = db.Column(db.SmallInteger)
    page_name = db.Column(db.String(64), index = True, unique = True)
    page_type = db.Column(db.String(120))
    visibility = db.Column(db.SmallInteger, default = VISIBILE)
    product = db.Column(db.String(120))
    variants = db.Column(db.String(120))
    test_pos = db.Column(db.Integer, default =-1)
    test_id = db.Column(db.Integer)

whooshalchemy.whoosh_index(app, LandingPage)


class SplitTest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    pageid = db.Column(db.Integer)
    variants = db.Column(db.String(120))
    test_code = db.Column(db.String(8))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger)
    rights = db.Column(db.SmallInteger, default = RIGHT_USER)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)
    @staticmethod
    def make_unique_email(email):
        if User.query.filter_by(email=email).first() is None:
            return email