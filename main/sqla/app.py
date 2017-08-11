import os
import os.path as op

from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text
from sqlalchemy.orm import relationship

import flask_admin as admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import helpers, expose
import flask_login as login
from wtforms import form, fields, validators

from werkzeug.security import generate_password_hash, check_password_hash



import dbconfig
# Create application
app = Flask(__name__)#,static_folder='/main/sqla/static',template_folder='/templates')

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
# app.config['DATABASE_FILE'] = 'sample_db.sqlite'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_DATABASE_URI'] ='{}://{}:{}@{}/{}'\
    .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password, dbconfig.db_hostname,dbconfig.db_name)

# # app.config['SQLALCHEMY_ECHO'] = True
# db = SQLAlchemy(app)


app.config.update(
    DEBUG=dbconfig.debug
)

# region EMAIL SETTINGS

from core.email import send_email_simple as send_email

app.secret_key = dbconfig.mail_secret_key
app.config["MAIL_SERVER"] = dbconfig.mail_server
app.config["MAIL_PORT"] = dbconfig.mail_port
app.config["MAIL_USE_SSL"] = dbconfig.mail_use_ssl
app.config["MAIL_USERNAME"] = dbconfig.mail_username
if not dbconfig.is_server_version:  # personal machine
    app.config["AAAS_MAIL_SENDER"] = dbconfig.mail_username
    app.config["MAIL_PASSWORD"] = dbconfig.mail_password
else:  # server
    app.config["AAAS_MAIL_SENDER"] = dbconfig.mail_sender
    app.config["MAIL_DEFAULT_SENDER"] = dbconfig.mail_sender

# endregion


# create views:

from jinja2 import TemplateNotFound
from flask import render_template, abort



if dbconfig.test:
    from core.mock_access_helper import MockAccessHelper as AccessHelper
else:
    from core.access_helper import AccessHelper
AH = AccessHelper()

import core.iaasldap as iaasldap
import ldapconfig as ldapconfig
current_user = iaasldap.LDAPUser()

import dev.models as devmodels

# region Flask views
@app.route('/group/<group_name>')
def show_groups(group_name):
    instances = AH.get_projects_for_group(group_name)
    try:
        return render_template("groupprojects.html",groupname=group_name,instances=instances)
    except TemplateNotFound:
        abort(404)

    return '<a href="/admin/">Click me to get to Admin!</a>'

@app.route('/')
def index():
    try:
        instances = AH.get_projects('dbas')
        return render_template("index.html", instances=instances)
    except TemplateNotFound:
        abort(404)

    return '<a href="/admin/">Click me to get to Admin!</a>'



@app.route('/<page>')
def show(page):
    try:
        return render_template("%s.html" % page,
                               )#username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
                               #servicelist=iaasldap.get_groups(iaasldap.uid_trim()))
    except TemplateNotFound:
        abort(404)

# endregion

# region EMAIL VIEWS
@app.route('/admin/emailsubscribers')
def emailsubscribers():
    return render_template("admin/email_subscribers.html")


@app.route('/admin/send_email_subscribers', methods=['GET', 'POST'])
def send_email_subscribers():
    s = AH.get_mailing_list()
    send_email(s, 'IAAS Enquiry', request.form['messagebody'])
    return redirect("/admin")


# endregion

# region ERROR VIEWS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

# endregion


# region EDITING TABLES

# creating a new table
@app.route("/projects/<application_name>/admin/newtable")
def newtable(application_name):

    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)

    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey="project_"+application_name+"_db"

    DBA = devmodels.DatabaseAssistant(db_string,dbbindkey,application_name)#, upload_folder=uploadfolder)

    tablenames,columnnames=DBA.getTableAndColumnNames()
    if not tablenames ==[]:
        return redirect("/projects/{}/{}/admin/newtable".format(application_name,tablenames[0]))

    return render_template("projects/create_table.html",
                           tablenames=tablenames,
                           columnnames=columnnames,
                           pname=application_name)


