import views
import dev.models as devmodels
import classes
import models as IAASmodels
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


class IPAddressView(BaseView):
    @expose('/')
    def index(self):
        return self.render('ip_addresses.html')

    @expose('/ports')
    def show_ports_in_use(self):
        return self.render('ports.html')


class DatabaseOps(BaseView):
    can_export = True

    def __init__(self, name, endpoint, database_name, db_string,
                 menu_class_name=None, db=None, C=None):
        super(DatabaseOps, self).__init__(name,
                                          endpoint=endpoint,
                                          menu_class_name=menu_class_name)
        self.database_name = database_name
        self.db_string = db_string
        self.db = db
        self.classes = C

    @expose('/')
    def index(self):
        return "DatabaseOps"  # self.render('analytics_index.html')

    @expose('/newtable', methods=['GET', 'POST'])
    def newtable(self):

        application_name = self.database_name

        if request.method == 'GET':
            if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
                return abort(401)

            dbbindkey = "project_" + self.database_name + "_db"

            DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey,
                                              self.database_name)  # , upload_folder=uploadfolder)

            tablenames, columnnames = DBA.getTableAndColumnNames()

            return self.render("projects/create_table.html",
                               tablenames=tablenames,
                               columnnames=columnnames,
                               pname=self.database_name)

        if not current_user.is_authorised(application_name=self.database_name, is_admin_only_page=True):
            return abort(401)

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

        if not current_user.is_authorised(application_name=application_name, is_admin_only_page=True):
            return abort(401)

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
            return abort(401)

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
            return abort(401)

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
        current_url = str.split(self.admin.url,'/')
        application_name = self.database_name
        print "Triggering reload: "+application_name
        # update svc_instance set schema_id=schema_id+1 where project_display_name=self-config['db']

        try:

            connection = pymysql.connect(host=dbconfig.db_hostname,
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=dbconfig.db_name)

            with connection.cursor() as cursor:
                cursor.execute("update svc_instances set schema_id=schema_id+1 where instance_identifier=%s",(str(application_name),))
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
        # if current_user.has_role('superusers') :
        #     return True
        #
        # current_url = str.split(self.admin.url,'/')
        # project_name=""
        # require_project_admin=False
        #
        # if current_url[1]=='projects':
        #     '''admin view of project'''
        #     project_name = current_url[2]
        #     require_project_admin = True
        # else:
        #     '''normal view of project'''
        #     project_name = current_url[1]
        #
        # if not current_user.is_active or not current_user.is_authenticated(project_name):
        #     return False
        # if require_project_admin and not current_user.has_role('{}_admin'.format(project_name)):
        #     return False


        return True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            pass
            # if current_user.is_authenticated:
            #     # permission denied
            #     abort(403)
            # else:
            #     # login
            #     return "not authenticated" #redirect(url_for('security.login', next=request.url))


class MyStandardView(Admin2):
    dbquota = 0
    dbuseage = 0

    def __init__(self, app, name, endpoint, url, database_name,
                 db_string,
                 template_mode='foundation',
                 base_template='my_master.html'):
        super(MyStandardView, self).__init__(app, name, template_mode=template_mode,
                                             url=url,
                                             endpoint=endpoint, base_template=base_template)
        self.database_name = database_name
        self.db_string = db_string
        self.setDBEngine(self.database_name)

    @expose('/')
    def home(self):

        return self.render('index.html')

    def getDBInfo(self):
        self.project_owner, self.project_maintainer, self.ip_address, self.svc_inst, self.port, self.username, self.password_if_secure, self.description, self.engine_type, self.engine_string = \
            AH.getDatabaseConnectionString(self.database_name)
        return ""

    def getDatabaseQuota(self):
        self.dbquota = 0

    def getDatabaseUseage(self):
        self.dbuseage = 0
        try:
            C = self.DBA.DBE.E.execute("SELECT Round(Sum(data_length + index_length) / 1024 / 1024, 1) 'db_size_mb' "
                                       "FROM information_schema.tables "
                                       "WHERE table_schema = '{}';".format(self.database_name))

            for inst in C:
                self.dbuseage = inst[0]
        except Exception as e:
            print(e)

        return self.dbuseage

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


