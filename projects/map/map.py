from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

map_app = Blueprint('map_app', __name__,
                        template_folder='templates',static_folder='static')




import json
import dbconfig
if dbconfig.test:
	from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
	from projects.map.dbhelper import DBHelper
DB=DBHelper()




@map_app.route("/map")
def map():
	try:
		data=DB.get_all_inputs()
		projects=DB.get_all_projects()
		projects=json.dumps(projects)
	except Exception as e:
		print e
		data=None
	print(data)
	return render_template("map.html",projects=projects,data=data)



@map_app.route("/submitproject", methods=['GET','POST'])
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
	return redirect(url_for('map'))

@map_app.route("/uploadxls", methods=['GET','POST'])
def upload():
	try:
		filename=request.form.get("filename")
		DB.uploadxls(filename)
	except Exception as e:
		print e
	return redirect(url_for('map'))
	#return map()

@map_app.route("/clear")
def clear():
	try:
		DB.clear_all()
	except Exception as e:
		print e
	return redirect(url_for('map'))
	#return map()

if __name__ =='__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)