# todo: move thissomewhere:
listOfColumnTypesByName = {"Integer":"INTEGER",
                           "String":"VARCHAR",
                           "Characters":"CHARACTER",
                           "Bool":"BOOLEAN",
                           "Time stamp":"TIMESTAMP",
                           "Date":"DATE",
                           "Time":"TIME",
                           "Really long string":"CLOB",
                           "Small integer":"SMALLINT",
                           "Real":"REAL",
                           "Float":"FLOAT",
                           "Double":"DOUBLE",
                           "Precision":"PRECISION",
                           "Text block":"TEXT"}
DataTypeNeedsN= {"INTEGER":False,
                 "VARCHAR":True,
                 "CHARACTER":True,
                 "BOOLEAN":False,
                 "TIMESTAMP":False,
                 "DATE":False,
                 "TIME":False,
                 "CLOB":True,
                 "SMALLINT":False,
                 "REAL":False,
                 "FLOAT":True,
                 "DOUBLE":False,
                 "PRECISION":False,
                 "TEXT":False}
listOfColumnTypesByDescriptor = dict(reversed(item) for item in listOfColumnTypesByName.items())

# adding a column to an existing table
# todo: unfinished
@app.route("/projects/<application_name>/admin/newcolumn")
# @app.route("/projects/<application_name>/<tablename>/admin/newcolumn")
def newcolumn(application_name,tablename=""):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

    tablenames, columnnames = DBA.getTableAndColumnNames()

    lstofdatatypes = listOfColumnTypesByName

    if not tablenames ==[]:
        return redirect("/projects/{}/{}/admin/newcolumn".format(application_name,tablenames[0]))
    return render_template("projects/add_column.html",
                           tablename=tablename,appname=application_name,
                           tablenames=tablenames,
                           listofdatatypes = lstofdatatypes,
                           columnnames=columnnames,
                           pname=application_name)
#
@app.route("/projects/<application_name>/admin/<tablename>/createcolumn", methods=['GET', 'POST'])
def createcolumn(application_name,tablename):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

    # create a new table either from scratch or from an existing csv
    tablenames, columnnames = DBA.getTableAndColumnNames(tablename)
    success = 0
    ret = ""



    # check for no column name
    if request.form.get("newcolumnname") == "":
        success = 0
        ret = "Enter column name"

    # check for existing table with this name
    elif request.form.get("newcolumnname") in columnnames[0]:
        success = 0
        ret = "Column " + request.form.get("newcolumnname") + " already exists, try a new name"


    # todo: get argument n which islength of string etc, default is curretly 10
    ret, success = DBA.addColumn(tablename, request.form.get("newcolumnname"), request.form.get("datatypes"))

    # redirects to the same page
    if success == 1:
        return render_template("projects/add_column.html",
                               tablenames=tablenames, columnnames=columnnames,
                               message="Column " +
                                       request.form.get("newcolumnname") + " created successfully!\n" + ret,
                               pname=application_name)

    else:
        return render_template("projects/add_column.html",
                               tablenames=tablenames, columnnames=columnnames,
                               error="Creation of column " + request.form.get("newcolumnname") +
                                     " failed!<br/>Error: " + ret,
                               pname=application_name)



# delete a whole table
@app.route("/projects/<application_name>/admin/deletetable/<tablename>")
def deletetable(application_name,tablename):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


    DBA.deleteTable(tablename)
    # DBA.DBE.refresh()
    return redirect("/projects/"+application_name+"/admin/")

# clear all entries from a table
@app.route("/projects/<application_name>/admin/cleartable/<tablename>")
def cleartable(application_name,tablename):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

    DBA.clearTable(tablename)
    return redirect("/projects/"+application_name+"/admin/")

# endregion

# region UPLOADING AND DOWNLOADING DATA

from werkzeug.utils import secure_filename
from datetime import datetime

# generate a blank cv given an existing table
@app.route("/projects/<application_name>/admin/genblankcsv", methods=['GET', 'POST'])
def genblankcsv(application_name):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


    try:
        return DBA.genBlankCSV(request.form.get("tablename"))
    except Exception as e:
        print(e)

    return redirect("/projects/"+application_name+"/admin/")

