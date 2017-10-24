from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def start_app():
    pass


def get_user_for_prefix(prefix):
    return prefix




def get_current_schema_id(prefix):
    import dev.models as devmodels
    import dbconfig
    iaas_main_db = '{}://{}:{}@{}/{}' \
        .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname, dbconfig.db_name)

    dba = devmodels.DatabaseAssistant(iaas_main_db, dbconfig.db_name, dbconfig.db_name)

    result, list_of_projects = dba.retrieveDataFromDatabase("svc_instances",
                                                            ["project_display_name", "instance_identifier",
                                                             "group_id", "schema_id", "priv_user", "priv_pass"],
                                                            classes_loaded=False)
    schema_ids = {}
    priv_users = {}
    priv_pass = {}
    for r in list_of_projects:
        print "checking schema_id for " + r[1]
        if (r[1] == prefix):
            # if not (r[2] == '1' or r[2] == '4'):  # then this is a database project
            #     continue
            schema_ids[r[1]] = r[4]
            priv_users[r[1]] = r[5]
            priv_pass[r[1]] = r[6]
    try:
        return schema_ids[prefix]
    except Exception as e:
        return 0


def create_app(instance_name):
    # my files
    from methods import *

    app = Flask(__name__)

    # region GENERAL SETTINGS

    # Create dummy secrey key so we can use sessions
    app.config['SECRET_KEY'] = '123456790'
    app.config["dispatched_app"] = instance_name
    app.config["db"] = dbconfig.db_name
    app.config["db_user"] = dbconfig.db_user
    app.config["db_pass"] = dbconfig.db_password
    app.config["db_hostname"] = dbconfig.db_hostname

    #    if (config_filename!="all") and (config_filename!=''):
    # We're in the dispatcher, use privilege separation
    #       app.config["db_user"],app.config["db_password"],app.config["db_hostname"] = get_db_creds(config_filename)
    # Create in-memory database
    # app.config['DATABASE_FILE'] = 'sample_db.sqlite'

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
    app.config['SQLALCHEMY_DATABASE_URI'] = '{}://{}:{}@{}/{}' \
        .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname, dbconfig.db_name)

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

    app.config['schema_id'] = -1
    db = SQLAlchemy(app)

    DBAS = DBAS(app, db)

    # services = DBAS.get_services()
    # for s in services:
    #     DBAS.setup_service(services[s])
    #
    # DBAS.initialise()

    if (instance_name != '') and (instance_name != 'all'):
        app.config['schema_id'] = DBAS.get_schema(instance_name)



    return app, app.config['schema_id']
