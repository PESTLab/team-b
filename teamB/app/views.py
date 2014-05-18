__author__ = 'Nick'
import os

from app import app, db, lm, oid, ALLOWED_EXTENSIONS
from flask import redirect, render_template, url_for, flash, request, g, session, render_template_string, make_response
from forms import SigninForm, adduserform, uploadlandingpg, newcampaign, funnelpg, prod_form, pgtype_form, add_varient, SearchForm
from flask_login import login_user, logout_user, current_user, login_required
from models import User, RIGHT_USER, RIGHT_ADMIN, ROLE_SALESEXEC, ROLE_WEBDEV, LandingPage, VISIBILE, HIDDEN, Campaign, \
    Funnel, ROLE_ADMIN, Product, Page_Type, SplitTest
from flask_googlelogin import GoogleLogin
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from config import basedir
from datetime import datetime
import requests
import json

from jinja2 import Environment, FileSystemLoader

googlelogin = GoogleLogin(app)

api_url = "http://54.228.201.142:81"

def get_all_prod_names():
    product_list = Product.query.all()
    prodnames = []
    for prod in product_list:
        prodnames.append((prod.name, prod.name))
    return prodnames
    
def get_all_page_types():
    pagetypes_list = Page_Type.query.all()
    pgtypes = []
    for ty in pagetypes_list:
        pgtypes.append((ty.type, ty.type))
    return pgtypes

def findcamp_byname(campname):
    campaign = Campaign.query.filter_by(name=campname).first()
    return campaign

def findcamp_byid(campid):
    campaign = Campaign.query.filter_by(id=campid).first()
    return campaign

def findfunnel_byname(funname):
    funnel = Funnel.query.filter_by(name=funname).first()
    return funnel

def findfunnel_byid(funid):
    funnel = Funnel.query.filter_by(id=funid).first()
    return funnel

def findlandpage_byid(pageid):
    landpage = LandingPage.query.filter_by(id=pageid).first()
    return landpage

def findlandpage_byname(pagename):
    landpage = LandingPage.query.filter_by(page_name = pagename).first()
    return landpage

def connect_to_bucket():
    keysfile = os.path.join(basedir, 'app')
    keysfile = os.path.join(keysfile, 'amakeys.txt')
    text_file = open(keysfile, "r")
    keys = text_file.read().split(',')
    conn = S3Connection(keys[0], keys[1])
    b = conn.get_bucket('broadcast.uniblue')
    return b

def upload_to_bucket(file_toupload, filename):
    k = Key(connect_to_bucket())
    k.key = filename
    k.set_contents_from_file(file_toupload, {"Content-Type": "text/html"})
    k.set_acl('public-read')

def getall_visiblepages():
    allfiles = LandingPage.query.all()
    visible_files = []
    for f in allfiles:
        if f.visibility == 2:
            visible_files.append(f)
    return visible_files

def get_testcode(testcode, newcode, varcode):
    newcode = newcode + "-" + str(varcode)
    if testcode == "notest":
        testcode = newcode
    else:
        testcode = testcode + "_" + newcode
    return testcode

@app.route('/<campname>/<productname>/<funnelname>/<pagetype>', methods=['GET'])
def broadcast(campname, productname, funnelname, pagetype):
    funnel = findfunnel_byname(funnelname)
    fun_pages = funnel.content_ids.split(",")
    pagename = ''
    mypage = LandingPage()
    for p in fun_pages:
        if p:
            page = findlandpage_byid(p)
            if (page.page_type == pagetype):
                mypage = page

    pinfunnel = mypage

    tst = request.args.get('TestCode')
    if tst is None:
        testcode = "notest"
    else:
        testcode = tst

    cookiename = 'splittest' + str(pinfunnel.test_id)
    already = request.cookies.get(cookiename)


    if mypage.test_pos != -1:

        if already != None:
            var_page = LandingPage.query.filter_by(id = int(already)).first()
        else:
            variants = mypage.variants.split(',')
            if mypage.test_pos == -2:
                var_page = mypage
            else:
                var_page = LandingPage.query.filter_by(id = variants[mypage.test_pos]).first()
            if mypage.test_pos == len(variants)-2:
                mypage.test_pos = -2
            elif mypage.test_pos == -2:
                mypage.test_pos = 0
            else:
                mypage.test_pos = mypage.test_pos + 1
            db.session.commit()
        varcode = var_page.id
        test = SplitTest.query.filter_by(id = mypage.test_id).first()
        newcode = test.test_code

        testcode = get_testcode(testcode, newcode, varcode)

        mypage = var_page

    pagename = mypage.page_name
    b = connect_to_bucket()
    k = Key(b)
    k.key = pagename
    rendered_page = k.get_contents_as_string()

    resp = make_response(render_template_string(rendered_page, p=mypage, pif = pinfunnel, tcode = testcode, f=funnel, title='Rendered Page'))

    if pinfunnel.test_pos != -1 and already == None:
        cookiename = 'splittest' + str(pinfunnel.test_id)
        resp.set_cookie(cookiename, str(mypage.id))

    return resp

