#!/usr/bin/env python
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json

from projects.map.map import map_app
from core.home import home
from core import create_app, db
from core.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

import dbconfig
if dbconfig.test:
	from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
	from projects.map.dbhelper import DBHelper


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

app.register_blueprint(home)
app.register_blueprint(map_app)
#app=Flask(__name__)
DB=DBHelper()




if __name__ =='__main__':
	app.run(host="0.0.0.0", port=3000, debug=True)









