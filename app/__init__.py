# project/__init__.py

from flask import Flask, render_template, request, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
import dbconfig
import importlib

app = Flask('dbas_app')
app.config.update(
        DEBUG=True
    )

app.config.from_object('config')

db = SQLAlchemy(app)
# bind the static database for iaas service admin - this is a static database
db.create_all(bind='iaas_db')
# db.create_all(bind='project_map_db')


# from projects.map import project_app as map
from core.home import home
from app.admin import admin



app.register_blueprint(home)
app.register_blueprint(admin, url_prefix='/admin',
                       template_folder='templates')



# do this for each project:
# uses database to do this dynamically
import dev, os

# create the database assistant instance
db = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                          dbconfig.db_password,
                                          "localhost",
                                          "iaas")
dba = dev.views.DatabaseAssistant(db,"iaas","iaas")
result, resultasstring = dba.retrieveDataFromDatabase("svc_instances",["project_display_name","instance_identifier","svc_type_id","group_id"])
print("registering DBAS services availableand adding to dictionary:")
for r in resultasstring:
    if r[2] == '1':#then this is a database project
        print("registering project: " + r[1])
        try:
            dev.register_project(s=r[1])
        except Exception as e:
            print(e)

        if r[1]=='map':
            try:
                # THE FOLLOWING ARE MAP-SPECIFIC - SHOULD BE MOVED TO MAP WEB APP
                my_module = importlib.import_module('projects.'+r[1])
                my_module.views.assignroutes(app,nm='map')
            except Exception as e:
                print e









@app.route('/admin')
def home():
    return render_template("admin/admin.html")
