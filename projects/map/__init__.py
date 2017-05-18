from flask import Blueprint
from app import app
from app.admin import *
import os

import dbconfig

# set the project name and get the relative path for uploads/downloads
project_name = 'map'
uploadfolder = dir_path = os.path.dirname(os.path.realpath(__file__))+'/data/'

# create the rpoject app (generic name)
project_app = Blueprint(project_name, __name__,template_folder='templates')#,static_folder='static')


# set the database entry point for this project
# database and project names should be the same
db = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
                                                 dbconfig.db_password,
                                                 project_app.name)

dbbindkey="project_"+project_name+"_db"


import views

# create the database assistant instance
DBA = views.DatabaseAssistant(db,dbbindkey,project_name)

views.assignroutes(project_app)
views.assignAdminRoutesForDatabase(project_app,DBA,upload_folder=uploadfolder)


