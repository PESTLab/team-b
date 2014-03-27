__author__ = 'Nick'
import os
import shutil

from BeautifulSoup import BeautifulSoup
from werkzeug.utils import secure_filename
from app import app, db, lm, oid, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import redirect, render_template, url_for, flash, request, g, session
from forms import SigninForm, adduserform, uploadlandingpg, newcampaign, funnelpg
from flask_login import login_user, logout_user, current_user, login_required
from models import User, RIGHT_USER, RIGHT_ADMIN, ROLE_SALESEXEC, ROLE_WEBDEV, LandingPage, VISIBILE, HIDDEN, Campaign, \
    Funnel
from flask_googlelogin import GoogleLogin
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from config import basedir
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
    return render_template('showallusers.html', title='All Users', Users=AllUsers)


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
        flash(
            'Added User with Address: ' + form.useremail.data + ' with ' + form.userright.data + ' rights, as a ' + form.userrole.data)
        return render_template('base.html', title='Home')

    return render_template('addusrs.html', title="User Management", form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def uploadpg():
    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    form = uploadlandingpg();
    if form.validate_on_submit():
        file = request.files['file']

        if form.visibility.data == 'visible':
            vis = VISIBILE
        else:
            vis = HIDDEN

        filerec = LandingPage(uploader_id=g.user.id, visibility=form.visibility.data, product=form.productname.data,
                              page_name=file.filename, page_type=form.page_type.data)

        checkpg = LandingPage.query.filter_by(page_name = file.filename).first()
        if not checkpg:
            if file and allowed_file(file.filename) and (filerec.product != ''):
                filename = secure_filename(file.filename)
                db.session.add(filerec)
                db.session.commit()
                flash('Added File with Name: ' + file.filename)
                AllFiles = LandingPage.query.all()
                keysfile = os.path.join(basedir, 'app')
                keysfile = os.path.join(keysfile, 'amakeys.txt')
                text_file = open(keysfile, "r")
                keys = text_file.read().split(',')
                conn = S3Connection(keys[0], keys[1])
                b = conn.get_bucket('broadcast.uniblue')

                k = Key(b)

                k.key = filename
                k.set_contents_from_file(file)

                return render_template('showallfiles.html', title='All Files', Files=AllFiles)
            else:
                flash('Either the Extension is not allowed or you left the Product Name Empty')
                return render_template('uploadlandpg.html', title='Upload Landing Page', form=form)
        else:
            flash('A Filename with the same name already exists. Please rename your file before Uploading')
            return render_template('uploadlandpg.html', title='Upload Landing Page', form=form)

    return render_template('uploadlandpg.html', title='Upload Landing Page', form=form)


@app.route('/showallfiles')
@login_required
def showallpages():
    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    AllFiles = LandingPage.query.all()
    return render_template('showallfiles.html', title='All Files', Files=AllFiles)


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

@app.route('/editpage', methods=['GET', 'POST'])
@login_required
def editpg():
    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))
    pgid = request.args.get('pageid')
    landpage = LandingPage.query.filter_by(id=pgid).first()
    form = uploadlandingpg()
    if form.validate_on_submit():
        landpage.product = form.productname.data
        landpage.page_type = form.page_type.data
        landpage.visibility = form.visibility.data
        db.session.commit()
        flash('Landing Page attributes Saved')
        return redirect(url_for('showallpages'))
    return render_template('editpage.html', title='Edit Landing Page', f=landpage, form=form)

@app.route('/deletepage', methods=['GET', 'POST'])
@login_required
def deletepg():
    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgid = request.args.get('pageid')
    landpage = LandingPage.query.filter_by(id=pgid).first()

    keysfile = os.path.join(basedir, 'app')
    keysfile = os.path.join(keysfile, 'amakeys.txt')
    text_file = open(keysfile, "r")
    keys = text_file.read().split(',')
    conn = S3Connection(keys[0], keys[1])

    b = conn.get_bucket('broadcast.uniblue')
    k = Key(b)
    k.key = landpage.page_name
    b.delete_key(k)

    db.session.delete(landpage)
    db.session.commit()
    flash('Template Deleted from S3 Bucket')
    return redirect(url_for('showallpages'))


