#!/usr/bin/env python


# from projects.map import map_app
#
# from core.home import home

from app import app

# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# manager = Manager(app)
# migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2000)#, debug=True)
