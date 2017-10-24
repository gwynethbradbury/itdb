from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text,Boolean
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from main.sqla.app import db
import pymysql


import dbconfig
# if dbconfig.debug==True:
from main.iaas import db
# else:
#     pass
# from ..app import db

Base = db.Model
metadata = Base.metadata




class Group(Base):
    __tablename__ = 'groups'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Groups'

    id = Column(Integer, primary_key=True)
    ldap_name = Column(String(70))
    name = Column(String(70), nullable=False, server_default=text("'-'"))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __init__(self,ldap_name,name):
        self.ldap_name=ldap_name
        self.name=name



class DatabaseEngine(Base):
    __tablename__ = 'database_engine'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Database Engine'

    id = Column(Integer, primary_key=True)
    connection_string = Column(String(100))
    name = Column(String(100), nullable=False, server_default=text("'-'"))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __init__(self,connection_string,name):
        self.connection_string=connection_string
        self.name = name



class DatabaseInstance(Base):
    __tablename__ = 'database_instances'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Database Instances'

    id = Column(Integer, primary_key=True)
    project_owner = Column(String(100))
    ip_address = Column(String(100))
    # svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    port = Column(Integer)
    username = Column(String(30))
    password_if_secure = Column(String(100))
    project_maintainer = Column(String(100))
    description = Column(Text)
    engine_type = Column(ForeignKey(u'database_engine.id'), nullable=False, index=True)
    database_name = Column(String(100))

    database_engine = relationship(u'DatabaseEngine')
    # svc_instance = relationship(u'SvcInstance')

    svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    svc_instance = relationship(u'SvcInstance', back_populates=u'databases')

    def ConnectAndExecute(self, query):
        try:
            conn = pymysql.connect(host=self.ip_address,
                                   port=self.port,
                                   user=self.username,
                                   passwd=self.password_if_secure,
                                   db=self.database_name)

            cur = conn.cursor()

            cur.execute(query)

            instances = []
            for inst in cur:
                instances.append(inst)
            cur.close()
            conn.close()

            return instances, "", 1
        except Exception as e:
            return [], e.__str__(), 0

    def GetExistingKeys(self, foreign=True, primary=False):
        P = ""
        if primary and foreign:
            P = ""
        else:
            if primary:
                P = "AND CONSTRAINT_NAME = 'PRIMARY'"
            elif foreign:
                P = "AND NOT CONSTRAINT_NAME = 'PRIMARY'"

        Q = self.ConnectAndExecute("SELECT CONSTRAINT_NAME,REFERENCED_TABLE_SCHEMA,"
                                   "TABLE_NAME,COLUMN_NAME,"
                                   "REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME "
                                   "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                                   "WHERE TABLE_SCHEMA='{}' {};".format(self.dbname, P))

        return Q

    def GetUseage(self):
        dbuseage = 0
        if self.engine_type == 'postgresql':
            # try:
            #     r = self.ConnectAndExecute("SELECT table_name, pg_size_pretty(total_bytes) AS total "
            #                            "FROM("
            #                            "SELECT *, total_bytes - index_bytes - COALESCE(toast_bytes, 0) AS table_bytes "
            #                            "FROM("
            #                            "SELECT c.oid, nspname AS table_schema, relname AS TABLE_NAME, c.reltuples AS row_estimate, pg_total_relation_size(c.oid) AS total_bytes, pg_indexes_size(c.oid) AS index_bytes, pg_total_relation_size(reltoastrelid) AS toast_bytes "
            #                            "FROM pg_class c LEFT JOIN pg_namespace n ON n.oid = c.relnamespace WHERE relkind = 'r' and nspname = 'public'"
            #                            ") a"
            #                            ") a;")
            # except Exception as e:
            #     print(e)

            return 0
        else:
            try:
                instances, msg, success = self.ConnectAndExecute(
                    "SELECT Round(Sum(data_length + index_length) / 1024 / 1024, 1) 'db_size_mb' "
                    "FROM information_schema.tables "
                    "WHERE table_schema = '{}';".format(self.dbname))

                for inst in instances:
                    dbuseage = inst[0]
            except Exception as e:
                print(e)

        return dbuseage

    def GetDatabaseQuota(self):
        return 0

    def GetConnectionString(self):
        if self.database_engine.name == 'postgresql':
            return '{}://{}:{}@{}:{}/{}'.format(self.database_engine.connection_string,
                                                self.username,
                                                self.password_if_secure,
                                                self.ip_address,
                                                self.port,
                                                self.database_name)
        else:
            if self.port=='':
                return '{}://{}:{}@{}/{}'.format(self.database_engine.connection_string,
                                                 self.username,
                                                 self.password_if_secure,
                                                 self.ip_address,
                                                 self.database_name)
            else:
                return '{}://{}:{}@{}:{}/{}'.format(self.database_engine.connection_string,
                                                 self.username,
                                                 self.password_if_secure,
                                                 self.ip_address,
                                                 self.port,
                                                 self.database_name)


    def __init__(self,svc_inst,project_owner="IT",ip_address="localhost",port=3306,username="iaas",
                 password_if_secure="",project_maintainer="IT",description="",
                 database_name="",database_engine=None):
        self.project_owner=project_owner
        self.ip_address = ip_address
        self.svc_inst_id=svc_inst
        self.port = port
        self.username = username
        self.password_if_secure=password_if_secure
        self.project_maintainer=project_maintainer
        self.description=description
        self.database_engine=database_engine
        self.database_name=database_name


    def __str__(self):
        return self.database_name

    def __repr__(self):
        return self.__str__()

class WebApp(Base):
    __tablename__ = 'web_apps'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Web Apps'

    id = Column(Integer, primary_key=True)
    name = Column(String(70))
    homepage = Column(String(100))
    ip_address = Column(String(100))
    assoc_db = Column(ForeignKey(u'database_instances.id'), nullable=True, index=True)

    database_instance = relationship(u'DatabaseInstance')

    svc_inst_id = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    svc_inst = relationship(u'SvcInstance', back_populates=u'webapps')

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

class NextcloudInstance(Base):
    __tablename__ = 'nextcloud_instances'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Nextcloud Instances'

    id = Column(Integer, primary_key=True)
    # svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    ip_address = Column(String(100))
    project_owner = Column(String(100))
    project_maintainer = Column(String(100))
    svc_inst_id = Column(Integer)
    link = Column(String(100))

    svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    svc_instance = relationship(u'SvcInstance', back_populates=u'nextclouds')

    def __str__(self):
        return self.svc_instance.instance_identifier

    def __repr__(self):
        return self.__str__()

class SvcInstance(Base):
    __tablename__ = 'svc_instances'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Service Instances'

    id = Column(Integer, primary_key=True)
    project_display_name = Column(String(30))
    instance_identifier = Column(String(70))
    # svc_type_id = Column(ForeignKey(u'services.id'), nullable=False, index=True, server_default=text("'2'"))
    group_id = Column(ForeignKey(u'groups.id'), nullable=False, index=True, server_default=text("'3'"))
    priv_user = Column(String(15))
    priv_pass = Column(String(30))
    db_ip = Column(String(100))
    schema_id = Column(Integer)

    group = relationship(u'Group')
    # svc_type = relationship(u'Service')

    webapps=relationship(u'WebApp', back_populates=u'svc_inst')
    databases=relationship(u'DatabaseInstance', back_populates=u'svc_instance')
    nextclouds=relationship(u'NextcloudInstance', back_populates=u'svc_instance')

    # group = relationship("Group",
    #                     secondary=permitted_svc.__table__,
    #                     backref="services")

    def myNCs(self):
        return NextcloudInstance.query.filter_by(svc_inst=self.id).all()
    def myVMs(self):
        return VirtualMachine.query.filter_by(svc_inst=self.id).all()

    def __str__(self):
        return self.project_display_name

    def __repr__(self):
        return self.__str__()


class permitted_svc(Base):
    __tablename__ = 'permitted_svc'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Permitted Service'
    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey(u'groups.id'), nullable=False, index=True)
    svc_id = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)
    instance_quota = Column(Integer)


    svc_inst = relationship(u'SvcInstance')
    group = relationship(u'Group')

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()


class IaasEvent(Base):
    __tablename__ = 'iaas_events'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'IAAS Events'

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    subtitle = Column(String(60))
    description = Column(String(255))
    room = Column(String(60))
    eventdate = Column(Date)
    starttime = Column(Time)
    endtime = Column(Time)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()



class Role(Base):
    __tablename__ = 'roles'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    description = Column(String(250))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Subscriber(Base):
    __tablename__ = 'subscribers'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(60))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class VirtualMachine(Base):
    __tablename__ = 'virtual_machines'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Virtual Machines'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(100))
    name = Column(String(100))
    owned_by = Column(String(100))
    svc_inst = Column(ForeignKey(u'svc_instances.id'), nullable=False, index=True)

    svc_instance = relationship(u'SvcInstance')

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class News(Base):
    __tablename__ = 'news'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'News'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()


class comment(Base):
    __tablename__ = 'comment'
    # __bind_key__ = dbconfig.db_name
    __display_name__ = 'Comment'
    id = Column(Integer, primary_key=True)
    news_id = Column(ForeignKey(u'news.id'), nullable=False, index=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Boolean)
    created_on = Column(DateTime)

    news = relationship(u'News')

    def __str__(self):
        return self.news.title

    def __repr__(self):
        return self.__str__()

