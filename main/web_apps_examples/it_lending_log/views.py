from flask import render_template, redirect, url_for, request,send_file
from ...sqla.app import app as map
from ...sqla.core.iaasldap import LDAPUser as iaasldap
iaasldap = iaasldap()
import json
# from .models import pages
import os
import csv
import sqlalchemy as sqAl
from main.sqla.dev.models import DatabaseAssistant


from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from werkzeug.utils import secure_filename
# from . import uploadfolder
from datetime import datetime

import dbconfig
# if dbconfig.test:
#     from mockdbhelper import MockDBHelper as DBHelper
# else:
from dbhelper import DBHelper

projects = []

DB = DBHelper("it_lending_log")#map.name)

from main.sqla.dev import *

import dataset

dbbb = 'mysql+pymysql://{}:{}@localhost/{}'.format(dbconfig.db_user,
                                                   dbconfig.db_password,
                                                   'it_lending_log')#map.name)
# db2 = dataset.connect(dbbb, row_type=pages)
dbbindkey="project_online_learning_db"
appname="it_lending_log"
DBA = DatabaseAssistant(dbbb,dbbindkey,appname)



def assignroutes(application):
    approute = "/it_lending_log/"
    templateroute = "projects/it_lending_log/"

    @application.route(approute)
    def it_lending_log():
        items = []
        log=[]
        fields = ['id','item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

        try:
            items = DB.getAllItems()
            logs = DB.getAllLogs()

            # projects = DB.get_all_projects()
            # projects = json.dumps(projects)
            return render_template(templateroute+"it_lending_log"+".html",
                                   itemlist=items,
                                   log=logs,
                                   fields=fields,
                                   username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                   servicelist=iaasldap.get_groups())
        except Exception as e:
            print e
            data = []
        # print(data)
        return render_template(templateroute+"it_lending_log"+".html",
                               log=log,
                               fields=fields,
                               itemlist=items,
                               username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               servicelist=iaasldap.get_groups())



    @application.route(approute+"submitentry", methods=['GET', 'POST'])
    def it_lending_log_submit():
        try:
            # fields = ['id', 'item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

            item = request.form.get("item")
            date_out = request.form.get("date_out")
            returned = (request.form.get("returned")=='on')
            borrower = request.form.get("borrower")
            signed_out_by = request.form.get("signed_out_by")
            comment = request.form.get("comment")
            DB.addEntry(item, date_out, returned, borrower, signed_out_by, comment)
        except Exception as e:
            print e
        # home()
        return redirect(approute)#url_for("map"+"_app."+"map"))

    @application.route(approute+"submititem", methods=['GET', 'POST'])
    def it_lending_item_submit():
        try:
            # fields = ['id', 'item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

            name = request.form.get("name")
            comment = request.form.get("comment")
            DB.addItem(name, comment)
        except Exception as e:
            print e
        # home()
        return redirect(approute)#url_for("map"+"_app."+"map"))

    @application.route(approute+"deleteitem/<table>/<id>")
    def it_lending_log_delete_item(table,id):
        try:
            DB.removeItem(table,id)
        except Exception as e:
            print e

        return redirect(approute)

    @application.route(approute+"markreturned/<id>")
    def it_lending_log_return_item(id):
        try:
            DB.returnItem(id)
        except Exception as e:
            print e

        return redirect(approute)

    @application.route(approute+"alter/<id>", methods=['GET','POST'])
    def it_lending_log_alter_log(id):

        if request.method == 'POST':
            try:
                # fields = ['id', 'item', 'date_out', 'returned', 'borrower', 'signed_out_by', 'comment']

                item = request.form.get("item")
                date_out = request.form.get("date_out")
                returned = (request.form.get("returned") == 'on')
                borrower = request.form.get("borrower")
                signed_out_by = request.form.get("signed_out_by")
                comment = request.form.get("comment")
                DB.alterLog(id, item, date_out, returned, borrower, signed_out_by, comment)
            except Exception as e:
                print e
        else:
            try:
                items = DB.getAllItems()
                logitem = DB.getLog(id)
                logitem=logitem[0]
                return render_template(templateroute+"alterlog"+".html",
                                       itemlist=items,
                                       logitem=logitem,
                                       username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                       servicelist=iaasldap.get_groups())
            except Exception as e:
                print e

        return redirect(approute)

    @application.route(approute+"alter/item/<id>", methods=['GET','POST'])
    def it_lending_log_alter_item(id):

        if request.method == 'POST':
            try:

                name = request.form.get("name")
                comment = request.form.get("comment")
                DB.alterItem(id, name, comment)

            except Exception as e:
                print e
        else:
            try:
                items = DB.getAllItems()
                thisitem = DB.getItem(id)
                thisitem=thisitem[0]
                return render_template(templateroute+"alteritem"+".html",
                                       itemlist=items,
                                       thisitem=thisitem,
                                       username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                                       servicelist=iaasldap.get_groups())
            except Exception as e:
                print e

        return redirect(approute)

    # @application.route(approute+"showpoints")
    # def showpoints():
    #     projects = []
    #     try:
    #         data = DB.getallpoints()
    #         print(data)
    #         projects = DB.get_all_projects()
    #         projects = json.dumps(projects)
    #     except Exception as e:
    #         print e
    #         data = []
    #     print(data)
    #     return render_template(templateroute+"map"+".html",
    #                            projects=projects, data=data)
    #
    # @application.route(approute+"submitproject", methods=['GET', 'POST'])
    # def submit():
    #     try:
    #         category = request.form.get("category")
    #         startdate = request.form.get("startdate")
    #         enddate = request.form.get("enddate")
    #         latitude = float(request.form.get("latitude"))
    #         longitude = float(request.form.get("longitude"))
    #         description = request.form.get("description")
    #         DB.add_project(latitude, longitude, startdate, enddate, category, description)
    #     except Exception as e:
    #         print e
    #     # home()
    #     return redirect(approute+"showpoints")#url_for("map"+"_app."+"map"))
    #
    # @application.route(approute+"uploadxls", methods=['GET', 'POST'])
    # def uploadxls():
    #     try:
    #         filename = request.form.get("filename")
    #         DB.uploadxls(filename)
    #     except Exception as e:
    #         print e
    #     return redirect(approute+"showpoints")#redirect(url_for('map_app.map'))

# def assignadminroutes(application):
#     adminroute = "/projects/"+application.name+"/admin/"
#     approute = "/projects/"+application.name+"/"
#
#     @application.route("/projects/"+application.name+"/admin/<tablename>/<id>/delete/")
#     # @application.route("/projects/map/admin/pro/5/delete/")
#     def deleteObject(tablename,id):
#         tns,cns = DBA.getTableAndColumnNames(tablename=tablename)
#         model = DBA.classFromTableName(classname=str(tablename),fields=cns[0])
#
#         sesh = sessionmaker(bind=DBA.DBE.E)
#         sesh = sesh()
#         ObjForm = model_form(model, sesh, exclude=None)
#
#
#
#
#         # works, given id from form but that bit is incorrect
#         obj = sesh.query(model).filter_by(id=id).first()
#         sesh.delete(obj)
#         sesh.commit()
#
#         q = select(from_obj=model, columns=['*'])
#         result = sesh.execute(q)
#
#         return redirect(adminroute+"tablename/")
#
#
#
# ##################
#
#
#     @application.route("/projects/"+application.name+"/admin/")
#     def showtables():
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#
#         print("tablenames are:")
#         print(tablenames)
#         print("end")
#         return render_template(approute+"mapadmin.html",tablenames=tablenames)
#
#
#
#
#     @application.route(adminroute+"newtable")
#     def newtable():
#
#         columnnames=[]
#         tablenames=[]
#
#
#         return render_template(approute+"create_table.html",
#                                tablenames=tablenames,columnnames=columnnames)
#
#     @application.route(adminroute+"addcolumn")
#     def addcolumn():
#
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#
#         DBA.addColumn("newtable", "test2","Time stamp")
#
#         return render_template(approute+"create_table.html",
#                                tablenames=tablenames,columnnames=columnnames)
#         # return showtables()
#
#     @application.route(adminroute+"deletetable/<page>")
#     def deletetable(page):
#         DBA.deleteTable(page)
#         return redirect(adminroute)
#
#     @application.route(adminroute+"cleartable/<page>")
#     def cleartable(page):
#         DBA.clearTable(page)
#         return redirect(adminroute)
#
#     @application.route(adminroute+"download")
#     def download():
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#
#         return render_template(approute+"download_table.html",
#                                tablenames=tablenames,columnnames=columnnames)
#
#
#     @application.route(adminroute+"servedata", methods=['GET', 'POST'])
#     def servedata():
#         #serves the requested data
#         # todo: problems with filename and extension
#
#
#         try:
#             return DBA.serveData(F=request.form,
#                                  ClassName=str(request.form.get("tablename")),
#                                  p=os.path.abspath(os.path.dirname(__file__)))
#         except Exception as e:
#             print( str(e))
#
#         return redirect(adminroute)
#
#
#     @application.route(adminroute+"createtable", methods=['GET', 'POST'])
#     def createtable():
#         #create a new table either from scratch or from an existing csv
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#         success=0
#         ret=""
#
#         #check for no table name
#         if request.form.get("newtablename")=="":
#             success=0
#             ret="Enter table name"
#
#         #check for existing table with this name
#         elif request.form.get("newtablename") in tablenames:
#             success=0
#             ret="Table "+request.form.get("newtablename")+" already exists, try a new name"
#
#         #check whether this should be an empty table or from existing data
#         elif request.form.get("source") == "emptytable":
#             success, ret = DBA.createEmptyTable(request.form.get("newtablename"))
#
#         elif 'file' not in request.files:
#             # check if the post request has the file part
#             print('No file found')
#             success=0
#             ret="No file part, contact admin"
#
#         else:
#             file = request.files['file']
#             # if user does not select file, browser also
#             # submit a empty part without filename
#             if file.filename == '':
#                 success=0
#                 ret = 'No selected file.'
#
#             elif file:  # and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
#                 file.save(os.path.join(uploadfolder, dt + '_' + filename))
#                 success, ret = DBA.createTableFromCSV(os.path.join(uploadfolder, filename),
#                                                       request.form.get("newtablename"))
#
#         if success==1:
#             # todo: this does not work on the fly
#
#             from subprocess import call
#             # print["touch " + os.path.dirname(__file__) + "/tmp.py"]
#             # call(["touch " + os.path.dirname(__file__) + "/tmp.py"])
#             # register_tables(application)
#             return render_template(approute+"create_table.html",
#                                    tablenames=tablenames, columnnames=columnnames,
#                                    message="Table " +
#                                            request.form.get("newtablename") + " created successfully!\n" + ret)
#         else:
#             return render_template(approute+"create_table.html",
#                                    tablenames=tablenames, columnnames=columnnames,
#                                    error="Creation of table " + request.form.get("newtablename") +
#                                            " failed!/nError: "+ret)
#
#
#
#
#
#     @application.route(adminroute+"genblankcsv", methods=['GET', 'POST'])
#     def genblankcsv():
#         try:
#             return DBA.genBlankCSV(request.form.get("tablename"),
#                                    p=os.path.abspath(os.path.dirname(__file__)))
#         except Exception as e:
#             print( str(e))
#
#         return redirect(adminroute)
#
#
#     @application.route(adminroute+"upload")
#     def upload():
#
#         tablenames, columnnames = DBA.getTableAndColumnNames()
#         # DBA.createTableFromCSV("/Users/cenv0594/Repositories/dbas/projects/map/data/export.csv", 'testtable2')
#
#         return render_template(approute+"upload_table.html",
#                                tablenames=tablenames)
#
#
#
#     @application.route(adminroute+"uploadcsv", methods=['GET', 'POST'])
#     def uploadcsv():
#         if request.method == 'POST':
#             # check if the post request has the file part
#             if 'file' not in request.files:
#                 print('No file part')
#                 return redirect(request.url)
#             file = request.files['file']
#             # if user does not select file, browser also
#             # submit a empty part without filename
#             if file.filename == '':
#                 print('No selected file')
#                 return redirect(request.url)
#             if file:# and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
#                 file.save(os.path.join(uploadfolder, dt+'_'+filename))
#                 print(filename)
#                 DB.uploadcsv(os.path.join(uploadfolder, filename))
#                 # return redirect(url_for('uploaded_file',
#                 #                         filename=filename))
#
#
#
#         return redirect(adminroute)
#
#
#
# # def register_tables(application):
# #     tablenames, columnnames = DBA.getTableAndColumnNames()
# #     i=0
# #     for tn in tablenames:
# #         t=str(tn)
# #
# #         C = DBA.classFromTableName(t,columnnames[i])
# #         i+=1
# #         print("registering "+t+" with columns: ")
# #         c1 = C()
# #         print(c1.fields)
# #
# #         registerCRUDforUnknownTable(map, '/projects/'+application.name+'/admin/'+t, t, C,
# #                                      list_template='projects/'+application.name+'/listview.html',
# #                                      detail_template='projects/'+application.name+'/detailview.html',
# #                                      dbbindkey=dbbindkey, appname=appname)
#
#
# #
assignroutes(map)
# # assignadminroutes(map)