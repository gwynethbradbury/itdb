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

from jinja2 import TemplateNotFound
from flask import render_template, abort
import dbconfig

if dbconfig.test:
    from core.mock_access_helper import MockAccessHelper as AccessHelper
else:
    from core.access_helper import AccessHelper
AH = AccessHelper()

from main.sqla.core.iaasldap import LDAPUser as LDAPUser
current_user = LDAPUser()


import dev.models as devmodels


from core.email import send_email_simple as send_email

from werkzeug.utils import secure_filename
from datetime import datetime

# todo: move thissomewhere:
listOfColumnTypesByName = {"Integer": "INTEGER",
                           "String": "VARCHAR",
                           "Characters": "CHARACTER",
                           "Bool": "BOOLEAN",
                           "Time stamp": "TIMESTAMP",
                           "Date": "DATE",
                           "Time": "TIME",
                           "Really long string": "CLOB",
                           "Small integer": "SMALLINT",
                           "Real": "REAL",
                           "Float": "FLOAT",
                           "Double": "DOUBLE",
                           "Precision": "PRECISION",
                           "Text block": "TEXT"}
DataTypeNeedsN = {"INTEGER": False,
                  "VARCHAR": True,
                  "CHARACTER": True,
                  "BOOLEAN": False,
                  "TIMESTAMP": False,
                  "DATE": False,
                  "TIME": False,
                  "CLOB": True,
                  "SMALLINT": False,
                  "REAL": False,
                  "FLOAT": True,
                  "DOUBLE": False,
                  "PRECISION": False,
                  "TEXT": False}
listOfColumnTypesByDescriptor = dict(reversed(item) for item in listOfColumnTypesByName.items())




# create views:



