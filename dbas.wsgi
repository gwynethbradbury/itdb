#!/usr/bin/python
import sys
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json
path=__file__[0:-9]
sys.path.insert(0,path)


# from projects.map import map_app
# from core.home import home
# from core import create_app, db
# from core.models import User, Role
# from flask_script import Manager, Shell
# from flask_migrate import Migrate, MigrateCommand
#
# #from dbas import app as application
#
# from app.admin import admin

# import dbconfig
#
# if dbconfig.test:
#     from projects.map.mockdbhelper import MockDBHelper as DBHelper
# else:
#     from projects.map.dbhelper import DBHelper

from app import app as application