# renders the upload form
@app.route("/projects/<application_name>/admin/uploaddata")
def uploaddata(application_name,msg="", err=""):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


    tablenames, columnnames = DBA.getTableAndColumnNames()
    return render_template("projects/upload_table.html",
                           tablenames=tablenames,
                           message=msg,
                           error=err,
                           pname=application_name)

# adds the data from the CSV to an existing table
@app.route("/projects/<application_name>/admin/uploaddatafrom", methods=['GET', 'POST'])
def uploaddatafrom(application_name):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return uploaddata(err="No file part")
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                return uploaddata(err="No selected file")
            if file:  # and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
                tablename = str(request.form.get("tablename"))

                success, ret = DBA.createTableFrom(os.path.join(DBA.uploadfolder, dt + '_' + filename),
                                                   tablename)
                if success:
                    ret = "Success, data added to table: %s%s%s" % (tablename, "<br/>", ret)
                    return uploaddata(msg=ret)
                else:
                    return uploaddata(err=ret)

    return redirect("/projects/"+application_name+"/admin/")

# creates a new table taking name from form
# if table exists, supplements it with the new data
# todo: check for column missmatch
# @app.route("/projects/<application_name>/admin/createtable", methods=['GET', 'POST'])
# def createtable(application_name):
#     if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
#         return abort(401)
#     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
#                                                      dbconfig.db_password,
#                                                      dbconfig.db_hostname,
#                                                      application_name)
#     dbbindkey = "project_" + application_name + "_db"
#
#     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)
#     # create a new table either from scratch or from an existing csv
#     tablenames, columnnames = DBA.getTableAndColumnNames()
#     success = 0
#     ret = ""
#
#     # check for no table name
#     if request.form.get("newtablename") == "":
#         success = 0
#         ret = "Enter table name"
#
#     # check for existing table with this name
#     elif request.form.get("newtablename") in tablenames:
#         success = 0
#         ret = "Table " + request.form.get("newtablename") + " already exists, try a new name"
#
#     # check whether this should be an empty table or from existing data
#     elif request.form.get("source") == "emptytable":
#         success, ret = DBA.createEmptyTable(request.form.get("newtablename"))
#
#     elif 'file' not in request.files:
#         # check if the post request has the file part
#         print('No file found')
#         success = 0
#         ret = "No file part, contact admin"
#
#     else:
#         file = request.files['file']
#         # if user does not select file, browser also
#         # submit a empty part without filename
#         if file.filename == '':
#             success = 0
#             ret = 'No selected file.'
#
#         elif file:  # and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
#             file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
#             success, ret = DBA.createTableFromCSV(os.path.join(DBA.uploadfolder, filename),
#                                                   request.form.get("newtablename"))
#
#     if success == 1:
#         # todo: this does not work on the fly
#         return render_template("projects/create_table.html",
#                                tablenames=tablenames, columnnames=columnnames,
#                                message="Table " +
#                                        request.form.get("newtablename") + " created successfully!\n" + ret,
#                                pname=application_name)
#     else:
#         return render_template("projects/create_table.html",
#                                tablenames=tablenames, columnnames=columnnames,
#                                error="Creation of table " + request.form.get("newtablename") +
#                                      " failed!<br/>Error: " + ret,
#                                pname=application_name)

# renders the download form
# @app.route("/projects/<application_name>/admin/download")
# def download(application_name):
#     if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
#         return abort(401)
#     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
#                                                      dbconfig.db_password,
#                                                      dbconfig.db_hostname,
#                                                      application_name)
#     dbbindkey = "project_" + application_name + "_db"
#
#     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)
#
#
#     tablenames, columnnames = DBA.getTableAndColumnNames()
#
#     return render_template("projects/download_table.html",
#                            tablenames=tablenames, columnnames=columnnames,
#                            pname=application_name,
#                            username=iaasldap.uid_trim(), fullname=iaasldap.get_fullname(),
#                            servicelist=iaasldap.get_groups(iaasldap.uid_trim()))

