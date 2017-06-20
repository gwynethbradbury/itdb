# project/__init__.py

from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy

from core.email import send_email_simple as send_email
from core.home import AH
import core.iaasldap as iaasldap

import dbconfig
import importlib


from config import config

app = Flask('dbas_app')
app.config.update(
        DEBUG=True
    )

# app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/iaas'.format(dbconfig.db_user, dbconfig.db_password)



print('setting up email settings')
app.secret_key = dbconfig.mail_secret_key
app.config["MAIL_SERVER"] = dbconfig.mail_server
app.config["MAIL_PORT"] = dbconfig.mail_port
app.config["MAIL_USE_SSL"] = dbconfig.mail_use_ssl
app.config["MAIL_USERNAME"] = dbconfig.mail_username
if not dbconfig.is_server_version:#personal machine
    app.config["AAAS_MAIL_SENDER"] = dbconfig.mail_username
    app.config["MAIL_PASSWORD"] = dbconfig.mail_password
else:#server
    app.config["AAAS_MAIL_SENDER"] = dbconfig.mail_sender
    app.config["MAIL_DEFAULT_SENDER"] = dbconfig.mail_sender

db = SQLAlchemy(app)



from core.home import home
from admin import admin
from flask import abort

app.register_blueprint(home)
app.register_blueprint(admin, url_prefix='/admin',
                       template_folder='templates')


@home.context_processor
def inject_url():
    iaas_url=dbconfig.iaas_route
    dbas_url=dbconfig.dbas_route
    return dict(iaas_url=iaas_url,dbas_url=dbas_url)

@app.route('/admin')
def admin():
    usersgroups = iaasldap.get_groups(iaasldap.uid_trim())
    if "superusers" in usersgroups:
        return render_template("admin/admin.html",
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(iaasldap.uid_trim()))
    else:
        return abort(401)

@app.route('/admin/emailsubscribers')
def emailsubscribers():
    return render_template("admin/email_subscribers.html",
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(iaasldap.uid_trim()))

@app.route('/admin/send_email_subscribers', methods=['GET', 'POST'])
def send_email_subscribers():
    s = AH.get_mailing_list()
    send_email(s, 'IAAS Enquiry', request.form['messagebody'])
    return redirect("/admin")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(iaasldap.uid_trim())), 404
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html',
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(iaasldap.uid_trim())), 500
@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html',
                           username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                           servicelist=iaasldap.get_groups(iaasldap.uid_trim())), 401





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
print("registering DBAS services available and adding to dictionary:")
for r in resultasstring:
    if r[2] == '1' or r[2] == '4':#then this is a database project
        print("registering project: " + r[1])
        try:
            dev.register_project(s=r[1])
        except Exception as e:
            print(e)




        if r[1]=='map':
            try:

                db = SQLAlchemy(app)
                import web_apps_examples
                # from web_apps_examples import map as maps

                # maps.assignroutes(app)#,nm='map')

                # # THE FOLLOWING ARE MAP-SPECIFIC - SHOULD BE MOVED TO MAP WEB APP
                # my_module = importlib.import_module('web_apps_examples.'+r[1])
                # my_module.views.assignroutes(app,nm='map')
            except Exception as e:
                print e