@app.route('/newcampaign', methods=['GET', 'POST'])
@login_required
def newcamp():
    if g.user.role != ROLE_SALESEXEC:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    form = newcampaign()
    if form.validate_on_submit():
        camp = Campaign(creator_id=g.user.id, name=form.campaignname.data)
        checkcamp = Campaign.query.filter_by(name = camp.name).first()
        if not checkcamp:
            db.session.add(camp)
            db.session.commit()
            newdir = os.path.join(app.config['UPLOAD_FOLDER'], str(camp.name))
            os.makedirs(newdir)
            return redirect(url_for('managecamp', cid=camp.id))
        else:
            flash('A campaign with the same name already exists, please chose another name')
            return render_template('newcampaign1.html', title='Add New Campaign', form=form)

    return render_template('newcampaign1.html', title='Add New Campaign', form=form)


@app.route('/managecampaign', methods=['GET', 'POST'])
@login_required
def managecamp():

    if g.user.role != ROLE_SALESEXEC:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    camp = Campaign.query.filter_by(id=request.args.get('cid')).first()
    funnelform = funnelpg()

    funnel_ids = []
    funnel_ids = camp.funnel_ids.split(",")
    funnels_arr = []

    for f_id in funnel_ids:
        f = Funnel.query.filter_by(id=f_id).first()
        if f:
            funnels_arr.append(f)

    AllFiles = LandingPage.query.all()


    if funnelform.validate_on_submit():
        match = False
        for fun in funnels_arr:
            if fun.name == funnelform.funnel_name.data:
                match = True
                StopIteration

        if not match:
            funnelrec = Funnel(campaign_id=camp.id, name=funnelform.funnel_name.data, product=funnelform.product_name.data)
            db.session.add(funnelrec)
            db.session.commit()

            if camp.funnel_ids == "NONE":
                camp.funnel_ids = str(funnelrec.id) + ","
            else:
                camp.funnel_ids = camp.funnel_ids + str(funnelrec.id) + ","

            db.session.commit()
            newdir = os.path.join(app.config['UPLOAD_FOLDER'], str(camp.name))
            newdir = os.path.join(newdir, str(funnelrec.name))
            os.makedirs(newdir)

            return redirect(url_for('managecamp', cid=camp.id))
        else:
            flash('Funnel with same name already exists in this Campaign, please enter another name')
            redirect(url_for('managecamp', cid=camp.id))

    return render_template('managecampaign.html', c=camp, form=funnelform, funnels=funnels_arr, allfiles = AllFiles)

@app.route('/showallcampaigns')
@login_required
def showallcamps():

    if g.user.role != ROLE_SALESEXEC:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    AllCamps = Campaign.query.all()
    return render_template('showallcamps.html', title='All Campaigns', Camps=AllCamps)

@app.route('/savechanges')
@login_required
def setfunids():

    if g.user.role != ROLE_SALESEXEC:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgids = request.args.get('pgids')
    c_id = request.args.get('cid')
    fun_id = request.args.get('fun_id')
    funnel = Funnel.query.filter_by(id=fun_id).first()
    funnel.content_ids = pgids
    camp = Campaign.query.filter_by(id=c_id).first()

    newdir = os.path.join(app.config['UPLOAD_FOLDER'], str(camp.name))
    newdir = os.path.join(newdir, str(funnel.name))

    pg_ids = funnel.content_ids.split(",")

    for pgid in pg_ids:
        pg = LandingPage.query.filter_by(id=pgid).first()
        if pg:
            pgname = pg.page_name

            f = open(os.path.join(app.config['UPLOAD_FOLDER'], pgname))
            page = f.read()
            soup = BeautifulSoup(page)
            f.close()
            html = soup.prettify("utf-8")



            with open(os.path.join(newdir, pgname), "w+") as file:
                file.write(html)

    files = os.listdir(newdir)
    for fi in files:
        myfi = LandingPage.query.filter_by(page_name=fi).first()

        if not (str(myfi.id) in pg_ids):
            filedir = os.path.join(newdir, str(fi))
            os.remove(filedir)

    db.session.commit()
    return redirect(url_for('managecamp', cid=c_id))

