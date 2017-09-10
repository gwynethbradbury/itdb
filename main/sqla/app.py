from flask import Flask
from flask_sqlalchemy import SQLAlchemy



## region Create application
#app = Flask(__name__)
#
## region GENERAL SETTINGS
#
## Create dummy secrey key so we can use sessions
#app.config['SECRET_KEY'] = '123456790'
#
## Create in-memory database
## app.config['DATABASE_FILE'] = 'sample_db.sqlite'
#
## app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
#app.config['SQLALCHEMY_DATABASE_URI'] ='{}://{}:{}@{}/{}'\
#    .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password, dbconfig.db_hostname,dbconfig.db_name)
#
#
#
#
#app.config.update(
#    DEBUG=dbconfig.debug
#)
## endregion
#
## region EMAIL SETTINGS
#
#app.secret_key = dbconfig.mail_secret_key
#app.config["MAIL_SERVER"] = dbconfig.mail_server
#app.config["MAIL_PORT"] = dbconfig.mail_port
#app.config["MAIL_USE_SSL"] = dbconfig.mail_use_ssl
#app.config["MAIL_USERNAME"] = dbconfig.mail_username
#if not dbconfig.is_server_version:  # personal machine
#    app.config["AAAS_MAIL_SENDER"] = dbconfig.mail_username
#    app.config["MAIL_PASSWORD"] = dbconfig.mail_password
#else:  # server
#    app.config["AAAS_MAIL_SENDER"] = dbconfig.mail_sender
#    app.config["MAIL_DEFAULT_SENDER"] = dbconfig.mail_sender
#
## endregion
#
#db = SQLAlchemy(app)
#
## endregion
#
#
#DBAS = DBAS(app,db)
#
def start_app():
    pass

def get_user_for_prefix(prefix):
    return prefix 

def get_current_schema_id(prefix):
        import dev.models as devmodels
        import dbconfig
        iaas_main_db ='{}://{}:{}@{}/{}'\
          .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password, dbconfig.db_hostname,dbconfig.db_name)
 
        dba = devmodels.DatabaseAssistant(iaas_main_db, "iaas", "iaas")

        result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
                                                              ["project_display_name", "instance_identifier",
                                                               "svc_type_id",
                                                               "group_id","schema_id"],
                                                              classes_loaded=False)
        schema_ids={}

        for r in list_of_projects:
          print "checking schema_id for "+r[1]
          if (r[1]==prefix):
            if not(r[2] == '1' or r[2] == '4'):  # then this is a database project
                continue
            schema_ids[r[1]] = r[4]
        return schema_ids[prefix]

#def increment_schema_id(prefix):
#        import dev.models as devmodels
#        import dbconfig
#        iaas_main_db ='{}://{}:{}@{}/{}'\
#          .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password, dbconfig.db_hostname,dbconfig.db_name)
#
#        dba = devmodels.DatabaseAssistant(iaas_main_db, "iaas", "iaas")

        # update svc_instance set schema_id=schema_id+1 where project_display_name=prefix



def create_app(config_filename):
    # my files
    from methods import *

    app = Flask(__name__)
#    app.config.from_pyfile(config_filename)

#    from yourapplication.model import db
#    db.init_app(app)

#    from yourapplication.views.admin import admin
#    from yourapplication.views.frontend import frontend
#    app.register_blueprint(admin)
#    app.register_blueprint(frontend)
    # region GENERAL SETTINGS
    
    # Create dummy secrey key so we can use sessions
    app.config['SECRET_KEY'] = '123456790'
    app.config["db"] =  config_filename    
    # Create in-memory database
    # app.config['DATABASE_FILE'] = 'sample_db.sqlite'
    
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
    app.config['SQLALCHEMY_DATABASE_URI'] ='{}://{}:{}@{}/{}'\
        .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password, dbconfig.db_hostname,dbconfig.db_name)
    
    
    
    
    app.config.update(
        DEBUG=dbconfig.debug
    )
    # endregion
    
    # region EMAIL SETTINGS
    
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
    app.config['schema_id']=-1
    db = SQLAlchemy(app)
    
    # endregion
    
    
    DBAS = DBAS(app,db)
   
    if (config_filename!='') and (config_filename!='all'):
       app.config['schema_id']=DBAS.get_schema(config_filename) 

    return app, app.config['schema_id']