# serves the data given the response from the download form
@app.route("/projects/<application_name>/admin/servedata", methods=['GET', 'POST'])
def servedata(application_name):
    if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
        return abort(401)
    db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                     dbconfig.db_password,
                                                     dbconfig.db_hostname,
                                                     application_name)
    dbbindkey = "project_" + application_name + "_db"

    DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

    # serves the requested data
    # todo: problems with filename and extension


    try:
        return DBA.serveData(F=request.form,
                             ClassName=str(request.form.get("tablename")))  # os.path.abspath(os.path.dirname(__file__)))
    except Exception as e:
        print(str(e))

    return redirect("/projects/"+application_name+"/admin/")


# endregion


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        # if user is None:
        #     raise validators.ValidationError('Invalid user')
        #
        # # we're comparing the plaintext pw with the the hash from the db
        # if not check_password_hash(user.password, self.password.data):
        # # to compare plain text passwords use
        # # if user.password != self.password.data:
        #     raise validators.ValidationError('Invalid password')

    def get_user(self):
        return current_user.uid_trim()
        # return db.session.query(User).filter_by(login=self.login.data).first()


# Create customized model view class
class MyModelView(ModelView,):
    current_user = iaasldap.LDAPUser()

    def is_accessible(self):
        if current_user.has_role('superusers') :
            return True
        current_url = str.split(self.admin.url,'/')
        project_name=""
        require_project_admin=False

        if current_url[1]=='projects':
            '''admin view of project'''
            project_name = current_url[2]
            require_project_admin = True
        else:
            '''normal view of project'''
            project_name = current_url[1]

        if not current_user.is_active or not current_user.is_authenticated(project_name):
            return False
        if require_project_admin and not current_user.has_role('{}_admin'.format(project_name)):
            return False


        return True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return "not authenticated" #redirect(url_for('security.login', next=request.url))


    @expose('/admin/newtable')
    def newtable(self):
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]

        if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
            return abort(401)

        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey="project_"+application_name+"_db"

        DBA = devmodels.DatabaseAssistant(db_string,dbbindkey,application_name)#, upload_folder=uploadfolder)

        tablenames,columnnames=DBA.getTableAndColumnNames()

        return self.render("projects/create_table.html",
                               tablenames=tablenames,
                               columnnames=columnnames,
                               pname=application_name)


        # return newtable(application_name)#self.render('analytics_index.html')

    @expose("/admin/createtable", methods=['GET', 'POST'])
    def createtable(self):
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)
        # create a new table either from scratch or from an existing csv
        tablenames, columnnames = DBA.getTableAndColumnNames()
        success = 0
        ret = ""

        # check for no table name
        if request.form.get("newtablename") == "":
            success = 0
            ret = "Enter table name"

        # check for existing table with this name
        elif request.form.get("newtablename") in tablenames:
            success = 0
            ret = "Table " + request.form.get("newtablename") + " already exists, try a new name"

        # check whether this should be an empty table or from existing data
        elif request.form.get("source") == "emptytable":
            success, ret = DBA.createEmptyTable(request.form.get("newtablename"))

        elif 'file' not in request.files:
            # check if the post request has the file part
            print('No file found')
            success = 0
            ret = "No file part, contact admin"

        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                success = 0
                ret = 'No selected file.'

            elif file:  # and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
                success, ret = DBA.createTableFromCSV(os.path.join(DBA.uploadfolder, filename),
                                                      request.form.get("newtablename"))

        if success == 1:
            # todo: this does not work on the fly
            add_single_view(request.form.get("newtablename"),application_name)
            return self.render("projects/create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   message="Table " +
                                           request.form.get("newtablename") + " created successfully!\n" + ret,
                                   pname=application_name)

        else:
            return self.render("projects/create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   error="Creation of table " + request.form.get("newtablename") +
                                         " failed!<br/>Error: " + ret,
                                   pname=application_name)

    @expose('/admin/newcolumn')
    def newcolumn(self):
        rule = str.split(str(request.url_rule),'/')
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        tablename=rule[3]

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        tablenames, columnnames = DBA.getTableAndColumnNames()

        lstofdatatypes = listOfColumnTypesByName


        return self.render("projects/add_column.html",
                               tablename=tablename, appname=application_name,
                               tablenames=tablenames,
                               listofdatatypes=lstofdatatypes,
                               columnnames=columnnames,
                               pname=application_name)

    @expose('/upload')
    def upload(self,msg="", err=""):
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


        tablenames, columnnames = DBA.getTableAndColumnNames()
        return self.render("projects/upload_table.html",
                               tablenames=tablenames,
                               message=msg,
                               error=err,
                               pname=application_name)

    @expose('/download')
    def download(self):
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


        tablenames, columnnames = DBA.getTableAndColumnNames()

        return self.render("projects/download_table.html",
                               tablenames=tablenames, columnnames=columnnames,
                               pname=application_name)

    @expose('/deletetable')
    def deletetable(self):
        rule = str.split(str(request.url_rule),'/')
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        tablename=rule[3]

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        # admin_pages_setup()
        # DBA.deleteTable(tablename)
        # DBA.DBE.refresh()
        return 'feature currently disabled' #redirect("/projects/" + application_name + "/admin/")

    @expose('/cleartable')
    def cleartable(self):
        rule = str.split(str(request.url_rule),'/')
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        tablename=rule[3]
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        DBA.clearTable(tablename)
        return redirect("/projects/" + application_name + "/admin/")


