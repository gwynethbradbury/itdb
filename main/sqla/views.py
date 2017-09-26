import os
import os.path as op

from flask import Flask, redirect, url_for, request, flash
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


#
# def get_db_creds():
#         import dev.models as devmodels
#         import dbconfig
#         iaas_main_db ='{}://{}:{}@{}/{}'\
#           .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password, dbconfig.db_hostname,dbconfig.db_name)
#
#         dba = devmodels.DatabaseAssistant(iaas_main_db, "iaas", "iaas")
#
#         result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
#                                                               ["project_display_name", "instance_identifier",
#                                                                "svc_type_id",
#                                                                "group_id","schema_id","priv_user","priv_pass","db_ip"],
#                                                               classes_loaded=False)
#         schema_ids={}
#         priv_users={}
#         priv_pass={}
#         db_ip={}
#         for r in list_of_projects:
#             if not(r[2] == '1' or r[2] == '4'):  # then this is a database project
#                 continue
#             schema_ids[r[1]] = r[4]
#             priv_users[r[1]] = r[5]
#             priv_pass[r[1]] = r[6]
#             db_ip[r[1]] = r[7]
#         return priv_users,priv_pass,db_ip
#
#
# db_user,db_pass,db_hostname = get_db_creds()
 
# todo: move thissomewhere:
from dev.models import listOfColumnTypesByName




# create views:

def set_nextcloud_views(app, names,nc_identifiers):
    @app.route('/nextcloud/<nc_identifier>')
    def show_cloud_details(nc_identifier):
        if nc_identifier in nc_identifiers:
            nc_name = names[nc_identifiers.index(nc_identifier)]
            return render_template("nextcloud_instance.html", nc_name=nc_name,nc_identifier=nc_identifier)
        else:
            flash("Not a valid nextcloud name.",category="error")
            return abort(404)


def set_webapp_views(app):
    pass

