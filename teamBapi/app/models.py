__author__ = 'Nick'

from app import db

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    funnel_ids = db.Column(db.String(500))

class Funnel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    campaign_id = db.Column(db.SmallInteger)
    name = db.Column(db.String(64), index = True, unique = True)
    product = db.Column(db.String(120))
    content_ids = db.Column(db.String(500))

class LandingPage(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    page_name = db.Column(db.String(64), index = True, unique = True)
    page_type = db.Column(db.String(120))
    product = db.Column(db.String(120))
    visibility = db.Column(db.SmallInteger)