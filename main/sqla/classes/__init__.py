from flask_sqlalchemy import SQLAlchemy
from main.sqla.app import db as db
import inspect
import importlib

db_list = ['map', 'it_lending_log', 'online_learning']

classesdict = {}
my_db = {}

for db_item in db_list:
    my_db[db_item] = importlib.import_module('.classes_master', __name__)
    my_db[db_item].init(db_item)
    # this doesn't work as we need to map to the class, not merely the name of the class!
    for i in my_db[db_item].class_list:
        classes_arr = i.split('_')
        cn = ""
        for cl in classes_arr:
            cn = cn + cl.capitalize()
        classesdict["cls_" + db_item + "_" + i] = getattr(my_db[db_item], cn)
