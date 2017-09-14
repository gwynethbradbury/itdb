from flask_sqlalchemy import SQLAlchemy
import inspect
import importlib



def initialise(db, db_list=['map'], dbstring_list=["mysql+pymysql://root:***@localhost/map"]):
    classesdict = {}
    my_db = {}
    for i in range(len(db_list)):
        try:
            db_item = db_list[i]
            dbstring=dbstring_list[i]
            my_db[db_item] = importlib.import_module('.classes_master', __name__)
            CL = my_db[db_item].init(db,db_item,dbstring)
            # my_db[db_item].init(db,db_item)
            # this doesn't work as we need to map to the class, not merely the name of the class!
            for i in CL:#my_db[db_item].class_list:
                classes_arr = i.split('_')
                # cn = ""
                # for cl in classes_arr:
                #     cn = cn + cl.capitalize()
                cn = "cls_"+db_item+"_"+str(i)
                try:
                    classesdict["cls_" + db_item + "_" + i] = getattr(my_db[db_item], cn)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
    return classesdict, my_db

def initialise_single_class(databasename,classname):
    from main.sqla.app import db
    classesdict, my_db = initialise(db, db_list=[databasename])
    return classesdict["cls_{}_{}".format(databasename,classname)]



# classesdict, my_db = initialise()
