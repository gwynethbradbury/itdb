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
from .views import register_tables


register_tables()