@app.context_processor
def inject_paths():
    return dict(iaas_url=dbconfig.iaas_route,
                dbas_url=dbconfig.dbas_route,
                LDAPUser=iaasldap.LDAPUser())

# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        # if not login.current_user.is_authenticated:
        if not current_user.is_authenticated:
            return "user not authenticatedr" #edirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    # @expose('/login/', methods=('GET', 'POST'))
    # def login_view(self):
    #     # handle user login
    #     form = LoginForm(request.form)
    #     if helpers.validate_form_on_submit(form):
    #         user = form.get_user()
    #         login.login_user(user)
    #
    #     if login.current_user.is_authenticated:
    #         return redirect(url_for('.index'))
    #     link = '<p>Don\'t have an account? <a href="' + url_for(
    #         '.register_view') + '">Click here to register.</a></p>'
    #     self._template_args['form'] = form
    #     self._template_args['link'] = link
    #     return super(MyAdminIndexView, self).index()

    # @expose('/register/', methods=('GET', 'POST'))
    # def register_view(self):
    #     form = RegistrationForm(request.form)
    #     if helpers.validate_form_on_submit(form):
    #         user = User()
    #
    #         form.populate_obj(user)
    #         # we hash the users password to avoid saving it as plaintext in the db,
    #         # remove to use plain text:
    #         user.password = generate_password_hash(form.password.data)
    #
    #         db.session.add(user)
    #         db.session.commit()
    #
    #         login.login_user(user)
    #         return redirect(url_for('.index'))
    #     link = '<p>Already have an account? <a href="' + url_for(
    #         '.login_view') + '">Click here to log in.</a></p>'
    #     self._template_args['form'] = form
    #     self._template_args['link'] = link
    #     return super(MyAdminIndexView, self).index()

    # @expose('/logout/')
    # def logout_view(self):
    #     login.logout_user()
    #     return redirect(url_for('.index'))

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        current_user.uid_trim()
        # return db.session.query(User).get(user_id)

# Initialize flask-login
init_login()






# do this for each project:
# uses database to do this dynamically
# import dev
import re
from flask import Blueprint

# create the database assistant instance to deal with the main IAAS databases
# used to find list of all managed DBs
iaas_main_db = app.config['SQLALCHEMY_DATABASE_URI']



modules = []
dictline = []
# bind_line = []


dba = devmodels.DatabaseAssistant(iaas_main_db, "iaas", "iaas")

result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
                                                      ["project_display_name", "instance_identifier",
                                                       "svc_type_id",
                                                       "group_id"],
                                                      classes_loaded=False)

