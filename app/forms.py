__author__ = 'Nick'

from flask_wtf import Form
from wtforms import TextField, BooleanField, RadioField, SelectField, FileField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Length, email

class SigninForm(Form):
    remember_me = BooleanField('remember_me', default=False)

class adduserform(Form):
    useremail = EmailField('useremail', [validators.Required()])
    userright = RadioField('userright', choices=[('user', 'User'), ('admin', 'Administrator')], default='user')
    userrole = RadioField('userrole', choices=[('webdev', 'Web Developer'), ('salesexec', 'Sales Executive')], default='webdev')

class uploadlandingpg(Form):
    page_type = SelectField('page_type', choices=[('download', 'Download Page'), ('product', 'Product Page')])
    productname= TextField('productname')
    visibility = RadioField('visibilty', choices=[('visible','Visible'), ('hidden', 'Hidden'), ('notset', 'Not Set')], default='visible')
    file = FileField('filename')

class newcampaign(Form):
    campaignname = TextField('campaignname', [validators.Required()])

class funnelpg(Form):
    funnel_name = TextField('funnel_name', [validators.Required()])
    product_name = TextField('product_name', [validators.Required()])



