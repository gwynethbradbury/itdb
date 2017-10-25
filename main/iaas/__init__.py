from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import dbconfig

iaasapp = Flask(__name__)


# Create dummy secrey key so we can use sessions
iaasapp.config['SECRET_KEY'] = '123456790'

iaas_uri = '{}://{}:{}@{}/{}' \
        .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname, dbconfig.db_name)

iaasapp.config['SQLALCHEMY_DATABASE_URI'] =iaas_uri
db = SQLAlchemy(iaasapp)

import main.iaas.iaas

# endregion