@app.route('/deletecampaign')
@login_required
def deletecamp():

    if g.user.role != ROLE_SALESEXEC:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    camp = Campaign.query.filter_by(id=request.args.get('cid')).first()
    if not (camp.funnel_ids in("NONE", None)):
        funnel_ids = camp.funnel_ids.split(",")
        for f_id in funnel_ids:
            if not (f_id in ('')):
                f = Funnel.query.filter_by(id=f_id).first()
                db.session.delete(f)

    db.session.delete(camp)
    db.session.commit()

    dir = os.path.join(app.config['UPLOAD_FOLDER'], str(camp.name))
    shutil.rmtree(dir)

    return redirect(url_for('showallcamps'))

@app.route('/editlandingpages')
@login_required
def showallhtmls():

    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    allcamps = Campaign.query.all()
    allfiles = LandingPage.query.all()
    htmlpgs=[]
    for h in allfiles:
        if h.page_name.split('.')[1] == "html":
            htmlpgs.append(h)
    return render_template('showhtml.html', title='All Landing Pages', pages = htmlpgs, camps = allcamps)


@app.route('/editlinks')
@login_required
def editlinks():

    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgid = request.args.get('pg_id')
    landpage = LandingPage.query.filter_by(id=pgid).first()
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], landpage.page_name))
    page = f.read()
    soup = BeautifulSoup(page)
    links = soup.findAll('a', {'href': True}, id='nextpage')
    f.close()

    return render_template('editlink.html', title='Edit Links', p = landpage, link = links[0])

@app.route('/updatelinks', methods=['GET', 'POST'])
@login_required
def changelinks():

    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgid = request.args.get('pageid')
    landpage = LandingPage.query.filter_by(id=pgid).first()
    funnel = Funnel.query.filter_by(id=request.args.get('fid')).first()
    camp = Campaign.query.filter_by(id=funnel.campaign_id).first()
    fdir = os.path.join(app.config['UPLOAD_FOLDER'], str(camp.name))
    fdir = os.path.join(fdir, str(funnel.name))
    f = open(os.path.join(fdir, landpage.page_name))
    page = f.read()
    soup = BeautifulSoup(page)
    links = soup.findAll('a', {'href': True}, id='nextpage')
    link = links[0]
    newlink = request.args.get('newlink')
    if newlink == "No Link":
        link['href'] = '#'
    else:
        link['href'] = request.args.get('newlink')
    f.close()
    html = soup.prettify("utf-8")
    with open(os.path.join(fdir, landpage.page_name), "wb") as file:
        file.write(html)
    flash('Link Changed')
    return redirect(url_for('showfunlinks', funid=funnel.id))

@app.route('/funnellinks', methods=['GET', 'POST'])
@login_required
def showfunlinks():

    if g.user.role != ROLE_WEBDEV:
        flash('Only Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    fid = request.args.get('funid')
    funnel = Funnel.query.filter_by(id=fid).first()
    if not (funnel.content_ids in 'none'):
        pg_ids = funnel.content_ids.split(",")
        pages = []
        for p_id in pg_ids:
            if not (p_id in ('')):
                p = LandingPage.query.filter_by(id=p_id).first()
                pages.append(p)

        camp = Campaign.query.filter_by(id=funnel.campaign_id).first()
        fdir = os.path.join(app.config['UPLOAD_FOLDER'], str(camp.name))
        fdir = os.path.join(fdir, str(funnel.name))
        files = os.listdir(fdir)
        mylinks = []
        for f in files:
            z = f
            f = open(os.path.join(fdir, f))
            page = f.read()
            soup = BeautifulSoup(page)
            links = soup.findAll('a', {'href': True}, id='nextpage')
            link = links[0]
            link['myfile'] = z
            mylinks.append(link)
    else:
        pages="No Pages"
        files=""
        mylinks=""


    return render_template('funnellinks.html', title='Funnel Links', pages = pages, f = funnel, files = files, nextlinks = mylinks)








