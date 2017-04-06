#!/usr/bin/env python
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json

from iaas_home.iaas_home import iaas_home
from iaas_home import create_app, db
from iaas_home.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

import dbconfig
if dbconfig.test:
	from mockdbhelper import MockDBHelper as DBHelper
else:
	from dbhelper import DBHelper


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
app.register_blueprint(iaas_home)
#app=Flask(__name__)
DB=DBHelper()

projects=[]






@app.route("/view")
def home():
	print("hi")
	projects=[]
	try:
		data=DB.get_all_inputs()
		projects=DB.get_all_projects()
		projects=json.dumps(projects)
		#print(str(projects.count))
	except Exception as e:
		print e
		data=None
	return render_template("index.html",projects=projects,data=data)


@app.route("/submitproject", methods=['GET','POST'])
def submit():
	try:
		category=request.form.get("category")
		startdate=request.form.get("startdate")
		enddate=request.form.get("enddate")
		latitude=float(request.form.get("latitude"))
		longitude=float(request.form.get("longitude"))
		description=request.form.get("description")
		DB.add_project(latitude,longitude,startdate,enddate,category,description)
	except Exception as e:
		print e
	home()
	return redirect(url_for('home'))

@app.route("/uploadxls", methods=['GET','POST'])
def upload():
	try:
		filename=request.form.get("filename")
		DB.uploadxls(filename)
	except Exception as e:
		print e
	return redirect(url_for('home'))
	#return home()

@app.route("/clear")
def clear():
	try:
		DB.clear_all()
	except Exception as e:
		print e
	return redirect(url_for('home'))
	#return home()

if __name__ =='__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)



