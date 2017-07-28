# coding: utf-8
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from . import database as db
from . import database as db
from . import database as db
Base = db.Model
metadata = Base.metadata


class News(Base):
    def __str__(self):
        return self.title
    def __str__(self):
        return self.title
    def __str__(self):
        return self.title
    __tablename__ = 'News'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    created_on = Column(Date)
    updated_on = Column(Date)


class Blog(Base):
    def __str__(self):
        return self.title
    __tablename__ = 'blog'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True)
    body = Column(Text)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)


class Comment(Base):
    def __str__(self):
        return self.news_id
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    news_id = Column(ForeignKey(u'News.id'), index=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Integer)
    created_on = Column(Date)

    news = relationship(u'News')


class Groups(Base):
    def __str__(self):
        return self.ldap_name
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    ldap_name = Column(String(70))


class IaasEvents(Base):
    def __str__(self):
        return self.title
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
    def __str__(self):
        return self.group_id
    __tablename__ = 'permitted_svc'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    svc_id = Column(Integer)


class Roles(Base):
    def __str__(self):
        return self.name
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True)
    description = Column(String(250))


class Services(Base):
    def __str__(self):
        return self.name
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Subscribers(Base):
    def __str__(self):
        return self.name
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(60))


class SvcInstances(Base):
    def __str__(self):
        return self.project_display_name
    __tablename__ = 'svc_instances'

    id = Column(Integer, primary_key=True)
    project_display_name = Column(String(30))
    instance_identifier = Column(String(70))
    svc_type_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)


class Users(Base):
    def __str__(self):
        return self.email
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    active = Column(Integer, nullable=False)
    creation_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    role = Column(ForeignKey(u'roles.name'), index=True)

    roles = relationship(u'Roles')