print("retrieving list of DBAS services available and adding to dictionary:")


'''checks the iaas db for dbas services and collects the db binds'''
def get_binds():
    class_db_dict = {}
    SQLALCHEMY_BINDS = {'iaas': '{}://{}:{}@{}/iaas'
        .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname)}
    db_list=[]

    for r in list_of_projects:
        if not(r[2] == '1' or r[2] == '4'):  # then this is a database project
            continue

        db_list.append(r[1])

        db_string = '{}://{}:{}@{}/{}'.format(dbconfig.db_engine,dbconfig.db_user,
                                                  dbconfig.db_password,
                                                  dbconfig.db_hostname,
                                                  r[1])
        SQLALCHEMY_BINDS["{}".format(r[1])] = db_string


        project_dba = devmodels.DatabaseAssistant(db_string, r[1], r[1])
        tns,cns = project_dba.getTableAndColumnNames()
        for t in tns:
            nm = line = re.sub('_', '', t.title())
            class_db_dict['cls_{}_{}'.format(r[1],t)] = r[1]

    return SQLALCHEMY_BINDS, class_db_dict, db_list

SQLALCHEMY_BINDS,class_db_dict,db_list = get_binds()



app.config['SQLALCHEMY_BINDS'] =SQLALCHEMY_BINDS

# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)




# region deal with the IAAS admin console

# import classes.iaas
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()
metadata = Base.metadata

# region iaas classes
class News(Base):
    __tablename__ = 'News'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    created_on = Column(Date)
    updated_on = Column(Date)


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    news_id = Column(ForeignKey(u'News.id'), index=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Integer)
    created_on = Column(Date)

    news = relationship(u'News')


class IaasEvents(Base):
    __tablename__ = 'iaas_events'

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    subtitle = Column(String(60))
    description = Column(String(255))
    room = Column(String(60))
    eventdate = Column(Date)
    starttime = Column(Time)
    endtime = Column(Time)


class PermittedSvc(Base):
    __tablename__ = 'permitted_svc'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    svc_id = Column(Integer)


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True)
    description = Column(String(250))


class Services(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Subscribers(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(60))


class SvcInstances(Base):
    __tablename__ = 'svc_instances'

    id = Column(Integer, primary_key=True)
    project_display_name = Column(String(30))
    instance_identifier = Column(String(70))
    svc_type_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)

# endregion
# Create admin
iaas_admin = admin.Admin(app, name='IAAS admin app', template_mode='foundation',
                         endpoint="admin",url="/admin",
                         base_template='my_master.html')


from flask_admin.menu import MenuLink as ML
# iaas_admin.add_links(ML('Test Internal Link', endpoint='applicationhome'),
#                      ML('Test External Link', url='http://python.org/'))
iaas_admin.add_links(ML('Application', endpoint='applicationhome'),
                     ML('New Table', url='/projects/iaas/admin/newtable'))

# Add views
iaas_admin.add_view(MyModelView(SvcInstances, db.session))
iaas_admin.add_view(MyModelView(Subscribers, db.session))
iaas_admin.add_view(MyModelView(News, db.session))
iaas_admin.add_view(MyModelView(Comment, db.session))


# endregion

import classes

def _add_a_view(proj_admin,c):
    proj_admin.add_view(MyModelView(c, db.session))

def add_collection_of_views(d, classesdict):
    proj_admin = admin.Admin(app, name='{} admin'.format(d),
                             template_mode='foundation',
                             endpoint=d,
                             url="/projects/{}".format(d),
                             base_template='my_master.html'
                             )
    proj_admin.add_menu_item(ML('New Table', url='/projects/{}/admin/newtable'.format(d),
                                category="actions"))
    proj_admin.add_links(ML('Application', url='/projects/{}/app'.format(d)))

    for c in class_db_dict:
        if d == class_db_dict[c]:
            print ('class {} is in db {}'.format(c, d))

            _add_a_view(proj_admin, classesdict[c])

