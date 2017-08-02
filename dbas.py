import os
import os.path as op


# from projects.map import map_app
#
# from core.home import home

from main.sqla import app as app

from main.sqla import *
from main.web_apps_examples import *
try:

    # db = SQLAlchemy(app)

    import main.web_apps_examples
    # from web_apps_examples import map as maps

    # maps.assignroutes(app)#,nm='map')

    # # THE FOLLOWING ARE MAP-SPECIFIC - SHOULD BE MOVED TO MAP WEB APP
    # my_module = importlib.import_module('web_apps_examples.'+r[1])
    # my_module.views.assignroutes(app,nm='map')
except Exception as e:
    print e
# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# manager = Manager(app)
# migrate = Migrate(app, db)


if __name__ == '__main__':
    # app_dir = op.realpath(os.path.dirname(__file__))
    app.run()
    # app.run(host="0.0.0.0", port=5000, debug=True)
