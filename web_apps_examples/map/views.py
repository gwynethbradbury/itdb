from flask import render_template, redirect, url_for, request,send_file
from . import map
import json
from models import project
import os
import csv
import sqlalchemy as sqAl
from app.dev.models import DatabaseAssistant


from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from werkzeug.utils import secure_filename
from . import uploadfolder
from datetime import datetime

import dbconfig
if dbconfig.test:
    from web_apps_examples.map.mockdbhelper import MockDBHelper as DBHelper
else:
    from web_apps_examples.map.dbhelper import DBHelper

projects = []

DB = DBHelper(map.name)

from core.dev import *

import dataset

dbbb = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
                                                   dbconfig.db_password,
                                                   map.name)
db2 = dataset.connect(dbbb, row_type=project)
dbbindkey="project_"+map.name+"_db"
appname=map.name
DBA = DatabaseAssistant(dbbb,dbbindkey,appname)



# @map.route('/projects/map/admin/', defaults={'page': 'index'})
# @map.route('/projects/map/admin/<page>')
# def show(page):
#     try:
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#         return render_template("/projects/map/mapadmin.html",tablenames=tablenames)
#     except Exception as E:#TemplateNotFound:
#         abort(404)

def assignroutes(application):
    approute = "/projects/"+application.name+"/app/"

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

def assignadminroutes(application):
    adminroute = "/projects/"+application.name+"/admin/"
    approute = "/projects/"+application.name+"/"

    @application.route("/projects/"+application.name+"/admin/<tablename>/<id>/delete/")
    # @application.route("/projects/map/admin/pro/5/delete/")
    def deleteObject(tablename,id):
        tns,cns = DBA.getTableAndColumnNames(tablename=tablename)
        model = DBA.classFromTableName(classname=str(tablename),fields=cns[0])

        sesh = sessionmaker(bind=DBA.DBE.E)
        sesh = sesh()
        ObjForm = model_form(model, sesh, exclude=None)




        # works, given id from form but that bit is incorrect
        obj = sesh.query(model).filter_by(id=id).first()
        sesh.delete(obj)
        sesh.commit()

        q = select(from_obj=model, columns=['*'])
        result = sesh.execute(q)

        return redirect(adminroute+"tablename/")



##################


    @application.route("/projects/"+application.name+"/admin/")
    def showtables():
        tablenames, columnnames = DBA.getTableAndColumnNames()

        print("tablenames are:")
        print(tablenames)
        print("end")
        return render_template(approute+"mapadmin.html",tablenames=tablenames)




    @application.route(adminroute+"newtable")
    def newtable():

        columnnames=[]
        tablenames=[]


        return render_template(approute+"create_table.html",
                               tablenames=tablenames,columnnames=columnnames)

    @application.route(adminroute+"addcolumn")
    def addcolumn():

        tablenames, columnnames = DBA.getTableAndColumnNames()

        DBA.addColumn("newtable", "test2","Time stamp")

        return render_template(approute+"create_table.html",
                               tablenames=tablenames,columnnames=columnnames)
        # return showtables()

    @application.route(adminroute+"deletetable/<page>")
    def deletetable(page):
        DBA.deleteTable(page)
        return redirect(adminroute)

    @application.route(adminroute+"cleartable/<page>")
    def cleartable(page):
        DBA.clearTable(page)
        return redirect(adminroute)

    @application.route(adminroute+"download")
    def download():
        tablenames, columnnames = DBA.getTableAndColumnNames()

        return render_template(approute+"download_table.html",
                               tablenames=tablenames,columnnames=columnnames)


    @application.route(adminroute+"servedata", methods=['GET', 'POST'])
    def servedata():
        #serves the requested data
        # todo: problems with filename and extension


        try:
            return DBA.serveData(F=request.form,
                                 ClassName=str(request.form.get("tablename")),
                                 p=os.path.abspath(os.path.dirname(__file__)))
        except Exception as e:
            print( str(e))

        return redirect(adminroute)


    @application.route(adminroute+"createtable", methods=['GET', 'POST'])
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

            from subprocess import call
            # print["touch " + os.path.dirname(__file__) + "/tmp.py"]
            # call(["touch " + os.path.dirname(__file__) + "/tmp.py"])
            # register_tables(application)
            return render_template(approute+"create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   message="Table " +
                                           request.form.get("newtablename") + " created successfully!\n" + ret)
        else:
            return render_template(approute+"create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   error="Creation of table " + request.form.get("newtablename") +
                                           " failed!/nError: "+ret)





    @application.route(adminroute+"genblankcsv", methods=['GET', 'POST'])
    def genblankcsv():
        try:
            return DBA.genBlankCSV(request.form.get("tablename"),
                                   p=os.path.abspath(os.path.dirname(__file__)))
        except Exception as e:
            print( str(e))

        return redirect(adminroute)


    @application.route(adminroute+"upload")
    def upload():

        tablenames, columnnames = DBA.getTableAndColumnNames()
        # DBA.createTableFromCSV("/Users/cenv0594/Repositories/dbas/projects/map/data/export.csv", 'testtable2')

        return render_template(approute+"upload_table.html",
                               tablenames=tablenames)



    @application.route(adminroute+"uploadcsv", methods=['GET', 'POST'])
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



        return redirect(adminroute)



# def register_tables(application):
#     tablenames, columnnames = DBA.getTableAndColumnNames()
#     i=0
#     for tn in tablenames:
#         t=str(tn)
#
#         C = DBA.classFromTableName(t,columnnames[i])
#         i+=1
#         print("registering "+t+" with columns: ")
#         c1 = C()
#         print(c1.fields)
#
#         registerCRUDforUnknownTable(map, '/projects/'+application.name+'/admin/'+t, t, C,
#                                      list_template='projects/'+application.name+'/listview.html',
#                                      detail_template='projects/'+application.name+'/detailview.html',
#                                      dbbindkey=dbbindkey, appname=appname)
    


assignroutes(map)
# assignadminroutes(map)