# coding: utf-8
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from . import db
Base=declarative_base()
metadata = Base.metadata


class News(Base):
    __tablename__ = 'News'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    created_on = Column(Date)
    updated_on = Column(Date)


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    news_id = Column(ForeignKey(u'News.id'), index=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Integer)
    created_on = Column(Date)

    news = relationship(u'News')


class IaasEvents(Base):
    __tablename__ = 'iaas_events'

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    subtitle = Column(String(60))
    description = Column(String(255))
    room = Column(String(60))
    eventdate = Column(Date)
    starttime = Column(Time)
    endtime = Column(Time)


class PermittedSvc(Base):
    __tablename__ = 'permitted_svc'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    svc_id = Column(Integer)


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True)
    description = Column(String(250))


class Services(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Subscribers(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(60))


class SvcInstances(Base):
    __tablename__ = 'svc_instances'

    id = Column(Integer, primary_key=True)
    project_display_name = Column(String(30))
    instance_identifier = Column(String(70))
    svc_type_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