'''user log-in'''


@app.route('/fm/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = SigninForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(app.config['GOOGLE_OPENID'], ask_for=['nickname', 'email'])
    return render_template('signin.html', title='Sign In', form=form, )

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


@app.route('/fm/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()


'''app home page'''


@app.route('/fm/index')
def index():
    return render_template('base.html', title='Home')


'''user management'''


@app.route('/fm/showallusers')
@login_required
def showallusers():
    if g.user.rights != RIGHT_ADMIN:
        flash('Only Users with Administrator Rights can access this page')
        return redirect(url_for('index'))
    AllUsers = User.query.all()
    return render_template('showallusers.html', title='All Users', Users=AllUsers)


@app.route('/fm/addusers', methods=['GET', 'POST'])
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
            if form.userrole.data == 'webdev':
                usrole = ROLE_WEBDEV
            else:
                usrole = ROLE_SALESEXEC
        else:
            right = RIGHT_ADMIN
            usrole = ROLE_ADMIN

        email = form.useremail.data
        email = User.make_unique_email(email)
        user = User(nickname=nickname, email=email, role=usrole, rights=right)
        db.session.add(user)
        db.session.commit()
        flash(
            'Added User with Address: ' + form.useremail.data + ' with ' + form.userright.data + ' rights, as a ' + form.userrole.data)
        return render_template('base.html', title='Home')

    return render_template('addusrs.html', title="User Management", form=form)

@app.route('/fm/deleteuser', methods=['GET', 'POST'])
@login_required
def deleteusers():
    if g.user.rights != RIGHT_ADMIN:
        flash('Only Users with Administrator Rights can access this page')
        return redirect(url_for('index'))

    userid = request.args.get('uid')

    user = User.query.filter_by(id=userid).first()
    db.session.delete(user)
    db.session.commit()

    flash('User Deleted')

    allusers = User.query.all()

    return redirect(url_for('showallusers'))


'''landing page management'''


@app.route('/fm/upload', methods=['GET', 'POST'])
@login_required
def uploadpg():

    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    form = uploadlandingpg()
    form.productname.choices = get_all_prod_names()
    form.page_type.choices = get_all_page_types()
    if form.validate_on_submit():
        file = request.files['file']

        if form.visibility.data == 'visible':
            vis = VISIBILE
        else:
            vis = HIDDEN

        prodlist = form.productname.data
        pg_prod = ",".join(prodlist)



        filerec = LandingPage(uploader_id=g.user.id, visibility=form.visibility.data, product=pg_prod,
                              page_name=file.filename, page_type=form.page_type.data)

        checkpg = findlandpage_byname(file.filename)

        if not checkpg:
            if file and allowed_file(file.filename) and (filerec.product != ''):

                db.session.add(filerec)
                db.session.commit()

                myname = str(file.filename)

                upload_to_bucket(file, myname)

                url = api_url + '/fmapi/addpg'
                data = {'id': filerec.id, 'name': filerec.page_name, 'pgtype': filerec.page_type, 'prod': filerec.product, 'vis': filerec.visibility}
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post(url, data=json.dumps(data), headers=headers, auth=('unibluefm', '123456789'))

                AllFiles = LandingPage.query.all()


                return render_template('showallfiles.html', title='All Files', Files=AllFiles)
            else:
                flash('Either the Extension is not allowed or you left the Product Name Empty')
                return render_template('uploadlandpg.html', title='Upload Landing Page', form=form)
        else:
            flash('A Filename with the same name already exists. Please rename your file before Uploading')
            return render_template('uploadlandpg.html', title='Upload Landing Page', form=form)

    return render_template('uploadlandpg.html', title='Upload Landing Page', form=form)


def allowed_file(filename):
    if filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


@app.route('/fm/showallfiles')
@login_required
def showallpages():

    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    AllFiles = LandingPage.query.all()

    s = request.args.get('s')

    if s != None:
        r = int(request.args.get('r'))
        if s == 'id':
            AllFiles.sort(key=lambda x: x.id, reverse=r)
        elif s == 'name':
            AllFiles.sort(key=lambda x: x.page_name, reverse=r)
        elif s == 'pro':
            AllFiles.sort(key=lambda x: x.product, reverse=r)
        elif s == 'typ':
            AllFiles.sort(key=lambda x: x.page_type, reverse=r)
    db.session.close_all()


    form = add_varient();

    return render_template('showallfiles.html', title='All Files', Files=AllFiles, form=form)


@app.route('/fm/editpage', methods=['GET', 'POST'])
@login_required
def editpg():

    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgid = request.args.get('pageid')

    landpage = findlandpage_byid(pgid)

    form = uploadlandingpg()

    pgtypes = get_all_page_types()
    old_type = ((landpage.page_type, landpage.page_type))
    pgtypes.remove(old_type)
    pgtypes.insert(0, old_type)
    form.page_type.choices = pgtypes

    form.productname.choices = get_all_prod_names()

    if form.validate_on_submit():
        if form.productname.data != []:
            landpage.product = form.productname.data
        landpage.page_type = form.page_type.data
        landpage.visibility = form.visibility.data
        db.session.commit()

        url = api_url + '/fmapi/updatepg/'+ str(landpage.id)
        data = {'pgprod': landpage.product, 'pgtype': landpage.page_type, 'pgvis': landpage.visibility}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.put(url, data=json.dumps(data), headers=headers, auth=('unibluefm', '123456789'))


        return redirect(url_for('showallpages'))

    return render_template('editpage.html', title='Edit Landing Page', f=landpage, form=form)


'''Delete Page option should be removed since if a page is deleted, funnels using this page will be affected.'''

@app.route('/fm/deletepage', methods=['GET', 'POST'])
@login_required
def deletepg():
    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgid = request.args.get('pageid')
    landpage = findlandpage_byid(pgid)

    b = connect_to_bucket()
    k = Key(b)
    k.key = landpage.page_name
    b.delete_key(k)

    db.session.delete(landpage)
    db.session.commit()

    url = api_url + '/fmapi/deletepage/' + str(landpage.id)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.delete(url, headers=headers, auth=('unibluefm', '123456789'))

    flash('Template Deleted from S3 Bucket')

    return redirect(url_for('showallpages'))


'''campaign management'''


@app.route('/fm/newcampaign', methods=['GET', 'POST'])
@login_required
def newcamp():
    if ((g.user.role != ROLE_SALESEXEC) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    form = newcampaign()

    if form.validate_on_submit():

        camp = Campaign(creator_id=g.user.id, name=form.campaignname.data)

        checkcamp = findcamp_byname(camp.name)

        if not checkcamp:

            db.session.add(camp)
            db.session.commit()

            url = api_url + '/fmapi/addcamp'
            data = {'id': camp.id, 'campname': camp.name, 'funids': 'none'}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(data), headers=headers, auth=('unibluefm', '123456789'))


            return redirect(url_for('managecamp', cid=camp.id))
        else:
            flash('A campaign with the same name already exists, please chose another name')
            return render_template('newcampaign1.html', title='Add New Campaign', form=form)

    return render_template('newcampaign1.html', title='Add New Campaign', form=form)


@app.route('/fm/managecampaign', methods=['GET', 'POST'])
@login_required
def managecamp():
    if ((g.user.role != ROLE_SALESEXEC) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Sales Executive Roles can access this page')
        return redirect(url_for('index'))

    camp = findcamp_byid(request.args.get('cid'))
    funnelform = funnelpg()

    funnel_ids = camp.funnel_ids.split(",")
    funnels_arr = []

    for f_id in funnel_ids:
        f = findfunnel_byid(f_id)
        if f:
            funnels_arr.append(f)

    AllFiles = LandingPage.query.all()
    alltypes = Page_Type.query.all()



    funnelform.product_name.choices=get_all_prod_names()
    if funnelform.validate_on_submit():
        match = False
        for fun in funnels_arr:
            if fun.name == funnelform.funnel_name.data:
                match = True
                StopIteration

        if not match:
            funnelrec = Funnel(campaign_id=camp.id, name=funnelform.funnel_name.data,
                               product=funnelform.product_name.data)
            db.session.add(funnelrec)
            db.session.commit()

            if camp.funnel_ids == "NONE":
                camp.funnel_ids = str(funnelrec.id) + ","
            else:
                camp.funnel_ids = camp.funnel_ids + str(funnelrec.id) + ","

            db.session.commit()

            url = api_url + '/fmapi/addfun'
            data = {'id': funnelrec.id, 'campid': camp.id, 'funname': funnelrec.name, 'prodname': funnelrec.product, 'contids': 'none'}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(data), headers=headers, auth=('unibluefm', '123456789'))

            url = api_url + '/fmapi/updatecamp/' + str(camp.id)
            data = {'funids': camp.funnel_ids}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.put(url, data=json.dumps(data), headers=headers, auth=('unibluefm', '123456789'))

            return redirect(url_for('managecamp', cid=camp.id))
        else:
            flash('Funnel with same name already exists in this Campaign, please enter another name')
            redirect(url_for('managecamp', cid=camp.id))

    return render_template('managecampaign.html', c=camp, form=funnelform, funnels=funnels_arr, allfiles=AllFiles, pagetypes = alltypes)


@app.route('/fm/showallcampaigns')
@login_required
def showallcamps():
    if ((g.user.role != ROLE_SALESEXEC) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    s = request.args.get('s')


    allcamps = Campaign.query.all()

    if s != None:
        r = int(request.args.get('r'))
        if s == 'id':
            allcamps.sort(key=lambda x: x.id, reverse=r)
        elif s == 'name':
            allcamps.sort(key=lambda x: x.name, reverse=r)
    db.session.close_all()

    return render_template('showallcamps.html', title='All Campaigns', Camps=allcamps)


@app.route('/fm/savechanges')
@login_required
def setfunids():
    if ((g.user.role != ROLE_SALESEXEC) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    pgids = request.args.get('pgids')
    c_id = request.args.get('cid')
    fun_id = request.args.get('fun_id')

    funnel = findfunnel_byid(fun_id)

    funnel.content_ids = pgids

    db.session.commit()

    url = api_url + '/fmapi/updatefun/' + str(funnel.id)
    data = {'content': funnel.content_ids}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.put(url, data=json.dumps(data), headers=headers, auth=('unibluefm', '123456789'))

    return redirect(url_for('managecamp', cid=c_id))


@app.route('/fm/deletecampaign')
@login_required
def deletecamp():
    if ((g.user.role != ROLE_SALESEXEC) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    camp = findcamp_byid(request.args.get('cid'))
    if not (camp.funnel_ids in ("NONE", None)):
        funnel_ids = camp.funnel_ids.split(",")
        for f_id in funnel_ids:
            if not (f_id in ('')):
                f = findfunnel_byid(f_id)
                db.session.delete(f)

    db.session.delete(camp)
    db.session.commit()

    url = api_url + '/fmapi/deletecamp/' + str(camp.id)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.delete(url, headers=headers, auth=('unibluefm', '123456789'))

    return redirect(url_for('showallcamps'))

@app.route('/fm/deletefunnel')
@login_required
def deletefun():

    if ((g.user.role != ROLE_SALESEXEC) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    camp = findcamp_byid(request.args.get('cid'))
    fun = findfunnel_byid(request.args.get('fid'))

    todel = str(fun.id) + ","
    camp.funnel_ids = camp.funnel_ids.replace(todel, "")
    db.session.delete(fun)
    db.session.commit()

    url = api_url + '/fmapi/deletefun/' + str(camp.id) + str(fun.id)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.delete(url, headers=headers, auth=('unibluefm', '123456789'))

    return redirect(url_for('showallcamps'))

'''Product List Management'''


@app.route('/fm/products', methods=['GET', 'POST'])
@login_required
def manageprodlist():
    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    form = prod_form()

    if form.validate_on_submit():
        prod = Product(name=str(form.product_name.data))
        check_prod = Product.query.filter_by(name=prod.name).first()
        if not check_prod:
            db.session.add(prod)
            db.session.commit()
            all_products = Product.query.all()
            flash('New Product Added')
        else:
            flash('Product with this name already exists')

        return redirect(url_for('manageprodlist'))

    all_products = Product.query.all()
    return render_template('prodlist.html', title='Product List', prods = all_products, form = form)

@app.route('/fm/deleteprod', methods=['GET', 'POST'])
@login_required
def deleteproduct():
    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    prodid = request.args.get('pid')
    prod = Product.query.filter_by(id=prodid).first()
    db.session.delete(prod)
    db.session.commit()

    flash('Product Deleted')

    return redirect(url_for('manageprodlist'))
    
'''Page Type Management'''

@app.route('/fm/pagetypes', methods=['GET', 'POST'])
@login_required
def managepagetypes():
    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    form = pgtype_form()

    if form.validate_on_submit():
        ptype = Page_Type(type=str(form.pg_type.data))
        check_type = Page_Type.query.filter_by(type=ptype.type).first()
        if not check_type:
            db.session.add(ptype)
            db.session.commit()
            all_page_types = Page_Type.query.all()
            flash('New Page Type Added')
        else:
            flash('Page Type already exists')

        return redirect(url_for('managepagetypes'))

    all_page_types = Page_Type.query.all()
    return render_template('pagetypes.html', title='Landing Page Types', types = all_page_types, form = form)

@app.route('/fm/deletepgtype', methods=['GET', 'POST'])
@login_required
def deletepagetype():
    if ((g.user.role != ROLE_WEBDEV) and (g.user.role != ROLE_ADMIN)):
        flash('Only an Administrator or Users with Web Developer Roles can access this page')
        return redirect(url_for('index'))

    typeid = request.args.get('tid')
    ptyp = Page_Type.query.filter_by(id=typeid).first()
    db.session.delete(ptyp)
    db.session.commit()

    flash('Page Type Deleted')

    return redirect(url_for('managepagetypes'))

def getproductlist():
    mylist = ['gorg', 'jason', 'toni']
    return mylist

env = Environment(loader=FileSystemLoader('/templates'))
env.globals['getproductlist'] = getproductlist()

'''split testing management'''

@app.route('/fm/addvariant', methods=['GET', 'POST'])
@login_required
def addvar():
    pid = request.args.get('pid')
    varnametoadd = request.args.get('varname')
    var = LandingPage.query.filter_by(page_name = varnametoadd).first()
    page = LandingPage.query.filter_by(id=pid).first()

    if page.product.find(',') != -1:

        allfunnels = Funnel.query.all()
        for f in allfunnels:
            if str(page.id) in f.content_ids.split(','):
                if f.product not in var.product.split(','):
                    flash('This Variant would cause a conflict with Funnel ' + f.name + ' which has ' + f.product + ' as its product')
                    return redirect(url_for('showallpages'))

    if page.variants == None:
        page.variants = str(var.id) + ","
    else:
        page.variants = page.variants + str(var.id) + ","
    db.session.commit()
    return redirect(url_for('showallpages'))

def get_seq_no(testid):
    if testid < 10:
        seq = "00" + str(testid)
    elif testid < 100:
        seq = "0" + str(testid)
    else:
        seq = str(testid)

    return seq

@app.route('/fm/startsplittest', methods=['GET', 'POST'])
@login_required
def starttest():
    pid = request.args.get('pid')
    page = LandingPage.query.filter_by(id = pid).first()
    page.test_pos = -2
    new_test = SplitTest(pageid=page.id, variants = page.variants)
    db.session.add(new_test)
    db.session.commit()

    currentYear = datetime.now().year
    year = str(currentYear)
    y = "" + year[2] + year[3]

    seq = get_seq_no(new_test.id)

    new_test.test_code = y + "-" + seq
    page.test_id = new_test.id
    db.session.commit()
    flash('Test for Page ' + page.page_name + ' started' )
    return redirect(url_for('showallpages'))

@app.route('/fm/stopsplittest', methods=['GET', 'POST'])
@login_required
def stoptest():
    pid = request.args.get('pid')
    page = LandingPage.query.filter_by(id = pid).first()
    page.test_pos = -1
    db.session.commit()
    flash('Test for Page ' + page.page_name + ' stopped' )
    return redirect(url_for('showallpages'))

''' Searching '''

@app.route('/fm/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    PageResults = LandingPage.query.whoosh_search(query, 10).all()
    FunnelResults = Funnel.query.whoosh_search(query, 10).all()
    return render_template('search_results.html',query = query, presults = PageResults, fresults = FunnelResults)