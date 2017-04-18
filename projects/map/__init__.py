from flask import Blueprint

map_app = Blueprint('map_app', __name__,template_folder='templates',static_folder='static')

from . import views


from dbas import app
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy




# #app = Flask('admin_app')
# app.config.update(
#         DEBUG=True,
#         SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
#     )
# db = SQLAlchemy(app)
#
# from admin import admin
# #app.register_blueprint(admin, url_prefix='/admin')
#
#
#
# @map_app.route('/mapadmin')
# def home():
#     return 'Blog be here'
#


