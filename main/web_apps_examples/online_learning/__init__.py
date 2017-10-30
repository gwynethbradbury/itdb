# from main.sqla.app import app

# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy(app)



from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import dbconfig

onlinelearnapp = Flask(__name__)


# Create dummy secrey key so we can use sessions
onlinelearnapp.config['SECRET_KEY'] = '123456790'

iaas_uri = '{}://{}:{}@{}/{}' \
        .format('mysql+pymysql',
                'cenv0594',
                'keVRN7tVkP4DxR2sAlqq',
                'IAAS-gateway.ouce.ox.ac.uk:1564',
                'online_learning')

onlinelearnapp.config['SQLALCHEMY_DATABASE_URI'] =iaas_uri
onlinelearningdb = SQLAlchemy(onlinelearnapp)

import models


import views


def init_app(app,root,uri):
    views.assignroutes(app, root,uri)
    iaas_uri=uri
    onlinelearningdb = SQLAlchemy(onlinelearnapp)