def set_views(app):
#    dbconfig.trigger_reload = False
#    file_object = open( os.path.abspath(os.path.dirname(__file__))+'/reload.py', 'w')
#    file_object.write('reload=True\n')
#    file_object.write("# " + str(datetime.utcnow()) + "\n")
#    file_object.close()
#    import reload as reload
    @app.context_processor
    def inject_paths():
        return dict(iaas_url=dbconfig.iaas_route,
                    dbas_url=dbconfig.dbas_route,
                    LDAPUser=LDAPUser(),
                    iaas_db_name=dbconfig.db_name
                    )

    # region Flask views
    @app.route('/group/<group_name>')
    def show_groups(group_name):
        if current_user.has_role(group_name) or current_user.has_role('superusers'):
            instances = AH.get_projects_for_group(group_name)
            try:
                return render_template("groupprojects.html",groupname=group_name,instances=instances)
            except TemplateNotFound:
                abort(404)
        else:
            abort(403)


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

    @app.errorhandler(403)
    def page_not_found(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404


    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('500.html'), 500


    @app.errorhandler(401)
    def page_not_found(e):
        return render_template('401.html'), 401



    # adding a column to an existing table
    # todo: unfinished
    @app.route("/projects/<svc_group>/newcolumn")
    # @app.route("/projects/<application_name>/<tablename>/newcolumn")
    def newcolumn(svc_group, tablename=""):
        if not current_user.is_authorised(service_name=applicsvc_groupation_name, is_admin_only_page=True):
            return abort(403)

        dbbindkey = "project_" + svc_group + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, svc_group)  # , upload_folder=uploadfolder)

        tablenames, columnnames = DBA.getTableAndColumnNames()

        listofdatatypes = listOfColumnTypesByName

        if not tablenames == []:
            return redirect("/projects/{}/{}/newcolumn".format(svc_group, tablenames[0]))
        return render_template("projects/add_column.html",
                               tablename=tablename, appname=svc_group,
                               tablenames=tablenames,
                               listofdatatypes=listofdatatypes,
                               columnnames=columnnames,
                               pname=svc_group)

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
    @app.route("/projects/<svc_group>/admin/deletetable/<tablename>")
    def deletetable(svc_group, tablename):
        if not current_user.is_authorised(service_name=svc_group, is_admin_only_page=True):
            return abort(403)

        dbbindkey = "project_" + svc_group + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, svc_group)  # , upload_folder=uploadfolder)

        DBA.deleteTable(tablename)
        self.trigger_reload()
        # DBA.DBE.refresh()
        return redirect("/projects/" + svc_group + "/admin/")

    # clear all entries from a table
    @app.route("/projects/<svc_group>/admin/cleartable/<tablename>")
    def cleartable(svc_group, tablename):
        if not current_user.is_authorised(service_name=svc_group, is_admin_only_page=True):
            return abort(403)

        dbbindkey = "project_" + svc_group + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, svc_group)  # , upload_folder=uploadfolder)

        DBA.clearTable(tablename)
        return redirect("/projects/" + svc_group + "/admin/")

    # endregion


    # region OTHER OUTES


    '''generate a blank cv given an existing table'''
    @app.route("/projects/<svc_group>/genblankcsv", methods=['GET', 'POST'])
    @app.route("/projects/<svc_group>/<tablename>/genblankcsv", methods=['GET', 'POST'])
    def genblankcsv(svc_group,tablename=""):
        if not current_user.is_authorised(service_name=svc_group, is_admin_only_page=True):
            return abort(403)

        dbbindkey = "project_" + svc_group + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, svc_group,
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



        return redirect("/projects/" + svc_group )


    # ''' renders the upload form '''
    # @app.route("/projects/<application_name>/admin/uploaddata")
    # def uploaddata(application_name, msg="", err=""):
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
    #     tablenames, columnnames = DBA.getTableAndColumnNames()
    #     return render_template("projects/upload_table.html",
    #                            tablenames=tablenames,
    #                            message=msg,
    #                            error=err,
    #                            pname=application_name)

    # serves the data given the response from the download form
    # @app.route("/projects/<application_name>/admin/servedata", methods=['GET', 'POST'])
    # @app.route("/projects/<application_name>/<tablename>/servedata", methods=['GET', 'POST'])
    # def servedata(application_name,tablename=""):
    #     if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
    #         return abort(401)
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey = "project_" + application_name + "_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
    #                                       upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')
    #
    #     # serves the requested data
    #     # todo: problems with filename and extension
    #     tablename = request.form.get("tablename")
    #
    #     if tablename=="":
    #         try:
    #             return DBA.serveData(F=request.form,
    #                                  ClassName=str(
    #                                      request.form.get("tablename")))  # os.path.abspath(os.path.dirname(__file__)))
    #         except Exception as e:
    #             print(str(e))
    #     else:
    #         try:
    #             return DBA.serveData(F=request.form,
    #                                  ClassName=str(tablename))  # os.path.abspath(os.path.dirname(__file__)))
    #         except Exception as e:
    #             print(str(e))
    #
    #     return redirect("/projects/" + application_name + "/"+application_name+"ops")

    # endregion

    # '''adds the data from the CSV to an existing table'''
    # @app.route("/projects/<application_name>/admin/uploaddatafrom", methods=['GET', 'POST'])
    # def uploaddatafrom(application_name):
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
    #     if request.method == 'POST':
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             return uploaddata(err="No file part")
    #         else:
    #             file = request.files['file']
    #             # if user does not select file, browser also
    #             # submit a empty part without filename
    #             if file.filename == '':
    #                 return uploaddata(err="No selected file")
    #             if file:  # and allowed_file(file.filename):
    #                 filename = secure_filename(file.filename)
    #                 dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
    #                 file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
    #                 tablename = str(request.form.get("tablename"))
    #
    #                 success, ret = DBA.createTableFrom(os.path.join(DBA.uploadfolder, dt + '_' + filename),
    #                                                    tablename)
    #                 if success:
    #                     ret = "Success, data added to table: %s%s%s" % (tablename, "<br/>", ret)
    #                     return uploaddata(msg=ret)
    #                 else:
    #                     return uploaddata(err=ret)
    #
    #     return redirect("/projects/" + application_name + "/admin/")





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



    # '''relationship builder'''
    # @app.route("/projects/<application_name>/admin/relationshipbuilder", methods=['GET', 'POST'])
    # def buildrelationship(application_name):
    #
    #     if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
    #         return abort(401)
    #
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey = "project_" + application_name + "_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)
    #
    #     tablenames, columnnames = DBA.getTableAndColumnNames()
    #     if not tablenames == []:
    #         return redirect("/projects/{}/{}/admin/relationshipbuilder".format(application_name, tablenames[0]))



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

