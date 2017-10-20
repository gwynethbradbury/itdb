from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text,Boolean
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from main.sqla.app import db


import dbconfig
# if dbconfig.debug==True:
from main.iaas import db
# else:
#     pass
# from ..app import db

Base = db.Model
metadata = Base.metadata



class DatabaseEngine(Base):
    __tablename__ = 'database_engine'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Database Engine'

    id = Column(Integer, primary_key=True)
    connection_string = Column(String(100))
    name = Column(String(100), nullable=False, server_default=text("'-'"))


class DatabaseInstance(Base):
    __tablename__ = 'database_instances'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Database Instances'

    id = Column(Integer, primary_key=True)
    project_owner = Column(String(100))
    ip_address = Column(String(100))
    svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    port = Column(Integer)
    username = Column(String(30))
    password_if_secure = Column(String(100))
    project_maintainer = Column(String(100))
    description = Column(Text)
    engine_type = Column(ForeignKey(u'database_engine.id'), nullable=False, index=True)
    database_name = Column(String(100))

    database_engine = relationship(u'DatabaseEngine')
    svc_instance = relationship(u'SvcInstance')


class Group(Base):
    __tablename__ = 'groups'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Groups'

    id = Column(Integer, primary_key=True)
    ldap_name = Column(String(70))
    name = Column(String(70), nullable=False, server_default=text("'-'"))


class IaasEvent(Base):
    __tablename__ = 'iaas_events'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'IAAS Events'

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    subtitle = Column(String(60))
    description = Column(String(255))
    room = Column(String(60))
    eventdate = Column(Date)
    starttime = Column(Time)
    endtime = Column(Time)


class NextcloudInstance(Base):
    __tablename__ = 'nextcloud_instances'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Nextcloud Instances'

    id = Column(Integer, primary_key=True)
    svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    ip_address = Column(String(100))
    project_owner = Column(String(100))
    project_maintainer = Column(String(100))
    svc_inst_id = Column(Integer)
    link = Column(String(100))

    svc_instance = relationship(u'SvcInstance')


class Role(Base):
    __tablename__ = 'roles'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    description = Column(String(250))


class Service(Base):
    __tablename__ = 'services'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Services'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Subscriber(Base):
    __tablename__ = 'subscribers'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(60))


class SvcInstance(Base):
    __tablename__ = 'svc_instances'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Service Instances'

    id = Column(Integer, primary_key=True)
    project_display_name = Column(String(30))
    instance_identifier = Column(String(70))
    svc_type_id = Column(ForeignKey(u'services.id'), nullable=False, index=True, server_default=text("'2'"))
    group_id = Column(ForeignKey(u'groups.id'), nullable=False, index=True, server_default=text("'3'"))
    priv_user = Column(String(15))
    priv_pass = Column(String(30))
    db_ip = Column(String(100))
    schema_id = Column(Integer)

    group = relationship(u'Group')
    svc_type = relationship(u'Service')


class VirtualMachine(Base):
    __tablename__ = 'virtual_machines'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Virtual Machines'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(100))
    name = Column(String(100))
    owned_by = Column(String(100))
    svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)

    svc_instance = relationship(u'SvcInstance')


class WebApp(Base):
    __tablename__ = 'web_apps'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Web Apps'

    id = Column(Integer, primary_key=True)
    name = Column(String(70))
    homepage = Column(String(100))
    svc_inst_id = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    ip_address = Column(String(100))
    assoc_db = Column(ForeignKey(u'database_instances.id'), nullable=False, index=True)

    database_instance = relationship(u'DatabaseInstance')
    svc_inst = relationship(u'SvcInstance')

class News(Base):
    __tablename__ = 'news'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'News'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)

class permitted_svc(Base):
    __tablename__ = 'permitted_svc'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Permitted Service'
    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey(u'groups.id'), nullable=False, index=True)
    svc_id = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    instance_quota = Column(Integer)


    svc_inst = relationship(u'SvcInstance')
    group = relationship(u'Group')

class comment(Base):
    __tablename__ = 'comment'
    __bind_key__ = dbconfig.db_name
    __display_name__ = 'Comment'
    id = Column(Integer, primary_key=True)
    news_id = Column(ForeignKey(u'news.id'), nullable=False, index=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Boolean)
    created_on = Column(DateTime)


    news = relationship(u'News')

