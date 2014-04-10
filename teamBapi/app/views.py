__author__ = 'Nick'

from flask import Flask, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from app import app, db
from models import Campaign, Funnel, LandingPage

auth = HTTPBasicAuth()

Allowed_Origins = ['http://54.228.201.142', 'http://127.0.0.1']

'''API Authorization'''

@auth.get_password
def get_password(username):
    if username == 'unibluefm':
        return '123456789'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

''' Get NextPage URL '''

@app.route('/fmapi/getnext/<int:funid>/<int:pgid>', methods=['GET'])
def getnexturl(funid,pgid):

    source_origin = str(request.remote_addr)
    source_origin = "http://" + source_origin

    if source_origin in Allowed_Origins:

        url = 'EndOfFunnel'

        page = LandingPage.query.filter_by(id=pgid).first()
        funnel = Funnel.query.filter_by(id=funid).first()
        camp = Campaign.query.filter_by(id=funnel.campaign_id).first()

        pg_ids = funnel.content_ids.split(",")
        pgs_arr = []

        for p_id in pg_ids:
            p = LandingPage.query.filter_by(id=p_id).first()
            if p:
                pgs_arr.append(p)

        x = pgs_arr.index(page)

        if x == (len(pgs_arr)-1):
            resp = make_response(jsonify(nextpg = url))
            resp.headers['Access-Control-Allow-Origin'] = "http://54.228.201.142"
            return resp
        else:
            nextpage = pgs_arr[x+1]

        Base_URL = source_origin

        url = Base_URL + '/' + camp.name + '/' + funnel.product + '/' + funnel.name + '/' + nextpage.page_type
        resp = make_response(jsonify(nextpg = url))
        resp.headers['Access-Control-Allow-Origin'] = "http://54.228.201.142"
        return resp

'''add records to db using POST Method'''

@app.route('/fmapi/addcamp', methods = ['POST'])
@auth.login_required
def addcampaign():
    newcamp = Campaign(id=request.json['id'], name=request.json['campname'], funnel_ids=request.json['funids'])
    db.session.add(newcamp)
    db.session.commit()
    return jsonify(msg= 'Campaign Added')

@app.route('/fmapi/addfun', methods = ['POST'])
@auth.login_required
def addfunnel():
    newfun = Funnel(id=request.json['id'], campaign_id=request.json['campid'], name=request.json['funname'], product=request.json['prodname'], content_ids = request.json['contids'])
    db.session.add(newfun)
    db.session.commit()
    return jsonify(msg = 'Funnel Added')

@app.route('/fmapi/addpg', methods = ['POST'])
@auth.login_required
def addpage():
    newpg = LandingPage(id=request.json['id'], page_name=request.json['name'], page_type=request.json['pgtype'], product=request.json['prod'], visibility= request.json['vis'])
    db.session.add(newpg)
    db.session.commit()
    return jsonify(msg = newpg.product + ' ' + newpg.page_type)

'''update db records using PUT method'''

@app.route('/fmapi/updatecamp/<int:campid>', methods = ['PUT'])
@auth.login_required
def updatecampaign(campid):
    camp = Campaign.query.filter_by(id=campid).first()
    camp.funnel_ids = request.json['funids']
    db.session.commit()
    return jsonify(msg = 'Campaign Updated')

@app.route('/fmapi/updatefun/<int:funid>', methods = ['PUT'])
@auth.login_required
def updatefunnel(funid):
    funnel = Funnel.query.filter_by(id=funid).first()
    funnel.content_ids = request.json['content']
    db.session.commit()
    return jsonify(msg = 'Funnel Updated')

@app.route('/fmapi/updatepg/<int:pgid>', methods = ['PUT'])
@auth.login_required
def updatepage(pgid):
    page = LandingPage.query.filter_by(id=pgid).first()
    page.product = request.json['pgprod']
    page.page_type = request.json['pgtype']
    page.visibility = request.json['pgvis']
    db.session.commit()
    return jsonify(msg = 'Page Details Updated')


'''delete db records using DELETE method'''
@app.route('/fmapi/deletecamp/<int:campid>', methods = ['DELETE'])
@auth.login_required
def deletecmp(campid):
    camp = Campaign.query.filter_by(id=campid).first()

    if not (camp.funnel_ids in ("NONE", "none", None)):
        funnel_ids = camp.funnel_ids.split(",")
        for f_id in funnel_ids:
            if not (f_id in ('')):
                f = Funnel.query.filter_by(id=f_id).first()
                if f:
                    db.session.delete(f)

    db.session.delete(camp)
    db.session.commit()

    return jsonify(msg = 'Campaign Deleted')


'''testing functions for CURL'''

@app.route('/fmapi/showcamp', methods = ['POST'])
@auth.login_required
def showcampaign():
    camp = Campaign.query.filter_by(id=request.json['campname']).first()
    return jsonify(ID=camp.id, Name=camp.name, Funnels = camp.funnel_ids)

@app.route('/fmapi/showpg', methods = ['POST'])
def showpage():
    page = LandingPage.query.filter_by(id=request.json['pgname']).first()
    return jsonify(ID=page.id, Product = page.product, Visibility = page.visibility, Type = page.page_type)

@app.route('/fmapi/showfun', methods = ['POST'])
@auth.login_required
def showfunnel():
    funnel = Funnel.query.filter_by(name=request.json['funname']).first()
    return jsonify(ID=funnel.id, Pages = funnel.content_ids)


