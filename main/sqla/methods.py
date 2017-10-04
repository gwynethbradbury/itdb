import views
import dev.models as devmodels
import classes
import flask_login as login
import flask_admin as admin
from flask_admin import Admin as ImpAdmin
from flask_admin.menu import MenuLink as ML

import dbconfig

if dbconfig.test:
    from core.mock_access_helper import MockAccessHelper as AccessHelper
else:
    from core.access_helper import AccessHelper
AH = AccessHelper()

from flask_admin import BaseView, expose
from main.sqla.core.iaasldap import LDAPUser as LDAPUser

current_user = LDAPUser()
from flask import abort, request, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask_admin.base import Admin as Admin2
import pymysql


class IPAddressView(BaseView):
    @expose('/')
    def index(self):
        return self.render('ip_addresses.html')

    @expose('/ports')
    def show_ports_in_use(self):
        return self.render('ports.html')


class DatabaseOps(BaseView):
    can_export = True

    def __init__(self, name, endpoint, database_name, db_string, svc_group,
                 menu_class_name=None, db=None, C=None):
        super(DatabaseOps, self).__init__(name,
                                          endpoint=endpoint,
                                          menu_class_name=menu_class_name)
        self.database_name = database_name
        self.svc_group = svc_group
        self.db_string = db_string
        self.db = db
        self.classes = C

    @expose('/')
    def index(self):
        return "DatabaseOps"  # self.render('analytics_index.html')

    @expose('/newtable', methods=['GET', 'POST'])
    def newtable(self):
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
        return "deletetable"  # self.render('analytics_index.html')

    @expose("/relationshipbuilder", methods=['GET', 'POST'])
    def relationshipbuilder(self):
        application_name = self.database_name

        if not current_user.is_authorised(service_name=self.svc_group, is_admin_only_page=True):
            return abort(403)

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
        keys = DBA.getExistingKeys(True, True)

        return self.render("projects/project_relationship_builder.html",
                           tablenames=tablenames, columnnames=columnnames,
                           keys=keys)

    @expose('/upload', methods=['GET', 'POST'])
    def upload(self, msg="", err=""):
        application_name = self.database_name
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
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
            else:
                file = request.files['file']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    flash("No selected file", 'error')
                if file:  # and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                    file.save(os.path.join(DBA.uploadfolder, dt + '_' + filename))
                    tablename = str(request.form.get("tablename"))

                    success, ret = DBA.createTableFrom(os.path.join(DBA.uploadfolder, dt + '_' + filename),
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
        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
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
        current_url = str.split(self.admin.url, '/')
        application_name = self.database_name
        print "Triggering reload: " + application_name
        # update svc_instance set schema_id=schema_id+1 where project_display_name=self-config['db']

        try:

            connection = pymysql.connect(host=dbconfig.db_hostname,
                                         user=dbconfig.db_user,
                                         passwd=dbconfig.db_password,
                                         db=dbconfig.db_name)

            with connection.cursor() as cursor:
                cursor.execute("update svc_instances set schema_id=schema_id+1 where instance_identifier=%s",
                               (str(application_name),))
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
        self.database_name = database_name
        self.svc_group = svc_group
        self.db_string = db_details.__str__()
        self.db_details = db_details
        self.setDBEngine(self.database_name)

    @expose('/')
    def home(self):
        if current_user.is_authorised(self.svc_group, False):

            return self.render('index.html')
        else:
            abort(403)

    def getDBInfo(self):
        self.project_owner, self.project_maintainer, self.ip_address, self.svc_inst, self.port, self.username, self.password_if_secure, self.description, self.engine_type, self.engine_string = \
            AH.getDatabaseConnectionString(self.database_name)
        return ""

    def getDatabaseQuota(self):
        self.dbquota = 0

    def getDatabaseUseage(self):
        self.dbuseage = 0
        return self.db_details.GetUseage()

    def setDBEngine(self, application_name):
        dbbindkey = "project_" + application_name + "_db"

        self.DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey,
                                               application_name)  # , upload_folder=uploadfolder)

        R = self.getDatabaseUseage()

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

