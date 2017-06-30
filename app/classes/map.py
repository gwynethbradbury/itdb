# coding: utf-8
from sqlalchemy import Column, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base


from . import database as db
Base = db.Model
metadata = Base.metadata


class Derp(Base):
    def __str__(self):
        return self.id
    __tablename__ = 'derp'

    id = Column(Integer, primary_key=True)


class Derp2(Base):
    def __str__(self):
        return self.id
    __tablename__ = 'derp2'

    id = Column(Integer, primary_key=True)


class Derp4(Base):
    def __str__(self):
        return self.latitude
    __tablename__ = 'derp4'

    imported_id = Column(Integer)
    latitude = Column(Float(asdecimal=True))
    longitude = Column(Float(asdecimal=True))
    startdate = Column(Text)
    enddate = Column(Text)
    category = Column(Text)
    description = Column(Text)
    updated_at = Column(Text)
    id = Column(Integer, primary_key=True)


class Pro(Base):
    def __str__(self):
        return self.latitude
    __tablename__ = 'pro'

    imported_id = Column(Integer)
    latitude = Column(Float(asdecimal=True))
    longitude = Column(Float(asdecimal=True))
    startdate = Column(Text)
    enddate = Column(Text)
    category = Column(Text)
    description = Column(Text)
    updated_at = Column(Text)
    id = Column(Integer, primary_key=True)


class Project(Base):
    def __str__(self):
        return self.latitude
    __tablename__ = 'project'

    imported_id = Column(Integer)
    latitude = Column(Float(asdecimal=True))
    longitude = Column(Float(asdecimal=True))
    startdate = Column(Text)
    enddate = Column(Text)
    category = Column(Text)
    description = Column(Text)
    updated_at = Column(Text)
    id = Column(Integer, primary_key=True)