__author__ = 'Nick'

from flask_wtf import Form
from wtforms import TextField, BooleanField, RadioField, SelectField, FileField, validators, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required
from app.models import User

class SearchForm(Form):
    search = TextField('search', validators = [Required()])

class SigninForm(Form):
    remember_me = BooleanField('remember_me', default=False)

class adduserform(Form):
    useremail = EmailField('useremail', [validators.Required()])
    userright = RadioField('userright', choices=[('user', 'User'), ('admin', 'Administrator')], default='user')
    userrole = RadioField('userrole', choices=[('webdev', 'Web Developer'), ('salesexec', 'Sales Executive')], default='webdev')

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email = self.useremail.data).first()
        if user is not None:
            self.useremail.errors.append('This email is already used. Please enter another email or login with it.')
            return False
        return True

class uploadlandingpg(Form):
    page_type = SelectField('page_type', choices=[('download', 'Download Page'), ('product', 'Product Page'), ('purchase', 'Purchase Page')])
    productname= SelectMultipleField('productname')
    visibility = RadioField('visibilty', choices=[('visible','Visible'), ('hidden', 'Hidden'), ('notset', 'Not Set')], default='visible')
    file = FileField('filename')

class newcampaign(Form):
    campaignname = TextField('campaignname', [validators.Required()])

class funnelpg(Form):
    funnel_name = TextField('funnel_name', [validators.Required()])
    product_name = SelectField('product_name', [validators.Required()])

class prod_form(Form):
    product_name = TextField('product_name', [validators.Required()])
    
class pgtype_form(Form):
    pg_type = TextField('pg_type', [validators.Required()])

class add_varient(Form):
    var_name = SelectField('var_name')



