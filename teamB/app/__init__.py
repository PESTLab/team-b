__author__ = 'Nick'

import os

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from flask_login import LoginManager
from config import basedir
import jinja2

UPLOAD_FOLDER = os.path.join(basedir, 'uploadfolder')
ALLOWED_EXTENSIONS = set(['html'])

app = Flask(__name__)

app.config.from_object('config')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('http://broadcast.uniblue.s3.amazonaws.com//'),
])
app.jinja_loader = my_loader

from app import views, models
from models import LandingPage, Funnel


def clever_function(funnel_id, page_type):
    pagelist = []
    allpages = LandingPage.query.all()
    f = Funnel.query.filter_by(id=funnel_id).first()
    for p in allpages:
        p_prods = p.product.split(',')
        if f.product.split(',')[0] in p_prods and p.page_type.lower() == page_type:
            pagelist.append(p)
    return pagelist


def variant_pages(pgid):
    pagelist = []
    allpages = LandingPage.query.all()
    pgvarlist = []
    page = LandingPage.query.filter_by(id=pgid).first()


    if page.variants != None:
        pgvarlist = page.variants.split(',')


    pageprods = page.product.split(',')

    for var in allpages:
        if var.page_type == page.page_type:
            var_prods = var.product.split(',')
            for prod in pageprods:
                if prod in var_prods and var.page_name != page.page_name and var not in pagelist:
                    if str(var.id) not in pgvarlist:
                        pagelist.append(var)
    return pagelist


def get_variants(pgid):
    pagenameslist = []
    page = LandingPage.query.filter_by(id=pgid).first()
    if page.variants != None:
        varsids = page.variants.split(',')
        for v_id in varsids:
            var = LandingPage.query.filter_by(id=v_id).first()
            if var:
                pagenameslist.append(var.page_name)
    return pagenameslist


app.jinja_env.globals.update(clever_function=clever_function)
app.jinja_env.globals.update(variant_pages=variant_pages)
app.jinja_env.globals.update(get_variants=get_variants)