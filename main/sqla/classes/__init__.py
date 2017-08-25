from flask_sqlalchemy import SQLAlchemy
import inspect
import importlib



def initialise(db, db_list=['map', 'it_lending_log', 'online_learning']):
    classesdict = {}
    my_db = {}
    for db_item in db_list:
        my_db[db_item] = importlib.import_module('.classes_master', __name__)
        my_db[db_item].init(db,db_item)
        for i in my_db[db_item].class_list:
#            classes_arr = i.split('_')
#            cn = ""
#            for cl in classes_arr:
#                cn = cn + cl.capitalize()
             classesdict["cls_" + db_item + "_" + i] = getattr(my_db[db_item], i)
    return classesdict, my_db

def initialise_single_class(tablename,classname):
    from main.sqla.app import db
    classesdict, my_db = initialise(db, db_list=[tablename])
    return classesdict["cls_{}_{}".format(tablename,classname)]



# classesdict, my_db = initialise()
