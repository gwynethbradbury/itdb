import flask_login as login
from flask_admin.menu import MenuLink as ML

import classes
import dbconfig
import dev.models as devmodels
import views
import main.iaas as iaas

if dbconfig.test:
    from core.mock_access_helper import MockAccessHelper as AccessHelper
else:
    from core.access_helper import AccessHelper
AH = AccessHelper()

from flask_admin import BaseView, expose
from main.auth.iaasldap import LDAPUser as LDAPUser

current_user = LDAPUser()
from flask import abort, request, flash, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask_admin.base import Admin as Admin2
import pymysql

import importlib

from ..iaas.iaas import SvcInstance


class IPAddressView(BaseView):
    @expose('/')
    def index(self):
        return self.render('ip_addresses.html')

    @expose('/ports')
    def show_ports_in_use(self):
        return self.render('ports.html')


class DatabaseOps(BaseView):
    can_export = True

    def __init__(self, name, endpoint, database_name, db_string, svc_group=None,
                 menu_class_name=None, db=None, C=None, dbinfo=None):
        super(DatabaseOps, self).__init__(name,
                                          endpoint=endpoint,
                                          menu_class_name=menu_class_name)
        self.database_name = database_name
        self.db_string = db_string
        self.db = db
        self.classes = C
        self.dbinfo = dbinfo
        if svc_group is None:
            self.svc_group = self.dbinfo.svc_instance.instance_identifier
        else:
            self.svc_group=svc_group

    @expose('/')
    def index(self):
        return "DatabaseOps"  # self.render('analytics_index.html')

    @expose('/newtable', methods=['GET', 'POST'])
    def newtable(self):
        if not self.dbinfo.is_dynamic:
            return abort(404)
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        if request.method == 'GET':
            dbbindkey = "project_" + self.database_name + "_db"

            DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey,
                                              self.database_name)  # , upload_folder=uploadfolder)

            tablenames, columnnames = DBA.getTableAndColumnNames()

            return self.render("projects/create_table.html",
                               tablenames=tablenames,
                               columnnames=columnnames,
                               pname=self.database_name)

        dbbindkey = "project_" + self.database_name + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, self.database_name,
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
                extension = os.path.splitext(filename)[1]
                dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                file.save(os.path.join(DBA.upload_folder, dt + '_' + filename))
                if extension.lower() == ".csv":
                    success, ret = DBA.createTableFromCSV(os.path.join(DBA.upload_folder, dt + '_' + filename),
                                                          request.form.get("newtablename"))
                elif extension.lower() == ".xlsx" or extension.lower() == ".xls":
                    success, ret = DBA.createTableFromXLS(os.path.join(DBA.upload_folder, dt + '_' + filename),
                                                          request.form.get("newtablename"))

        if success:
            self.trigger_reload()
            flash("Table " + request.form.get("newtablename") + " created successfully!\n" + ret +
                  "\nBUT app needs to reload", category="info")
        else:
            flash("Creation of table " + request.form.get("newtablename") +
                  " failed!<br/>Error: " + ret, "error")

        return self.render("projects/create_table.html",
                           tablenames=tablenames,
                           columnnames=columnnames,
                           pname=self.database_name)

    @expose('/deletetable')
    def deletetable(self):
        if not self.dbinfo.is_dynamic:
            return abort(404)
        return "deletetable"  # self.render('analytics_index.html')

    @expose("/relationshipbuilder", methods=['GET', 'POST'])
    def relationshipbuilder(self):
        if not self.dbinfo.is_dynamic:
            return abort(404)
        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

        application_name = self.database_name
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)

        if request.method == 'POST':
            try:
                fromtbl = request.form.get("fromtblnames")
                fromcol = request.form.get("fromcolnames_" + fromtbl)
                totbl = request.form.get("totblnames")
                tocol = request.form.get("tocolnames_" + totbl)
                k = request.form.get("keyname")
                success, ret = DBA.createOneToOneRelationship(fromtbl,
                                                              fromcol,
                                                              totbl,
                                                              tocol,
                                                              k)
            except Exception as E:
                success = 0
                ret = "One or more inputs is missing or incomplete."

            if success:
                flash(ret, "info")
            else:
                flash(ret, "error")

        tablenames, columnnames = DBA.getTableAndColumnNames()
        keys = self.dbinfo.GetExistingKeys(True, True)

        return self.render("projects/project_relationship_builder.html",
                           tablenames=tablenames, columnnames=columnnames,
                           keys=keys)

    @expose('/upload', methods=['GET', 'POST'])
    def upload(self, msg="", err=""):
        application_name = self.dbinfo.svc_instance.instance_identifier
        if not current_user.is_authorised(service_name=application_name, is_admin_only_page=True):
            return abort(403)

        if request.method == 'GET':
            dbbindkey = "project_" + application_name + "_db"

            DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, application_name,
                                              upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

            tablenames, columnnames = DBA.getTableAndColumnNames()


        else:
            dbbindkey = "project_" + application_name + "_db"

            DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, application_name,
                                              upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

            # check if the post request has the file part
            if 'file' not in request.files:
                flash("No file part", category="error")
            elif request.form.get("submit")==u'Download Template':
                return DBA.genBlankCSV(tablename=request.form.get("tablename"))
            else:
                file = request.files['file']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    flash("No selected file", 'error')
                if file:  # and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                    file.save(os.path.join(DBA.upload_folder, dt + '_' + filename))
                    tablename = str(request.form.get("tablename"))

                    success, ret = DBA.createTableFrom(os.path.join(DBA.upload_folder, dt + '_' + filename),
                                                       tablename)
                    if success:
                        ret = "Success, data added to table: %s%s%s" % (tablename, "<br/>", ret)
                        flash(ret, 'info')
                    else:
                        flash(ret, 'error')

        tablenames, columnnames = DBA.getTableAndColumnNames()

        return self.render("projects/upload_table.html",
                           tablenames=tablenames,
                           message=msg,
                           error=err,
                           pname=application_name)

    @expose('/download', methods=['GET', 'POST'])
    def download(self):
        application_name = self.database_name
        if not current_user.is_authorised(service_name=application_name, is_admin_only_page=True):
            return abort(403)

        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, application_name,
                                          upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

        if request.method == 'POST':

            # serves the requested data
            # todo: problems with filename and extension
            tablename = request.form.get("tablename")
            if tablename == "":
                try:
                    return DBA.serveData(F=request.form,
                                         ClassName=str(
                                             request.form.get(
                                                 "tablename")),
                                         db=self.db,
                                         C=self.classes['cls_{}_{}'.format(application_name, str(
                                             tablename))])  # os.path.abspath(os.path.dirname(__file__)))
                except Exception as e:
                    print(str(e))
            else:
                try:
                    return DBA.serveData(F=request.form,
                                         ClassName=str(tablename),
                                         db=self.db,
                                         C=self.classes['cls_{}_{}'.format(application_name, str(
                                             tablename))])  # os.path.abspath(os.path.dirname(__file__)))
                except Exception as e:
                    print(str(e))

        tablenames, columnnames = DBA.getTableAndColumnNames()

        return self.render("projects/download_table.html",
                           tablenames=tablenames, columnnames=columnnames,
                           pname=application_name)

    def trigger_reload(self):

        import pymysql
        # current_url = str.split(self.admin.url, '/')
        # application_name = self.svc_group
        print "Triggering reload: " + self.svc_group
        # update svc_instance set schema_id=schema_id+1 where project_display_name=self-config['db']

        try:

            connection = pymysql.connect(host=dbconfig.db_hostname,
                                         user=dbconfig.db_user,
                                         passwd=dbconfig.db_password,
                                         db=dbconfig.db_name)

            with connection.cursor() as cursor:
                cursor.execute("update svc_instances set schema_id=schema_id+1 where instance_identifier=%s",
                               (str(self.svc_group),))
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()
        # dbconfig.trigger_reload = False
        # file_object = open(os.path.abspath(os.path.dirname(__file__)) + '/reload.py', 'w')
        # file_object.write('True\n')
        # file_object.write("# " + str(datetime.utcnow()) + "\n")
        # file_object.close()
        return 'reloaded'

    def is_accessible(self):
        if not current_user.is_active:
            return False

        # check project authentication
        if current_user.is_authorised(self.svc_group, is_admin_only_page=True):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            abort(403)


