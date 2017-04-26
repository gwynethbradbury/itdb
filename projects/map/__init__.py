from flask import Blueprint
from app import app
from app.admin import *

map = Blueprint('map', __name__,template_folder='templates')#,static_folder='static')


import views

from app.admin import register_crud

from .models import project

#register the admin CRUD for each table
register_crud(map, '/projects/map/admin/projects', 'project', project)
# register_crud(admin, '/projects/map/test1', 'comments', Comment, filters=comment_filters)
