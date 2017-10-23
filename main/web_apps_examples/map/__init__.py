from flask import Blueprint
# from ... import app
# from app.admin import *
import os
# from app.dev.models import DatabaseAssistant

from flask_sqlalchemy import SQLAlchemy

# map = Blueprint('map', __name__,template_folder='templates')#,static_folder='static')
# uploadfolder = dir_path = os.path.dirname(os.path.realpath(__file__))+'/data/'
#
# print(uploadfolder)

# db = SQLAlchemy(app)

import views

def init_app(app,root):
    views.assignroutes(app,root)

# from app.admin import register_crud

# db = SQLAlchemy(app)
# # from .models import project
# # from .views import register_tables
#
# from app.dev import *
#
# import dbconfig
# dbbb = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
#                                                    dbconfig.db_password,
#                                                    'map')
# dbbindkey="project_"+"map"+"_db"
# appname="map"#app.name
#
# DBA = DatabaseAssistant(dbbb,dbbindkey,appname)

# register_tables(map)