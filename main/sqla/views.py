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

# todo: move thissomewhere:
from dev.models import listOfColumnTypesByName

import pymysql
def TriggerReload(application_name):
    print "Triggering reload: " + application_name
    # update svc_instance set schema_id=schema_id+1 where project_display_name=self-config['db']

    try:
        connection = pymysql.connect(host=dbconfig.db_hostname,
                                     user=dbconfig.db_user,
                                     passwd=dbconfig.db_password,
                                     db=dbconfig.db_name)
        query = "update svc_instances set schema_id=schema_id+1 where instance_identifier={};".format(
            str(application_name))
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
    except Exception as e:
        print(e)
    finally:
        connection.close()
    return 'reloaded'







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

    @app.context_processor
    def inject_paths():
        return dict(iaas_url=dbconfig.iaas_route,
                    dbas_url=dbconfig.dbas_route,
                    LDAPUser=LDAPUser(),
                    iaas_db_name=dbconfig.db_name
                    )

    @app.route('/account', methods=["GET", "POST"])
    def account():
        if current_user.is_authenticated():
            instances=[]
            groups = current_user.get_groups()
            for g in groups:
                instances.append(AH.get_projects_for_group(g))


            from core.auth.forms import ChangePWForm
            form = ChangePWForm()
            if form.validate_on_submit():
                user=current_user
                # user = User(username=form.username.data,
                #             email=form.username.data,
                #             password=form.password.data)
                success,ret = current_user.change_password(form.oldpw,form.password,form.password2)
                if success:
                    flash(ret,category='message')
                else:
                    flash(ret,category="error")

                # return redirect(url_for('index'))

            try:
                return render_template("account.html",groups=groups,instances=instances, form=form)
            except TemplateNotFound:
                abort(404)

        else:
            abort(403)


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




    @app.route('/<page>')
    def show(page):
        try:
            return render_template("%s.html" % page)
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

    # endregion

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


# Create customized model view class
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
        # print "VIEW CREATED FOR " + str(self.tablename)
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

    @expose('/admin/reloadapp')
    def trigger_reload(self):
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        return TriggerReload(self.svc_group)


    @expose('/admin/newcolumn', methods=['GET', 'POST'])
    def newcolumn(self):
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        colname = request.form.get("newcolumnname")
        coltype = request.form.get("datatypes")
        columnnames = [i[0] for i in self.get_column_names(self.scaffold_list_columns(), [])]

        '''respond to form'''
        if request.method == 'POST':
            success = 1
            ret = ""

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
                flash(ret, 'info')
                return self.render("projects/add_column.html",
                                   message="Column " +
                                           request.form.get("newcolumnname") + " created successfully!\n" + ret,
                                   listofdatatypes=listofdatatypes,
                                   pname=self.svc_group)

            else:
                flash(ret, 'error')
                return self.render("projects/add_column.html",
                                   error="Creation of column " + request.form.get("newcolumnname") +
                                         " failed!<br/>Error: " + ret,
                                   listofdatatypes=listofdatatypes,
                                   pname=self.svc_group)

        else:
            '''render form'''
            lstofdatatypes = listOfColumnTypesByName


            return self.render("projects/add_column.html",
                               appname=self.svc_group,
                                   listofdatatypes=lstofdatatypes,
                                   pname=self.svc_group)

    @expose('/admin/removecolumn', methods=['GET', 'POST'])
    def removecolumn(self):

        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        colname = request.form.get("newcolumnname")
        coltype = request.form.get("datatypes")
        columnnames = [i[0] for i in self.get_column_names(self.scaffold_list_columns(), [])]

        '''respond to form'''
        if request.method == 'POST':

            colname = request.form.get("colnames")

            success = 0
            ret = ""

            # check for no column name
            if colname == "":
                success = 0
                ret = "Select column"

            # check for existing table with this name
            elif not colname in columnnames:
                ret = "failed, could not find column in table {}".format(str(self.tablename))
                success = 0

            else:
                query = "ALTER TABLE {} DROP COLUMN {};".format(str(self.tablename), colname)
                res, ret, success = self.db_details.ConnectAndExecute(query)

            # redirects to the same page
            if success == 1:
                self.trigger_reload()
                flash(message="Column " + request.form.get("colnames") + " removed successfully!\n" + ret,
                      category="info")
                return self.render("projects/rem_column.html",
                                   columnnames=columnnames,
                                   pname=self.svc_group)

            else:
                flash(message = "Removal of column " + request.form.get("colnames") + " failed!<br/>Error: " + ret,
                      category="error")
                return self.render("projects/rem_column.html",
                                   columnnames=columnnames,
                                   error="Removal of column " + request.form.get("colnames") +
                                         " failed!<br/>Error: " + ret,
                                   pname=self.svc_group)

        else:
            '''render form'''

            return self.render("projects/rem_column.html",
                                   tablename=self.tablename, appname=self.svc_group,
                                   columnnames=columnnames,
                                   pname=self.svc_group)

    @expose('/admin/deletetable')
    def deletetable(self):
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
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

