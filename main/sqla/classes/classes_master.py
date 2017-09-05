from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship, RelationshipProperty
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import reflection
import dbconfig


def ClassStr(self):
    if hasattr(self, 'title'):
        return self.title
    if hasattr(self, 'name'):
        return self.name
    if hasattr(self, 'id'):
        return str(self.id)


class_list = []


def init(db, db_name):
    Base = declarative_base()
    engine = create_engine('{}://{}:{}@{}/{}'
                           .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname,
                                   db_name))
    metadata = MetaData(bind=engine)
    metadata.reflect()
    insp = reflection.Inspector.from_engine(engine)

    mddict = {}
    tempdict = {}
    names = []
    failed = []
    for key, value in metadata.tables.items():
        names.append(key)
        failed.append(key)
    # for i in range(len(names)):
    #     name = names[i]
    # for name in names:
    numattempts=0
    maxattempts=100
    while len(names)>0 and numattempts<maxattempts:
        numattempts=numattempts+1
        for name in metadata.tables:
            if name not in names:
                continue
            # print name
            class_name_arr = str(name).split('_')
            class_name = ''
            class_list.append(name)
            for cn in class_name_arr:
                class_name = class_name + cn.capitalize()
            md = {}
            success=True
            for key in insp.get_foreign_keys(name):
               # print key['referred_table']
               try:
                  md[key['referred_table']]= relationship(globals()[key['referred_table'].capitalize()])
               except Exception as e:
                   try:
                       md[key['referred_table']]=relationship(globals()[key['referred_table']])
                   except Exception as ee:
                       print(ee)
                       success=False
                       # pass

            md['__table__'] = metadata.tables[name]
            md['__bind_key__'] = db_name
            # cls = type("_" + str(class_name), (db.Model,), md)
            # tempdict[cls.__name__] = cls
            # mddict[cls.__name__] = md

            if success or numattempts==maxattempts:
                cls = type( str(class_name), (db.Model,), md)
                globals()[cls.__name__] = cls
                setattr(globals()[cls.__name__], "__str__", ClassStr)
                setattr(globals()[cls.__name__], "__repr__", ClassStr)
                print "Generated Class: " + class_name
                if success:
                    failed.remove(name)
                names.remove(name)
        names.reverse()

    if len(failed)>0:
        print str(len(failed))+" failed"
    return
    # for key, value in metadata.tables.items():
    #     names.append(key)
    # for i in range(len(names)):
    #     name = names[i]
    # # for name in metadata.tables:
    #     print name
    #     class_name_arr = str(name).split('_')
    #     class_name = ''
    #     class_list.append(name)
    #     for cn in class_name_arr:
    #         class_name = class_name + cn.capitalize()
    #     md = {}  # mddict["_"+str(class_name)]
    #     k = []
    #     for key in insp.get_foreign_keys(name):
    #         print key['referred_table']
    #         try:
    #             md[key['referred_table']] = relationship(globals()[key['referred_table'].capitalize()])
    #         except Exception as e:
    #             try:
    #                 md[key['referred_table']] = relationship(globals()[key['referred_table']])
    #             except Exception as ee:
    #                 print(ee)
    #
    #     cls = type(str(class_name), (tempdict["_" + str(class_name)],), md)
    #     globals()[cls.__name__] = cls
    #     setattr(globals()[cls.__name__], "__str__", ClassStr)
    #     setattr(globals()[cls.__name__], "__repr__", ClassStr)

#

#  for name in metadata.tables:

#      md = {}
#      for key in insp.get_foreign_keys(name):
#         print "FOUND_FOREIGN_KEY"
#         print key['referred_table']
#         globals()[name].__setattr__(key['referred_table'],relationship(globals()[key['referred_table']]))