class DBDetails():
    def __init__(self, engine_type, username, passwd, host, port, dbname):
        self.engine_type = engine_type
        self.username = username
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dbname = dbname

    def ConnectAndExecute(self, query):
        try:
            conn = pymysql.connect(host=self.host,
                                   port=self.port,
                                   user=self.username,
                                   passwd=self.passwd,
                                   db=self.dbname)

            cur = conn.cursor()

            cur.execute(query)

            instances = []
            for inst in cur:
                instances.append(inst)
            cur.close()
            conn.close()

            return instances, "", 1
        except Exception as e:
            return [], e.__str__(), 0

    def GetExistingKeys(self, foreign=True, primary=False):
        P = ""
        if primary and foreign:
            P = ""
        else:
            if primary:
                P = "AND CONSTRAINT_NAME = 'PRIMARY'"
            elif foreign:
                P = "AND NOT CONSTRAINT_NAME = 'PRIMARY'"

        Q = self.ConnectAndExecute("SELECT CONSTRAINT_NAME,REFERENCED_TABLE_SCHEMA,"
                                   "TABLE_NAME,COLUMN_NAME,"
                                   "REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME "
                                   "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                                   "WHERE TABLE_SCHEMA='{}' {};".format(self.dbname, P))

        return Q


    def GetUseage(self):
        dbuseage = 0
        if self.engine_type == 'postgresql':
            # try:
            #     r = self.ConnectAndExecute("SELECT table_name, pg_size_pretty(total_bytes) AS total "
            #                            "FROM("
            #                            "SELECT *, total_bytes - index_bytes - COALESCE(toast_bytes, 0) AS table_bytes "
            #                            "FROM("
            #                            "SELECT c.oid, nspname AS table_schema, relname AS TABLE_NAME, c.reltuples AS row_estimate, pg_total_relation_size(c.oid) AS total_bytes, pg_indexes_size(c.oid) AS index_bytes, pg_total_relation_size(reltoastrelid) AS toast_bytes "
            #                            "FROM pg_class c LEFT JOIN pg_namespace n ON n.oid = c.relnamespace WHERE relkind = 'r' and nspname = 'public'"
            #                            ") a"
            #                            ") a;")
            # except Exception as e:
            #     print(e)

            return 0
        else:
            try:
                instances, msg, success = self.ConnectAndExecute(
                    "SELECT Round(Sum(data_length + index_length) / 1024 / 1024, 1) 'db_size_mb' "
                    "FROM information_schema.tables "
                    "WHERE table_schema = '{}';".format(self.dbname))

                for inst in instances:
                    dbuseage = inst[0]
            except Exception as e:
                print(e)

        return dbuseage

    def __str__(self):
        if self.engine_type == 'postgresql':
            return '{}://{}:{}@{}:{}/{}'.format(self.engine_type,
                                                self.username,
                                                self.passwd,
                                                self.host,
                                                self.port,
                                                self.dbname)
        else:

            return '{}://{}:{}@{}:{}/{}'.format(self.engine_type,
                                             self.username,
                                             self.passwd,
                                             self.host,
                                             self.port,
                                             self.dbname)

class NextCloud():

    def __init__(self, link, ip):
        self.ip = ip
        self.link = link

class VirtualMachine():

    def __init__(self, name, ip, owned_by):
        self.name = name
        self.owned_by = owned_by
        self.ip = ip

class WebApp():

    def __init__(self, homepage, name):
        self.name = name
        self.homepage = homepage


class SvcDetails():

    def __init__(self, svc_id=-1, svc_name="",
                 _list_of_dbs=[], _list_of_ncs=[], _list_of_vms=[], _list_of_was=[]):
        self.svc_id = svc_id
        self.svc_name = svc_name

        self.nc = []
        self.db = []
        self.wa = []
        self.vm = []
        self.MY_SQLALCHEMY_BINDS={}
        for d in _list_of_dbs:
            DBD = DBDetails(engine_type=d[0], username=d[1],
                            passwd=d[2], host=d[3], port=d[4],
                            dbname=d[5])
            self.db.append(DBD)

            self.MY_SQLALCHEMY_BINDS[DBD.dbname] = DBD.__str__()

        for n in _list_of_ncs:
            self.nc.append(NextCloud(n[0], n[1]))

        for v in _list_of_vms:
            self.vm.append(VirtualMachine(v[0], v[1], v[2]))

        for w in _list_of_was:
            self.wa.append(NextCloud(w[0], w[1]))

class DBAS():


    def __init__(self, _app, _db):
        self.app = _app
        self.db = _db
        self.class_db_dict = {}

        self.SQLALCHEMY_BINDS = {}
        self.SQLALCHEMY_BINDS2 = {}
        self.db_list = []
        self.db_strings = []
        self.schema_ids = {}
        self.db_details_dict = {}
        self.svc_groups = {}


        self.services = self.get_services()
        for s in self.services:
            for d in self.services[s].MY_SQLALCHEMY_BINDS:
                self.SQLALCHEMY_BINDS2[d] = self.services[s].MY_SQLALCHEMY_BINDS[d]
        self.setup()
        self.setup_pages()

        print("BINDS")
        print(self.SQLALCHEMY_BINDS)
        print(GLOBAL_SQLALCHEMY_BINDS)

    def setup(self):
        # self.SQLALCHEMY_BINDS, self.class_db_dict, self.db_list, self.schema_ids, self.db_strings, self.db_details_dict, self.svc_groups = \
        self.get_binds()

        self.nextcloud_identifiers, self.nextcloud_names = self.get_nextclouds()

        self.app.config['SQLALCHEMY_BINDS'] = self.SQLALCHEMY_BINDS

        self.init_classes()

    def setup_pages(self):
        # Initialize flask-login
        self.init_login()
        views.set_views(self.app)
        views.set_nextcloud_views(self.app, self.nextcloud_names, self.nextcloud_identifiers)

        # put the database views in
        self.dbas_admin_pages_setup(self.db_list, self.classesdict, self.class_db_dict, self.svc_groups)

    def get_services(self, id=-1):

        controlDB = DBDetails(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password,
                              dbconfig.db_hostname, 3306, dbconfig.db_name)

        list_of_services, msg, ret = controlDB.ConnectAndExecute("SELECT id, instance_identifier "
                                                                 "FROM svc_instances;")

        S = {}
        for r in list_of_services:
            if r[1] is not None and (id == -1 or id == int(r[0])):
                list_of_was = []
                list_of_vms = []
                list_of_ncs = []
                list_of_dbs = []

                list_of_dbs_tmp, msg, ret = controlDB.ConnectAndExecute(
                    "SELECT engine_type, username, password_if_secure, ip_address, port, database_name "
                    "FROM database_instances "
                    "WHERE svc_inst = '{}';".format(int(r[0])))
                list_of_dbs = []
                for i in range(len(list_of_dbs_tmp)):
                    d = list_of_dbs_tmp[i]
                    engine_type, msg, ret = controlDB.ConnectAndExecute("SELECT connection_string "
                                                                        "FROM database_engine "
                                                                        "WHERE id = '{}';"
                                                                        .format((d[0])))
                    L = list(d)
                    L[0] = engine_type[0][0]
                    list_of_dbs.append(L)

                list_of_ncs, msg, ret = controlDB.ConnectAndExecute("SELECT link, ip_address "
                                                                    "FROM nextcloud_instances "
                                                                    "WHERE svc_inst_id = '{}';"
                                                                    .format(int(r[0])))
                list_of_vms, msg, ret = controlDB.ConnectAndExecute("SELECT name, ip_address, owned_by "
                                                                    "FROM virtual_machines "
                                                                    "WHERE svc_inst = '{}';"
                                                                    .format(int(r[0])))
                list_of_was, msg, ret = controlDB.ConnectAndExecute("SELECT name, homepage, name "
                                                                    "FROM web_apps "
                                                                    "WHERE svc_inst = '{}';"
                                                                    .format(int(r[0])))
                S[r[1]] = SvcDetails(int(r[0]), r[1],
                                     _list_of_was=list_of_was,
                                     _list_of_vms=list_of_vms,
                                     _list_of_ncs=list_of_ncs,
                                     _list_of_dbs=list_of_dbs)
        self.services = S
        return S

    def setup_service(self, svc_info):
        return
        if len(svc_info.db) > 0:
            for d in svc_info.db:
                self.classesdict, my_db = classes.initialise(self.db, [d.dbname], [d.__str__()])
                self.db_details_dict[d.dbname] = d
                try:
                    self.add_collection_of_views(d.dbname, self.classesdict,
                                                 class_db_dict={}, svc_group=self.svc_groups[d.dbname],#svc_info.svc_id,
                                                 db_details=d)
                except Exception as e:
                    print(e)


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
        return self.schema_ids[prefix];

    def get_nextclouds(self):

        iaas_main_db = self.app.config['SQLALCHEMY_DATABASE_URI']
        dba = devmodels.DatabaseAssistant(iaas_main_db, dbconfig.db_name, dbconfig.db_name)

        result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
                                                                ["project_display_name", "instance_identifier",
                                                                 "svc_type_id",
                                                                 "group_id", "schema_id", "priv_user", "priv_pass",
                                                                 "db_ip"],
                                                                classes_loaded=False)

        identifiers = []
        names = []
        for r in list_of_projects:
            if (r[2] == '2'):  # then this is a database project
                identifiers.append(r[1])
                names.append(r[0])

        return identifiers, names

    def get_binds(self):
        """checks the iaas db for dbas services and collects the db binds"""

        iaas_main_db = self.app.config['SQLALCHEMY_DATABASE_URI']
        dba = devmodels.DatabaseAssistant(iaas_main_db, dbconfig.db_name, dbconfig.db_name)

        result, list_of_databases = dba.retrieveDataFromDatabase("database_instances",
                                                                 ["svc_inst",
                                                                  "ip_address", "port",
                                                                  "engine_type", "username", "password_if_secure"],
                                                                 classes_loaded=False)

        # self.class_db_dict = {}

        self.SQLALCHEMY_BINDS = {dbconfig.db_name: '{}://{}:{}@{}/{}'
            .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname, dbconfig.db_name)}

        # self.db_list = []
        # self.db_strings = []
        # self.schema_ids = {}
        # self.db_details_dict = {}
        self.db_details_dict[dbconfig.db_name] = DBDetails(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password,
                                                      dbconfig.db_hostname, 3306, dbconfig.db_name)
        # self.svc_groups = {}
        self.svc_groups[dbconfig.db_name] = 'superusers'

        controlDB = DBDetails(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password,
                              dbconfig.db_hostname, 3306, dbconfig.db_name)

        list_of_dbs_tmp, msg, ret = controlDB.ConnectAndExecute(
                                        "SELECT svc_inst, ip_address, port, engine_type, username, password_if_secure "
                                        "FROM database_instances;")

        for r in list_of_dbs_tmp:

            if r[5] == '':  # postgres or insecure password
                continue

            result, engine_type = dba.retrieveDataFromDatabase("database_engine",
                                                               ["connection_string"],
                                                               wherefield="id", whereval=r[3],
                                                               classes_loaded=False)
            engine_type = engine_type[0][0]

            result, svc_inst = dba.retrieveDataFromDatabase("svc_instances",
                                                            ["project_display_name",
                                                             "instance_identifier",
                                                             "group_id",
                                                             "schema_id", "priv_user", "priv_pass", "db_ip"],
                                                            wherefield="id", whereval=r[0],
                                                            classes_loaded=False)
            svc_inst = svc_inst[0]
            if not ((svc_inst[1] == self.app.config['dispatched_app']) or
                        (self.app.config['dispatched_app'] == 'all')):
                continue

            self.schema_ids[svc_inst[1]] = svc_inst[3]
            self.db_list.append(svc_inst[1])
            if r[2] == 'None':
                r[2] = '0'
            db_string = DBDetails(engine_type,
                                  r[4],
                                  r[5],
                                  r[1],
                                  int(r[2]),
                                  svc_inst[1])
            self.db_details_dict[svc_inst[1]] = db_string

            self.db_strings.append(db_string.__str__())

            self.SQLALCHEMY_BINDS["{}".format(svc_inst[1])] = db_string.__str__()
            self.svc_groups["{}".format(svc_inst[1])] = svc_inst[2]

            project_dba = devmodels.DatabaseAssistant(db_string.__str__(), svc_inst[1], svc_inst[1])
            try:
                tns, cns = project_dba.getTableAndColumnNames()
                for t in tns:
                    self.class_db_dict['cls_{}_{}'.format(svc_inst[1], t)] = svc_inst[1]
            except Exception as e:
                # flash(e,'error')
                print(e)
                print "failed - authentication?"


        return

    # def set_iaas_admin_console(self, class_db_dict, classesdict):
    #     """set up the admin console, depnds on predefined classes"""
    #
    #     # endregion
    #     # Create admin
    #     # todo: change bootstrap3 back to foundation to use my templates
    #     print "CONNECTING TO IAAS ON " + self.SQLALCHEMY_BINDS[dbconfig.db_name]
    #     iaas_admin = MyIAASView(db_details=self.db_details_dict[dbconfig.db_name],
    #                             app=self.app, name='IAAS admin app', template_mode='foundation',
    #                             endpoint=dbconfig.db_name, url="/projects/{}".format(dbconfig.db_name),
    #                             base_template='my_master.html', database_name=dbconfig.db_name, svc_group='superusers')
    #
    #     # example adding links:
    #     #     iaas_admin.add_links(ML('Test Internal Link', endpoint='applicationhome'),
    #     #                          ML('Test External Link', url='http://python.org/'))
    #     #
    #     iaas_admin.add_links(ML('New Table', url='/projects/{}/ops/newtable'.format(dbconfig.db_name)),
    #                          ML('Import Data', url='/projects/{}/ops/upload'.format(dbconfig.db_name)),
    #                          # ML('Export Data',url='/admin/ops/download'),
    #                          ML('Relationship Builder',
    #                             url='/projects/{}/ops/relationshipbuilder'.format(dbconfig.db_name)),
    #                          ML('IPs in use', url='/projects/{}/ip_addresses/'.format(dbconfig.db_name),
    #                             category="Useage"),
    #                          ML('Ports in use', url='/projects/{}/ip_addresses/ports'.format(dbconfig.db_name),
    #                             category="Useage"))
    #
    #     iaas_admin.add_hidden_view(DatabaseOps(name='Edit Database', endpoint='ops',
    #                                            db_string=self.SQLALCHEMY_BINDS[dbconfig.db_name],
    #                                            database_name=dbconfig.db_name, svc_group='superusers',
    #                                            db=self.db))
    #
    #     iaas_admin.add_hidden_view(IPAddressView(name="IP Addresses", endpoint="ip_addresses", category="Useage"))
    #     print "ADDING IAAS CLASSES " + str(len(class_db_dict))
    #     for c in class_db_dict:
    #         print c + " " + class_db_dict[c]
    #
    #         if dbconfig.db_name == class_db_dict[c]:
    #             print c
    #             self._add_a_view(iaas_admin, classesdict[c], db_name=dbconfig.db_name, svc_group='superusers')

    def _add_a_view(self, proj_admin, c, db_name, svc_group):
        proj_admin.add_view(
            views.MyModelView(c, self.db.session, name=c.__display_name__, databasename=proj_admin.database_name,
                              endpoint=proj_admin.database_name + "_" + c.__display_name__, category="Tables",
                              db_string=self.db_details_dict[db_name].__str__(), svc_group=svc_group,
                              db_details=self.db_details_dict[db_name]))

    def add_collection_of_views(self, d, classesdict, class_db_dict, svc_group):
        if d == dbconfig.db_name:

            print "CONNECTING TO IAAS ON " + self.SQLALCHEMY_BINDS[d]
            proj_admin = MyIAASView(db_details=self.db_details_dict[d],
                                    app=self.app, name='IAAS admin app', template_mode='foundation',
                                    endpoint=d, url="/projects/{}".format(d),
                                    base_template='my_master.html', database_name=d,
                                    svc_group='superusers')

            proj_admin.add_links(ML('IPs in use', url='/projects/{}/ip_addresses/'.format(d),
                                    category="Useage"),
                                 ML('Ports in use', url='/projects/{}/ip_addresses/ports'.format(d),
                                    category="Useage"))

            proj_admin.add_hidden_view(IPAddressView(name="IP Addresses", endpoint="ip_addresses", category="Useage"))

            # proj_admin.add_hidden_view(DatabaseOps(name='Edit Database',
            #                                        endpoint='ops',
            #                                        db_string=self.SQLALCHEMY_BINDS[d],
            #                                        database_name=d,
            #                                        svc_group='superusers',
            #                                        db=self.db))

            print "ADDING IAAS CLASSES " + str(len(class_db_dict))


        else:
            print("ASHDIASDJKL",self.db_details_dict)
            # todo: change bootstrap3 back to foundation to use my templates
            proj_admin = MyStandardView(self.app, name='{} admin'.format(d),
                                        template_mode='foundation',
                                        endpoint=d,
                                        url="/projects/{}".format(d),
                                        base_template='my_master.html',
                                        database_name=d,
                                        db_details=self.db_details_dict[d],
                                        svc_group=svc_group
                                        )


            proj_admin.add_links(ML('Application', url='/projects/{}/app'.format(d)))

        # general
        proj_admin.add_hidden_view(DatabaseOps(name='Edit Database'.format(d),
                                               endpoint='{}_ops'.format(d),
                                               db_string=self.SQLALCHEMY_BINDS[d],
                                               database_name=d,
                                               db=self.db,
                                               C=self.classesdict,
                                               svc_group=svc_group))

        proj_admin.add_links(ML('New Table', url='/projects/{}/ops/newtable'.format(d)),
                             ML('Import Data', url='/projects/{}/ops/upload'.format(d)),
                             # ML('Export Data',url='/admin/ops/download'),
                             ML('Relationship Builder',
                                url='/projects/{}/ops/relationshipbuilder'.format(d)))
        for c in class_db_dict:
            if d == class_db_dict[c]:
                if 'spatial_ref_sys' in c.lower():
                    continue

                try:
                    self._add_a_view(proj_admin, classesdict[c], db_name=d, svc_group=svc_group)
                except Exception as e:
                    print(e)
                    print("failed")

    def init_classes(self):
        self.classesdict, self.my_db = classes.initialise(self.db, self.db_list, self.db_strings)
        return

    def dbas_admin_pages_setup(self, db_list, classesdict, class_db_dict, svc_groups):

        binds = self.SQLALCHEMY_BINDS2
        print("LHLASHDFJLASDFHAJSDFHAJSDF")
        print(self.SQLALCHEMY_BINDS2 is self.SQLALCHEMY_BINDS)
        print(self.SQLALCHEMY_BINDS==self.SQLALCHEMY_BINDS2)
        for d in binds:
            print(d, binds[d])

            self.add_collection_of_views(d.__str__(), classesdict, class_db_dict, svc_group=d)







            # # Create customized index view class that handles login & registration
            # class MyAdminIndexView(admin.AdminIndexView):
            #
            #     @expose('/')
            #     def index(self):
            #         # if not login.current_user.is_authenticated:
            #         if not current_user.is_authenticated:
            #             return "user not authenticatedr" #edirect(url_for('.login_view'))
            #         return super(MyAdminIndexView, self).index()
            #
            #     # @expose('/login/', methods=('GET', 'POST'))
            #     # def login_view(self):
            #     #     # handle user login
            #     #     form = LoginForm(request.form)
            #     #     if helpers.validate_form_on_submit(form):
            #     #         user = form.get_user()
            #     #         login.login_user(user)
            #     #
            #     #     if login.current_user.is_authenticated:
            #     #         return redirect(url_for('.index'))
            #     #     link = '<p>Don\'t have an account? <a href="' + url_for(
            #     #         '.register_view') + '">Click here to register.</a></p>'
            #     #     self._template_args['form'] = form
            #     #     self._template_args['link'] = link
            #     #     return super(MyAdminIndexView, self).index()
            #
            #     # @expose('/register/', methods=('GET', 'POST'))
            #     # def register_view(self):
            #     #     form = RegistrationForm(request.form)
            #     #     if helpers.validate_form_on_submit(form):
            #     #         user = User()
            #     #
            #     #         form.populate_obj(user)
            #     #         # we hash the users password to avoid saving it as plaintext in the db,
            #     #         # remove to use plain text:
            #     #         user.password = generate_password_hash(form.password.data)
            #     #
            #     #         db.session.add(user)
            #     #         db.session.commit()
            #     #
            #     #         login.login_user(user)
            #     #         return redirect(url_for('.index'))
            #     #     link = '<p>Already have an account? <a href="' + url_for(
            #     #         '.login_view') + '">Click here to log in.</a></p>'
            #     #     self._template_args['form'] = form
            #     #     self._template_args['link'] = link
            #     #     return super(MyAdminIndexView, self).index()
            #
            #     # @expose('/logout/')
            #     # def logout_view(self):
            #     #     login.logout_user()
            #     #     return redirect(url_for('.index'))

