from flask import render_template, redirect, url_for, request,send_file
from . import map
import json
from models import project
import os
import csv
import sqlalchemy as sqAl


import dbconfig
if dbconfig.test:
    from projects.map.mockdbhelper import MockDBHelper as DBHelper
else:
    from projects.map.dbhelper import DBHelper

projects = []

DB = DBHelper("map")

@map.route("/projects/map/admin/")
def showtables():
    return render_template("/projects/map/mapadmin.html")


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



import dataset

dbbb = 'mysql+pymysql://{}:{}@localhost/map'.format(dbconfig.db_user, dbconfig.db_password)
db2 = dataset.connect(dbbb, row_type=project)


# @map.route("/projects/map/submitproject", methods=['GET', 'POST'])
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
#     return redirect(url_for('map_app.map'))

@map.route("/projects/map/admin/download")
def download():
    engine = sqAl.create_engine(dbbb)
    tablenames=[]

    from sqlalchemy import MetaData
    m = MetaData()
    m.reflect(engine)
    for table in m.tables.values():
        print(table.name)
        tablenames.append(table.name)
        # for column in table.c:
        #     print(column.name)



    return render_template('projects/map/download_table.html',
                           tablenames=tablenames)
    # return showtables()


@map.route("/projects/map/admin/servedata", methods=['GET', 'POST'])
def servedata():
    # form = DownloadTableForm()
    # if form.validate_on_submit():
        print('Download requested for table="%s"' %
              (request.form.get("tablename")))

        #DOWNLOAD WHOLE TABLE DATA HERE

        if request.form.get("wholetable"):
            print('yes')
        else:
            print('no')
        metadata = sqAl.MetaData()
        engine = sqAl.create_engine(dbbb)
        metadata.bind = engine

        mytable = sqAl.Table(request.form.get("tablename"), metadata, autoload=True)#.data, metadata, autoload=True)
        # mytable = sqAl.Table('project', metadata, autoload=True)
        db_connection = engine.connect()

        select = sqAl.sql.select([mytable])
        result = db_connection.execute(select)

        projbasedir = os.path.abspath(os.path.dirname(__file__))
        exportpath = projbasedir + '/data/export.csv'
        fh = open(exportpath, 'wb')
        outcsv = csv.writer(fh)

        outcsv.writerow(result.keys())
        outcsv.writerows(result)

        fh.close()

        try:
            # return
            return send_file(exportpath,
                             attachment_filename='export.csv')
        except Exception as e:
            print( str(e))

        return redirect('/projects/map/admin/')

@map.route("/projects/map/admin/genblankcsv", methods=['GET', 'POST'])
def genBlankCSV():
    # generates an empty file to upload data for the selected table

    metadata = sqAl.MetaData()
    engine = sqAl.create_engine(dbbb)
    metadata.bind = engine

    mytable = sqAl.Table(request.form.get("tablename"), metadata, autoload=True)#.data, metadata, autoload=True)
    # mytable = sqAl.Table('project', metadata, autoload=True)
    db_connection = engine.connect()

    select = sqAl.sql.select([mytable])
    result = db_connection.execute(select)

    projbasedir = os.path.abspath(os.path.dirname(__file__))
    exportpath = projbasedir + '/data/upload.csv'
    fh = open(exportpath, 'wb')
    outcsv = csv.writer(fh)

    outcsv.writerow(result.keys())
    # outcsv.writerows(result)

    fh.close()

    try:
        # return
        return send_file(exportpath,
                         attachment_filename='export.csv')
    except Exception as e:
        print( str(e))

    return redirect('/projects/map/admin/')

@map.route("/projects/map/admin/upload")
def upload():
    engine = sqAl.create_engine(dbbb)
    tablenames=[]

    from sqlalchemy import MetaData
    m = MetaData()
    m.reflect(engine)
    for table in m.tables.values():
        print(table.name)
        tablenames.append(table.name)
        # for column in table.c:
        #     print(column.name)



    return render_template('projects/map/upload_table.html',
                           tablenames=tablenames)
    # return showtables()


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