# coding: utf-8
from sqlalchemy import Column, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base


from . import database as db
Base = db.Model
metadata = Base.metadata


class Emptytable(Base):
    def __str__(self):
        return self.id
    __tablename__ = 'emptytable'

    id = Column(Integer, primary_key=True)


class Project(Base):
    def __str__(self):
        return self.latitude
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    latitude = Column(Float(asdecimal=True))
    longitude = Column(Float(asdecimal=True))
    startdate = Column(Text)
    enddate = Column(Text)
    category = Column(Text)
    description = Column(Text)
    updated_at = Column(Text)


class Testtable(Base):
    def __str__(self):
        return self.id
    __tablename__ = 'testtable'

    id = Column(Integer, primary_key=True)
