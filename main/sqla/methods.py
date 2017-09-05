
import views
import dev.models as devmodels
import classes
import models as IAASmodels
import flask_login as login
import flask_admin as admin
from flask_admin import Admin as ImpAdmin
from flask_admin.menu import MenuLink as ML

import dbconfig


class myAdmin(ImpAdmin):

    def getDBInfo(self):

        pass

    def setDBEngine(self, application_name):
        db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                         dbconfig.db_password,
                                                         dbconfig.db_hostname,
                                                         application_name)
        dbbindkey = "project_" + application_name + "_db"

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name)  # , upload_folder=uploadfolder)


        pass

from flask_admin import BaseView, expose
from main.sqla.core.iaasldap import LDAPUser as LDAPUser
current_user = LDAPUser()
from flask import abort, request, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

class DatabaseOps(BaseView):


    @expose('/')
    def index(self):
        return "DatabaseOps"#self.render('analytics_index.html')

    @expose('/newtable', methods=['GET', 'POST'])
    def newtable(self):

        current_url = str.split(self.admin.url, '/')
        application_name = current_url[2]


        if request.method == 'GET':
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
                extension = os.path.splitext(filename)[1]
                dt = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
                file.save(os.path.join(DBA.upload_folder, dt + '_' + filename))
                if extension.lower()==".csv":
                    success, ret = DBA.createTableFromCSV(os.path.join(DBA.upload_folder, dt + '_' + filename),
                                                          request.form.get("newtablename"))
                elif extension.lower()==".xlsx" or extension.lower()==".xls":
                    success, ret = DBA.createTableFromXLS(os.path.join(DBA.upload_folder, dt + '_' + filename),
                                                          request.form.get("newtablename"))


        if success:
            from main.sqla.app import DBAS as DBAS
            DBAS.setup()
            self.trigger_reload()
            flash("Table " + request.form.get("newtablename") + " created successfully!\n" + ret +
                                       "\nBUT app needs to reload",category="info")
        else:
            flash("Creation of table " + request.form.get("newtablename") +
                                     " failed!<br/>Error: " + ret,"error")


        return self.render("projects/create_table.html",
                               tablenames=tablenames,
                               columnnames=columnnames,
                               pname=application_name)


    @expose('/deletetable')
    def deletetable(self):
        return "deletetable"#self.render('analytics_index.html')

    @expose("/relationshipbuilder", methods=['GET', 'POST'])
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
            try:
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
            except Exception as E:
                success = 0
                ret = "One or more inputs is missing or incomplete."

            if success:
                flash(ret,"info")
            else:
                flash(ret,"error")


        tablenames, columnnames = DBA.getTableAndColumnNames()
        keys = DBA.getExistingKeys(True,True)

        return self.render("projects/project_relationship_builder.html",
                           tablenames=tablenames,columnnames=columnnames,
                           keys=keys)

    @expose('/upload', methods=['GET', 'POST'])
    def upload(self,msg="", err=""):
        current_url = str.split(self.admin.url,'/')
        application_name = current_url[2]
        if not current_user.is_authorised(application_name=application_name,is_admin_only_page=True):
            return abort(401)

        if request.method=='GET':
            db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                             dbconfig.db_password,
                                                             dbconfig.db_hostname,
                                                             application_name)
            dbbindkey = "project_" + application_name + "_db"

            DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
                                              upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

            tablenames, columnnames = DBA.getTableAndColumnNames()


        else:
            db_string = 'mysql+pymysql://{}:{}@{}/{}'.format(dbconfig.db_user,
                                                             dbconfig.db_password,
                                                             dbconfig.db_hostname,
                                                             application_name)
            dbbindkey = "project_" + application_name + "_db"

            DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
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
                        flash(ret,'error')

        tablenames, columnnames = DBA.getTableAndColumnNames()

        return self.render("projects/upload_table.html",
                    tablenames=tablenames,
                    message=msg,
                    error=err,
                    pname=application_name)

    @expose('/download', methods=['GET', 'POST'])
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

        DBA = devmodels.DatabaseAssistant(db_string, dbbindkey, application_name,
                                          upload_folder=os.path.dirname(os.path.realpath(__file__)) + '/data/')

        if request.method=='POST':

            # serves the requested data
            # todo: problems with filename and extension
            tablename=request.form.get("tablename")
            if tablename == "":
                try:
                    return DBA.serveData(F=request.form,
                                         ClassName=str(
                                             request.form.get(
                                                 "tablename")))  # os.path.abspath(os.path.dirname(__file__)))
                except Exception as e:
                    print(str(e))
            else:
                try:
                    return DBA.serveData(F=request.form,
                                         ClassName=str(tablename))  # os.path.abspath(os.path.dirname(__file__)))
                except Exception as e:
                    print(str(e))


        tablenames, columnnames = DBA.getTableAndColumnNames()

        return self.render("projects/download_table.html",
                               tablenames=tablenames, columnnames=columnnames,
                               pname=application_name)




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
from flask_admin.base import Admin as Admin2
class MyAdmin(Admin2):

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