class MyStandardView(Admin2):
    dbquota = 0
    dbuseage = 0

    def __init__(self, app, name, endpoint, url, database_name, svc_group,
                 db_details,
                 template_mode='foundation',
                 base_template='my_master.html'):
        super(MyStandardView, self).__init__(app, name, template_mode=template_mode,
                                             url=url,
                                             endpoint=endpoint, base_template=base_template)
        self.svc_group = svc_group
        self.db_details = db_details

    @expose('/')
    def home(self):
        if current_user.is_authorised(self.svc_group, False):

            return self.render('index.html')
        else:
            abort(403)



    def add_hidden_view(self, view):
        """
            Add a view to the collection.

            :param view:
                View to add.
        """
        # Add to views
        self._views.append(view)

        # If app was provided in constructor, register view with Flask app
        if self.app is not None:
            self.app.register_blueprint(view.create_blueprint(self))

            # self._add_view_to_menu(view)
            # pass


GLOBAL_SQLALCHEMY_BINDS={}
# global_class_db_dict={}
# global_classes_dict={}

class MyIAASView(MyStandardView):
    def __init__(self, db_details,
                 app, name, template_mode, svc_group,
                 endpoint, url, base_template, database_name):
        super(MyIAASView, self).__init__(app=app, name=name, db_details=db_details, svc_group=svc_group,
                                         template_mode=template_mode,
                                         endpoint=endpoint, url=url, base_template=base_template,
                                         database_name=database_name)
        self.db_details = db_details

    def getIPAddresses(self):
        instances, msg, success = self.db_details.ConnectAndExecute(query="SELECT ip_address FROM database_instances "
                                                                          "UNION "
                                                                          "SELECT ip_address from nextcloud_instances "
                                                                          "UNION "
                                                                          "SELECT ip_address from web_apps "
                                                                          "UNION "
                                                                          "SELECT ip_address from virtual_machines;")
        return instances

    def getPorts(self):
        instances, msg, success = self.db_details.ConnectAndExecute(
            query="SELECT ip_address, port from database_instances;")
        return instances


