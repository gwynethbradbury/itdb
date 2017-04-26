from flask import render_template, redirect, url_for, request
from . import map#, DB
import json
from jinja2 import TemplateNotFound


import dbconfig
if dbconfig.test:
    from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
    from projects.map.dbhelper import DBHelper

projects = []

DB = DBHelper("map")

@map.route("/projects/map/admin/")
def showtables():
    return render_template("/projects/map/admin.html")


@map.route("/projects/map/showpoints")
def showpoints():
    projects = []
    try:
        data = DB.getallpoints()
        print(data)
        projects = DB.get_all_projects()
        projects = json.dumps(projects)
    except Exception as e:
        print e
        data = []
    print(data)
    return render_template("projects/map/map.html", projects=projects, data=data)


@map.route("/projects/map/clear")
def clear():
    try:
        DB.clear_all()
    except Exception as e:
        print e
    return redirect(url_for('map'))


@map.route("/projects/map/submitproject", methods=['GET', 'POST'])
def submit():
    try:
        category = request.form.get("category")
        startdate = request.form.get("startdate")
        enddate = request.form.get("enddate")
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        description = request.form.get("description")
        DB.add_project(latitude, longitude, startdate, enddate, category, description)
    except Exception as e:
        print e
    # home()
    return redirect(url_for('map_app.map'))


@map.route("/projects/map/uploadxls", methods=['GET', 'POST'])
def upload():
    try:
        filename = request.form.get("filename")
        DB.uploadxls(filename)
    except Exception as e:
        print e
    return redirect(url_for('map_app.map'))


@map.route("/projects/map/")
def map():
    projects = []
    try:
        data = DB.get_all_inputs()
        projects = DB.get_all_projects()
        projects = json.dumps(projects)
    except Exception as e:
        print e
        data = []
    print(data)
    return render_template("projects/map/map.html", projects=projects, data=data)


