import os
import os.path as op


# from projects.map import map_app
#
# from core.home import home

from main.sqla import app as app

from main.sqla import *
from main.web_apps_examples import *

# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# manager = Manager(app)
# migrate = Migrate(app, db)


if __name__ == '__main__':
    # app_dir = op.realpath(os.path.dirname(__file__))
    app.run()
    # app.run(host="0.0.0.0", port=5000, debug=True)
