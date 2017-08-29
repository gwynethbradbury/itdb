from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import reflection
import dbconfig

def ClassStr(self):
        if hasattr(self, 'title'):
            return self.title
        if hasattr(self,'name'):
            return self.name
        if hasattr(self,'id'):
            return str(self.id)


class_list=[]
def init(db, db_name):
  Base = declarative_base()
  engine = create_engine('{}://{}:{}@{}/{}'
                        .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password,dbconfig.db_hostname,db_name))
  metadata = MetaData(bind=engine)
  metadata.reflect()
  insp = reflection.Inspector.from_engine(engine)
  for name in metadata.tables:
      print name
      class_name_arr=str(name).split('_')
      class_name=''
      class_list.append(name)
      for cn in class_name_arr:
         class_name=class_name+cn.capitalize()
      md = {}
      for key in insp.get_foreign_keys(name):
         print key['referred_table']
         try:
            md[key['referred_table']]=relationship(globals()[key['referred_table'].capitalize()])
         except Exception as e:
             try:
                 md[key['referred_table']]=relationship(globals()[key['referred_table']])
             except Exception as ee:
                 pass

      md['__table__']=metadata.tables[name]
      md['__bind_key__']=db_name
      cls = type(str(class_name), (db.Model,), md)
      globals()[cls.__name__] = cls
      setattr(globals()[cls.__name__], "__str__", ClassStr)
      setattr(globals()[cls.__name__], "__repr__", ClassStr)
      print "Generated Class: "+class_name

#  for name in metadata.tables:

#      md = {}
#      for key in insp.get_foreign_keys(name):
#         print "FOUND_FOREIGN_KEY"
#         print key['referred_table']
#         globals()[name].__setattr__(key['referred_table'],relationship(globals()[key['referred_table']]))