def add_single_view(c,d):
    classesdict, my_db = classes.initialise(db_list)

    # iaas_admin = admin.Admin(app, name='{} admin'.format(d),
    #                          template_mode='foundation',
    #                          endpoint=d,
    #                          url="/projects/{}".format(d),
    #                          base_template='my_master.html'
    #                          )
    # iaas_admin.add_menu_item(ML('New Table', url='/projects/{}/admin/newtable'.format(d),
    #                             category="actions"))
    # iaas_admin.add_links(ML('Application', url='/projects/{}/app'.format(d)))


    print ('class {} is in db {}'.format(c, d))

    _add_a_view(iaas_admin, classesdict['cls_{}_{}'.format(d,c)])

def admin_pages_setup():
    classesdict, my_db = classes.initialise(db_list)

    binds = app.config['SQLALCHEMY_BINDS']
    for d in binds:
        print(d,binds[d])

        add_collection_of_views(d,classesdict)

admin_pages_setup()

# def build_sample_db():
#     """
#     Populate a small db with some example entries.
#     """
#
#     import random
#     import datetime
#
#     db.drop_all()
#     db.create_all()
#
#     # Create sample Users
#     first_names = [
#         'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
#         'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
#         'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
#     ]
#     last_names = [
#         'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
#         'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
#         'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
#     ]
#
#     user_list = []
#     for i in range(len(first_names)):
#         user = User()
#         user.first_name = first_names[i]
#         user.username = first_names[i].lower()
#         user.last_name = last_names[i]
#         user.email = user.username + "@example.com"
#         user_list.append(user)
#         db.session.add(user)
#
#     # Create sample Tags
#     tag_list = []
#     for tmp in ["YELLOW", "WHITE", "BLUE", "GREEN", "RED", "BLACK", "BROWN", "PURPLE", "ORANGE"]:
#         tag = Tag()
#         tag.name = tmp
#         tag_list.append(tag)
#         db.session.add(tag)
#
#     # Create sample Posts
#     sample_text = [
#         {
#             'title': "de Finibus Bonorum et Malorum - Part I",
#             'content': "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor \
#                         incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud \
#                         exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure \
#                         dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
#                         Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt \
#                         mollit anim id est laborum."
#         },
#         {
#             'title': "de Finibus Bonorum et Malorum - Part II",
#             'content': "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque \
#                         laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto \
#                         beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur \
#                         aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi \
#                         nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, \
#                         adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam \
#                         aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam \
#                         corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum \
#                         iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum \
#                         qui dolorem eum fugiat quo voluptas nulla pariatur?"
#         },
#         {
#             'title': "de Finibus Bonorum et Malorum - Part III",
#             'content': "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium \
#                         voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati \
#                         cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id \
#                         est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam \
#                         libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod \
#                         maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. \
#                         Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet \
#                         ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur \
#                         a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis \
#                         doloribus asperiores repellat."
#         }
#     ]
#
#     for user in user_list:
#         entry = random.choice(sample_text)  # select text at random
#         post = Post()
#         post.user = user
#         post.title = entry['title']
#         post.text = entry['content']
#         tmp = int(1000*random.random())  # random number between 0 and 1000:
#         post.date = datetime.datetime.now() - datetime.timedelta(days=tmp)
#         post.tags = random.sample(tag_list, 2)  # select a couple of tags at random
#         db.session.add(post)
#
#     # Create a sample Tree structure
#     trunk = Tree(name="Trunk")
#     db.session.add(trunk)
#     for i in range(5):
#         branch = Tree()
#         branch.name = "Branch " + str(i+1)
#         branch.parent = trunk
#         db.session.add(branch)
#         for j in range(5):
#             leaf = Tree()
#             leaf.name = "Leaf " + str(j+1)
#             leaf.parent = branch
#             db.session.add(leaf)
#
#     db.session.commit()
#     return

def run():
# if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = op.realpath(os.path.dirname(__file__))
    # database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    # if not os.path.exists(database_path):
    #     build_sample_db()

    # Start app
    app.run(debug=True)
