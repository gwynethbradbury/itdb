from flask_sqlalchemy import SQLAlchemy
import inspect
import importlib
import main.iaas.iaas as iaas_classes
import classes_master


def initialise2(db, dbs):
    classesdict = {}
    my_db = {}
    for d in dbs:
        db_item = d.database_name
        dbstring = d.GetConnectionString()
        my_db[db_item] = importlib.import_module('.classes_master', __name__)

        if d.is_dynamic or (d.link_to_explicit_class_python_file is None):
            try:
                CL = my_db[db_item].init(db, db_item, dbstring)
                # my_db[db_item].init(db,db_item)
                # this doesn't work as we need to map to the class, not merely the name of the class!
                for c in CL:  # my_db[db_item].class_list:
                    classes_arr = c.split('_')
                    # cn = ""
                    # for cl in classes_arr:
                    #     cn = cn + cl.capitalize()
                    cn = "cls_" + db_item + "_" + str(c)
                    try:
                        classesdict["cls_" + d.svc_instance.instance_identifier + "_" + db_item + "_" + c] = getattr(my_db[db_item], cn)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

        else:
            p = d.link_to_explicit_class_python_file
            if '/' in p:
                import sys
                # the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
                sys.path.append(p)
                import imp

                i = imp.load_source(d.database_name, p+'models.py')
                # i = importlib.import_module('models',d.database_name)

            else:
                i = importlib.import_module(p,d.database_name)

            for name, c in inspect.getmembers(i):
                if hasattr(c,'metadata') and hasattr(c,'id'):
                    md = {}
                    cn = "cls_" + d.svc_instance.instance_identifier + "_" + db_item + "_" + c.__tablename__

                    setattr(c,'__table__',c.__tablename__)
                    setattr(c,'__bind_key__',d.database_name)
                    setattr(c,'__display_name__',str(c.__tablename__).title().replace('_', ' '))

                    try:
                        cls = c#type(str(cn), (db.Model,), md)
                        globals()[cls.__name__] = cls
                        setattr(globals()[cls.__name__], "__str__", classes_master.ClassStr)
                        setattr(globals()[cls.__name__], "__repr__", classes_master.ClassStr)
                        print "Generated Class: " + cn
                        classesdict[cn] \
                            = cls#getattr(my_db[db_item], cn)
                    except Exception as e:
                        print(e)


            pass
    return classesdict, my_db


def initialise(db, db_list=[], dbstring_list=[],db_identifier=[]):
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
            for c in CL:#my_db[db_item].class_list:
                classes_arr = c.split('_')
                # cn = ""
                # for cl in classes_arr:
                #     cn = cn + cl.capitalize()
                cn = "cls_"+db_item+"_"+str(c)
                try:
                    classesdict["cls_" + db_identifier[i] + "_" + db_item + "_" + c] = getattr(my_db[db_item], cn)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
    return classesdict, my_db

def initialise_single_class(db,databasename,classname,identifier):
    # from main.sqla.app import db
    classesdict, my_db = initialise(db, db_list=[databasename])
    return classesdict["cls_{}_{}_{}".format(identifier,databasename,classname)]



# classesdict, my_db = initialise()