def set_views(app):
    dbconfig.trigger_reload = False
    file_object = open( os.path.abspath(os.path.dirname(__file__))+'/reload.py', 'w')
    file_object.write('reload=True\n')
    file_object.write("# " + str(datetime.utcnow()) + "\n")
    file_object.close()

    import reload as reload

    @app.context_processor
    def inject_paths():
        return dict(iaas_url=dbconfig.iaas_route,
                    dbas_url=dbconfig.dbas_route,
                    LDAPUser=LDAPUser())

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

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)

        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        tablenames, columnnames = DBA.getTableAndColumnNames()
        if not tablenames == []:
            return redirect("/projects/{}/{}/admin/newtable".format(application_name, tablenames[0]))

        return render_template("projects/create_table.html",
                               tablenames=tablenames,
                               columnnames=columnnames,
                               pname=application_name)


    # adding a column to an existing table
    # todo: unfinished
    @app.route("/projects/<application_name>/admin/newcolumn")
    # @app.route("/projects/<application_name>/<tablename>/admin/newcolumn")
    def newcolumn(application_name, tablename=""):
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        tablenames, columnnames = DBA.getTableAndColumnNames()

        listofdatatypes = listOfColumnTypesByName

        if not tablenames == []:
            return redirect("/projects/{}/{}/admin/newcolumn".format(application_name, tablenames[0]))
        return render_template("projects/add_column.html",
                               tablename=tablename, appname=application_name,
                               tablenames=tablenames,
                               listofdatatypes=listofdatatypes,
                               columnnames=columnnames,
                               pname=application_name)

    #
    # @app.route("/projects/<application_name>/admin/<tablename>/createcolumn", methods=['GET', 'POST'])
    # @app.route("/projects/<application_name>/<tablename>/admin/createcolumn", methods=['GET', 'POST'])
    # def createcolumn(application_name, tablename):
    #     if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
    #         return abort(401)
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey = "project_" + application_name + "_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)
    #
    #     # create a new table either from scratch or from an existing csv
    #     tablenames, columnnames = DBA.getTableAndColumnNames(tablename)
    #     success = 0
    #     ret = ""
    #
    #     # check for no column name
    #     if request.form.get("newcolumnname") == "":
    #         success = 0
    #         ret = "Enter column name"
    #
    #     # check for existing table with this name
    #     elif request.form.get("newcolumnname") in columnnames[0]:
    #         success = 0
    #         ret = "Column " + request.form.get("newcolumnname") + " already exists, try a new name"
    #
    #     # todo: get argument n which islength of string etc, default is curretly 10
    #     ret, success = DBA.addColumn(tablename, request.form.get("newcolumnname"), request.form.get("datatypes"))
    #
    #     # redirects to the same page
    #     if success == 1:
    #         return render_template("projects/add_column.html",
    #                                tablenames=tablenames, columnnames=columnnames,
    #                                message="Column " +
    #                                        request.form.get("newcolumnname") + " created successfully!\n" + ret,
    #                                pname=application_name)
    #
    #     else:
    #         return render_template("projects/add_column.html",
    #                                tablenames=tablenames, columnnames=columnnames,
    #                                error="Creation of column " + request.form.get("newcolumnname") +
    #                                      " failed!<br/>Error: " + ret,
    #                                pname=application_name)

    # delete a whole table
    @app.route("/projects/<application_name>/admin/deletetable/<tablename>")
    def deletetable(application_name, tablename):
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        DBA.deleteTable(tablename)
        # DBA.DBE.refresh()
        return redirect("/projects/" + application_name + "/admin/")

    # clear all entries from a table
    @app.route("/projects/<application_name>/admin/cleartable/<tablename>")
    def cleartable(application_name, tablename):
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

    # endregion


    # region OTHER OUTES


    '''generate a blank cv given an existing table'''
    @app.route("/projects/<application_name>/genblankcsv", methods=['GET', 'POST'])
    @app.route("/projects/<application_name>/<tablename>/genblankcsv", methods=['GET', 'POST'])
    def genblankcsv(application_name,tablename=""):
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
                                          upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

        if tablename=="":
            try:
                return DBA.genBlankCSV(request.form.get("tablename"))
            except Exception as e:
                print(e)
        else:

            try:
                return DBA.genBlankCSV(tablename)
            except Exception as e:
                print(e)



        return redirect("/projects/" + application_name )

    ''' renders the upload form '''
    @app.route("/projects/<application_name>/admin/uploaddata")
    def uploaddata(application_name, msg="", err=""):
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
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

    # serves the data given the response from the download form
    @app.route("/projects/<application_name>/admin/servedata", methods=['GET', 'POST'])
    @app.route("/projects/<application_name>/<tablename>/servedata", methods=['GET', 'POST'])
    def servedata(application_name,tablename=""):
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
                                          upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

        # serves the requested data
        # todo: problems with filename and extension

        if tablename=="":
            try:
                return DBA.serveData(F=request.form,
                                     ClassName=str(
                                         request.form.get("tablename")))  # os.path.abspath(os.path.dirname(__file__)))
            except Exception as e:
                print(str(e))
        else:
            try:
                return DBA.serveData(F=request.form,
                                     ClassName=str(tablename))  # os.path.abspath(os.path.dirname(__file__)))
            except Exception as e:
                print(str(e))

        return redirect("/projects/" + application_name + "/admin/")

    # endregion

    '''adds the data from the CSV to an existing table'''
    @app.route("/projects/<application_name>/admin/uploaddatafrom", methods=['GET', 'POST'])
    def uploaddatafrom(application_name):
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
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

        return redirect("/projects/" + application_name + "/admin/")





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


    '''relationship builder'''
    @app.route("/projects/<application_name>/admin/relationshipbuilder", methods=['GET', 'POST'])
    def buildrelationship(application_name):

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)

        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        tablenames, columnnames = DBA.getTableAndColumnNames()
        if not tablenames == []:
            return redirect("/projects/{}/{}/admin/relationshipbuilder".format(application_name, tablenames[0]))



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



