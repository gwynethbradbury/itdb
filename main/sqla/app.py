from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# my files
from methods import *



# region Create application
app = Flask(__name__)

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

def start_app():
    pass