from flask_admin.model.template import EndpointLinkRowAction, LinkRowAction

class MyModelView(ModelView):
    can_export=True
    # export_types = ['csv','xls','json']
    # column_extra_row_actions = [
    #     LinkRowAction('glyphicon glyphicon-off', 'http://direct.link/?id={row_id}'),
    #     # EndpointLinkRowAction('glyphicon glyphicon-test', '/admin/createcolumn')
    # ]

    def __init__(self,
                 c,
                 session, name,databasename,db_string,
                 endpoint, svc_group, db_details,
                 category = "Tables"):

        super(MyModelView, self).__init__(c,session, name=name,endpoint=endpoint,category=category)
        self.tablename = c.__table__
        print "VIEW CREATED FOR " + str(self.tablename)
        self.svc_group=svc_group
        self.db_string = db_string
        self.db_details = db_details

    '''test that this project is accessible to the user'''
    def is_accessible(self):
        if not current_user.is_active:
            return False
        if current_user.is_authorised(self.svc_group):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            abort(403)



    # @expose('/')
    # def index(self):
        # rule = str.split(str(request.url_rule),'/')
        # current_url = str.split(self.admin.url,'/')
        # application_name = current_url[2]
        # return self.render("admin/index.html",dbinfo="hihihihi")


    # @expose("/admin/relationshipbuilder", methods=['GET', 'POST'])
    # def relationshipbuilder(self):
    #     rule = str.split(str(request.url_rule),'/')
    #     current_url = str.split(self.admin.url,'/')
    #     application_name = current_url[2]
    #     tablename=rule[3]
    #
    #     if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
    #         return abort(401)
    #
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey = "project_" + application_name + "_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)
    #
    #     if request.method == 'POST':
    #         try:
    #             fromtbl = request.form.get("fromtblnames")
    #             fromcol = request.form.get("fromcolnames_"+fromtbl)
    #             totbl=request.form.get("totblnames")
    #             tocol = request.form.get("tocolnames_"+totbl)
    #             k = request.form.get("keyname")
    #             success, ret = DBA.createOneToOneRelationship(fromtbl,
    #                                                           fromcol,
    #                                                           totbl,
    #                                                           tocol,
    #                                                           k)
    #         except Exception as E:
    #             success = 0
    #             ret = "One or more inputs is missing or incomplete."
    #
    #         if success:
    #             flash(ret,"info")
    #         else:
    #             flash(ret,"error")
    #
    #
    #     tablenames, columnnames = DBA.getTableAndColumnNames()
    #     keys = DBA.getExistingKeys(True,True)
    #
    #     return self.render("projects/project_relationship_builder.html",
    #                        tablenames=tablenames,columnnames=columnnames,
    #                        keys=keys)

    # @expose('/admin/newtable')
    # def newtable(self):
    #     current_url = str.split(self.admin.url,'/')
    #     application_name = current_url[2]
    #
    #     if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
    #         return abort(401)
    #
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey="project_"+application_name+"_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string,dbbindkey,application_name)#, upload_folder=uploadfolder)
    #
    #     tablenames,columnnames=DBA.getTableAndColumnNames()
    #
    #     return self.render("projects/create_table.html",
    #                            tablenames=tablenames,
    #                            columnnames=columnnames,
    #                            pname=application_name)
    #
    #
    #     # return newtable(application_name)#self.render('analytics_index.html')

    # @expose("/admin/createtable", methods=['GET', 'POST'])
    # def createtable(self):
    #     current_url = str.split(self.admin.url,'/')
    #     application_name = current_url[2]
    #     if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
    #         return abort(401)
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey = "project_" + application_name + "_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
    #                                       upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')
    #
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
    #             file.save(os.path.join(DBA.upload_folder, dt + '_' + filename))
    #             success, ret = DBA.createTableFromCSV(os.path.join(DBA.upload_folder, dt + '_' + filename),
    #                                                   request.form.get("newtablename"))
    #
    #     if success == 1:
    #         # todo: this does not work on the fly
    #         from main.sqla.app import DBAS as DBAS
    #         DBAS.setup()
    #         self.trigger_reload()
    #         return self.render("projects/create_table.html",
    #                                tablenames=tablenames, columnnames=columnnames,
    #                                message="Table " +
    #                                        request.form.get("newtablename") + " created successfully!\n" + ret +
    #                                        "\nBUT app needs to reload",
    #                                pname=application_name)
    #
    #     else:
    #         return self.render("projects/create_table.html",
    #                                tablenames=tablenames, columnnames=columnnames,
    #                                error="Creation of table " + request.form.get("newtablename") +
    #                                      " failed!<br/>Error: " + ret,
    #                                pname=application_name)

    @expose('/admin/reloadapp')
    def trigger_reload(self):
        import pymysql
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        print "Triggering reload: "+application_name
        # update svc_instance set schema_id=schema_id+1 where project_display_name=self-config['db']

        try:
            connection = pymysql.connect(host=dbconfig.db_hostname,
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=dbconfig.db_name)
            query = "update svc_instances set schema_id=schema_id+1 where instance_identifier={};".format(str(application_name))
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()
#        dbconfig.trigger_reload = False
#        file_object = open( os.path.abspath(os.path.dirname(__file__))+'/reload.py', 'w')
#        file_object.write('True\n')
#        file_object.write("# " + str(datetime.utcnow()) + "\n")
#        file_object.close()
        return 'reloaded'


    @expose('/admin/newcolumn')
    def newcolumn(self):

        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        lstofdatatypes = listOfColumnTypesByName


        return self.render("projects/add_column.html",
                           appname=self.svc_group,
                               listofdatatypes=lstofdatatypes,
                               pname=self.svc_group)

    @expose('/admin/removecolumn')
    def removecolumn(self):

        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        columnnames=[i[0] for i in self.get_column_names(self.scaffold_list_columns(),[])]


        return self.render("projects/rem_column.html",
                               tablename=self.tablename, appname=self.svc_group,
                               columnnames=columnnames,
                               pname=self.svc_group)


    # @expose('/upload')
    # def upload(self,msg="", err=""):
    #     current_url = str.split(self.admin.url,'/')
    #     application_name = current_url[2]
    #     if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
    #         return abort(401)
    #     db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
    #                                                      dbconfig.db_password,
    #                                                      dbconfig.db_hostname,
    #                                                      application_name)
    #     dbbindkey = "project_" + application_name + "_db"
    #
    #     DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
    #                                       upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')
    #
    #     tablenames, columnnames = DBA.getTableAndColumnNames()
    #     return self.render("projects/upload_table.html",
    #                            tablenames=tablenames,
    #                            message=msg,
    #                            error=err,
    #                            pname=application_name)
    #
    # @expose('/download')
    # def download(self):
    #     current_url = str.split(self.admin.url,'/')
    #     application_name = current_url[2]
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
    #     return self.render("projects/download_table.html",
    #                            tablenames=tablenames, columnnames=columnnames,
    #                            pname=application_name)

    @expose('/admin/deletetable')
    def deletetable(self):
        if not current_user.is_authorised(service_name=self.application_name, is_admin_only_page=True):
            return abort(403)

        dbbindkey = "project_" + self.svc_group + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, self.svc_group)  # , upload_folder=uploadfolder)

        # admin_pages_setup()
        DBA.deleteTable(self.tablename)
        # DBA.DBE.refresh()
        # todo: fix this

        # from app import DBAS
        # DBAS.setup()
        self.trigger_reload()

        # return '{}: table {} deleted from app but app needs to reload'.format(application_name,tablename)
        return redirect("/projects/" + self.svc_group)

    @expose('/admin/cleartable')
    def cleartable(self):

        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)
        dbbindkey = "project_" + self.svc_group + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, self.svc_group)

        DBA.clearTable(self.tablename)

        return redirect(url_for('index'))

    # @app.route("/projects/<application_name>/admin/<tablename>/createcolumn", methods=['GET', 'POST'])
    @expose('/admin/createcolumn', methods=['GET', 'POST'])
    def createcolumn(self):
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        colname=request.form.get("newcolumnname")
        coltype=request.form.get("datatypes")
        columnnames = [i[0] for i in self.get_column_names(self.scaffold_list_columns(), [])]


        # dbbindkey = "project_" + self.svc_group + "_db"
        # DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, self.svc_group)  # , upload_folder=uploadfolder)

        success = 1
        ret = ""
        columnnames = [i[0] for i in self.get_column_names(self.scaffold_list_columns(), [])]

        # check for no column name
        if request.form.get("newcolumnname") == "":
            success = 0
            ret = "Enter column name"

        # check for existing table with this name
        elif request.form.get("newcolumnname") in columnnames:
            success = 0
            ret = "Column " + request.form.get("newcolumnname") + " already exists, try a new name"

        elif colname in columnnames:
                ret = (colname + " already exists in table.")
                success = 0

        else:
            data_type_formatted = devmodels.desc2formattedtype(coltype, 100)

            query = "ALTER TABLE {} ADD COLUMN {} {};".format(str(self.tablename), colname, data_type_formatted)

            res, ret, success = self.db_details.ConnectAndExecute(query)




        listofdatatypes = listOfColumnTypesByName
        # redirects to the same page
        if success == 1:
            self.trigger_reload()
            flash(ret,'info')
            return self.render("projects/add_column.html",
                               message="Column " +
                                       request.form.get("newcolumnname") + " created successfully!\n" + ret,
                               listofdatatypes=listofdatatypes,
                               pname=self.svc_group)

        else:
            flash(ret,'error')
            return self.render("projects/add_column.html",
                               error="Creation of column " + request.form.get("newcolumnname") +
                                     " failed!<br/>Error: " + ret,
                               listofdatatypes=listofdatatypes,
                               pname=self.svc_group)

    @expose('/admin/remcolumn', methods=['GET', 'POST'])
    def remcolumn(self):
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        colname = request.form.get("colnames")

        success = 0
        ret = ""
        columnnames = [i[0] for i in self.get_column_names(self.scaffold_list_columns(), [])]

        # check for no column name
        if colname == "":
            success = 0
            ret = "Select column"

        # check for existing table with this name
        elif not colname in columnnames:
            ret="failed, could not find column in table {}".format(str(self.tablename))
            success=0

        else:
            query = "ALTER TABLE {} DROP COLUMN {};".format(str(self.tablename), colname)
            res,ret,success = self.db_details.ConnectAndExecute(query)


        # redirects to the same page
        if success == 1:
            self.trigger_reload()

            return self.render("projects/rem_column.html",
                               columnnames=columnnames,
                               message="Column " +
                                       request.form.get("colnames") + " removed successfully!\n" + ret,
                               pname=self.svc_group)

        else:
            return self.render("projects/rem_column.html",
                               columnnames=columnnames,
                               error="Removal of column " + request.form.get("colnames") +
                                     " failed!<br/>Error: " + ret,
                               pname=self.svc_group)


