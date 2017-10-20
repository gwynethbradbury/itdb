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
    for d in self.__dict__:
        x=''
        if 'name' in d.lower():
            x=d
            if not 'username' in d.lower():
                return getattr(self,x)
    for d in self.__dict__:
        if 'title' in d.lower():
            return getattr(self,d)

    if hasattr(self, 'id'):
        return str(self.id)




def init(db, db_name, dbstring):
    class_list = []
    Base = declarative_base()
    engine = create_engine(dbstring)
    # engine = create_engine('{}://{}:{}@{}/{}'
    #                        .format(dbconfig.db_engine, dbconfig.db_user, dbconfig.db_password, dbconfig.db_hostname,
    #                                db_name))
    metadata = MetaData(bind=engine)
    metadata.reflect()
    insp = reflection.Inspector.from_engine(engine)

    names = []
    failed = []
    for key, value in metadata.tables.items():
        names.append(key)
        failed.append(key)

    numattempts=0
    maxattempts=100
    while len(names)>0 and numattempts<maxattempts:
        numattempts=numattempts+1
        for name in metadata.tables:
            if name not in names:
                continue
            # print name
            # class_name_arr = str(name).split('_')
            # class_name = ''
            class_list.append(name)
            # for cn in class_name_arr:
            #     class_name = class_name + cn.capitalize()
            class_name = "cls_"+db_name+"_"+str(name)
            md = {}
            success=True
            for key in insp.get_foreign_keys(name):
                try:
                    md[key['referred_table']] = relationship(
                        globals()["cls_" + db_name + "_" + key['referred_table'].capitalize()])
                except Exception as e:
                    try:
                        md[key['referred_table']] = relationship(
                            globals()["cls_" + db_name + "_" + key['referred_table']])
                    except Exception as ee:
                        # print(ee)
                        success = False
                        # pass
                # try:
                #
                #     class_name_arr = str(key['referred_table']).split('_')
                #     rt = ''
                #     for cn in class_name_arr:
                #         rt = rt + cn.capitalize()
                #     print "Attempting to build relationship between "+key['referred_table']+" and "+rt
                #     md[key['referred_table']]= relationship(globals()[rt])
                #
                # except Exception as e:
                #     try:
                #          print "Didn't work, attempting to build relationship between "+key['referred_table']+" and "+key['referred_table']
                #          md[key['referred_table']]=relationship(globals()[key['referred_table']])
                #     except Exception as ee:
                #          print "Still didn't work!"
                #          print(ee)
                #          success=False
                #          # pass

            md['__table__'] = metadata.tables[name]
            md['__bind_key__'] = db_name
            md['__display_name__'] = str(name).title().replace('_',' ')

            if success or numattempts==maxattempts:
                try:
                    cls = type( str(class_name), (db.Model,), md)
                    globals()[cls.__name__] = cls
                    setattr(globals()[cls.__name__], "__str__", ClassStr)
                    setattr(globals()[cls.__name__], "__repr__", ClassStr)
                    print "Generated Class: " + class_name
                except Exception as e:
                    pass#print(e)
                if success:
                    failed.remove(name)
                names.remove(name)
        names.reverse()

    if len(failed)>0:
        print str(len(failed))+" failed"
    return class_list
