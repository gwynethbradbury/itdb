# project/__init__.py

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import dbconfig, config




app = Flask('dbas_app')
app.config.update(
        DEBUG=True
    )
# app.config.update(
#         DEBUG=True,
#         SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
#     )
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/iaas'.format(dbconfig.db_user, dbconfig.db_password)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/iaas'.format(dbconfig.db_user, dbconfig.db_password),
# app.config['SQLALCHEMY_BINDS'] = {
#     'iaas_db': 'mysql+pymysql://{}:{}@localhost/iaas'.format(dbconfig.db_user, dbconfig.db_password),
#     'project_map_db': 'mysql+pymysql://{}:{}@localhost/map'.format(dbconfig.db_user, dbconfig.db_password)
# }

app.config.from_object('config')

db = SQLAlchemy(app)
db.create_all(bind='iaas_db')
db.create_all(bind='project_map_db')


from projects.map import map
from core.home import home
from admin import admin



app.register_blueprint(home)
app.register_blueprint(admin, url_prefix='/admin',
                       template_folder='templates')
app.register_blueprint(map)





@app.route('/admin')
def home():
    return render_template("admin/admin.html")