class MyIAASView(MyStandardView):
    def __init__(self, db_string,
                 app, name, template_mode,
                 endpoint, url, base_template, database_name):
        super(MyIAASView, self).__init__(app=app, name=name, db_string=db_string, template_mode=template_mode,
                                         endpoint=endpoint, url=url,base_template=base_template,
                                         database_name=database_name)
        self.db_string = db_string

    def getIPAddresses(self):
        dbbindkey = "project_{}_db".format(dbconfig.db_name)

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, dbconfig.db_name)
        R = DBA.DBE.E.execute("SELECT ip_address FROM database_instances "
                              "UNION "
                              "SELECT ip_address from nextcloud_instances "
                              "UNION "
                              "SELECT ip_address from web_apps;")
        instances = []
        for inst in R:
            instances.append(inst[0])

        return instances

    def getPorts(self):

        dbbindkey = "project_{}_db".format(dbconfig.db_name)

        DBA = devmodels.DatabaseAssistant(self.db_string, dbbindkey, dbconfig.db_name)
        R = DBA.DBE.E.execute("SELECT ip_address, port from database_instances;")
        instances = []
        for inst in R:
            instances.append([inst[0], inst[1]])

        return instances


class DBAS():
    def __init__(self, _app, _db):
        self.app = _app
        self.db = _db
        self.setup()
        self.setup_pages()

    def setup(self):
        self.SQLALCHEMY_BINDS, self.class_db_dict, self.db_list, self.schema_ids, self.db_strings = self.get_binds()

        self.nextcloud_identifiers, self.nextcloud_names = self.get_nextclouds()

        self.app.config['SQLALCHEMY_BINDS'] = self.SQLALCHEMY_BINDS

        self.classesdict, self.my_db = self.init_classes(self.db_list, self.class_db_dict)

    def setup_pages(self):
        # Initialize flask-login
        self.init_login()
        views.set_views(self.app)
        views.set_nextcloud_views(self.app, self.nextcloud_names, self.nextcloud_identifiers)

        # put the database views in
        self.set_iaas_admin_console(self.class_db_dict, self.classesdict)
        self.dbas_admin_pages_setup(self.db_list, self.classesdict, self.class_db_dict)

    def init_login(self):
        login_manager = login.LoginManager()
        login_manager.init_app(self.app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            views.current_user.uid_trim()
            # return db.session.query(User).get(user_id)

    def get_schema(self, prefix):
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

        class_db_dict = {}

        SQLALCHEMY_BINDS = {dbconfig.db_name: '{}://{}:{}@{}/{}'
            .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname, dbconfig.db_name)}

        db_list = []
        db_string_list = []
        schema_ids = {}
        for r in list_of_databases:

            if  r[5]=='':# postgres or insecure password
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
                                                               "schema_id","priv_user","priv_pass", "db_ip"],
                                                                wherefield="id",whereval=r[0],
                                                              classes_loaded=False)
            svc_inst=svc_inst[0]
            if not 'iaas' in svc_inst[1]:# todo: check this clause
                if not ((svc_inst[1] == self.app.config['db']) or (self.app.config['db'] == 'all')):
                    continue


            schema_ids[svc_inst[1]] = svc_inst[3]
            db_list.append(svc_inst[1])

            if r[3] == '2':

                db_string = '{}://{}:{}@{}:{}/{}'.format(engine_type,
                                                         r[4],
                                                         r[5],
                                                         r[1],
                                                         r[2],
                                                         svc_inst[1])
            else:
                db_string = '{}://{}:{}@{}/{}'.format(engine_type,
                                                      r[4],
                                                      r[5],
                                                      r[1],
                                                      svc_inst[1])

            db_string_list.append(db_string)

            SQLALCHEMY_BINDS["{}".format(svc_inst[1])] = db_string

            project_dba = devmodels.DatabaseAssistant(db_string, svc_inst[1], svc_inst[1])
            try:
                tns, cns = project_dba.getTableAndColumnNames()
                for t in tns:
                    class_db_dict['cls_{}_{}'.format(svc_inst[1], t)] = svc_inst[1]
            except Exception as e:
                # flash(e,'error')
                print(e)
                print "failed - authentication?"

        return SQLALCHEMY_BINDS, class_db_dict, db_list, schema_ids, db_string_list

    def set_iaas_admin_console(self, class_db_dict, classesdict):
        """set up the admin console, depnds on predefined classes"""

        # endregion
        # Create admin
        # todo: change bootstrap3 back to foundation to use my templates
        print "CONNECTING TO IAAS ON " + self.SQLALCHEMY_BINDS[dbconfig.db_name]
        iaas_admin = MyIAASView(db_string = self.SQLALCHEMY_BINDS[dbconfig.db_name],
                                app=self.app, name='IAAS admin app', template_mode='foundation',
                                endpoint="admin", url="/admin/iaas",
                                base_template='my_master.html', database_name=dbconfig.db_name)

        # example adding links:
        #     iaas_admin.add_links(ML('Test Internal Link', endpoint='applicationhome'),
        #                          ML('Test External Link', url='http://python.org/'))
        #
        iaas_admin.add_links(ML('New Table', url='/admin/iaas/ops/newtable'),
                             ML('Import Data', url='/admin/iaas/ops/upload'),
                             # ML('Export Data',url='/admin/ops/download'),
                             ML('Relationship Builder', url='/admin/ops/relationshipbuilder'),
                             ML('IPs in use', url='/admin/iaas/ip_addresses/', category="Useage"),
                             ML('Ports in use', url='/admin/iaas/ip_addresses/ports', category="Useage"))

        iaas_admin.add_hidden_view(DatabaseOps(name='Edit Database', endpoint='ops',
                                               db_string=self.SQLALCHEMY_BINDS[dbconfig.db_name],
                                               database_name=dbconfig.db_name,
                                               db=self.db))

        iaas_admin.add_hidden_view(IPAddressView(name="IP Addresses", endpoint="ip_addresses", category="Useage"))
        print "ADDING IAAS CLASSES " + str(len(class_db_dict))
        for c in class_db_dict:
            print c + " "+ class_db_dict[c]
            
            if dbconfig.db_name == class_db_dict[c]:
                print c
                self._add_a_view(iaas_admin, classesdict[c],db_string=self.SQLALCHEMY_BINDS[dbconfig.db_name])

    def _add_a_view(self, proj_admin, c, db_string):
        proj_admin.add_view(
            views.MyModelView(c, self.db.session, name=c.__display_name__, databasename=proj_admin.database_name,
                              endpoint=proj_admin.database_name + "_" + c.__display_name__, category="Tables",
                              db_string=db_string))

    def add_collection_of_views(self, d, classesdict, class_db_dict):
        if d == dbconfig.db_name:
            return

        # todo: change bootstrap3 back to foundation to use my templates
        proj_admin = MyStandardView(self.app, name='{} admin'.format(d),
                                    template_mode='foundation',
                                    endpoint=d,
                                    url="/projects/{}".format(d),
                                    base_template='my_master.html',
                                    database_name=d,
                                    db_string=self.SQLALCHEMY_BINDS[d]
                                    )

        proj_admin.add_hidden_view(DatabaseOps(name='Edit Database'.format(d),
                                               endpoint='{}_ops'.format(d),
                                               db_string=self.SQLALCHEMY_BINDS[d],
                                               database_name=d,
                                               db=self.db,
                                               C=self.classesdict))

        proj_admin.add_links(ML('New Table', url='/projects/{}/{}_ops/newtable'.format(d, d)),
                             ML('Import Data', url='/projects/{}/{}_ops/upload'.format(d, d)),
                             # ML('Export Data',url='/projects/{}/{}_ops/download'.format(d,d)),
                             ML('Relationship Builder', url='/projects/{}/{}_ops/relationshipbuilder'.format(d, d)),
                             ML('Application', url='/projects/{}/app'.format(d)))

        for c in class_db_dict:
            if d == class_db_dict[c]:
                if 'spatial_ref_sys' in c.lower():
                    continue

                try:
                    self._add_a_view(proj_admin, classesdict[c],db_string=self.SQLALCHEMY_BINDS[d])
                except Exception as e:
                    print(e)
                    print("failed")

    def init_classes(self, db_list, class_db_dict):
        classesdict, my_db = classes.initialise(self.db, self.db_list, self.db_strings)
        return classesdict, my_db

    def dbas_admin_pages_setup(self, db_list, classesdict, class_db_dict):

        binds = self.app.config['SQLALCHEMY_BINDS']
        for d in binds:
            print(d, binds[d])

            self.add_collection_of_views(d, classesdict, class_db_dict)







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
