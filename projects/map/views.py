from flask import render_template, redirect, url_for, request, flash
from . import map#, DB
import json
from jinja2 import TemplateNotFound
from .forms import DownloadTableForm
from app import db
from models import project
import StringIO
import os


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
def upload():
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


@map.route("/projects/map/admin/download/", methods=['GET', 'POST'])
def download_table():
    form = DownloadTableForm()
    if form.validate_on_submit():
        print('Download requested for table="%s", whole_table=%s' %
              (form.tablename.data, str(form.whole_table.data)))
        flash('Download requested for table="%s", whole_table=%s' %
              (form.tablename.data, str(form.whole_table.data)))

        #DOWNLOAD WHOLE TABLE DATA HERE



        import csv
        import sqlalchemy as sqAl

        metadata = sqAl.MetaData()
        engine = sqAl.create_engine(dbbb)
        metadata.bind = engine

        mytable = sqAl.Table('project', metadata, autoload=True)
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

        return render_template('projects/map/download_link.html',
                               title='Download Data')
        # return redirect('/projects/map/data/export.csv')




        # import csv
        # outfile = open('/Users/cenv0594/Repositories/dbout.csv', 'wb')
        # # outfile = open('mydump.csv', 'wb')
        # outcsv = csv.writer(outfile)
        # records = session.query(db).all()
        # [outcsv.writerow([getattr(curr, column.name) for column in db.__mapper__.columns]) for curr in records]
        # # or maybe use outcsv.writerows(records)
        #
        # outfile.close()


        # def fake_close():
        #     pass
        #
        # out_iostr = StringIO.StringIO()
        # original_close = out_iostr.close
        # alarms_table = db2['project']
        #
        # # Retrieve the db as a json StringIO without the close method
        # out_iostr.close = fake_close
        # dataset.freeze(alarms_table.all(), format='json', fileobj=out_iostr)
        # out_str = out_iostr.getvalue()
        # out_iostr.close = original_close
        # out_iostr.close()
        #
        # # Get only the required data and format it
        # alarms_dict = {'id': json.loads(out_str)['id']}
        #
        # # This commented out line would prettify the string
        # # json.dumps(alarms_dict, indent=4, separators=(',', ': '))
        # return json.dumps(alarms_dict)







        # result = db2['project'].all()
        # print(result)
        #
        # fh = open('/Users/cenv0594/Repositories/dbout.csv', 'wb')
        # dataset.freeze(result, format='csv', fileobj=fh)
        #
        #
        #
        # return redirect('/projects/map/admin/')
    return render_template('projects/map/download_table.html',
                           title='Select Data',
                           form=form)
    # return showtables()


