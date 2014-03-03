'''
Created on 02 Mar 2014

@author: Nick
'''
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config.py')

from app import views