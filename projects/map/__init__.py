from flask import Blueprint
from app import app
from app.admin import *
import os

map = Blueprint('map', __name__,template_folder='templates')#,static_folder='static')
uploadfolder = dir_path = os.path.dirname(os.path.realpath(__file__))+'/data/'

print(uploadfolder)
import views

from app.admin import register_crud

from .models import project

#register the admin CRUD for each table
register_crud(map, '/projects/map/admin/projects', 'project', project,
              list_template='projects/map/listview.html',detail_template='projects/map/detailview.html')
# register_crud(admin, '/projects/map/test1', 'comments', Comment, filters=comment_filters)
