import os
import os.path as op


# from projects.map import map_app
#
# from core.home import home


from main.sqla import *

# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# manager = Manager(app)
# migrate = Migrate(app, db)

from threading import Lock
from werkzeug.wsgi import pop_path_info, extract_path_info, peek_path_info
from main.sqla.app import create_app, get_user_for_prefix, get_current_schema_id

app, schema_id, db = create_app('all')

# from main.web_apps_examples import map, it_lending_log, online_learning
# map.init_app(app)
# it_lending_log.init_app(app)
# online_learning.init_app(app)

if __name__ == '__main__':
    # app_dir = op.realpath(os.path.dirname(__file__))
    #app.run()
    app.run(host="0.0.0.0", port=5500, debug=True)
