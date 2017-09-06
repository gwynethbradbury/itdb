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
    print "Prefix: "+prefix
    return prefix 

def create_app(config_filename):
    # my files
    from methods import *
    print "Prefix: creating app: "+config_filename

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
    
    db = SQLAlchemy(app)
    
    # endregion
    
    
    DBAS = DBAS(app,db)
    

    return app




