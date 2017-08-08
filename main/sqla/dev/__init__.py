dictionary_of_databases = {}


import dbconfig
from models import *
from views import *


def register_project(s):
    # set the project name and get the relative path for uploads/downloads
    project_name = s
    uploadfolder = dir_path = os.path.dirname(os.path.realpath(__file__))+'/data/'

    # create the project app (generic name)
    # project_app = Blueprint(project_name, __name__,template_folder='templates')#,static_folder='static')


    # set the database entry point for this project
    # database and project names should be the same
    db2 = '{}://{}:{}@{}/{}'.format(dbconfig.db_engine,dbconfig.db_user,
                                                     dbconfig.db_password,dbconfig.db_hostname,
                                                     s)

    dbbindkey="project_"+project_name+"_db"

    # create the database assistant instance
    DBA = views.DatabaseAssistant(db2, dbbindkey, project_name, upload_folder=uploadfolder)
    # adminroute = "/projects/" + project_name + "/admin/")

    # import projects.map.views as vv
    # views.assignroutes(project_app,s)
    # views.assignAdminRoutesForDatabase(project_app,DBA,upload_folder=uploadfolder)

    # app.register_blueprint(project_app)

    dictionary_of_databases[project_name] = DBA

    print "adding dictionary entry for database assistant: dictionary_of_databases['{}'] contains ".format(project_name), \
        dictionary_of_databases[project_name].mydatabasename