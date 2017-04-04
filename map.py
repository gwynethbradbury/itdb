from flask import Flask
from flask import render_template
from flask import request
import json
import dbconfig
if dbconfig.test:
	from mockdbhelper import MockDBHelper as DBHelper
else:
	from dbhelper import DBHelper

app=Flask(__name__)
DB=DBHelper()

@app.route("/")
def home():
	projects=None
	try:
		projects=DB.get_all_projects()
		projects=json.dumps(projects)
	except Exception as e:
		print e
	return render_template("home.html",projects=projects)

@app.route("/add", methods=['GET','POST'])
def add():
	try:
		data=request.form.get("userinput")
		DB.add_input(data)
	except Exception as e:
		print e
	return home()

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
	return home()

@app.route("/clear")
def clear():
	try:
		DB.clear_all()
	except Exception as e:
		print e
	return home()

if __name__ =='__main__':
	app.run(port=5000, debug=True)



