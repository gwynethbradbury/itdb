# project/__init__.py

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import dbconfig


app = Flask('dbas_app')
app.config.update(
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
    )

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/iaas'.format(dbconfig.db_user, dbconfig.db_password)

db = SQLAlchemy(app)


from admin import admin

app.register_blueprint(admin, url_prefix='/admin', template_folder='templates')


@app.route('/admin')
def home():
    return render_template("admin/admin.html")
