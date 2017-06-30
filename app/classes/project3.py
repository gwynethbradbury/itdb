# coding: utf-8
from sqlalchemy import Column, Float, Integer
from sqlalchemy.ext.declarative import declarative_base


from . import database as db
Base = db.Model
metadata = Base.metadata


class NewTable(Base):
    def __str__(self):
        return self.id
    __tablename__ = 'new_table'

    id = Column(Integer, primary_key=True)
    new_col = Column(Float(asdecimal=True))
    col2 = Column(Float(asdecimal=True))


class Newtable(Base):
    def __str__(self):
        return self.id
    __tablename__ = 'newtable'

    id = Column(Integer, primary_key=True)
