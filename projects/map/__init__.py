from flask import Blueprint
from app import app
from app.admin import *
import os

map = Blueprint('map', __name__,template_folder='templates')#,static_folder='static')
uploadfolder = dir_path = os.path.dirname(os.path.realpath(__file__))+'/data/'

import views

from app.admin import register_crud

from .models import project
from .views import register_tables

from core.dev import *

import dbconfig
dbbb = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
                                                   dbconfig.db_password,
                                                   map.name)
dbbindkey="project_"+map.name+"_db"
appname=map.name

DBA = DatabaseAssistant(dbbb,dbbindkey,appname)

register_tables(map)