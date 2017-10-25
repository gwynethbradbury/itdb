# from main.sqla.app import app

# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy(app)

import views


def init_app(app,root,uri):
    views.assignroutes(app, root,uri)



