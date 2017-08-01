# coding: utf-8
from sqlalchemy import Column, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base


from . import db
Base=db.Model
metadata = Base.metadata


class Emptytable(Base):
    def __str__(self):
<<<<<<< HEAD:app/classes/map.py
        return self.id
    __tablename__ = 'emptytable'
=======
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self,'name'):
            return self.name
        elif hasattr(self,'id'):
            return self.id
    __bind_key__ = 'map'
    __tablename__ = 'derp'
>>>>>>> 0255d14853abc282d386706787c958bdae27e1fc:app/sqla/classes/map.py

    id = Column(Integer, primary_key=True)


<<<<<<< HEAD:app/classes/map.py
class Project(Base):
    def __str__(self):
        return self.latitude
    __tablename__ = 'project'
=======
class Derp2(Base):
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self,'name'):
            return self.name
        elif hasattr(self,'id'):
            return self.id
    __bind_key__ = 'map'
    __tablename__ = 'derp2'

    id = Column(Integer, primary_key=True)


class Derp4(Base):
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self,'name'):
            return self.name
        elif hasattr(self,'id'):
            return self.id
    __bind_key__ = 'map'
    __tablename__ = 'derp4'
>>>>>>> 0255d14853abc282d386706787c958bdae27e1fc:app/sqla/classes/map.py

    id = Column(Integer, primary_key=True)
<<<<<<< HEAD:app/classes/map.py
=======


class Pro(Base):
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self,'name'):
            return self.name
        elif hasattr(self,'id'):
            return self.id
    __bind_key__ = 'map'
    __tablename__ = 'pro'

    imported_id = Column(Integer)
>>>>>>> 0255d14853abc282d386706787c958bdae27e1fc:app/sqla/classes/map.py
    latitude = Column(Float(asdecimal=True))
    longitude = Column(Float(asdecimal=True))
    startdate = Column(Text)
    enddate = Column(Text)
    category = Column(Text)
    description = Column(Text)
    updated_at = Column(Text)


class Testtable(Base):
    def __str__(self):
<<<<<<< HEAD:app/classes/map.py
        return self.id
    __tablename__ = 'testtable'
=======
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self,'name'):
            return self.name
        elif hasattr(self,'id'):
            return self.id
    __bind_key__ = 'map'
    __tablename__ = 'project'
>>>>>>> 0255d14853abc282d386706787c958bdae27e1fc:app/sqla/classes/map.py

    id = Column(Integer, primary_key=True)
