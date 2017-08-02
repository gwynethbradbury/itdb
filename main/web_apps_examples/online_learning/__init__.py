from main.sqla.app import app

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

import views

# views.assignroutes(app)


