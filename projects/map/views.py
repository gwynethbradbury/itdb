# from flask import render_template, redirect, url_for, request,send_file
import json
# from models import project
# import os
# import csv
# import sqlalchemy as sqAl
#
# from sqlalchemy import *
# from sqlalchemy.orm import sessionmaker
#
# from werkzeug.utils import secure_filename
# # from . import uploadfolder
# from datetime import datetime

#todo: remove dependence on DB, this functionality should be all in the DBA
import dbconfig
if dbconfig.test:
    from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
    from projects.map.dbhelper import DBHelper

from projects.map import project_app
DB = DBHelper(project_app.name)



from core.dev import *

# import dataset



# projects = []


# @map.route('/projects/map/admin/', defaults={'page': 'index'})
# @map.route('/projects/map/admin/<page>')
# def show(page):
#     try:
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#         return render_template("/projects/map/mapadmin.html",tablenames=tablenames)
#     except Exception as E:#TemplateNotFound:
#         abort(404)

def assignroutes(application):
    approute = "/projects/"+application.name+"/"

    @application.route(approute+"showpoints")
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
        return render_template(approute+application.name+".html",
                               projects=projects, data=data)

    @application.route(approute+"submitproject", methods=['GET', 'POST'])
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
        return redirect(url_for(application.name+"_app."+application.name))

    @application.route(approute+"uploadxls", methods=['GET', 'POST'])
    def uploadxls():
        try:
            filename = request.form.get("filename")
            DB.uploadxls(filename)
        except Exception as e:
            print e
        return redirect(url_for('map_app.map'))

    @application.route(approute+"")
    def applicationhome():
        projects = []
        try:
            data = DB.get_all_inputs()
            projects = DB.get_all_projects()
            projects = json.dumps(projects)
        except Exception as e:
            print e
            data = []
        print(data)
        return render_template(approute+application.name+".html",
                               projects=projects, data=data)





