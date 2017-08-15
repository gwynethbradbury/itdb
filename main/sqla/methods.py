
import views
import dev.models as devmodels
import classes
import models as IAASmodels
import flask_login as login
import flask_admin as admin
from flask_admin.menu import MenuLink as ML

import dbconfig

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
        self.set_iaas_admin_console()
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

    def set_iaas_admin_console(self):
        """set up the admin console, depnds on predefined classes"""

        # endregion
        # Create admin
        iaas_admin = admin.Admin(self.app, name='IAAS admin app', template_mode='foundation',
                                 endpoint="admin",url="/admin",
                                 base_template='my_master.html')

        # example adding links:
        #     iaas_admin.add_links(ML('Test Internal Link', endpoint='applicationhome'),
        #                          ML('Test External Link', url='http://python.org/'))
        #
        iaas_admin.add_links(ML('Application', endpoint='applicationhome'),
                             ML('New Table', url='/projects/iaas/admin/newtable'))

        # Add IAAS views
        iaas_admin.add_view(views.MyModelView(IAASmodels.SvcInstances, self.db.session))
        iaas_admin.add_view(views.MyModelView(IAASmodels.Subscribers, self.db.session))
        iaas_admin.add_view(views.MyModelView(IAASmodels.News, self.db.session))
        iaas_admin.add_view(views.MyModelView(IAASmodels.Comment, self.db.session))

    def _add_a_view(self, proj_admin,c):
        proj_admin.add_view(views.MyModelView(c, self.db.session))

    def add_collection_of_views(self, d, classesdict,class_db_dict):
        proj_admin = admin.Admin(self.app, name='{} admin'.format(d),
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