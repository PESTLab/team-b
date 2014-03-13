__author__ = 'Nick'
import os

from werkzeug.utils import secure_filename
from app import app, db, lm, oid, ALLOWED_EXTENSIONS
from flask import redirect, render_template, url_for, flash, request, g, session
from forms import SigninForm, adduserform, uploadlandingpg, newcampaign, funnelpg
from flask_login import login_user, logout_user, current_user, login_required
from models import User, RIGHT_USER, RIGHT_ADMIN, ROLE_SALESEXEC, ROLE_WEBDEV, LandingPage , VISIBILE, HIDDEN, Campaign, Funnel
from flask_googlelogin import GoogleLogin
from datetime import datetime

googlelogin = GoogleLogin(app)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title='Home')

@app.route('/showall')
@login_required
def showallusers():
    if g.user.rights != RIGHT_ADMIN:
        flash('Only Users with Administrator Rights can access this page')
        return redirect(url_for('index'))
    AllUsers = User.query.all()
    return render_template('showallusers.html', title='All Users', Users = AllUsers)

@app.route('/addusers', methods=['GET', 'POST'])
@login_required
def addusers():
    if g.user.rights != RIGHT_ADMIN:
        flash('Only Users with Administrator Rights can access this page')
        return redirect(url_for('index'))
    form = adduserform();
    if form.validate_on_submit():
        nickname = form.useremail.data.split('@')[0]
        if form.userright.data == 'user':
            right = RIGHT_USER
        else:
            right = RIGHT_ADMIN

        if form.userrole.data == 'webdev':
            usrole = ROLE_WEBDEV
        else:
            usrole = ROLE_SALESEXEC

        user = User(nickname=nickname, email=form.useremail.data, role=usrole, rights=right)
        db.session.add(user)
        db.session.commit()
        flash('Added User with Address: ' + form.useremail.data + ' with ' + form.userright.data + ' rights, as a ' + form.userrole.data)
        return render_template('base.html', title='Home')

    return render_template('addusrs.html', title="User Management", form=form)

@app.route('/upload', methods=['GET', 'POST'])
def uploadpg():
    form = uploadlandingpg();

    if form.validate_on_submit():
        file = request.files['file']

        if form.visibility.data == 'visible':
            vis = VISIBILE
        else:
            vis = HIDDEN

        filerec= LandingPage(uploader_id=g.user.id, visibility=form.visibility.data, product=form.productname.data, page_name=file.filename, page_type=form.page_type.data)
        db.session.add(filerec)
        db.session.commit()
        flash('Added File with Name: ' + file.filename)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return render_template('base.html', title='Home')

    return render_template('uploadlandpg.html', title='Upload Landing Page', form = form)

@app.route('/showallfiles')
@login_required
def showallpages():
    AllFiles = LandingPage.query.all()
    return render_template('showallfiles.html', title='All Files', Files = AllFiles)

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = SigninForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(app.config['GOOGLE_OPENID'], ask_for=['nickname', 'email'])
    return render_template('signin.html',
                           title='Sign In',
                           form=form, )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        flash('Not A Registered UniBlue FM user')
        return redirect(url_for('login'))

    """
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, rights = RIGHT_USER)
        db.session.add(user)
        db.session.commit()"""
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/redirecting')
def redirector():
    return redirect(url_for('file:///C:/Users/Nick.Nick-PC/PycharmProjects/teamB/landingpages/pageA.html'), 302)

@app.route('/editpage', methods=['GET', 'POST'])
def editpg():
    pgid = request.args.get('pageid')
    landpage = LandingPage.query.filter_by(id=pgid).first()
    form = uploadlandingpg()
    if form.validate_on_submit():
        landpage.product = form.productname.data
        landpage.page_type = form.page_type.data
        landpage.visibility= form.visibility.data
        db.session.commit()
        flash('Landing Page attributes Saved')
        return redirect(url_for('showallpages'))
    return render_template('editpage.html', title='Edit Landing Page', f=landpage, form = form)

@app.route('/newcampaign', methods=['GET', 'POST'])
def newcamp():
    form = newcampaign()
    if form.validate_on_submit():
        camp=Campaign(crea)
        db.session.add(camp)
        db.session.commit()
        flash('Added File with Name: ' + file.filename)
    return render_template('newcampaign1.html', title='Add New Campaign', form = form)

@app.route('/addfunnel', methods=['GET', 'POST'])
def addfunnel():
    form = funnelpg()
    if form.validate_on_submit():
        funnelrec = Funnel(campaign_id=form.campaign_id.data, name=form.funnel_name.data, product=form.product_name.data)
        db.session.add(funnelrec)
        db.session.commit()
        flash('Added Funnel with Name: ' + form.funnel_name.data)
        return render_template('base.html', title='Home')
    return render_template('addfunnel.html', title='Add Funnel Page', form=form)


