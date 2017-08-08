# coding: utf-8
from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import dbconfig
from . import db

class_list=[]
def init(db_name):
  Base = declarative_base()
  engine = create_engine('{}://{}:{}@{}/{}'
                        .format(dbconfig.db_engine,dbconfig.db_user,dbconfig.db_password,dbconfig.db_hostname,db_name))
  metadata = MetaData(bind=engine)
  metadata.reflect()
  for name in metadata.tables:
      class_name_arr=str(name).split('_')
      class_name=''
      class_list.append(name)
      for cn in class_name_arr:
         class_name=class_name+cn.capitalize()
      cls = type(class_name, (db.Model,), {'__table__': metadata.tables[name],  '__bind_key__': db_name})
      globals()[cls.__name__] = cls
