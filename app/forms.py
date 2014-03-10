__author__ = 'Nick'

from flask_wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, PasswordField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Length, email

class SigninForm(Form):
    remember_me = BooleanField('remember_me', default = False)

class adduserform(Form):
    useremail = EmailField('useremail')
    userright = RadioField('userright', choices=[('user','User'), ('admin','Administrator')], default='user')
    userrole = RadioField('userrole', choices=[('webdev','Web Developer'),('salesexec','Sales Executive')], default='webdev')

