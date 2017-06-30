# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from . import database as db
Base = db.Model
metadata = Base.metadata


class Items(Base):
    def __str__(self):
        return self.name
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    comment = Column(Text)


class Log(Base):
    def __str__(self):
        return self.date_out
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    date_out = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    returned = Column(Integer)
    borrower = Column(String(100))
    signed_out_by = Column(String(100))
    comment = Column(Text)
    item = Column(ForeignKey(u'items.id'), index=True)

    items = relationship(u'Items')