class DBAS():


    def __init__(self, _app, _db):
        self.app = _app
        self.db = _db
        self.class_db_dict = {}

        # self.SQLALCHEMY_BINDS = {}
        self.SQLALCHEMY_BINDS2 = {}
        self.db_list = []
        self.db_strings = []
        self.db_identifiers = []
        self.schema_ids = {}
        self.db_details_dict = {}
        self.svc_groups = {}
        self.setup()

        views.set_views(self.app)

        self.get_services()
        for s in self.services:
            if s.instance_identifier==self.app.config['dispatched_app'] \
                    or s.instance_identifier.startswith('iaas')\
                    or self.app.config['dispatched_app']=='all':
                for d in s.databases:
                    self.SQLALCHEMY_BINDS2[d.database_name] = d.GetConnectionString()


        self.setup_pages()
        self.setup_iaas()

        for s in self.services:
            if s.instance_identifier==self.app.config['dispatched_app'] \
                    or s.instance_identifier.startswith('iaas')\
                    or self.app.config['dispatched_app']=='all':
                self.setup_service(s)



        # print("BINDS")
        # print(self.SQLALCHEMY_BINDS2)


        return


    def setup(self):
        self.init_login()

        self.get_binds()

        # self.nextcloud_identifiers, self.nextcloud_names = self.get_nextclouds()
        self.init_classes()



    def setup_pages(self):
        self.app.config['SQLALCHEMY_BINDS'] = self.SQLALCHEMY_BINDS2
        # Initialize flask-login



    def get_services(self, id=-1):

        list_of_services = iaas.iaas.SvcInstance.query.all()

        S = {}
        for r in list_of_services:
            if r.instance_identifier is not None and (id == -1 or id == r.id):


                if r.instance_identifier==self.app.config['dispatched_app'] \
                        or self.app.config['dispatched_app']=='all':
                    pass
                    # self.setup_service(S[r[1]])
                    # self.setup_service(r)
        self.services = list_of_services
        # return list_of_services

    def setup_iaas(self):
        self.add_iaas_views(dbconfig.db_name)


    def setup_service(self, svc_info):
        if svc_info.instance_identifier.startswith('iaas'):
            return

        # if len(svc_info.myDBs()) > 0:
        for d in svc_info.databases:
            # self.classesdict, my_db = classes.initialise(self.db, [d.dbname], [d.__str__()])
            self.db_details_dict[d.database_name] = d
            try:
                self.add_collection_of_views(svc_info.instance_identifier, d.database_name, self.classesdict,
                                             class_db_dict=self.class_db_dict,
                                             svc_group=d.database_name,
                                             svc_info=svc_info)

            except Exception as e:
                print(e)

        for w in svc_info.webapps:

            try:
                d=''
                try:
                    d = w.database_instance.GetConnectionString()
                except Exception as e:
                    print(e)

                i = importlib.import_module("main.web_apps_examples."+w.name)
                i.init_app(self.app,"/projects/{}/app/{}/".format(w.svc_inst.instance_identifier,w.name),d)
            except Exception as e:
                print(e)

        pass


    def init_login(self):
        login_manager = login.LoginManager()
        login_manager.init_app(self.app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            views.current_user.uid_trim()
            # return db.session.query(User).get(user_id)

    def get_schema(self, prefix):
        print "self.schema_ids"
        print self.schema_ids
        try:
            return self.schema_ids[prefix];
        except Exception as e:
            return 0

    def get_nextclouds(self):

        iaas_main_db = self.app.config['SQLALCHEMY_DATABASE_URI']
        dba = devmodels.DatabaseAssistant(iaas_main_db, dbconfig.db_name, dbconfig.db_name)

        result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
                                                                ["project_display_name", "instance_identifier",
                                                                 "group_id", "schema_id", "priv_user", "priv_pass",
                                                                 "db_ip"],
                                                                classes_loaded=False)

        identifiers = []
        names = []
        # for r in list_of_projects:
        #     if (r[2] == '2'):  # then this is a database project
        #         identifiers.append(r[1])
        #         names.append(r[0])

        return identifiers, names

    def get_binds(self):
        #todo: strip down
        """checks the iaas db for dbas services and collects the db binds"""

        iaas_main_db = self.app.config['SQLALCHEMY_DATABASE_URI']
        # dba = devmodels.DatabaseAssistant(iaas_main_db, dbconfig.db_name, dbconfig.db_name)

        x = iaas.iaas.DatabaseEngine.query.filter_by(connection_string=dbconfig.db_engine).first()
        self.db_details_dict[dbconfig.db_name] = iaas.iaas.DatabaseInstance(svc_inst=0,database_engine=x,
                                                                            username=dbconfig.db_user,
                                                                            password_if_secure=dbconfig.db_password,
                                                                            ip_address=dbconfig.db_hostname,
                                                                            port=3306,
                                                                            database_name=dbconfig.db_name)
        # self.svc_groups = {}
        self.svc_groups[dbconfig.db_name] = 'superusers'


        list_of_dbs_tmp = iaas.iaas.DatabaseInstance.query.all()

        for r in list_of_dbs_tmp:

            if r.password_if_secure == '':  # insecure password
                continue

            # svc_inst = r.svc_instance
            if not ((r.svc_instance.instance_identifier == self.app.config['dispatched_app'])
                    or (self.app.config['dispatched_app'] == 'all')):
                continue

            self.schema_ids[r.svc_instance.instance_identifier] = r.svc_instance.schema_id
            self.db_list.append(r.database_name)
            if r.port == 'None':
                r.port = '0'
            db_string =r.GetConnectionString()

            self.db_details_dict[r.svc_instance.instance_identifier] = r

            self.db_strings.append(db_string)

            self.db_identifiers.append(r.svc_instance.instance_identifier)

            self.svc_groups["{}".format(r.svc_instance.instance_identifier)] = r.svc_instance.group_id

            project_dba = devmodels.DatabaseAssistant(db_string, r.svc_instance.instance_identifier, r.svc_instance.instance_identifier)
            try:
                tns, cns = project_dba.getTableAndColumnNames()
                for t in tns:
                    if not r.is_dynamic:
                        pass
                    self.class_db_dict['cls_{}_{}_{}'.format(r.svc_instance.instance_identifier, r.database_name, t)] \
                        = r.svc_instance.instance_identifier + "_" + r.database_name
                # main.web_apps_examples.[].models

            except Exception as e:
                # flash(e,'error')
                print(e)
                print "failed - authentication?"


        return


    def _add_a_view(self, proj_admin, c, db_name, svc_group):
        v= views.MyModelView(c, self.db.session, name=c.__display_name__,
                              endpoint=proj_admin.db_details.database_name + "_" + c.__display_name__, category="Tables",
                              svc_group=svc_group,
                              db_details=self.db_details_dict[db_name])
        proj_admin.add_view(v)
        pass

    def add_iaas_views(self,d):
        iaas_admin = MyIAASView(db_details=self.db_details_dict[d],
                                app=self.app, name='IAAS admin app', template_mode='foundation',
                                endpoint=d, url="/admin",
                                base_template='my_master.html', database_name=d,
                                svc_group='superusers')

        iaas_admin.add_links(ML('IPs in use', url='/admin/ip_addresses/'.format(d),
                                category="Useage"),
                             ML('Ports in use', url='/admin/ip_addresses/ports'.format(d),
                                category="Useage"))

        iaas_admin.add_hidden_view(IPAddressView(name="IP Addresses", endpoint="ip_addresses", category="Useage"))


        # general
        iaas_admin.add_hidden_view(DatabaseOps(name='Edit Database'.format(d),
                                               endpoint='db_ops'.format(d),
                                               db_string= iaas.iaas_uri,#self.SQLALCHEMY_BINDS2[d],
                                               database_name=d,
                                               db=self.db,
                                               C=self.classesdict,
                                               svc_group='superusers',
                                               dbinfo=self.db_details_dict[d]))

        # this isnt a good idea with a fixed schema as used in iaas now
        # iaas_admin.add_links(ML('New Table', url='/admin/db_ops/newtable'.format(d,d)),
        #                      ML('Import Data', url='/admin/db_ops/upload'.format(d,d)),
        #                      # ML('Export Data',url='/admin/ops_download'),
        #                      ML('Relationship Builder',
        #                         url='/admin/db_ops/relationshipbuilder'.format(d,d)))


        self._add_a_view(iaas_admin, iaas.iaas.DatabaseEngine, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.DatabaseInstance, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.Group, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.IaasEvent, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.NextcloudInstance, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.Role, db_name=d, svc_group='superusers')
        # self._add_a_view(iaas_admin, iaas.iaas.Service, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.Subscriber, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.SvcInstance, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.VirtualMachine, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.WebApp, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.News, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.permitted_svc, db_name=d, svc_group='superusers')
        self._add_a_view(iaas_admin, iaas.iaas.comment, db_name=d, svc_group='superusers')


    def add_collection_of_views(self, identifier, d, classesdict, class_db_dict, svc_group, svc_info=None):

        # print("ASHDIASDJKL",self.db_details_dict)
        # todo: change bootstrap3 back to foundation to use my templates
        proj_admin = MyStandardView(self.app, name='{} admin'.format(d),
                                    template_mode='foundation',
                                    endpoint=d,
                                    url="/projects/{}/databases/{}".format(identifier,d),
                                    base_template='my_master.html',
                                    database_name=d,
                                    db_details=self.db_details_dict[d],
                                    svc_group=svc_group,
                                    )


        # proj_admin.add_links(ML('Application', url='/projects/{}/databases/{}/app'.format(identifier,d)))

        # general
        proj_admin.add_hidden_view(DatabaseOps(name='Edit Database'.format(d),
                                               endpoint='{}_ops'.format(d),
                                               db_string=self.SQLALCHEMY_BINDS2[d],
                                               database_name=d,
                                               db=self.db,
                                               C=self.classesdict,
                                               svc_group=svc_group,
                                               dbinfo=self.db_details_dict[d]))

        proj_admin.add_links(ML('Import Data', url='/projects/{}/databases/{}/{}_ops/upload'.format(identifier, d, d)))
        # ML('Export Data',url='/admin/ops_download'),

        if self.db_details_dict[d].is_dynamic:
            proj_admin.add_links(ML('New Table', url='/projects/{}/databases/{}/{}_ops/newtable'.format(identifier,d,d)))
            proj_admin.add_links(ML('Relationship Builder',
                                    url='/projects/{}/databases/{}/{}_ops/relationshipbuilder'.format(identifier,d,d)))
        for c in class_db_dict:
            if (identifier+"_"+d) == class_db_dict[c]:
                if 'spatial_ref_sys' in c.lower():
                    continue

                try:
                    self._add_a_view(proj_admin, classesdict[c], db_name=d, svc_group=svc_group)
                except Exception as e:
                    print(e)
                    print("failed")

    def init_classes(self):
        list_of_dbs = iaas.iaas.DatabaseInstance.query.all()
        self.classesdict, self.my_db = classes.initialise2(self.db,list_of_dbs)
        # self.classesdict, self.my_db = classes.initialise(self.db, self.db_list, self.db_strings,self.db_identifiers)
        return