class DBAS():

    def __init__(self, _app, _db):
        self.app = _app
        self.db = _db
        self.setup()
        self.setup_pages()

    def setup(self):
        SQLALCHEMY_BINDS, self.class_db_dict, self.db_list = self.get_binds()

        self.app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS

        self.classesdict, self.my_db = self.init_classes(self.db_list,self.class_db_dict)

    def setup_pages(self):
        # Initialize flask-login
        self.init_login()
        views.set_views(self.app)
        self.set_iaas_admin_console(self.class_db_dict,self.classesdict)
        self.admin_pages_setup(self.db_list, self.classesdict, self.class_db_dict)


    def init_login(self):
        login_manager = login.LoginManager()
        login_manager.init_app(self.app)

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            views.current_user.uid_trim()
            # return db.session.query(User).get(user_id)

    def get_binds(self):
        """checks the iaas db for dbas services and collects the db binds"""
        print("retrieving list of DBAS services available and adding to dictionary:")

        iaas_main_db = self.app.config['SQLALCHEMY_DATABASE_URI']
        dba = devmodels.DatabaseAssistant(iaas_main_db, "iaas", "iaas")

        result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
                                                              ["project_display_name", "instance_identifier",
                                                               "svc_type_id",
                                                               "group_id"],
                                                              classes_loaded=False)
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
                class_db_dict['cls_{}_{}'.format(r[1],t)] = r[1]


        return SQLALCHEMY_BINDS, class_db_dict, db_list

    def set_iaas_admin_console(self,class_db_dict,classesdict):
        """set up the admin console, depnds on predefined classes"""

        # endregion
        # Create admin
        # todo: change bootstrap3 back to foundation to use my templates
        iaas_admin = MyAdmin(self.app, name='IAAS admin app', template_mode='foundation',
                                 endpoint="admin",url="/admin",
                                 base_template='my_master.html',)

        # example adding links:
        #     iaas_admin.add_links(ML('Test Internal Link', endpoint='applicationhome'),
        #                          ML('Test External Link', url='http://python.org/'))
        #
        iaas_admin.add_links(ML('New Table', url='/admin/iaas_ops/newtable'),
                             ML('Import Data',url='/admin/iaas_ops/upload'),
                             ML('Export Data',url='/admin/iaas_ops/download'),
                             ML('Relationship Builder', url='/admin/iaas_ops/relationshipbuilder'))

        iaas_admin.add_hidden_view(DatabaseOps(name='Edit Database', endpoint='iaas_ops'))


        for c in class_db_dict:
            if 'iaas' == class_db_dict[c]:
                print ('class {} is in db {}'.format(c, 'iaas'))

                self._add_a_view( iaas_admin, classesdict[c])



    def _add_a_view(self, proj_admin,c):
        proj_admin.add_view(views.MyModelView(c, self.db.session))

    def add_collection_of_views(self, d, classesdict,class_db_dict):
        if d=='iaas':
            return


        # todo: change bootstrap3 back to foundation to use my templates
        proj_admin = MyAdmin(self.app, name='{} admin'.format(d),
                                 template_mode='foundation',
                                 endpoint=d,
                                 url="/projects/{}".format(d),
                                 base_template='my_master.html'
                                 )

        proj_admin.add_hidden_view(DatabaseOps(name='Edit Database'.format(d),
                                        endpoint='{}_ops'.format(d),
                                        menu_class_name="hi"))




        proj_admin.add_links(ML('New Table',url='/projects/{}/{}_ops/newtable'.format(d,d)),
                             ML('Import Data',url='/projects/{}/{}_ops/upload'.format(d,d)),
                             ML('Export Data',url='/projects/{}/{}_ops/download'.format(d,d)),
                             ML('Relationship Builder',url='/projects/{}/{}_ops/relationshipbuilder'.format(d,d)),
                             ML('Application', url='/projects/{}/app'.format(d)))

        for c in class_db_dict:
            if d == class_db_dict[c]:
                print ('class {} is in db {}'.format(c, d))

                self._add_a_view( proj_admin, classesdict[c])

    def add_single_view(self, c,d,db_list,admin_view):
        classesdict, my_db = classes.initialise(db=self.db, db_list=db_list)


        print ('class {} is in db {}'.format(c, d))

        self._add_a_view(admin_view, classesdict['cls_{}_{}'.format(d,c)]) # admin_view = iaas_view for eg

    def init_classes(self,db_list, class_db_dict):
        classesdict, my_db = classes.initialise(self.db, db_list)
        return classesdict, my_db

    def admin_pages_setup(self, db_list, classesdict, class_db_dict):

        binds = self.app.config['SQLALCHEMY_BINDS']
        for d in binds:
            print(d,binds[d])

            self.add_collection_of_views(d,classesdict, class_db_dict)







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