# Create customized model view class
class MyModelView(ModelView,):
    current_user = current_user

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

    @expose("/admin/relationshipbuilder", methods=['GET', 'POST'])
    def relationshipbuilder(self):
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

        if request.method == 'POST':
            fromtbl = request.form.get("fromtblnames")
            fromcol = request.form.get("fromcolnames_"+fromtbl)
            totbl=request.form.get("totblnames")
            tocol = request.form.get("tocolnames_"+totbl)
            k = request.form.get("keyname")
            success, ret = DBA.createOneToOneRelationship(fromtbl,
                                                          fromcol,
                                                          totbl,
                                                          tocol,
                                                          k)
            return self.render('/')
        else:


            tablenames, columnnames = DBA.getTableAndColumnNames()
            return self.render("projects/project_relationship_builder.html",tablenames=tablenames,columnnames=columnnames)

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

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
                                          upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

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
                file.save(os.path.join(DBA.upload_folder, dt + '_' + filename))
                success, ret = DBA.createTableFromCSV(os.path.join(DBA.upload_folder, dt + '_' + filename),
                                                      request.form.get("newtablename"))

        if success == 1:
            # todo: this does not work on the fly
            from main.sqla.app import DBAS as DBAS
            DBAS.setup()
            self.trigger_reload()
            return self.render("projects/create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   message="Table " +
                                           request.form.get("newtablename") + " created successfully!\n" + ret +
                                           "\nBUT app needs to reload",
                                   pname=application_name)

        else:
            return self.render("projects/create_table.html",
                                   tablenames=tablenames, columnnames=columnnames,
                                   error="Creation of table " + request.form.get("newtablename") +
                                         " failed!<br/>Error: " + ret,
                                   pname=application_name)

    @expose('/admin/reloadapp')
    def trigger_reload(self):
        dbconfig.trigger_reload = False
        file_object = open( os.path.abspath(os.path.dirname(__file__))+'/reload.py', 'w')
        file_object.write('True\n')
        file_object.write("# " + str(datetime.utcnow()) + "\n")
        file_object.close()
        return 'reloaded'


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

    @expose('/admin/removecolumn')
    def removecolumn(self):
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

        tablenames, columnnames = DBA.getTableAndColumnNames(tablename)

        lstofdatatypes = listOfColumnTypesByName


        return self.render("projects/rem_column.html",
                               tablename=tablename, appname=application_name,
                               tablenames=tablenames,
                               listofdatatypes=lstofdatatypes,
                               columnnames=columnnames[0],
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

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
                                          upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

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
        DBA.deleteTable(tablename)
        # DBA.DBE.refresh()
        # todo: fix this

        from main.sqla.app import DBAS
        DBAS.setup()
        self.trigger_reload()

        # return '{}: table {} deleted from app but app needs to reload'.format(application_name,tablename)
        return redirect("/projects/" + application_name)

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

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)

        DBA.clearTable(tablename)
        return redirect("/projects/" + application_name + "/" + tablename)

    # @app.route("/projects/<application_name>/admin/<tablename>/createcolumn", methods=['GET', 'POST'])
    @expose('/admin/createcolumn', methods=['GET', 'POST'])
    def createcolumn(self):
        rule = str.split(str(request.url_rule), '/')
        application_name = rule[2]
        tablename = rule[3]

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
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

        listofdatatypes = listOfColumnTypesByName
        # redirects to the same page
        if success == 1:
            from main.sqla.app import DBAS
            self.trigger_reload()
            return self.render("projects/add_column.html",
                               tablenames=tablenames, columnnames=columnnames,
                               message="Column " +
                                       request.form.get("newcolumnname") + " created successfully!\n" + ret,
                               listofdatatypes=listofdatatypes,
                               pname=application_name)

        else:
            return self.render("projects/add_column.html",
                               tablenames=tablenames, columnnames=columnnames,
                               error="Creation of column " + request.form.get("newcolumnname") +
                                     " failed!<br/>Error: " + ret,
                               listofdatatypes=listofdatatypes,
                               pname=application_name)

    @expose('/admin/remcolumn', methods=['GET', 'POST'])
    def remcolumn(self):

        rule = str.split(str(request.url_rule), '/')
        application_name = rule[2]
        tablename = rule[3]

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
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
        if request.form.get("colnames") == "":
            success = 0
            ret = "Select column"

        # check for existing table with this name
        elif request.form.get("colnames") in columnnames[0]:
            success = 0
            ret, success = DBA.remColumn(tablename, request.form.get("colnames"))

        else:
            ret="could not find column " + request.form.get("colnames")
            success=0

        # redirects to the same page
        if success == 1:
            # todo: fixthe following

            from main.sqla.app import DBAS

            # return "{}: column {} removed from table {} but app needs to be reloaded to proceed"\
            #     .format(application_name,request.form.get("colnames"),tablename)
            self.trigger_reload()

            return self.render("projects/rem_column.html",
                               columnnames=columnnames[0],
                               tablename=tablename, appname=application_name,
                               message="Column " +
                                       request.form.get("colnames") + " removed successfully!\n" + ret,
                               pname=application_name)

        else:
            return self.render("projects/rem_column.html",
                               columnnames=columnnames[0],
                               tablename=tablename, appname=application_name,
                               error="Removal of column " + request.form.get("colnames") +
                                     " failed!<br/>Error: " + ret,
                               pname=application_name)


