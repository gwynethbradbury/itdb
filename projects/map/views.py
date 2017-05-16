from flask import render_template, redirect, url_for, request,send_file
from . import map
import json
from models import project
import os
import csv
import sqlalchemy as sqAl

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


import dbconfig
if dbconfig.test:
    from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
    from projects.map.dbhelper import DBHelper

projects = []

DB = DBHelper("map")

from core.dev import *

import dataset

dbbb = 'mysql+pymysql://{}:{}@localhost/map'.format(dbconfig.db_user, dbconfig.db_password)
db2 = dataset.connect(dbbb, row_type=project)
dbbindkey="project_map_db"
appname="map"
DBA = DatabaseAssistant(dbbb,dbbindkey,appname)



# @map.route('/projects/map/admin/', defaults={'page': 'index'})
# @map.route('/projects/map/admin/<page>')
# def show(page):
#     try:
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#         return render_template("/projects/map/mapadmin.html",tablenames=tablenames)
#     except Exception as E:#TemplateNotFound:
#         abort(404)





@map.route("/projects/map/admin/")
def showtables():
    tablenames, columnnames = DBA.getTableAndColumnNames()

    print("tablenames are:")
    print(tablenames)
    print("end")
    return render_template("/projects/map/mapadmin.html",tablenames=tablenames)

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
def uploadxls():
    try:
        filename = request.form.get("filename")
        DB.uploadxls(filename)
    except Exception as e:
        print e
    return redirect(url_for('map_app.map'))

@map.route("/projects/map/")
def maphome():
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

@map.route("/projects/map/admin/newtable")
def newtable():

    columnnames=[]
    tablenames=[]


    return render_template('projects/map/create_table.html',
                           tablenames=tablenames,columnnames=columnnames)

@map.route("/projects/map/admin/addcolumn")
def addcolumn():

    tablenames, columnnames = DBA.getTableAndColumnNames()

    DBA.addColumn("newtable", "test2","Time stamp")

    return render_template('projects/map/create_table.html',
                           tablenames=tablenames,columnnames=columnnames)
    # return showtables()

@map.route("/projects/map/admin/deletetable/<page>")
def deletetable(page):
    DBA.deleteTable(page)
    return redirect('/projects/map/admin/')

@map.route("/projects/map/admin/cleartable/<page>")
def cleartable(page):
    DBA.clearTable(page)
    return redirect('/projects/map/admin/')

@map.route("/projects/map/admin/download")
def download():
    tablenames, columnnames = DBA.getTableAndColumnNames()

    return render_template('projects/map/download_table.html',
                           tablenames=tablenames,columnnames=columnnames)


@map.route("/projects/map/admin/servedata", methods=['GET', 'POST'])
def servedata():
    #serves the requested data
    # todo: problems with filename and extension


    try:
        return DBA.serveData(F=request.form,
                             ClassName=str(request.form.get("tablename")),
                             p=os.path.abspath(os.path.dirname(__file__)))
    except Exception as e:
        print( str(e))

    return redirect('/projects/map/admin/')


@map.route("/projects/map/admin/createtable", methods=['GET', 'POST'])
def createtable():
    #create a new table either from scratch or from an existing csv
    tablenames, columnnames = DBA.getTableAndColumnNames()
    success=0
    ret=""

    #check for no table name
    if request.form.get("newtablename")=="":
        success=0
        ret="Enter table name"

    #check for existing table with this name
    elif request.form.get("newtablename") in tablenames:
        success=0
        ret="Table "+request.form.get("newtablename")+" already exists, try a new name"

    #check whether this should be an empty table or from existing data
    elif request.form.get("source") == "emptytable":
        success, ret = DBA.createEmptyTable(request.form.get("newtablename"))

    elif 'file' not in request.files:
        # check if the post request has the file part
        print('No file found')
        success=0
        ret="No file part, contact admin"

    else:
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            success=0
            ret = 'No selected file.'

        elif file:  # and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
            file.save(os.path.join(uploadfolder, dt + '_' + filename))
            success, ret = DBA.createTableFromCSV(os.path.join(uploadfolder, filename),
                                                  request.form.get("newtablename"))

    if success==1:
        # todo: this does not work on the fly
        register_tables()
        return render_template('projects/map/create_table.html',
                               tablenames=tablenames, columnnames=columnnames,
                               message="Table " +
                                       request.form.get("newtablename") + " created successfully!\n" + ret)
    else:
        return render_template('projects/map/create_table.html',
                               tablenames=tablenames, columnnames=columnnames,
                               error="Creation of table " + request.form.get("newtablename") +
                                       " failed!/nError: "+ret)


def register_tables():
    tablenames, columnnames = DBA.getTableAndColumnNames()
    i=0
    for tn in tablenames:
        t=str(tn)

        C = DBA.classFromTableName(t,columnnames[i])
        i+=1
        print("registering "+t+" with columns: ")
        c1 = C()
        print(c1.fields)

        registerCRUDforUnknownTable(map, '/projects/map/admin/'+t, t, C,
                                     list_template='projects/map/listview.html',
                                     detail_template='projects/map/detailview.html',
                                     dbbindkey=dbbindkey, appname=appname)



@map.route("/projects/map/admin/genblankcsv", methods=['GET', 'POST'])
def genblankcsv():
    try:
        return DBA.genBlankCSV(request.form.get("tablename"),
                               p=os.path.abspath(os.path.dirname(__file__)))
    except Exception as e:
        print( str(e))

    return redirect('/projects/map/admin/')


@map.route("/projects/map/admin/upload")
def upload():

    tablenames, columnnames = DBA.getTableAndColumnNames()
    # DBA.createTableFromCSV("/Users/cenv0594/Repositories/dbas/projects/map/data/export.csv", 'testtable2')

    return render_template('projects/map/upload_table.html',
                           tablenames=tablenames)


from werkzeug.utils import secure_filename
from . import uploadfolder
from datetime import datetime

@map.route("/projects/map/admin/uploadcsv", methods=['GET', 'POST'])
def uploadcsv():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file:# and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
            file.save(os.path.join(uploadfolder, dt+'_'+filename))
            print(filename)
            DB.uploadcsv(os.path.join(uploadfolder, filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))



    return redirect('/projects/map/admin/')